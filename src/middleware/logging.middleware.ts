/**
 * Request and response logging middleware
 */

import { Request, Response, NextFunction } from 'express';
import logger from '../config/logger';

/**
 * Middleware to log incoming requests
 */
export const requestLoggingMiddleware = (req: Request, _res: Response, next: NextFunction) => {
  logger.debug(`Request: ${req.method} ${req.path}`);
  if (req.is('application/json')) {
    logger.debug(`Request body size: ${JSON.stringify(req.body).length} bytes`);
  }
  next();
};

/**
 * Middleware to log outgoing responses
 */
export const responseLoggingMiddleware = (req: Request, res: Response, next: NextFunction) => {
  const originalSend = res.send;
  res.send = function(body: any) {
    logger.debug(`Response: ${res.statusCode} for ${req.method} ${req.path}`);
    return originalSend.call(this, body);
  };
  next();
};

