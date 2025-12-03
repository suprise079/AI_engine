/**
 * Chat routes - handles chat API endpoints
 */

import { Router } from 'express';
import { chat } from '../controllers/chat.controller';
import { validateChatRequest } from '../middleware/validation.middleware';

const router = Router();

// Chat endpoint
router.post('/chat', validateChatRequest, chat);

// Alternative API path for chat (backwards compatibility)
router.post('/api/chat', validateChatRequest, chat);

export default router;

