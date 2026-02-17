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
 * Validates that request body contains a prompt/message string for chat.
 * Accepts: prompt (legacy), message (RAG payload), or content (backend DTO field).
 */
export const validateChatRequest = (
  req: Request,
  res: Response,
  next: NextFunction
): void => {
  const body = req.body;
  if (!body || typeof body !== 'object') {
    res.status(400).json({
      error: 'Invalid request. Body must be a JSON object with prompt, message, or content (non-empty string).'
    });
    return;
  }

  const prompt = body.prompt;
  const message = body.message ?? body.content; // backend sends "message", DTO uses "content"

  const hasLegacyPrompt = typeof prompt === 'string' && prompt.trim().length > 0;
  const hasMessage = typeof message === 'string' && message.trim().length > 0;

  if (!hasLegacyPrompt && !hasMessage) {
    res.status(400).json({
      error: 'Invalid request. Either prompt (legacy), message, or content is required and must be a non-empty string.'
    });
    return;
  }
  next();
};

