/**
 * Pages routes - handles page detection
 */

import { Router } from 'express';
import { detectPages } from '../controllers/pages.controller';
import { validateActionsRequest } from '../middleware/validation.middleware';

const router = Router();

router.post('/detect-pages', validateActionsRequest, detectPages);

export default router;

