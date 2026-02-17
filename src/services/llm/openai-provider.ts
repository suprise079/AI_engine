/**
 * OpenAI provider using the Responses API (client.responses.create, response.output_text).
 * Used as fallback when Ollama times out or fails.
 */

import OpenAI from 'openai';
import { config } from '../../config/config';
import logger from '../../config/logger';
import type { LlmProvider, LlmResult } from './types';

const OPENAI_REQUEST_TIMEOUT_MS = 60_000;
const MAX_RETRIES = 2;
const RETRY_DELAYS_MS = [250, 1000];

function isRetryableStatus(status: number): boolean {
  return status === 429 || (status >= 500 && status < 600);
}

export function createOpenAIProvider(): LlmProvider {
  const apiKey = config.OPENAI_API_KEY?.trim();
  if (!apiKey) {
    throw new Error('OPENAI_API_KEY is not configured; cannot use OpenAI provider.');
  }

  const client = new OpenAI({ apiKey });

  return {
    name: 'openai',
    async generateText(
      prompt: string,
      _opts?: { requestId?: string; signal?: AbortSignal }
    ): Promise<LlmResult> {
      const start = Date.now();
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), OPENAI_REQUEST_TIMEOUT_MS);
      const signal = controller.signal;

      let lastError: Error | null = null;
      for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
        try {
          if (attempt > 0) {
            const delay = RETRY_DELAYS_MS[attempt - 1] ?? 1000;
            await new Promise((r) => setTimeout(r, delay));
          }

          const response = await client.responses.create(
            { model: config.OPENAI_MODEL, input: prompt },
            { signal }
          );

          clearTimeout(timeoutId);
          const durationMs = Date.now() - start;
          const text = (response as { output_text?: string }).output_text ?? '';
          return {
            text: String(text).trim(),
            provider: 'openai',
            durationMs,
          };
        } catch (err: any) {
          lastError = err;
          const status = err?.status ?? err?.response?.status;
          if (attempt < MAX_RETRIES && status !== undefined && isRetryableStatus(status)) {
            logger.warn(
              `OpenAI request failed (attempt ${attempt + 1}/${MAX_RETRIES + 1}), retrying: ${err?.message}`
            );
            continue;
          }
          if (err?.name === 'AbortError') {
            clearTimeout(timeoutId);
            throw new Error(`OpenAI request timeout after ${OPENAI_REQUEST_TIMEOUT_MS}ms`);
          }
          throw err;
        }
      }
      clearTimeout(timeoutId);
      throw lastError ?? new Error('OpenAI request failed');
    },
  };
}
