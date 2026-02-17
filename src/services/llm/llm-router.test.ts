/**
 * Unit tests for hybrid LLM router.
 */

import type { LlmProvider, LlmResult } from './types';
import {
  generateText,
  createLlmRouter,
  type LlmRouterOptions,
} from './llm-router';

function makeOllamaProvider(result: LlmResult): LlmProvider {
  return {
    name: 'ollama',
    async generateText(_prompt: string, opts?: { signal?: AbortSignal }): Promise<LlmResult> {
      if (opts?.signal?.aborted) throw new DOMException('Aborted', 'AbortError');
      return result;
    },
  };
}

function makeOllamaProviderThatHangs(ms: number): LlmProvider {
  return {
    name: 'ollama',
    async generateText(_prompt: string, opts?: { signal?: AbortSignal }): Promise<LlmResult> {
      await new Promise<void>((resolve, reject) => {
        const t = setTimeout(resolve, ms);
        opts?.signal?.addEventListener?.('abort', () => {
          clearTimeout(t);
          reject(new DOMException('Aborted', 'AbortError'));
        });
      });
      return { text: 'ollama', provider: 'ollama', durationMs: ms, fallbackTriggered: false };
    },
  };
}

function makeOllamaProviderThatThrows(err: Error): LlmProvider {
  return {
    name: 'ollama',
    async generateText(): Promise<LlmResult> {
      throw err;
    },
  };
}

function makeOpenAIProvider(result: LlmResult): LlmProvider {
  return {
    name: 'openai',
    async generateText(): Promise<LlmResult> {
      return result;
    },
  };
}

const openaiResult: LlmResult = {
  text: 'openai response',
  provider: 'openai',
  durationMs: 10,
};

describe('llm-router', () => {
  const shortTimeout = 30;

  it('uses Ollama when it resolves within timeout', async () => {
    const ollama = makeOllamaProvider({
      text: 'ollama response',
      provider: 'ollama',
      durationMs: 5,
      fallbackTriggered: false,
    });
    const options: LlmRouterOptions = {
      ollamaProvider: ollama,
      openaiProvider: makeOpenAIProvider(openaiResult),
      fallbackTimeoutMs: shortTimeout,
      fallbackEnabled: true,
    };
    const result = await generateText('hello', {}, options);
    expect(result.provider).toBe('ollama');
    expect(result.text).toBe('ollama response');
    expect(result.fallbackTriggered).toBeFalsy();
  });

  it('falls back to OpenAI when Ollama hangs past timeout', async () => {
    const ollama = makeOllamaProviderThatHangs(500);
    const openai = makeOpenAIProvider(openaiResult);
    const options: LlmRouterOptions = {
      ollamaProvider: ollama,
      openaiProvider: openai,
      fallbackTimeoutMs: shortTimeout,
      fallbackEnabled: true,
    };
    const result = await generateText('hello', {}, options);
    expect(result.provider).toBe('openai');
    expect(result.text).toBe('openai response');
    expect(result.fallbackTriggered).toBe(true);
  }, 5000);

  it('falls back to OpenAI when Ollama throws immediately', async () => {
    const ollama = makeOllamaProviderThatThrows(new Error('connection refused'));
    const openai = makeOpenAIProvider(openaiResult);
    const options: LlmRouterOptions = {
      ollamaProvider: ollama,
      openaiProvider: openai,
      fallbackTimeoutMs: shortTimeout,
      fallbackEnabled: true,
    };
    const result = await generateText('hello', {}, options);
    expect(result.provider).toBe('openai');
    expect(result.fallbackTriggered).toBe(true);
  });

  it('propagates Ollama error when fallback is disabled', async () => {
    const ollama = makeOllamaProviderThatThrows(new Error('ollama down'));
    const options: LlmRouterOptions = {
      ollamaProvider: ollama,
      openaiProvider: makeOpenAIProvider(openaiResult),
      fallbackTimeoutMs: shortTimeout,
      fallbackEnabled: false,
    };
    await expect(generateText('hello', {}, options)).rejects.toThrow('ollama down');
  });

  it('propagates Ollama error when OpenAI provider is null (not configured)', async () => {
    const ollama = makeOllamaProviderThatThrows(new Error('connection refused'));
    const options: LlmRouterOptions = {
      ollamaProvider: ollama,
      openaiProvider: null,
      fallbackTimeoutMs: shortTimeout,
      fallbackEnabled: true,
    };
    await expect(generateText('hello', {}, options)).rejects.toThrow('connection refused');
  });

  it('truncates prompt when over 120_000 chars', async () => {
    const longPrompt = 'x'.repeat(120_001);
    let receivedPrompt = '';
    const ollama: LlmProvider = {
      name: 'ollama',
      async generateText(prompt: string): Promise<LlmResult> {
        receivedPrompt = prompt;
        return { text: 'ok', provider: 'ollama', durationMs: 0 };
      },
    };
    const options: LlmRouterOptions = {
      ollamaProvider: ollama,
      openaiProvider: null,
      fallbackTimeoutMs: shortTimeout,
      fallbackEnabled: false,
    };
    await generateText(longPrompt, {}, options);
    expect(receivedPrompt.length).toBe(120_000);
    expect(receivedPrompt.startsWith('x')).toBe(true);
  });

  it('createLlmRouter returns object with generateText', async () => {
    const ollama = makeOllamaProvider({
      text: 'routed',
      provider: 'ollama',
      durationMs: 1,
    });
    const router = createLlmRouter({
      ollamaProvider: ollama,
      openaiProvider: null,
      fallbackTimeoutMs: shortTimeout,
      fallbackEnabled: false,
    });
    const result = await router.generateText('hi', { requestId: 'req-1' });
    expect(result.text).toBe('routed');
    expect(result.provider).toBe('ollama');
  });
});
