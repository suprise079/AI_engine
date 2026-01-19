/**
 * Analysis controller - handles action analysis and feedback
 */

import { Request, Response } from 'express';
import logger from '../config/logger';
import { Action, FeedbackData } from '../types';
import { suggestionGenerator } from '../services';
import { validateTimestamp } from '../utils/timestamp-validator';
import { OllamaService } from '../services/ollama-service';
import { config } from '../config/config';

/**
 * Analyze actions endpoint handler
 */
export const analyzeActions = async (req: Request, res: Response) => {
  try {
    const data = req.body;
    logger.info(`Received analysis request for session ${data.sessionId} with ${data.actions?.length || 0} actions`);

    // Validate and fix timestamps
    const fixedActions = data.actions.map((action: Action) => validateTimestamp(action));

    // Generate suggestions using Llama
    const suggestions = await suggestionGenerator.generateSuggestions({
      sessionId: data.sessionId,
      actions: fixedActions
    });

    logger.info(`Generated ${suggestions.length} suggestions`);

    return res.json({
      sessionId: data.sessionId,
      suggestions: suggestions.map(s => s.toDict())
    });
  } catch (error: any) {
    logger.error(`Error analyzing actions: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while analyzing actions'
    });
  }
};

/**
 * Analyze bug reasoning endpoint handler
 * Provides AI reasoning for detected bugs based on observations
 */
export const analyzeBugReasoning = async (req: Request, res: Response) => {
  try {
    const data = req.body;
    logger.info(`Received bug reasoning request for session ${data.sessionId}, action ${data.actionId}`);

    const {
      sessionId,
      actionId,
      bugResult,
      observations,
      actionContext
    } = data;

    if (!bugResult || !observations) {
      return res.status(400).json({
        error: 'Bad Request',
        message: 'bugResult and observations are required'
      });
    }

    // Create prompt for AI reasoning
    const prompt = createBugReasoningPrompt(bugResult, observations, actionContext);

    // Query AI for reasoning
    const ollamaService = new OllamaService(config.OLLAMA_MODEL, config.OLLAMA_TIMEOUT);
    logger.info('Querying AI for bug reasoning...');
    const aiResponse = await ollamaService.query(prompt);

    // Parse AI response
    const reasoning = parseBugReasoningResponse(aiResponse);

    logger.info(`Generated bug reasoning for action ${actionId}`);

    return res.json({
      sessionId,
      actionId,
      bugResult,
      reasoning: {
        enhancedReasoning: reasoning.reasoning || bugResult.reason,
        severity: reasoning.severity || bugResult.severity,
        recommendations: reasoning.recommendations || [],
        confidence: reasoning.confidence || 'MEDIUM',
        context: reasoning.context || {}
      }
    });
  } catch (error: any) {
    logger.error(`Error analyzing bug reasoning: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while analyzing bug reasoning'
    });
  }
};

/**
 * Parse AI response for bug reasoning
 */
function parseBugReasoningResponse(aiResponse: string): any {
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
      context: {}
    };
  } catch (error) {
    logger.warn('Failed to parse AI reasoning response, using fallback');
    return {
      reasoning: aiResponse.trim(),
      severity: 'MEDIUM',
      recommendations: [],
      confidence: 'MEDIUM',
      context: {}
    };
  }
}

/**
 * Process feedback endpoint handler
 */
export const processFeedback = (req: Request, res: Response) => {
  try {
    const data: FeedbackData = req.body;
    logger.info(`Received feedback for suggestion ${data.suggestionId}`);

    suggestionGenerator.processFeedback(
      data.suggestionId,
      data.status,
      data.feedback
    );

    return res.json({ status: 'success' });
  } catch (error: any) {
    logger.error(`Error processing feedback: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while processing feedback'
    });
  }
};
