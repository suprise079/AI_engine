/**
 * Prompt Composer - Combines live context, retrieved chunks, and task instructions
 * Enforces token budget and handles overflow
 */

import { ActionSequence } from '../types';
import { retrievalClient, ContextChunk } from './retrieval-client';
import logger from '../config/logger';

export interface PromptCompositionOptions {
  sessionId: number | string;
  tenantId: number;
  projectId?: number;
  appId?: number;
  env?: string;
  pageUrl?: string;
  intent: 'SUGGEST_NEXT_TESTS' | 'CREATE_CANDIDATE_TEST_CASES' | 'BUG_TRIAGE' | 'GENERATE_AUTOMATION_SKELETON';
  actionSequence: ActionSequence;
  maxTokens?: number;
}

export interface ComposedPrompt {
  prompt: string;
  liveContextTokens: number;
  retrievedContextTokens: number;
  taskInstructionTokens: number;
  totalTokens: number;
  chunksUsed: number;
}

/**
 * Simple token estimation (~4 chars = 1 token)
 */
function estimateTokens(text: string): number {
  if (!text) return 0;
  return Math.ceil(text.length / 4.0);
}

/**
 * Summarize chunks if they exceed token budget
 */
function summarizeChunks(chunks: ContextChunk[], maxTokens: number): string {
  let totalTokens = 0;
  const includedChunks: string[] = [];

  // Include chunks in order of score (highest first) until budget is reached
  for (const chunk of chunks) {
    const chunkTokens = chunk.tokenCount || estimateTokens(chunk.chunkText);
    if (totalTokens + chunkTokens <= maxTokens) {
      includedChunks.push(`[${chunk.chunkType}] ${chunk.chunkText}`);
      totalTokens += chunkTokens;
    } else {
      // Try to include partial chunk if there's room
      const remainingTokens = maxTokens - totalTokens;
      if (remainingTokens > 50) { // Only if meaningful space remains
        const words = chunk.chunkText.split(' ');
        const wordsToInclude = Math.floor((remainingTokens * 4) / 10); // Rough estimate
        const partialText = words.slice(0, wordsToInclude).join(' ') + '...';
        includedChunks.push(`[${chunk.chunkType}] ${partialText}`);
      }
      break;
    }
  }

  return includedChunks.join('\n\n');
}

/**
 * Compose prompt with live context, retrieved chunks, and task instruction
 */
export async function composePrompt(options: PromptCompositionOptions): Promise<ComposedPrompt> {
  const liveContextMaxTokens = 800;
  const retrievedContextMaxTokens = 1200;

  logger.info(`Composing prompt for session ${options.sessionId}, intent: ${options.intent}`);

  // 1. Build live context (last 15-30 actions)
  const liveContext = buildLiveContext(options.actionSequence, liveContextMaxTokens);
  const liveContextTokens = estimateTokens(liveContext);

  // 2. Retrieve relevant chunks
  const queryText = buildQueryText(options.actionSequence, options.intent);
  const retrievalResponse = await retrievalClient.query({
    tenantId: options.tenantId,
    projectId: options.projectId,
    appId: options.appId,
    env: options.env,
    sessionId: typeof options.sessionId === 'number' ? options.sessionId : undefined,
    pageUrl: options.pageUrl,
    queryText,
    intent: options.intent,
    topK: 15,
    minScore: 0.5,
  });

  // 3. Build retrieved context (respect token budget)
  const retrievedContext = summarizeChunks(retrievalResponse.chunks, retrievedContextMaxTokens);
  const retrievedContextTokens = estimateTokens(retrievedContext);

  // 4. Build task instruction
  const taskInstruction = buildTaskInstruction(options.intent);
  const taskInstructionTokensActual = estimateTokens(taskInstruction);

  // 5. Compose final prompt
  const prompt = `${taskInstruction}

=== LIVE CONTEXT (Current Session) ===
${liveContext}

=== RETRIEVED CONTEXT (Similar Past Sessions/Issues) ===
${retrievedContext || 'No similar context found.'}

=== ANALYSIS REQUEST ===
Based on the live context and retrieved context above, provide your analysis.`;

  const totalTokens = liveContextTokens + retrievedContextTokens + taskInstructionTokensActual;

  logger.info(`Composed prompt: ${totalTokens} tokens (live: ${liveContextTokens}, retrieved: ${retrievedContextTokens}, instruction: ${taskInstructionTokensActual})`);

  return {
    prompt,
    liveContextTokens,
    retrievedContextTokens,
    taskInstructionTokens: taskInstructionTokensActual,
    totalTokens,
    chunksUsed: retrievalResponse.chunks.length,
  };
}

/**
 * Build live context from action sequence (last 15-30 actions)
 */
