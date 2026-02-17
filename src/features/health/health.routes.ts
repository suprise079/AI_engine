import { Router } from 'express';
import { getHealth, getLlmHealth } from './health.controller';

const router = Router();

router.get('/health', getHealth);
router.get('/health/llm', getLlmHealth);

export default router;

