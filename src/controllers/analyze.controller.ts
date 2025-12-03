/**
 * Analysis controller - handles action analysis and feedback
 */

import { Request, Response } from 'express';
import logger from '../config/logger';
import { Action, FeedbackData } from '../types';
import { suggestionGenerator } from '../services';
import { validateTimestamp } from '../utils/timestamp-validator';

/**
 * Analyze actions endpoint handler
 */
export const analyzeActions = async (req: Request, res: Response) => {
  try {
    const data = req.body;
    logger.info(`Received analysis request for session ${data.sessionId} with ${data.actions?.length || 0} actions`);

    // Validate and fix timestamps
    const fixedActions = data.actions.map((action: Action) => validateTimestamp(action));

    // Generate suggestions using DeepSeek
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

