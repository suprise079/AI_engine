/**
 * Routes aggregator - registers all route modules
 */

import { Express } from 'express';
import healthRoutes from './health.routes';
import analyzeRoutes from './analyze.routes';
import pagesRoutes from './pages.routes';
import testCasesRoutes from './test-cases.routes';
import testScriptRoutes from './test-script.routes';
import chatRoutes from './chat.routes';

/**
 * Register all routes with the Express app
 */
export const registerRoutes = (app: Express) => {
  app.use('/', healthRoutes);
  app.use('/', analyzeRoutes);
  app.use('/', pagesRoutes);
  app.use('/', testCasesRoutes);
  app.use('/', testScriptRoutes);
  app.use('/', chatRoutes);
};

