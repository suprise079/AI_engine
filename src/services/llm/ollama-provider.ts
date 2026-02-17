/**
 * Ollama provider wrapping OllamaService; returns LlmResult for the hybrid router.
 */

import type { OllamaService } from '../ollama-service';
import type { LlmProvider, LlmResult } from './types';

export function createOllamaProvider(ollamaService: OllamaService): LlmProvider {
  return {
    name: 'ollama',
    async generateText(
      prompt: string,
      opts?: { requestId?: string; signal?: AbortSignal }
    ): Promise<LlmResult> {
      const start = Date.now();
      const text = await ollamaService.query(prompt, opts?.signal);
      const durationMs = Date.now() - start;
      return {
        text: text.trim(),
        provider: 'ollama',
        durationMs,
        fallbackTriggered: false,
      };
    },
  };
}
