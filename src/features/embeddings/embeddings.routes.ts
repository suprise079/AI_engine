import { Router } from 'express';
import { generateEmbedding, generateBatchEmbeddings } from './embeddings.controller';

const router = Router();

// Mounted at /api/embeddings
router.post('/generate', generateEmbedding);
router.post('/batch', generateBatchEmbeddings);

export default router;

