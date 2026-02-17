/**
 * Main Express application for AI Engine
 */

import express from 'express';
import { config } from './config/config';
import { corsMiddleware } from './middleware/cors.middleware';
import { requestLoggingMiddleware, responseLoggingMiddleware } from './middleware/logging.middleware';
import { errorHandlerMiddleware } from './middleware/error-handler.middleware';
import { registerFeatureRoutes } from './features';

const app = express();

// Apply middleware in order
app.use(corsMiddleware);
app.use(express.json({ limit: `${config.MAX_CONTENT_LENGTH}b` }));
app.use(requestLoggingMiddleware);
app.use(responseLoggingMiddleware);

// Register all feature routes
registerFeatureRoutes(app);

// Error handler middleware (must be last)
app.use(errorHandlerMiddleware);

export default app;

