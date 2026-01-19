/**
 * Analysis routes - handles action analysis and feedback
 */

import { Router } from 'express';
import { analyzeActions, processFeedback, analyzeBugReasoning } from '../controllers/analyze.controller';
import { validateActionsRequest } from '../middleware/validation.middleware';

const router = Router();

router.post('/analyze', validateActionsRequest, analyzeActions);
router.post('/analyze-bug', analyzeBugReasoning);
router.post('/feedback', processFeedback);

export default router;

