/**
 * Suggestion Generator with Llama AI integration
 * Generates testing suggestions based on action sequences using Llama via Ollama
 */

import { TestSuggestionModel } from '../models';
import { ActionSequence } from '../types';
import { OllamaService } from './ollama-service';
import logger from '../config/logger';
import { config } from '../config/config';

export class SuggestionGenerator {
  private ollamaService: OllamaService;
  private feedbackHistory: Array<{
    suggestionId: number | string;
    status: string;
    feedback?: string;
    timestamp: string;
  }> = [];
  private sessionSuggestions: Record<string | number, Set<string>> = {};

  constructor(_learningMode: boolean = true) {
    // learningMode reserved for future use
    this.ollamaService = new OllamaService(config.OLLAMA_MODEL, config.OLLAMA_TIMEOUT);
  }

  async generateSuggestions(actionSequence: ActionSequence): Promise<TestSuggestionModel[]> {
    logger.info(`Generating suggestions for session ${actionSequence.sessionId} with ${actionSequence.actions.length} actions`);

    const sessionId = actionSequence.sessionId;
    if (!this.sessionSuggestions[sessionId]) {
      this.sessionSuggestions[sessionId] = new Set();
    }

    try {
      // Create comprehensive prompt for Llama
      const prompt = this.createAnalysisPrompt(actionSequence);

      // Query Llama via Ollama
      logger.info('Querying Llama for software issue analysis...');
      const aiResponse = await this.ollamaService.query(prompt);

      // Parse AI response into suggestions
      const suggestions = this.parseAIResponse(aiResponse, actionSequence);

      // Filter out duplicates
      const uniqueSuggestions: TestSuggestionModel[] = [];
      for (const suggestion of suggestions) {
        const suggestionKey = `${suggestion.title}:${suggestion.suggestionType}`;
        if (!this.sessionSuggestions[sessionId].has(suggestionKey)) {
          uniqueSuggestions.push(suggestion);
          this.sessionSuggestions[sessionId].add(suggestionKey);
        }
      }

      // Sort by priority
      const sortedSuggestions = this.prioritizeSuggestions(uniqueSuggestions);

      // Limit to top 10 suggestions
      const finalSuggestions = sortedSuggestions.slice(0, 10);
      logger.info(`Generated ${finalSuggestions.length} unique suggestions`);

      return finalSuggestions;
    } catch (error) {
      logger.error(`Error generating suggestions: ${error}`);
      // Return fallback suggestions if AI fails
      return this.generateFallbackSuggestions(actionSequence);
    }
  }

  private createAnalysisPrompt(actionSequence: ActionSequence): string {
    const actionsSummary = this.summarizeActions(actionSequence.actions);
    const uniquePages = actionSequence.actions
      .map(a => a.url || a.pageTitle)
      .filter((v, i, arr) => v && arr.indexOf(v) === i)
      .slice(0, 10);

    // Extract observations summary
    const observationsSummary = this.summarizeObservations(actionSequence.actions);

    return `You are a software testing expert analyzing a test session with detailed observations. Analyze the following action sequence and identify ALL possible software issues, testing gaps, and improvement opportunities.

ACTION SEQUENCE SUMMARY:
${actionsSummary}

OBSERVATIONS DATA:
${observationsSummary}

UNIQUE PAGES VISITED: ${uniquePages.join(', ') || 'N/A'}

Analyze this sequence comprehensively for:
1. SECURITY vulnerabilities (authentication, authorization, input validation, data exposure, XSS, CSRF, injection attacks)
2. PERFORMANCE issues (slow page loads, inefficient operations, memory leaks, resource bottlenecks)
3. ACCESSIBILITY problems (keyboard navigation, screen reader support, ARIA labels, color contrast)
4. USABILITY concerns (confusing flows, unclear error messages, poor navigation, missing feedback)
5. EDGE CASES (boundary conditions, error handling, null/empty inputs, special characters, very long inputs)
6. VALIDATION gaps (missing client-side validation, insufficient server-side validation, format checks)
7. ERROR HANDLING issues (unclear error messages, missing error recovery, unhandled exceptions)
8. DATA INTEGRITY concerns (data persistence, transaction handling, concurrent access, data corruption)
9. BUGS DETECTED FROM OBSERVATIONS (network errors, console errors, UI changes, timing issues)

For each issue found, provide:
- Title: Short, descriptive title
- Description: Detailed explanation of the issue
- Type: One of SECURITY, PERFORMANCE, ACCESSIBILITY, USABILITY, EDGE_CASE, VALIDATION, ERROR_HANDLING, DATA_INTEGRITY, BUG, or OTHER
- Priority: HIGH, MEDIUM, or LOW
- Suggested Action: Specific testing action to verify or address the issue

Format your response as a JSON array of objects with these exact fields:
[
  {
    "title": "Issue title",
    "description": "Detailed description",
    "suggestionType": "SECURITY|PERFORMANCE|ACCESSIBILITY|USABILITY|EDGE_CASE|VALIDATION|ERROR_HANDLING|DATA_INTEGRITY|BUG|OTHER",
    "priority": "HIGH|MEDIUM|LOW",
    "suggestedAction": "Specific action to take"
  }
]

Provide 5-15 suggestions covering different aspects. Focus on actionable, testable issues. Pay special attention to the observations data which contains real-time evidence of bugs (network errors, console errors, UI issues, performance problems).`;
  }

