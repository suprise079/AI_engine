import { Router } from 'express';
import { generateTestCases } from './test-cases.controller';
import { validatePagesRequest } from '../../middleware/validation.middleware';

const router = Router();

router.post('/generate-test-cases', validatePagesRequest, generateTestCases);

export default router;

