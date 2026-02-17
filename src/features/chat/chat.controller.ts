import { Request, Response } from 'express';
import logger from '../../config/logger';
import { config } from '../../config/config';
import { ollamaService } from '../../services';
import { ChatService } from './chat.service';

const chatService = new ChatService();

/**
 * Chat endpoint handler (non-streaming).
 * Delegates core logic to ChatService.
 */
export const chat = async (req: Request, res: Response) => {
  try {
    const result = await chatService.handleChat(req.body);
    return res.json(result);
  } catch (error: any) {
    logger.error(`Error in chat endpoint: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: error.message || 'An error occurred while processing the chat request',
    });
  }
};

/**
 * Streaming chat endpoint handler (SSE).
 * Emits token events as the model generates output.
 *
 * This keeps the existing SSE behavior but lives in the feature module.
 */
export const chatStream = async (req: Request, res: Response) => {
  if (!config.ENABLE_STREAMING_CHAT) {
    return res.status(501).json({
      error: 'Not Implemented',
      message:
        'Streaming chat is disabled. Set ENABLE_STREAMING_CHAT=true or use development config to enable.',
    });
  }

  const { requestId, prompt } = req.body || {};

  if (!requestId || !prompt || typeof requestId !== 'string' || typeof prompt !== 'string') {
    return res.status(400).json({
      error: 'Bad Request',
      message: 'requestId and prompt are required',
    });
  }

  logger.info(`Starting streaming chat for requestId=${requestId}`);

  // Set SSE headers
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  const sendEvent = (event: string, data: any) => {
    try {
      res.write(`event: ${event}\n`);
      res.write(`data: ${JSON.stringify(data)}\n\n`);
    } catch (e: any) {
      logger.warn(`Failed to write SSE event ${event}: ${e.message}`);
    }
  };

  const abortController = new AbortController();

  // Abort if client disconnects
  req.on('close', () => {
    logger.info(`Client disconnected for streaming chat requestId=${requestId}`);
    abortController.abort();
  });

  try {
    await ollamaService.streamChat(
      prompt,
      (chunk) => {
        sendEvent('token', { requestId, chunk });
      },
      abortController.signal
    );

    sendEvent('done', { requestId });
    res.end();
  } catch (error: any) {
    if (abortController.signal.aborted) {
      logger.info(`Streaming chat aborted for requestId=${requestId}`);
      // Do not send error if client already disconnected
      try {
        res.end();
      } catch {
        // ignore
      }
      return;
    }

    logger.error(`Error in chatStream endpoint: ${error.message}`, { error });
    try {
      sendEvent('error', {
        requestId,
        message: error.message || 'Streaming chat failed',
      });
      res.end();
    } catch {
      // ignore
    }
  }

  return;
};