  private summarizeActions(actions: Array<{ actionType: string; url?: string; pageTitle?: string; elementSelector?: string; inputData?: string }>): string {
    const actionCounts: Record<string, number> = {};
    const pageTransitions: string[] = [];
    const formSubmissions: string[] = [];
    const inputFields: string[] = [];

    for (const action of actions) {
      actionCounts[action.actionType] = (actionCounts[action.actionType] || 0) + 1;

      if (action.actionType === 'NAVIGATE' && (action.url || action.pageTitle)) {
        pageTransitions.push(action.url || action.pageTitle || '');
      }

      if (action.actionType === 'SUBMIT') {
        formSubmissions.push(action.elementSelector || 'unknown form');
      }

      if (action.actionType === 'TYPE' && action.elementSelector) {
        inputFields.push(action.elementSelector);
      }
    }

    let summary = `Total actions: ${actions.length}\n`;
    summary += `Action types: ${Object.entries(actionCounts).map(([type, count]) => `${type}(${count})`).join(', ')}\n`;
    
    if (pageTransitions.length > 0) {
      summary += `Pages visited: ${pageTransitions.slice(0, 5).join(', ')}${pageTransitions.length > 5 ? '...' : ''}\n`;
    }

    if (formSubmissions.length > 0) {
      summary += `Forms submitted: ${formSubmissions.length}\n`;
    }

    if (inputFields.length > 0) {
      summary += `Input fields used: ${inputFields.length}\n`;
    }

    return summary;
  }

  private summarizeObservations(actions: Array<{ sequenceNumber?: number; actionType: string; observations?: string }>): string {
    const observations: string[] = [];
    let networkErrors = 0;
    let consoleErrors = 0;
    let slowActions = 0;
    let noUIChangeActions = 0;

    for (const action of actions) {
      if (action.observations) {
        try {
          const obs = JSON.parse(action.observations);
          
          // Count network errors
          if (obs.network && Array.isArray(obs.network)) {
            const errors = obs.network.filter((n: any) => n.error || (n.status >= 400));
            networkErrors += errors.length;
            if (errors.length > 0) {
              observations.push(`Action ${action.sequenceNumber || '?'} (${action.actionType}): ${errors.length} network error(s) - ${errors.map((e: any) => `${e.method} ${e.url} (${e.status || 'failed'})`).join(', ')}`);
            }
          }

          // Count console errors
          if (obs.consoleErrors && Array.isArray(obs.consoleErrors)) {
            consoleErrors += obs.consoleErrors.length;
            if (obs.consoleErrors.length > 0) {
              observations.push(`Action ${action.sequenceNumber || '?'} (${action.actionType}): ${obs.consoleErrors.length} console error(s) - ${obs.consoleErrors.map((e: any) => e.message).slice(0, 3).join('; ')}`);
            }
          }

          // Check for slow actions
          if (obs.timing && obs.timing.actionDurationMs && obs.timing.actionDurationMs > 3000) {
            slowActions++;
            observations.push(`Action ${action.sequenceNumber || '?'} (${action.actionType}): Slow response (${obs.timing.actionDurationMs}ms)`);
          }

          // Check for no UI change
          if (obs.ui && obs.ui.pageChanged === false && action.actionType !== 'TYPE') {
            noUIChangeActions++;
            observations.push(`Action ${action.sequenceNumber || '?'} (${action.actionType}): No UI change detected after action`);
          }
        } catch (e) {
          // Invalid JSON, skip
        }
      }
    }

    let summary = `Total observations analyzed: ${actions.filter(a => a.observations).length} actions\n`;
    if (networkErrors > 0) summary += `Network errors detected: ${networkErrors}\n`;
    if (consoleErrors > 0) summary += `Console errors detected: ${consoleErrors}\n`;
    if (slowActions > 0) summary += `Slow actions (>3s): ${slowActions}\n`;
    if (noUIChangeActions > 0) summary += `Actions with no UI change: ${noUIChangeActions}\n`;
    
    if (observations.length > 0) {
      summary += `\nDetailed observations:\n${observations.slice(0, 20).join('\n')}`;
      if (observations.length > 20) summary += `\n... and ${observations.length - 20} more`;
    } else {
      summary += `No significant issues detected in observations.`;
    }

    return summary;
  }

  private parseAIResponse(aiResponse: string, _actionSequence: ActionSequence): TestSuggestionModel[] {
    const suggestions: TestSuggestionModel[] = [];

    try {
      // Try to extract JSON from the response
      let jsonStr = aiResponse.trim();

      // Remove markdown code blocks if present
      jsonStr = jsonStr.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();

      // Try to find JSON array in the response
      const jsonMatch = jsonStr.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        jsonStr = jsonMatch[0];
      }

      const parsed = JSON.parse(jsonStr);
      
      if (Array.isArray(parsed)) {
        for (const item of parsed) {
          if (item.title && item.description && item.suggestionType && item.priority) {
            suggestions.push(new TestSuggestionModel(
              item.title,
              item.description,
              item.suggestionType.toUpperCase(),
              item.priority.toUpperCase() as 'HIGH' | 'MEDIUM' | 'LOW',
              item.suggestedAction
            ));
          }
        }
      }
    } catch (error) {
      logger.warn(`Failed to parse AI response as JSON: ${error}. Attempting text parsing...`);
      // Fallback: try to parse as text
      return this.parseTextResponse(aiResponse);
    }

