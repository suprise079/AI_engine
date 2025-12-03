/**
 * Server entry point - handles server startup and graceful shutdown
 */

import app from './app';
import { config } from './config/config';
import logger from './config/logger';

const PORT = config.PORT;
const HOST = config.HOST;

// Start server
const server = app.listen(PORT, HOST, () => {
  logger.info(`Starting ${config.APP_NAME} v${config.APP_VERSION}`);
  logger.info(`Environment: ${process.env.NODE_ENV || 'development'}`);
  logger.info(`Debug mode: ${config.DEBUG}`);
  logger.info(`Log level: ${config.LOG_LEVEL}`);
  logger.info(`Server starting on ${HOST}:${PORT}`);
});

// Graceful shutdown handler
const gracefulShutdown = (signal: string) => {
  logger.info(`${signal} received. Starting graceful shutdown...`);
  
  server.close(() => {
    logger.info('HTTP server closed.');
    process.exit(0);
  });

  // Force close server after 10 seconds
  setTimeout(() => {
    logger.error('Could not close connections in time, forcefully shutting down');
    process.exit(1);
  }, 10000);
};

// Listen for termination signals
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason: any, promise: Promise<any>) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error: Error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

export default server;

