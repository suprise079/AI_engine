/**
 * Health check controller
 */

import { Request, Response } from 'express';
import { config } from '../config/config';
import logger from '../config/logger';
import { patternRecognizer, suggestionGenerator, componentRecognizer, testCaseGenerator, testScriptGenerator } from '../services';

/**
 * Health check endpoint handler
 */
export const getHealth = (_req: Request, res: Response) => {
  try {
    const componentsStatus = {
      pattern_recognizer: patternRecognizer !== null,
      suggestion_generator: suggestionGenerator !== null,
      component_recognizer: componentRecognizer !== null,
      test_case_generator: testCaseGenerator !== null,
      test_script_generator: testScriptGenerator !== null
    };

    const allHealthy = Object.values(componentsStatus).every(v => v !== null);

    res.status(allHealthy ? 200 : 503).json({
      status: allHealthy ? 'healthy' : 'degraded',
      version: config.APP_VERSION,
      components: componentsStatus,
      timestamp: new Date().toISOString()
    });
  } catch (error: any) {
    logger.error(`Health check failed: ${error.message}`, { error });
    res.status(503).json({
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
};

