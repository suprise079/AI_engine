import { Router } from 'express';
import { analyzeActions, processFeedback, analyzeBugReasoning, generateBugReport } from './analyze.controller';
import { validateActionsRequest } from '../../middleware/validation.middleware';

const router = Router();

router.post('/analyze', validateActionsRequest, analyzeActions);
router.post('/analyze-bug', analyzeBugReasoning);
router.post('/generate-bug-report', generateBugReport);
router.post('/feedback', processFeedback);

export default router;

