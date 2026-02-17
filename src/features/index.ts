import { Express } from 'express';

// Route imports point to src/features/* for each HTTP feature.
import healthRoutes from './health/health.routes';
import analyzeRoutes from './analyze/analyze.routes';
import pagesRoutes from './pages/pages.routes';
import testCasesRoutes from './test-cases/test-cases.routes';
import testScriptRoutes from './test-script/test-script.routes';
import chatRoutes from './chat/chat.routes';
import embeddingsRoutes from './embeddings/embeddings.routes';

export const registerFeatureRoutes = (app: Express) => {
  app.use('/', healthRoutes);
  app.use('/', analyzeRoutes);
  app.use('/', pagesRoutes);
  app.use('/', testCasesRoutes);
  app.use('/', testScriptRoutes);
  app.use('/', chatRoutes);
  app.use('/api/embeddings', embeddingsRoutes);
};


