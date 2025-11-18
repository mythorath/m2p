"""
Configuration settings for Mine-to-Play application.

This module defines configuration classes for different environments
(development, production) and game constants.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Base configuration class with settings common to all environments.

    Settings are primarily loaded from environment variables with sensible
    defaults for development.
    """

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

    # Database settings
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/m2p'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQL_ECHO', 'False').lower() in ('true', '1', 't')

    # CORS settings
    CORS_ORIGINS = os.getenv(
        'CORS_ORIGINS',
        'http://localhost:3000,http://localhost:5173'
    ).split(',')

    # SocketIO settings
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_CORS_ALLOWED_ORIGINS = CORS_ORIGINS

    # Mining pool configurations
    MINING_POOLS = {
        'cpu-pool': {
            'name': 'cpu-pool.com',
            'api_url': 'https://cpu-pool.com/api',
            'wallet_endpoint': '/wallet',
            'enabled': True
        },
        'rplant': {
            'name': 'rplant.xyz',
            'api_url': 'https://rplant.xyz/api',
            'wallet_endpoint': '/walletEx',
            'enabled': True
        },
        'zpool': {
            'name': 'zpool.ca',
            'api_url': 'https://zpool.ca/api',
            'wallet_endpoint': '/wallet',
            'enabled': True
        }
    }

    # Game constants
    ADVC_TO_AP_RATE = 100  # 1 ADVC = 100 AP
    MIN_VERIFICATION_AMOUNT = 0.01  # Minimum ADVC to verify wallet
    POLL_INTERVAL_SECONDS = 300  # Check pools every 5 minutes

    # Developer donation wallet
    DEV_WALLET_ADDRESS = os.getenv(
        'DEV_WALLET_ADDRESS',
        'AdVcash_placeholder_wallet_address_here'
    )

    # Blockchain settings
    ADVCASH_EXPLORER_URL = os.getenv(
        'ADVCASH_EXPLORER_URL',
        'https://explorer.advcash.org'
    )

    # Achievement settings
    ACHIEVEMENT_CHECK_INTERVAL = 60  # Check for new achievements every minute

    # API rate limiting
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'True').lower() in ('true', '1', 't')
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100 per hour')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/m2p.log')

    # Session settings
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() in ('true', '1', 't')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Server settings
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))

    @staticmethod
    def init_app(app):
        """
        Perform any additional app initialization.

        Args:
            app: Flask application instance
        """
        pass


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

    @staticmethod
    def init_app(app):
        """Production-specific initialization."""
        Config.init_app(app)

        # Log to stderr in production
        import logging
        from logging import StreamHandler

        handler = StreamHandler()
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://postgres:postgres@localhost:5432/m2p_test'
    )
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """
    Get configuration object for specified environment.

    Args:
        env: Environment name ('development', 'production', 'testing')
             If None, uses FLASK_ENV environment variable or 'default'

    Returns:
        Config class for the specified environment
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'default')

    return config.get(env, config['default'])
