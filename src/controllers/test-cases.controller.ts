/**
 * Test cases controller - handles test case generation
 */

import { Request, Response } from 'express';
import logger from '../config/logger';
import { testCaseGenerator } from '../services';

/**
 * Generate test cases endpoint handler
 */
export const generateTestCases = (req: Request, res: Response) => {
  try {
    const data = req.body;
    logger.info(`Received test case generation request for session ${data.sessionId}`);

    const actions = data.actions || [];
    const pages = data.pages || [];
    const testCases = testCaseGenerator.generateTestCases(pages, actions);

    logger.info(`Generated ${testCases.length} test cases`);

    return res.json({
      sessionId: data.sessionId,
      testCases: testCases
    });
  } catch (error: any) {
    logger.error(`Error generating test cases: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while generating test cases'
    });
  }
};