    return suggestions;
  }

  private parseTextResponse(text: string): TestSuggestionModel[] {
    const suggestions: TestSuggestionModel[] = [];
    
    // Try to extract suggestions from text format
    const lines = text.split('\n');
    let currentSuggestion: Partial<{ title: string; description: string; type: string; priority: string; action: string }> | null = null;

    for (const line of lines) {
      const trimmed = line.trim();
      
      if (trimmed.match(/^\d+[\.\)]/) || trimmed.toLowerCase().includes('title:')) {
        if (currentSuggestion && currentSuggestion.title) {
          suggestions.push(this.createSuggestionFromParts(currentSuggestion));
        }
        currentSuggestion = {};
        const titleMatch = trimmed.match(/title:\s*(.+)/i) || trimmed.match(/^\d+[\.\)]\s*(.+)/);
        if (titleMatch) {
          currentSuggestion.title = titleMatch[1].trim();
        }
      } else if (trimmed.toLowerCase().includes('description:')) {
        const descMatch = trimmed.match(/description:\s*(.+)/i);
        if (descMatch && currentSuggestion) {
          currentSuggestion.description = descMatch[1].trim();
        }
      } else if (trimmed.toLowerCase().includes('type:') || trimmed.toLowerCase().includes('category:')) {
        const typeMatch = trimmed.match(/(?:type|category):\s*(.+)/i);
        if (typeMatch && currentSuggestion) {
          currentSuggestion.type = typeMatch[1].trim().toUpperCase();
        }
      } else if (trimmed.toLowerCase().includes('priority:')) {
        const priorityMatch = trimmed.match(/priority:\s*(.+)/i);
        if (priorityMatch && currentSuggestion) {
          currentSuggestion.priority = priorityMatch[1].trim().toUpperCase();
        }
      } else if (currentSuggestion && !currentSuggestion.description) {
        // Accumulate description lines
        if (!currentSuggestion.description) {
          currentSuggestion.description = trimmed;
        } else {
          currentSuggestion.description += ' ' + trimmed;
        }
      }
    }

    if (currentSuggestion && currentSuggestion.title) {
      suggestions.push(this.createSuggestionFromParts(currentSuggestion));
    }

    return suggestions.length > 0 ? suggestions : this.generateFallbackSuggestions({ sessionId: 0, actions: [] });
  }

  private createSuggestionFromParts(parts: Partial<{ title: string; description: string; type: string; priority: string; action: string }>): TestSuggestionModel {
    return new TestSuggestionModel(
      parts.title || 'Testing Suggestion',
      parts.description || 'Review this area for potential issues',
      parts.type || 'OTHER',
      (parts.priority || 'MEDIUM') as 'HIGH' | 'MEDIUM' | 'LOW',
      parts.action
    );
  }

  private generateFallbackSuggestions(actionSequence: ActionSequence): TestSuggestionModel[] {
    logger.info('Generating fallback suggestions');
    const suggestions: TestSuggestionModel[] = [];

    // Basic validation suggestion
    suggestions.push(new TestSuggestionModel(
      'Explore validation scenarios',
      'Try testing with invalid inputs to verify validation behavior.',
      'VALIDATION',
      'MEDIUM',
      'Test with empty values, very long inputs, and special characters to ensure proper validation.'
    ));

    // Security suggestion if there are forms
    const hasForms = actionSequence.actions.some(a => a.actionType === 'SUBMIT' || a.actionType === 'TYPE');
    if (hasForms) {
      suggestions.push(new TestSuggestionModel(
        'Test input sanitization',
        'Verify that user inputs are properly sanitized to prevent injection attacks.',
        'SECURITY',
        'HIGH',
        'Try inputs with SQL injection patterns, XSS scripts, and special characters.'
      ));
    }

    return suggestions;
  }

  private prioritizeSuggestions(suggestions: TestSuggestionModel[]): TestSuggestionModel[] {
    const priorityValues: Record<string, number> = { HIGH: 3, MEDIUM: 2, LOW: 1 };

    return suggestions.sort((a, b) => {
      const scoreA = priorityValues[a.priority] || 0;
      const scoreB = priorityValues[b.priority] || 0;
      return scoreB - scoreA;
    });
  }

  processFeedback(suggestionId: number | string, status: string, feedback?: string): boolean {
    const feedbackData = {
      suggestionId,
      status,
      feedback,
      timestamp: new Date().toISOString()
    };

    this.feedbackHistory.push(feedbackData);
    logger.info(`Received feedback for suggestion ${suggestionId}: status=${status}`);

    return true;
  }
}

