import { Router } from 'express';
import { chat, chatStream } from './chat.controller';
import { validateChatRequest } from '../../middleware/validation.middleware';

const router = Router();

// Chat endpoint
router.post('/chat', validateChatRequest, chat);

// Alternative API path for chat (backwards compatibility)
router.post('/api/chat', validateChatRequest, chat);

// Streaming chat endpoint (SSE)
router.post('/chat/stream', chatStream);

export default router;

