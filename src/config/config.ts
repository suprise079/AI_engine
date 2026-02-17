/**
 * Configuration management for AI Engine
 * Supports environment-based configuration (dev/prod/qa)
 */

import dotenv from 'dotenv';

dotenv.config();

export interface Config {
  APP_NAME: string;
  APP_VERSION: string;
  HOST: string;
  PORT: number;
  DEBUG: boolean;
  LOG_LEVEL: string;
  CORS_ORIGINS: string[];
  CORS_CREDENTIALS: boolean;
  CORS_METHODS: string[];
  CORS_HEADERS: string[];
  MAX_CONTENT_LENGTH: number;
  REQUEST_TIMEOUT: number;
  OLLAMA_MODEL: string;
  OLLAMA_TIMEOUT: number;
  LLM_CONCURRENCY_LIMIT: number;
  LLM_QUEUE_TIMEOUT_MS: number;
  BACKEND_URL: string;
  HYDRA_EMBEDDING_MODEL: string;
  /** Enable POST /chat/stream (SSE). Set ENABLE_STREAMING_CHAT=true or use development. */
  ENABLE_STREAMING_CHAT: boolean;
  /** OpenAI API key for fallback when Ollama times out or fails. */
  OPENAI_API_KEY: string;
  /** OpenAI model for fallback (e.g. gpt-4o-mini). */
  OPENAI_MODEL: string;
  /** Timeout in ms before falling back to OpenAI (default 10000). */
  LLM_FALLBACK_TIMEOUT_MS: number;
  /** Enable fallback to OpenAI when Ollama is slow or fails. */
  LLM_ENABLE_FALLBACK: boolean;
  /** Primary LLM (e.g. ollama). */
  LLM_PRIMARY: string;
  /** Fallback LLM (e.g. openai). */
  LLM_FALLBACK: string;
  /** When true, add meta (provider, fallbackTriggered, durationMs) to chat/analyze responses. */
  DEBUG_LLM: boolean;
  /** Effective fallback enabled (false when OPENAI_API_KEY missing despite LLM_ENABLE_FALLBACK). */
  LLM_FALLBACK_EFFECTIVE: boolean;
  /** Ollama host URL (for health). */
  OLLAMA_HOST: string;
}

class BaseConfig implements Config {
  APP_NAME = 'Hydra AI Engine';
  APP_VERSION = '1.0.0';
  HOST = process.env.HOST || '0.0.0.0';
  PORT = parseInt(process.env.PORT || '3006', 10);
  DEBUG = process.env.DEBUG === 'true';
  LOG_LEVEL = process.env.LOG_LEVEL || 'INFO';
  CORS_ORIGINS = (process.env.CORS_ORIGINS || '*').split(',');
  CORS_CREDENTIALS = process.env.CORS_CREDENTIALS !== 'false';
  CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'];
  CORS_HEADERS = ['Content-Type', 'Authorization'];
  MAX_CONTENT_LENGTH = parseInt(process.env.MAX_CONTENT_LENGTH || '16777216', 10); // 16MB
  REQUEST_TIMEOUT = parseInt(process.env.REQUEST_TIMEOUT || '200', 10); // 200 seconds
  OLLAMA_MODEL = process.env.OLLAMA_MODEL || 'mistral:7b-instruct-q4_K_M';
  OLLAMA_TIMEOUT = parseInt(process.env.OLLAMA_TIMEOUT || '240000', 10); // 240 seconds
  LLM_CONCURRENCY_LIMIT = parseInt(process.env.LLM_CONCURRENCY_LIMIT || '2', 10);
  LLM_QUEUE_TIMEOUT_MS = parseInt(process.env.LLM_QUEUE_TIMEOUT_MS || '240000', 10);
  BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080';
  HYDRA_EMBEDDING_MODEL = process.env.HYDRA_EMBEDDING_MODEL || 'Xenova/all-MiniLM-L6-v2';
  ENABLE_STREAMING_CHAT = process.env.ENABLE_STREAMING_CHAT === 'true';
  OPENAI_API_KEY = process.env.OPENAI_API_KEY ?? '';
  OPENAI_MODEL = process.env.OPENAI_MODEL || 'gpt-4o-mini';
  LLM_FALLBACK_TIMEOUT_MS = parseInt(process.env.LLM_FALLBACK_TIMEOUT_MS || '10000', 10);
  LLM_ENABLE_FALLBACK = process.env.LLM_ENABLE_FALLBACK !== 'false';
  LLM_PRIMARY = process.env.LLM_PRIMARY || 'ollama';
  LLM_FALLBACK = process.env.LLM_FALLBACK || 'openai';
  DEBUG_LLM = process.env.DEBUG_LLM === 'true';
  OLLAMA_HOST = process.env.OLLAMA_HOST || 'http://127.0.0.1:11434';
  /** Set after getConfig() and validation: fallback disabled when key missing. */
  LLM_FALLBACK_EFFECTIVE = true;
}

class DevelopmentConfig extends BaseConfig {
  DEBUG = true;
  LOG_LEVEL = 'DEBUG';
}

class ProductionConfig extends BaseConfig {
  DEBUG = false;
  LOG_LEVEL = 'INFO';
  CORS_ORIGINS = (process.env.CORS_ORIGINS || 'https://*.qotsystems.co.za').split(',');
}

class QaConfig extends BaseConfig {
  DEBUG = false;
  LOG_LEVEL = 'INFO';
}

const configs: Record<string, new () => Config> = {
  development: DevelopmentConfig,
  production: ProductionConfig,
  qa: QaConfig,
  default: DevelopmentConfig
};

export function getConfig(): Config {
  const env = (process.env.NODE_ENV || process.env.FLASK_ENV || 'development').toLowerCase();
  const ConfigClass = configs[env] || configs.default;
  const c = new ConfigClass();
  if (c.LLM_ENABLE_FALLBACK && !c.OPENAI_API_KEY?.trim()) {
    console.warn(
      'LLM_ENABLE_FALLBACK is true but OPENAI_API_KEY is missing; fallback to OpenAI is disabled.'
    );
    c.LLM_FALLBACK_EFFECTIVE = false;
  }
  return c;
}

export const config = getConfig();

