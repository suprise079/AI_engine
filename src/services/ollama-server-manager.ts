/**
 * Ollama Server Manager - handles starting and checking Ollama server
 */

import { spawn } from 'child_process';
import * as http from 'http';
import logger from '../config/logger';

export class OllamaServerManager {
  private ollamaProcess: any = null;
  private readonly OLLAMA_PORT = 11434;
  private readonly OLLAMA_HOST = '127.0.0.1';

  /**
   * Check if Ollama server is already running
   */
  async isServerRunning(): Promise<boolean> {
    try {
      // Try to connect to Ollama's default port
      return new Promise((resolve) => {
        const req = http.get(`http://${this.OLLAMA_HOST}:${this.OLLAMA_PORT}/api/tags`, (res) => {
          resolve(res.statusCode === 200);
          logger.info(`Ollama server is running on ${this.OLLAMA_HOST}:${this.OLLAMA_PORT}`);
        });
        
        req.on('error', () => {
          resolve(false);
        });
        
        req.setTimeout(2000, () => {
          req.destroy();
          resolve(false);
        });
      });
    } catch (error) {
      return false;
    }
  }

  /**
   * Start Ollama server if not already running
   */
  async startServer(): Promise<void> {
    // Check if server is already running
    const isRunning = await this.isServerRunning();
    if (isRunning) {
      logger.info('Ollama server is already running');
      return;
    }

    logger.info('Starting Ollama server...');
    
    try {
      // Start Ollama server as background process
      this.ollamaProcess = spawn('ollama', ['serve'], {
        detached: false,
        stdio: ['ignore', 'pipe', 'pipe']
      });

      // Log Ollama server output
      this.ollamaProcess.stdout.on('data', (data: Buffer) => {
        logger.debug(`Ollama: ${data.toString().trim()}`);
      });

      this.ollamaProcess.stderr.on('data', (data: Buffer) => {
        logger.debug(`Ollama: ${data.toString().trim()}`);
      });

      // Handle process errors
      this.ollamaProcess.on('error', (error: Error) => {
        logger.error(`Failed to start Ollama server: ${error.message}`);
      });

      // Wait a bit for server to start, then verify
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const serverRunning = await this.isServerRunning();
      if (serverRunning) {
        logger.info('Ollama server started successfully');
      } else {
        logger.warn('Ollama server may not have started properly. It may already be running or there may be an issue.');
      }
    } catch (error: any) {
      logger.error(`Error starting Ollama server: ${error.message}`);
      throw error;
    }
  }

  /**
   * Stop Ollama server (if started by this manager)
   */
  stopServer(): void {
    if (this.ollamaProcess) {
      logger.info('Stopping Ollama server...');
      this.ollamaProcess.kill();
      this.ollamaProcess = null;
    }
  }
}

// Export singleton instance
export const ollamaServerManager = new OllamaServerManager();

