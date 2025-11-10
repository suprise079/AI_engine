"""
Configuration management for AI Engine.
Supports environment-based configuration (dev/prod/qa).
"""
import os
import logging
from typing import List


class Config:
    """Base configuration class."""
    
    # Application settings
    APP_NAME = "Hydra AI Engine"
    APP_VERSION = "1.0.0"
    
    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # CORS configuration
    CORS_ORIGINS: List[str] = os.getenv(
        'CORS_ORIGINS',
        'http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000,http://127.0.0.1:8080'
    ).split(',')
    CORS_CREDENTIALS = os.getenv('CORS_CREDENTIALS', 'True').lower() == 'true'
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    CORS_HEADERS = ['Content-Type', 'Authorization']
    
    # API settings
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # Request settings
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB
    
    # Timeout settings
    REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 300))  # 5 minutes
    
    @staticmethod
    def init_app(app):
        """Initialize application with configuration."""
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format=Config.LOG_FORMAT,
            datefmt=Config.LOG_DATE_FORMAT
        )
        
        # Configure Flask settings
        app.config['JSON_AS_ASCII'] = Config.JSON_AS_ASCII
        app.config['JSON_SORT_KEYS'] = Config.JSON_SORT_KEYS
        app.config['JSONIFY_PRETTYPRINT_REGULAR'] = Config.JSONIFY_PRETTYPRINT_REGULAR
        app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    
    # Production-specific CORS origins (should be set via env vars)
    CORS_ORIGINS: List[str] = os.getenv(
        'CORS_ORIGINS',
        'https://localhost:3000,https://localhost:8080'
    ).split(',')


class QaConfig(Config):
    """QA/Testing configuration."""
    DEBUG = False
    LOG_LEVEL = 'INFO'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'qa': QaConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment."""
    env = os.getenv('FLASK_ENV', 'development').lower()
    return config.get(env, config['default'])

