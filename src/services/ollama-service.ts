/**
 * Ollama Service for interacting with DeepSeek model via Ollama HTTP API
 */

import * as logger from '../config/logger';

interface OllamaGenerateResponse {
  response: string;
  done?: boolean;
  context?: number[];
  total_duration?: number;
  load_duration?: number;
  prompt_eval_count?: number;
  prompt_eval_duration?: number;
  eval_count?: number;
  eval_duration?: number;
}

export class OllamaService {
  private ollamaUrl: string;
  private modelName: string;
  private timeout: number;

  constructor(ollamaUrl: string = 'http://localhost:11434', modelName: string = 'deepseek-coder', timeout: number = 60000) {
    this.ollamaUrl = ollamaUrl.replace(/\/$/, ''); // Remove trailing slash
    this.modelName = modelName;
    this.timeout = timeout;
  }

  /**
   * Query Ollama with a prompt and return the response
   */
  async query(prompt: string): Promise<string> {
    logger.default.info(`Querying Ollama with model: ${this.modelName} at ${this.ollamaUrl}`);
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(`${this.ollamaUrl}/api/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: this.modelName,
          prompt: prompt,
          stream: false,
        }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text();
        logger.default.error(`Ollama API error: ${response.status} ${response.statusText} - ${errorText}`);
        throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json() as OllamaGenerateResponse;
      const responseText = data.response || '';
      
      logger.default.info(`Ollama response received (${responseText.length} chars)`);
      return responseText.trim();
    } catch (error: any) {
      clearTimeout(timeoutId);
      
      if (error.name === 'AbortError') {
        logger.default.error(`Ollama query timeout after ${this.timeout}ms`);
        throw new Error(`Ollama query timeout after ${this.timeout}ms`);
      }
      
      if (error.message) {
        logger.default.error(`Ollama API error: ${error.message}`);
        throw error;
      }
      
      logger.default.error(`Ollama connection error: ${error}`);
      throw new Error(`Failed to connect to Ollama at ${this.ollamaUrl}: ${error.message || error}`);
    }
  }

  /**
   * Check if Ollama is available
   */
  async isAvailable(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      const response = await fetch(`${this.ollamaUrl}/api/tags`, {
        method: 'GET',
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      return false;
    }
  }
}

