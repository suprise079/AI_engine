import { Request, Response } from 'express';
import logger from '../../config/logger';
import { TestCasesService } from './test-cases.service';

const testCasesService = new TestCasesService();

/**
 * Generate test cases endpoint handler (feature-based).
 */
export const generateTestCases = (req: Request, res: Response) => {
  try {
    const result = testCasesService.generateTestCases(req.body);
    return res.json(result);
  } catch (error: any) {
    logger.error(`Error generating test cases: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while generating test cases',
    });
  }
};