function buildLiveContext(actionSequence: ActionSequence, maxTokens: number): string {
  const actions = actionSequence.actions || [];
  const recentActions = actions.slice(-30); // Last 30 actions

  const summary: string[] = [];
  summary.push(`Session ID: ${actionSequence.sessionId}`);
  summary.push(`Total Actions: ${actions.length}`);
  summary.push(`Recent Actions (last ${recentActions.length}):`);

  // Summarize recent actions
  const actionSummaries: string[] = [];
  for (const action of recentActions) {
    const actionSummary = formatAction(action);
    if (actionSummary) {
      actionSummaries.push(actionSummary);
    }
  }

  // Truncate if too long
  let contextText = summary.join('\n') + '\n' + actionSummaries.join('\n');
  let tokens = estimateTokens(contextText);

  if (tokens > maxTokens) {
    // Keep reducing actions until within budget
    for (let i = actionSummaries.length - 1; i >= 0 && tokens > maxTokens; i--) {
      actionSummaries.pop();
      contextText = summary.join('\n') + '\n' + actionSummaries.join('\n');
      tokens = estimateTokens(contextText);
    }
  }

  // Add latest observations/errors if available
  const latestAction = recentActions[recentActions.length - 1];
  if (latestAction?.observations) {
    try {
      const obs = JSON.parse(latestAction.observations);
      const errors: string[] = [];
      
      if (obs.consoleErrors && Array.isArray(obs.consoleErrors) && obs.consoleErrors.length > 0) {
        errors.push(`Console Errors: ${obs.consoleErrors.slice(0, 3).map((e: any) => e.message).join('; ')}`);
      }
      
      if (obs.network && Array.isArray(obs.network)) {
        const networkErrors = obs.network.filter((n: any) => n.error || (n.status >= 400));
        if (networkErrors.length > 0) {
          errors.push(`Network Errors: ${networkErrors.length} failed requests`);
        }
      }

      if (errors.length > 0) {
        contextText += '\n\nLatest Observations:\n' + errors.join('\n');
      }
    } catch (e) {
      // Invalid JSON, skip
    }
  }

  // Add current page info
  if (latestAction?.url || latestAction?.pageTitle) {
    contextText += `\n\nCurrent Page: ${latestAction.pageTitle || latestAction.url || 'Unknown'}`;
    if (latestAction.url) {
      contextText += ` (${latestAction.url})`;
    }
  }

  return contextText;
}

/**
 * Format a single action for display
 */
function formatAction(action: any): string {
  const parts: string[] = [];
  
  if (action.sequenceNumber !== undefined) {
    parts.push(`#${action.sequenceNumber}`);
  }
  
  parts.push(action.actionType || 'UNKNOWN');
  
  if (action.pageTitle) {
    parts.push(`on "${action.pageTitle}"`);
  } else if (action.url) {
    parts.push(`at ${action.url}`);
  }
  
  if (action.elementSelector) {
    parts.push(`(${action.elementSelector})`);
  }
  
  if (action.inputData) {
    parts.push(`input: "${action.inputData.substring(0, 50)}"`);
  }

  return parts.join(' ');
}

/**
 * Build query text for retrieval based on action sequence and intent
 */
function buildQueryText(actionSequence: ActionSequence, intent: string): string {
  const actions = actionSequence.actions || [];
  const recentActions = actions.slice(-10); // Last 10 actions for query

  const queryParts: string[] = [];

  // Add intent-specific keywords
  switch (intent) {
    case 'SUGGEST_NEXT_TESTS':
      queryParts.push('testing suggestions', 'test cases', 'exploratory testing');
      break;
    case 'CREATE_CANDIDATE_TEST_CASES':
      queryParts.push('test case creation', 'test steps', 'test scenarios');
      break;
    case 'BUG_TRIAGE':
      queryParts.push('bug issues', 'defects', 'errors');
      break;
    case 'GENERATE_AUTOMATION_SKELETON':
      queryParts.push('automation', 'test scripts', 'selenium playwright');
      break;
  }

  // Add recent action types
  const actionTypes = recentActions.map(a => a.actionType).filter(Boolean);
  if (actionTypes.length > 0) {
    queryParts.push(...actionTypes.slice(0, 5));
  }

  // Add page context
  const latestAction = recentActions[recentActions.length - 1];
  if (latestAction?.pageTitle) {
    queryParts.push(latestAction.pageTitle);
  }

  return queryParts.join(' ');
}

/**
 * Build task instruction based on intent
 */
function buildTaskInstruction(intent: string): string {
  switch (intent) {
    case 'SUGGEST_NEXT_TESTS':
      return `You are a software testing expert analyzing a test session. Based on the live context and retrieved context, suggest the next testing actions to take. Focus on:
1. SECURITY vulnerabilities
2. PERFORMANCE issues
3. ACCESSIBILITY problems
4. USABILITY concerns
5. EDGE CASES
6. VALIDATION gaps
7. ERROR HANDLING issues
8. DATA INTEGRITY concerns
9. BUGS detected from observations

Provide actionable, testable suggestions.`;

    case 'CREATE_CANDIDATE_TEST_CASES':
      return `You are a test case author. Based on the live context and retrieved context, create candidate test cases. Each test case should include:
- Title
- Preconditions (if applicable)
- Steps (action + expected result per step)
- Expected result
- Tags/category

Format as JSON array.`;

    case 'BUG_TRIAGE':
      return `You are a bug triage expert. Based on the live context and retrieved context, analyze the detected issues. Provide:
- Enhanced reasoning for each bug
- Severity assessment
- Recommendations for fixing
- Confidence level

Focus on patterns from similar past issues.`;

    case 'GENERATE_AUTOMATION_SKELETON':
      return `You are a test automation engineer. Based on the live context and retrieved context, generate an automation test skeleton. Include:
- Page Object Model structure
- Test steps with locators
- Assertions
- Error handling

Use the patterns from similar test cases.`;

    default:
      return `Analyze the provided context and provide relevant insights.`;
  }
}
