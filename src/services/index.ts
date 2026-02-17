/**
 * Services container - initializes and exports all service instances
 */

import { SuggestionGenerator } from './suggestion-generator';
import { ComponentRecognizer } from './component-recognizer';
import { TestCaseGenerator } from './test-case-generator';
import { TestScriptGenerator } from './test-script-generator';
import { OllamaService } from './ollama-service';
import { config } from '../config/config';
import { createOllamaProvider } from './llm/ollama-provider';
import { createOpenAIProvider } from './llm/openai-provider';
import {
  createLlmRouterOptions,
  createLlmRouter,
  type LlmRouter,
} from './llm/llm-router';

// Initialize services (singleton pattern)
export const patternRecognizer = null; // Removed as per requirements
export const ollamaService = new OllamaService(config.OLLAMA_MODEL, config.OLLAMA_TIMEOUT);

const ollamaProvider = createOllamaProvider(ollamaService);
let openaiProvider: ReturnType<typeof createOpenAIProvider> | null = null;
if (config.OPENAI_API_KEY?.trim()) {
  try {
    openaiProvider = createOpenAIProvider();
  } catch {
    openaiProvider = null;
  }
}

const llmRouterOptions = createLlmRouterOptions(ollamaProvider, openaiProvider);
export const llmRouter: LlmRouter = createLlmRouter(llmRouterOptions);

export const suggestionGenerator = new SuggestionGenerator(llmRouter);
export const componentRecognizer = new ComponentRecognizer();
export const testCaseGenerator = new TestCaseGenerator();
export const testScriptGenerator = new TestScriptGenerator();

