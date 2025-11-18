"""
Configuration for M2P Wallet Verification System
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///m2p.db')

# Developer donation wallet address for verification
DEV_WALLET_ADDRESS = os.getenv('DEV_WALLET_ADDRESS', 'your_dev_wallet_address_here')

# Verification settings
VERIFICATION_TIMEOUT_HOURS = int(os.getenv('VERIFICATION_TIMEOUT_HOURS', '24'))
VERIFICATION_CHECK_INTERVAL_MINUTES = int(os.getenv('VERIFICATION_CHECK_INTERVAL_MINUTES', '5'))
MIN_CONFIRMATIONS = int(os.getenv('MIN_CONFIRMATIONS', '6'))
AP_REFUND_MULTIPLIER = int(os.getenv('AP_REFUND_MULTIPLIER', '100'))  # 1 ADVC = 100 AP

# ADVC Explorer API endpoints
ADVC_EXPLORER_API = os.getenv('ADVC_EXPLORER_API', 'https://api.adventurecoin.quest')
ADVC_EXPLORER_WEB = os.getenv('ADVC_EXPLORER_WEB', 'https://adventurecoin.quest')

# Pool API endpoints
POOL_API_URL = os.getenv('POOL_API_URL', 'https://cpu-pool.com/api')

# API request timeout (seconds)
API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))

# WebSocket configuration
SOCKETIO_MESSAGE_QUEUE = os.getenv('SOCKETIO_MESSAGE_QUEUE', None)
SOCKETIO_ASYNC_MODE = os.getenv('SOCKETIO_ASYNC_MODE', 'threading')

# Admin authentication
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', 'change_this_in_production')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', str(BASE_DIR / 'logs' / 'verifier.log'))
