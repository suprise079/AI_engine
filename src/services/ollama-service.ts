/**
 * Ollama Service for interacting with a running Ollama server via HTTP
 */

import logger from '../config/logger';
import { llmQueue } from '../utils/llm-queue';

const OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://127.0.0.1:11434';

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

interface ChatRequest {
  model: string;
  messages: ChatMessage[];
  stream?: boolean;
}

interface ChatResponse {
  message: {
    role: string;
    content: string;
  };
}

export class OllamaService {
  private readonly modelName: string;
  private readonly timeout: number;
  private readonly baseUrl: string;

  constructor(modelName: string, timeout: number) {
    console.log(`Initializing OllamaService with model: ${modelName} and timeout: ${timeout}`);
    this.modelName = modelName;
    this.timeout = timeout;
    this.baseUrl = OLLAMA_HOST.replace(/\/$/, '');
  }

  /**
   * Query Ollama with a prompt and return the response.
   * When signal is provided (e.g. from LLM router fallback timeout), it is used for fetch and no internal timeout is set.
   * When signal is not provided, the instance timeout is used.
   */
  async query(prompt: string, signal?: AbortSignal): Promise<string> {
    logger.info(`\n\nQuerying Ollama with model: ${this.modelName}`);
    console.log('[Ollama service] prompt received:', prompt);

    const requestBody: ChatRequest = {
      model: this.modelName,
      messages: [{ role: 'user', content: prompt }],
      stream: false
    };

    return llmQueue.enqueue(async () => {
      let timeoutId: ReturnType<typeof setTimeout> | undefined;
      let effectiveSignal: AbortSignal;
      if (signal) {
        effectiveSignal = signal;
      } else {
        const controller = new AbortController();
        timeoutId = setTimeout(() => controller.abort(), this.timeout);
        effectiveSignal = controller.signal;
      }

      try {
        const response = await fetch(`${this.baseUrl}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody),
          signal: effectiveSignal
        });

        if (timeoutId !== undefined) clearTimeout(timeoutId);

        if (!response.ok) {
          const errorText = await response.text().catch(() => response.statusText);
          console.error('[Ollama service] HTTP error:', response.status, errorText);
          logger.error(`Ollama HTTP error ${response.status}: ${errorText}`);
          throw new Error(`Ollama HTTP error ${response.status}: ${errorText}`);
        }

        const data = await response.json() as ChatResponse;
        const content = data.message?.content || '';

        logger.info(`Ollama response received (${content.length} chars)`);
        console.log('[Ollama service] response:', content);
        return content.trim();
      } catch (error: any) {
        if (timeoutId !== undefined) clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
          console.error('[Ollama service] query timeout:', signal ? 'external signal' : `${this.timeout}ms`);
          logger.error(`Ollama query timeout after ${signal ? 'external signal' : this.timeout + 'ms'}`);
          throw new Error(`Ollama query timeout after ${signal ? 'external signal' : this.timeout + 'ms'}`);
        }
        console.error('[Ollama service] request failed:', error?.message, error);
        logger.error(`Ollama request failed: ${error.message}`, { error });
        throw error;
      }
    });
  }

  /**
   * Stream chat tokens from Ollama. Calls onChunk for each content fragment.
   * The returned promise resolves when the stream completes or rejects on error.
   */
  async streamChat(
    prompt: string,
    onChunk: (chunk: string) => void,
    abortSignal?: AbortSignal
  ): Promise<void> {
    logger.info(`Streaming from Ollama with model: ${this.modelName}`);
    console.log('[Ollama service] streamChat prompt received:', prompt);

    const requestBody: ChatRequest = {
      model: this.modelName,
      messages: [{ role: 'user', content: prompt }],
      stream: true
    };

    return llmQueue.enqueue(async () => {
      const controller = new AbortController();
      const signal = abortSignal ?? controller.signal;
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      try {
        const response = await fetch(`${this.baseUrl}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestBody),
          signal
        });

        if (!response.ok) {
          const errorText = await response.text().catch(() => response.statusText);
          console.error('[Ollama service] streamChat HTTP error:', response.status, errorText);
          logger.error(`Ollama HTTP error (stream) ${response.status}: ${errorText}`);
          throw new Error(`Ollama HTTP error ${response.status}: ${errorText}`);
        }

        if (!response.body) {
          console.warn('[Ollama service] streamChat response has no body');
          logger.warn('Ollama stream response has no body');
          return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';
        let fullContent = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            break;
          }
          buffer += decoder.decode(value, { stream: true });

          let newlineIndex: number;
          while ((newlineIndex = buffer.indexOf('\n')) >= 0) {
            const line = buffer.slice(0, newlineIndex).trim();
            buffer = buffer.slice(newlineIndex + 1);
            if (!line) {
              continue;
            }

            try {
              const parsed = JSON.parse(line) as any;
              const contentFragment = parsed?.message?.content;
              if (typeof contentFragment === 'string' && contentFragment.length > 0) {
                fullContent += contentFragment;
                onChunk(contentFragment);
              }
            } catch (e: any) {
              logger.warn(`Failed to parse Ollama stream line: ${e.message}`);
            }
          }
        }
        console.log('[Ollama service] streamChat response:', fullContent);
      } catch (error: any) {
        if (error.name === 'AbortError') {
          console.error('[Ollama service] streamChat aborted:', this.timeout, 'ms or external cancel');
          logger.warn(`Ollama stream aborted after timeout=${this.timeout}ms or external cancel`);
          throw new Error('Ollama stream aborted');
        }
        console.error('[Ollama service] streamChat failed:', error?.message, error);
        logger.error(`Ollama stream failed: ${error.message}`, { error });
        throw error;
      } finally {
        clearTimeout(timeoutId);
      }
    });
  }

  /**
   * Check if Ollama server is available
   */
  async isAvailable(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${this.baseUrl}/api/tags`, {
        method: 'GET',
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch {
      return false;
    }
  }
}
