/**
 * Global error handler middleware
 */

import { Request, Response, NextFunction } from 'express';
import logger from '../config/logger';

/**
 * Global error handler middleware
 */
export const errorHandlerMiddleware = (
  err: Error,
  _req: Request,
  res: Response,
  _next: NextFunction
) => {
  logger.error(`Unhandled exception: ${err.message}`, { error: err });
  res.status(500).json({
    error: 'Internal Server Error',
    message: 'An unexpected error occurred. Please try again later.'
  });
};

