import logger from '../../config/logger';
import { Action, FeedbackData } from '../../types';
import { suggestionGenerator, llmRouter } from '../../services';
import { validateTimestamp } from '../../utils/timestamp-validator';
import { createBugReasoningPrompt } from '../../services/analyzer-service';
import { retrievalClient } from '../../services/retrieval-client';

export class AnalyzeService {
  /**
   * Analyze actions and generate suggestions.
   */
  async analyzeActions(data: any): Promise<{ sessionId: any; suggestions: any[] }> {
    logger.info(
      `Received analysis request for session ${data.sessionId} with ${data.actions?.length || 0} actions`
    );

    // Validate and fix timestamps
    const fixedActions = data.actions.map((action: Action) => validateTimestamp(action));

    // Generate suggestions using Llama (with RAG if tenantId provided)
    const suggestions = await suggestionGenerator.generateSuggestions(
      {
        sessionId: data.sessionId,
        actions: fixedActions,
      },
      {
        tenantId: data.tenantId,
        projectId: data.projectId,
        appId: data.appId,
        env: data.env,
        pageUrl: data.pageUrl,
      }
    );

    logger.info(`Generated ${suggestions.length} suggestions`);

    return {
      sessionId: data.sessionId,
      suggestions: suggestions.map((s) => s.toDict()),
    };
  }

  /**
   * Analyze bug reasoning with optional RAG context.
   */
  async analyzeBugReasoning(data: any): Promise<any> {
    logger.info(
      `Received bug reasoning request for session ${data.sessionId}, action ${data.actionId}`
    );

    const { sessionId, actionId, bugResult, observations, actionContext } = data;

    if (!bugResult || !observations) {
      const error = new Error('bugResult and observations are required');
      (error as any).statusCode = 400;
      throw error;
    }

    // Build base prompt for AI reasoning (live bug context)
    let prompt = createBugReasoningPrompt(bugResult, observations, actionContext);

    // Enrich bug reasoning with retrieved historical context via RAG when tenantId is available
    if (data.tenantId) {
      try {
        const queryTextParts: string[] = [];
        if (bugResult?.type) queryTextParts.push(String(bugResult.type));
        if (bugResult?.reason) queryTextParts.push(String(bugResult.reason));
        if (actionContext?.pageTitle) queryTextParts.push(String(actionContext.pageTitle));
        if (actionContext?.url) queryTextParts.push(String(actionContext.url));

        const queryText = queryTextParts.join(' ').trim() || 'bug reasoning';

        const retrieval = await retrievalClient.query({
          tenantId: data.tenantId,
          projectId: data.projectId,
          appId: data.appId,
          env: data.env,
          sessionId: typeof sessionId === 'number' ? sessionId : undefined,
          pageUrl: data.pageUrl || actionContext?.url,
          queryText,
          intent: 'BUG_TRIAGE',
          topK: 10,
          minScore: 0.4,
        });

        if (retrieval.chunks.length > 0) {
          const relatedContext = retrieval.chunks
            .slice(0, 8)
            .map((chunk) => `[${chunk.chunkType}] ${chunk.chunkText}`)
            .join('\n\n');

          prompt += `\n\n=== RELATED PAST ISSUES AND SESSIONS (for reference) ===\n${relatedContext}\n`;
        }
      } catch (e: any) {
        logger.warn(
          `BUG_TRIAGE retrieval failed, continuing without RAG context: ${e.message}`
        );
      }
    }

    // Query AI for reasoning via hybrid LLM router
    logger.info('Querying AI for bug reasoning...');
    const { text: aiResponse } = await llmRouter.generateText(prompt, {
      requestId: data.requestId,
    });

    // Parse AI response
    const reasoning = this.parseBugReasoningResponse(aiResponse);

    logger.info(`Generated bug reasoning for action ${actionId}`);

    return {
      sessionId,
      actionId,
      bugResult,
      reasoning: {
        enhancedReasoning: reasoning.reasoning || bugResult.reason,
        severity: reasoning.severity || bugResult.severity,
        recommendations: reasoning.recommendations || [],
        confidence: reasoning.confidence || 'MEDIUM',
        context: reasoning.context || {},
      },
    };
  }

