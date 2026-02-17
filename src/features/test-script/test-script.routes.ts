import { Router } from 'express';
import { generateScript } from './test-script.controller';
import { validateTestCaseRequest } from '../../middleware/validation.middleware';

const router = Router();

router.post('/generate-script', validateTestCaseRequest, generateScript);

export default router;

