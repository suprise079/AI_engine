/**
 * Ollama Service for interacting with DeepSeek model via Ollama CLI
 */

import { spawn } from 'child_process';
import * as logger from '../config/logger';

export class OllamaService {
  private modelName: string;
  private timeout: number;

  constructor(modelName: string = 'llama3.1', timeout: number = 60000) {
    this.modelName = modelName;
    this.timeout = timeout;
  }

  /**
   * Query Ollama with a prompt and return the response
   */
  async query(prompt: string): Promise<string> {
    return new Promise((resolve, reject) => {
      logger.default.info(`Querying Ollama with model: ${this.modelName}`);
      
      const ollama = spawn('ollama', ['run', this.modelName]);
      let output = '';
      let errorOutput = '';

      // Set timeout
      const timeoutId = setTimeout(() => {
        ollama.kill();
        reject(new Error(`Ollama query timeout after ${this.timeout}ms`));
      }, this.timeout);

      // Write prompt to stdin
      ollama.stdin.write(prompt + '\n');
      ollama.stdin.end();

      // Collect stdout
      ollama.stdout.on('data', (data: Buffer) => {
        output += data.toString();
      });

      // Collect stderr
      ollama.stderr.on('data', (data: Buffer) => {
        errorOutput += data.toString();
      });

      // Handle process completion
      ollama.on('close', (code: number) => {
        clearTimeout(timeoutId);
        
        if (code !== 0) {
          logger.default.error(`Ollama process exited with code ${code}: ${errorOutput}`);
          reject(new Error(`Ollama process failed: ${errorOutput || 'Unknown error'}`));
          return;
        }

        const trimmedOutput = output.trim();
        logger.default.info(`Ollama response received (${trimmedOutput.length} chars)`);
        resolve(trimmedOutput);
      });

      // Handle process errors
      ollama.on('error', (error: Error) => {
        clearTimeout(timeoutId);
        logger.default.error(`Ollama spawn error: ${error.message}`);
        reject(new Error(`Failed to spawn Ollama process: ${error.message}`));
      });
    });
  }

  /**
   * Check if Ollama is available
   */
  async isAvailable(): Promise<boolean> {
    return new Promise((resolve) => {
      const check = spawn('ollama', ['--version']);
      
      check.on('close', (code) => {
        resolve(code === 0);
      });

      check.on('error', () => {
        resolve(false);
      });

      // Timeout after 5 seconds
      setTimeout(() => {
        check.kill();
        resolve(false);
      }, 5000);
    });
  }
}

