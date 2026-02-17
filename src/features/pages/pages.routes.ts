import { Router } from 'express';
import { detectPages } from './pages.controller';
import { validateActionsRequest } from '../../middleware/validation.middleware';

const router = Router();

router.post('/detect-pages', validateActionsRequest, detectPages);

export default router;

