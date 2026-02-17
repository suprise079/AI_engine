/**
 * Hybrid LLM router: Ollama first with timeout, then fallback to OpenAI when slow or failing.
 */

import { config } from '../../config/config';
import logger from '../../config/logger';
import type { LlmProvider, LlmResult } from './types';

const PROMPT_MAX_CHARS = 120_000;

export interface LlmRouterOptions {
  ollamaProvider: LlmProvider;
  openaiProvider: LlmProvider | null;
  fallbackTimeoutMs: number;
  fallbackEnabled: boolean;
}

export interface GenerateTextOptions {
  requestId?: string;
}

/**
 * Generate text: try Ollama with timeout; on timeout or error, fall back to OpenAI if enabled.
 */
export async function generateText(
  prompt: string,
  opts: GenerateTextOptions,
  routerOptions: LlmRouterOptions
): Promise<LlmResult> {
  const { requestId } = opts;
  const promptChars = prompt.length;

  if (prompt.length > PROMPT_MAX_CHARS) {
    logger.warn(
      `Prompt length ${prompt.length} exceeds ${PROMPT_MAX_CHARS} chars; truncating to last ${PROMPT_MAX_CHARS} chars`
    );
    prompt = prompt.slice(-PROMPT_MAX_CHARS);
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), routerOptions.fallbackTimeoutMs);

  const tryOllama = (): Promise<LlmResult> =>
    routerOptions.ollamaProvider.generateText(prompt, { requestId, signal: controller.signal });

  try {
    console.log('[Llm router] Trying reasoning with Ollama:', prompt);
    const result = await tryOllama();
    console.log('[Llm router] Ollama result:', result);
    clearTimeout(timeoutId);
    logger.info('llm_request_completed', {
      requestId,
      provider: result.provider,
      fallbackTriggered: result.fallbackTriggered ?? false,
      durationMs: result.durationMs,
      promptChars,
    });
    return result;
  } catch (ollamaError: any) {
    clearTimeout(timeoutId);
    controller.abort();

    const isAbort = ollamaError?.name === 'AbortError' || ollamaError?.message?.includes('timeout');
    const shouldFallback =
      routerOptions.fallbackEnabled &&
      routerOptions.openaiProvider &&
      (isAbort || !isAbort);

    if (shouldFallback && routerOptions.openaiProvider) {
      logger.info(
        `Ollama ${isAbort ? 'timeout' : 'error'}, falling back to OpenAI`,
        { requestId, error: ollamaError?.message }
      );
      try {
        console.log('[Llm router] Falling back to OpenAI:', prompt);
        const fallbackResult = await routerOptions.openaiProvider!.generateText(prompt, {
          requestId,
        });
        console.log('[Llm router] OpenAI result:', fallbackResult);
        const result: LlmResult = {
          ...fallbackResult,
          fallbackTriggered: true,
        };
        logger.info('llm_request_completed', {
          requestId,
          provider: result.provider,
          fallbackTriggered: true,
          durationMs: result.durationMs,
          promptChars,
        });
        return result;
      } catch (openaiError: any) {
        console.log('[Llm router] OpenAI fallback failed:', openaiError?.message);
        logger.error(`OpenAI fallback failed: ${openaiError?.message}`, { requestId });
        throw openaiError;
      }
    }

    throw ollamaError;
  }
}

export function createLlmRouterOptions(
  ollamaProvider: LlmProvider,
  openaiProvider: LlmProvider | null
): LlmRouterOptions {
  return {
    ollamaProvider,
    openaiProvider,
    fallbackTimeoutMs: config.LLM_FALLBACK_TIMEOUT_MS,
    fallbackEnabled: config.LLM_FALLBACK_EFFECTIVE && config.LLM_ENABLE_FALLBACK,
  };
}

export interface LlmRouter {
  generateText(prompt: string, opts?: GenerateTextOptions): Promise<LlmResult>;
}

export function createLlmRouter(options: LlmRouterOptions): LlmRouter {
  return {
    async generateText(prompt: string, opts: GenerateTextOptions = {}): Promise<LlmResult> {
      return generateText(prompt, opts, options);
    },
  };
}
