import { Request, Response } from 'express';
import logger from '../../config/logger';
import { AnalyzeService } from './analyze.service';

const analyzeService = new AnalyzeService();

/**
 * Analyze actions endpoint handler (feature-based).
 */
export const analyzeActions = async (req: Request, res: Response) => {
  try {
    const result = await analyzeService.analyzeActions(req.body);
    return res.json(result);
  } catch (error: any) {
    logger.error(`Error analyzing actions: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while analyzing actions',
    });
  }
};

/**
 * Analyze bug reasoning endpoint handler.
 */
export const analyzeBugReasoning = async (req: Request, res: Response) => {
  try {
    const result = await analyzeService.analyzeBugReasoning(req.body);
    return res.json(result);
  } catch (error: any) {
    if (error.statusCode === 400) {
      return res.status(400).json({
        error: 'Bad Request',
        message: error.message,
      });
    }

    logger.error(`Error analyzing bug reasoning: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while analyzing bug reasoning',
    });
  }
};

/**
 * Generate full bug report endpoint handler.
 */
export const generateBugReport = async (req: Request, res: Response) => {
  try {
    const result = await analyzeService.generateBugReport(req.body);
    return res.json(result);
  } catch (error: any) {
    logger.error(`Error generating bug report: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while generating bug report',
    });
  }
};

/**
 * Process feedback endpoint handler.
 */
export const processFeedback = (req: Request, res: Response) => {
  try {
    const result = analyzeService.processFeedback(req.body);
    return res.json(result);
  } catch (error: any) {
    logger.error(`Error processing feedback: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while processing feedback',
    });
  }
};

