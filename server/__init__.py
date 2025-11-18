"""
Flask application factory for Mine-to-Play.

This module provides the application factory pattern for creating and
configuring the Flask application with all necessary extensions.
"""

import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_migrate import Migrate

from .config import get_config
from .models import db

# Initialize extensions (will be bound to app in create_app)
socketio = SocketIO()
migrate = Migrate()


def create_app(config_name=None):
    """
    Create and configure the Flask application.

    Args:
        config_name: Configuration environment name ('development', 'production', 'testing')
                    If None, uses FLASK_ENV environment variable

    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    config_class = get_config(config_name)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config['CORS_ORIGINS'])
    socketio.init_app(
        app,
        cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS'],
        async_mode=app.config['SOCKETIO_ASYNC_MODE']
    )

    # Configure logging
    setup_logging(app)

    # Register blueprints (to be created later)
    # from .api import api_bp
    # app.register_blueprint(api_bp, url_prefix='/api')

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    # Perform any additional initialization
    config_class.init_app(app)

    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return {'status': 'healthy', 'service': 'mine-to-play'}, 200

    app.logger.info(f'Mine-to-Play application started in {config_name} mode')

    return app


def setup_logging(app):
    """
    Configure application logging.

    Args:
        app: Flask application instance
    """
    log_level = getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO)
    app.logger.setLevel(log_level)

    # Create logs directory if it doesn't exist
    log_file = app.config.get('LOG_FILE')
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Add file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
