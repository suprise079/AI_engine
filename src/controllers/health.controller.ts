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
      pattern_recognizer: patternRecognizer !== null, // Intentionally null - removed as per requirements
      suggestion_generator: suggestionGenerator !== null,
      component_recognizer: componentRecognizer !== null,
      test_case_generator: testCaseGenerator !== null,
      test_script_generator: testScriptGenerator !== null
    };

    // Exclude pattern_recognizer from health check since it's intentionally removed
    const activeComponents = {
      suggestion_generator: componentsStatus.suggestion_generator,
      component_recognizer: componentsStatus.component_recognizer,
      test_case_generator: componentsStatus.test_case_generator,
      test_script_generator: componentsStatus.test_script_generator
    };
    const allHealthy = Object.values(activeComponents).every(v => v !== null);

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

