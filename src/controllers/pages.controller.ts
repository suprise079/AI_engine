/**
 * Pages controller - handles page detection
 */

import { Request, Response } from 'express';
import logger from '../config/logger';
import { Action } from '../types';
import { componentRecognizer } from '../services';
import { validateTimestamp } from '../utils/timestamp-validator';

/**
 * Detect pages endpoint handler
 */
export const detectPages = (req: Request, res: Response) => {
  try {
    const data = req.body;
    logger.info(`Received page detection request for session ${data.sessionId}`);

    // Validate and fix timestamps
    const fixedActions = data.actions.map((action: Action) => validateTimestamp(action));

    // Use ComponentRecognizer to identify pages and components
    const pages = componentRecognizer.identifyPagesAndComponents(fixedActions);
    logger.info(`Identified ${pages.length} pages with components`);

    return res.json({
      sessionId: data.sessionId,
      pages: pages
    });
  } catch (error: any) {
    logger.error(`Error detecting pages: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while detecting pages'
    });
  }
};

