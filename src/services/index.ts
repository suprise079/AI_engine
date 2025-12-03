/**
 * Services container - initializes and exports all service instances
 */

import { SuggestionGenerator } from './suggestion-generator';
import { ComponentRecognizer } from './component-recognizer';
import { TestCaseGenerator } from './test-case-generator';
import { TestScriptGenerator } from './test-script-generator';
import { OllamaService } from './ollama-service';
import { config } from '../config/config';

// Initialize services (singleton pattern)
export const patternRecognizer = null; // Removed as per requirements
export const suggestionGenerator = new SuggestionGenerator();
export const componentRecognizer = new ComponentRecognizer();
export const testCaseGenerator = new TestCaseGenerator();
export const testScriptGenerator = new TestScriptGenerator();
export const ollamaService = new OllamaService(config.OLLAMA_MODEL, config.OLLAMA_TIMEOUT);

