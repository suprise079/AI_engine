import { Request, Response } from 'express';
import logger from '../../config/logger';
import { HealthService } from './health.service';
import { ollamaService } from '../../services';
import { config } from '../../config/config';

const healthService = new HealthService();

/**
 * Health check endpoint handler (feature-based).
 */
export const getHealth = (_req: Request, res: Response) => {
  try {
    const { httpStatus, body } = healthService.getHealthStatus();
    return res.status(httpStatus).json(body);
  } catch (error: any) {
    logger.error(`Health check failed: ${error.message}`, { error });
    return res.status(503).json({
      status: 'unhealthy',
      error: error.message,
      timestamp: new Date().toISOString(),
    });
  }
};

/**
 * LLM health: Ollama availability and OpenAI configuration.
 */
export const getLlmHealth = async (_req: Request, res: Response) => {
  try {
    const ollamaOk = await ollamaService.isAvailable();
    const ollamaHost = config.OLLAMA_HOST?.replace(/\/$/, '') ?? 'http://127.0.0.1:11434';
    const ollamaModel = config.OLLAMA_MODEL ?? '';
    const openaiConfigured = !!config.OPENAI_API_KEY?.trim();
    const openaiModel = config.OPENAI_MODEL ?? '';

    return res.status(200).json({
      ollama: { ok: ollamaOk, host: ollamaHost, model: ollamaModel },
      openai: { configured: openaiConfigured, model: openaiModel },
    });
  } catch (error: any) {
    logger.error(`LLM health check failed: ${error.message}`, { error });
    return res.status(503).json({
      error: error.message,
      timestamp: new Date().toISOString(),
    });
  }
};

