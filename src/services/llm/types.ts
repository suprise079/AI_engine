/**
 * LLM provider types for hybrid Ollama + OpenAI fallback.
 */

export type LlmResult = {
  text: string;
  provider: 'ollama' | 'openai';
  durationMs: number;
  fallbackTriggered?: boolean;
};

export interface LlmProvider {
  name: 'ollama' | 'openai';
  generateText(
    prompt: string,
    opts?: { requestId?: string; signal?: AbortSignal }
  ): Promise<LlmResult>;
}