  /**
   * Generate full bug report for Report Issue dialog.
   */
  async generateBugReport(data: any): Promise<any> {
    logger.info(
      `Received generate-bug-report for session ${data.sessionId}, suggestion ${data.suggestionId}`
    );

    const { bugDetection, testCaseContext, recentActions, constraints } = data;
    const maxTitleLength = constraints?.maxTitleLength ?? 100;
    const maxNotesLength = constraints?.maxNotesLength ?? 500;

    const prompt = `You are a QA expert generating a complete bug report for the Report Issue form.

BUG DETECTION:
- Type: ${bugDetection?.type || 'UNKNOWN'}
- Severity: ${bugDetection?.severity || 'MEDIUM'}
- Enhanced Reason: ${bugDetection?.enhancedReason || 'No details'}
- Signature: ${bugDetection?.signature || 'N/A'}
- Confidence: ${bugDetection?.confidence ?? 0}

TEST CASE CONTEXT:
${testCaseContext?.title ? `Title: ${testCaseContext.title}` : 'None'}
${testCaseContext?.steps?.length ? `Steps:\n${testCaseContext.steps.map((s: string, i: number) => `${i + 1}. ${s}`).join('\n')}` : ''}

RECENT ACTIONS (last actions in session):
${(recentActions || []).map((a: any, i: number) => `${i + 1}. [${a.type}] ${a.summary}${a.observationsSummary?.network ? ` | Network: ${a.observationsSummary.network}` : ''}${a.observationsSummary?.consoleErrors?.length ? ` | Console errors` : ''}${a.observationsSummary?.durationMs ? ` | ${a.observationsSummary.durationMs}ms` : ''}`).join('\n')}

CONSTRAINTS:
- Title: max ${maxTitleLength} characters
- Additional notes: max ${maxNotesLength} characters

Return ONLY valid JSON with this exact structure (no markdown, no extra text):
{
  "title": "Concise bug title (max ${maxTitleLength} chars)",
  "severity": "LOW|MEDIUM|HIGH|CRITICAL",
  "description": "Detailed description of the issue",
  "stepsToReproduce": ["Step 1", "Step 2", "Step 3"],
  "expectedBehavior": "What should have happened",
  "actualBehavior": "What actually happened",
  "additionalNotes": "Debugging hints: endpoint, console error, timing (max ${maxNotesLength} chars, no huge dumps)",
  "confidence": 0,
  "signature": "${bugDetection?.signature || ''}"
}

Rules:
- Use test case steps first in stepsToReproduce if relevant, then augment with action sequence
- expectedBehavior and actualBehavior must be present even if short
- additionalNotes: include debugging hints, where in actions it occurred, avoid huge dumps`;

    const { text: aiResponse } = await llmRouter.generateText(prompt, {
      requestId: data.requestId,
    });

    const parsed = this.parseGenerateBugReportResponse(aiResponse);
    return {
      ...parsed,
      intent: data.intent || 'BUG',
      relatedActionIds: (recentActions || []).map((a: any) => a.id).filter(Boolean),
      relatedTestCase: testCaseContext?.id
        ? {
            id: testCaseContext.id,
            title: testCaseContext.title,
            status: testCaseContext.status || '',
            updatedAt: testCaseContext.updatedAt,
            steps: testCaseContext.steps || [],
          }
        : null,
    };
  }

  private parseGenerateBugReportResponse(aiResponse: string): any {
    try {
      const jsonMatch = aiResponse.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]);
        return {
          title: parsed.title || 'Bug detected',
          severity: parsed.severity || 'MEDIUM',
          description: parsed.description || '',
          stepsToReproduce: Array.isArray(parsed.stepsToReproduce) ? parsed.stepsToReproduce : [],
          expectedBehavior: parsed.expectedBehavior || '',
          actualBehavior: parsed.actualBehavior || '',
          additionalNotes: parsed.additionalNotes || '',
          confidence: typeof parsed.confidence === 'number' ? parsed.confidence : 0,
          signature: parsed.signature || '',
        };
      }
    } catch (error) {
      logger.warn('Failed to parse generate-bug-report response');
    }
    return {
      title: 'Bug detected',
      severity: 'MEDIUM',
      description: '',
      stepsToReproduce: [],
      expectedBehavior: '',
      actualBehavior: '',
      additionalNotes: '',
      confidence: 0,
      signature: '',
    };
  }

  /**
   * Process feedback for a suggestion.
   */
  processFeedback(data: FeedbackData): { status: string } {
    logger.info(`Received feedback for suggestion ${data.suggestionId}`);

    suggestionGenerator.processFeedback(data.suggestionId, data.status, data.feedback);

    return { status: 'success' };
  }

  /**
   * Parse AI response for bug reasoning.
   */
  private parseBugReasoningResponse(aiResponse: string): any {
    try {
      // Try to extract JSON from response
      const jsonMatch = aiResponse.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }

      // Fallback: create structured response from text
      return {
        reasoning: aiResponse.trim(),
        severity: 'MEDIUM',
        recommendations: [],
        confidence: 'MEDIUM',
        context: {},
      };
    } catch (error) {
      logger.warn('Failed to parse AI reasoning response, using fallback');
      return {
        reasoning: aiResponse.trim(),
        severity: 'MEDIUM',
        recommendations: [],
        confidence: 'MEDIUM',
        context: {},
      };
    }
  }
}

