import { Request, Response } from 'express';
import logger from '../../config/logger';
import { EmbeddingsService } from './embeddings.service';

const embeddingsService = new EmbeddingsService();

/**
 * Generate embedding for a single text.
 */
export const generateEmbedding = async (req: Request, res: Response) => {
  try {
    const { text } = req.body;

    if (!text || typeof text !== 'string') {
      return res.status(400).json({
        error: 'Bad Request',
        message: 'text field is required and must be a string',
      });
    }

    const result = await embeddingsService.generate(text);
    return res.json(result);
  } catch (error: any) {
    logger.error(`Error generating embedding: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while generating embedding',
    });
  }
};

/**
 * Generate embeddings for multiple texts.
 */
export const generateBatchEmbeddings = async (req: Request, res: Response) => {
  try {
    const { texts } = req.body;

    if (!texts || !Array.isArray(texts) || texts.length === 0) {
      return res.status(400).json({
        error: 'Bad Request',
        message: 'texts field is required and must be a non-empty array',
      });
    }

    const result = await embeddingsService.generateBatch(texts);
    return res.json(result);
  } catch (error: any) {
    logger.error(`Error generating batch embeddings: ${error.message}`, { error });
    return res.status(500).json({
      error: 'Internal Server Error',
      message: 'An error occurred while generating batch embeddings',
    });
  }
};

