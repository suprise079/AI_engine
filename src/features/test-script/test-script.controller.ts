import { Request, Response } from 'express';
import logger from '../../config/logger';
import { TestScriptService } from './test-script.service';

const testScriptService = new TestScriptService();

/**
 * Generate script endpoint handler (feature-based).
 */
export const generateScript = (req: Request, res: Response) => {
  try {
    const result = testScriptService.generateScript(req.body);
    return res.json(result);
  } catch (error: any) {
    logger.error(`Error generating script: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while generating script',
    });
  }
};

