/**
 * Chat controller - handles chat API endpoints
 */

import { Request, Response } from 'express';
import logger from '../config/logger';
import { ollamaService } from '../services';

/**
 * Chat endpoint handler
 */
export const chat = async (req: Request, res: Response) => {
  try {
    const { prompt } = req.body;

    logger.info(`Received chat request with prompt: ${prompt}`);

    // Query DeepSeek via Ollama
    const response = await ollamaService.query(prompt);

    logger.info(`Chat response generated (${response.length} chars)`);

    return res.json({ 
      response: response.trim() 
    });
  } catch (error: any) {
    logger.error(`Error in chat endpoint: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: error.message || 'An error occurred while processing the chat request'
    });
  }
};

