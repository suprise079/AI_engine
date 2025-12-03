/**
 * Ollama Service for interacting with a running Ollama server via HTTP
 */

import logger from '../config/logger';

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

  constructor(modelName: string = 'llama3.1', timeout: number = 60000) {
    this.modelName = modelName;
    this.timeout = timeout;
    this.baseUrl = OLLAMA_HOST.replace(/\/$/, '');
  }

  /**
   * Query Ollama with a prompt and return the response.
   * Assumes `ollama serve` is already running and the model is pulled.
   */
  async query(prompt: string): Promise<string> {
    logger.info(`Querying Ollama with model: ${this.modelName}`);

    const requestBody: ChatRequest = {
      model: this.modelName,
      messages: [{ role: 'user', content: prompt }],
      stream: false
    };

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(`${this.baseUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        const errorText = await response.text().catch(() => response.statusText);
        logger.error(`Ollama HTTP error ${response.status}: ${errorText}`);
        throw new Error(`Ollama HTTP error ${response.status}: ${errorText}`);
      }

      const data = await response.json() as ChatResponse;
      const content = data.message?.content || '';
      
      logger.info(`Ollama response received (${content.length} chars)`);
      return content.trim();
    } catch (error: any) {
      if (error.name === 'AbortError') {
        logger.error(`Ollama query timeout after ${this.timeout}ms`);
        throw new Error(`Ollama query timeout after ${this.timeout}ms`);
      }
      logger.error(`Ollama request failed: ${error.message}`, { error });
      throw error;
    }
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
