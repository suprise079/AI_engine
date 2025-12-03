/**
 * Request validation middleware helpers
 */

import { Request, Response, NextFunction } from 'express';

/**
 * Validates that request body contains actions array
 */
export const validateActionsRequest = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const data = req.body;
  if (!data || !data.actions || !Array.isArray(data.actions) || data.actions.length === 0) {
    res.status(400).json({ error: 'Invalid request. Actions data is required.' });
    return;
  }
  next();
};

/**
 * Validates that request body contains pages data
 */
export const validatePagesRequest = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const data = req.body;
  if (!data || !data.pages) {
    res.status(400).json({ error: 'Invalid request. Pages data is required.' });
    return;
  }
  next();
};

/**
 * Validates that request body contains test case data
 */
export const validateTestCaseRequest = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const data = req.body;
  if (!data || !data.testCase) {
    res.status(400).json({ error: 'Invalid request. Test case data is required.' });
    return;
  }
  next();
};

/**
 * Validates that request body contains a prompt string
 */
export const validateChatRequest = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const { prompt } = req.body;
  if (!prompt || typeof prompt !== 'string') {
    res.status(400).json({ 
      error: 'Invalid request. Prompt is required and must be a string.' 
    });
    return;
  }
  next();
};

