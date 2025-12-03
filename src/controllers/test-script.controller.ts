/**
 * Test script controller - handles test script generation
 */

import { Request, Response } from 'express';
import logger from '../config/logger';
import { testScriptGenerator } from '../services';

/**
 * Generate script endpoint handler
 */
export const generateScript = (req: Request, res: Response) => {
  try {
    const data = req.body;
    logger.info('Received script generation request');

    const testCase = data.testCase;
    const framework = data.framework || 'selenium';
    const testData = data.testData || {};

    const script = testScriptGenerator.generateScript(testCase, testData, framework);
    logger.info(`Generated ${framework} script`);

    const language = framework === 'selenium' ? 'java' : 'javascript';

    return res.json({
      script: script,
      language: language,
      framework: framework
    });
  } catch (error: any) {
    logger.error(`Error generating script: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while generating script'
    });
  }
};

