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
}

class BaseConfig implements Config {
  APP_NAME = 'Hydra AI Engine';
  APP_VERSION = '1.0.0';
  HOST = process.env.HOST || '0.0.0.0';
  PORT = parseInt(process.env.PORT || '3002', 10);
  DEBUG = process.env.DEBUG === 'true';
  LOG_LEVEL = process.env.LOG_LEVEL || 'INFO';
  CORS_ORIGINS = (process.env.CORS_ORIGINS || 'http://*.qotsystems.co.za').split(',');
  CORS_CREDENTIALS = process.env.CORS_CREDENTIALS !== 'false';
  CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'];
  CORS_HEADERS = ['Content-Type', 'Authorization'];
  MAX_CONTENT_LENGTH = parseInt(process.env.MAX_CONTENT_LENGTH || '16777216', 10); // 16MB
  REQUEST_TIMEOUT = parseInt(process.env.REQUEST_TIMEOUT || '200', 10); // 200 seconds
  OLLAMA_MODEL = process.env.OLLAMA_MODEL || 'llama3.1';
  OLLAMA_TIMEOUT = parseInt(process.env.OLLAMA_TIMEOUT || '60000', 10); // 60 seconds
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
  return new ConfigClass();
}

export const config = getConfig();

