"""
Pytest configuration and fixtures for M2P test suite.
"""
import pytest
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from faker import Faker

# Note: These imports will work once the actual implementation is in place
# For now, they serve as a blueprint for the expected structure

fake = Faker()


@pytest.fixture
def app():
    """Create and configure a Flask app instance for testing."""
    # Import will be available when implementation is in place
    # from server.app import create_app

    # Mock app for now - replace with actual app creation
    app = MagicMock()
    app.config = {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False,
    }
    return app


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def db(app):
    """Create a test database."""
    # from server.models import db as _db

    # Mock database for now
    _db = MagicMock()
    _db.create_all = Mock()
    _db.drop_all = Mock()
    _db.session = MagicMock()

    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def session(db):
    """Create a database session for testing."""
    return db.session


@pytest.fixture
def sample_wallet():
    """Generate a sample Alephium wallet address."""
    # Alephium addresses start with '1' and are base58 encoded
    return f"1{fake.sha256()[:42]}"


@pytest.fixture
def sample_player_data(sample_wallet):
    """Generate sample player data."""
    return {
        'wallet_address': sample_wallet,
        'username': fake.user_name(),
        'total_ap': 0,
        'daily_ap': 0,
        'weekly_ap': 0,
        'monthly_ap': 0,
        'total_mined': 0.0,
        'verified': False,
        'verification_expires': None,
    }


@pytest.fixture
def verified_player_data(sample_player_data):
    """Generate sample verified player data."""
    data = sample_player_data.copy()
    data['verified'] = True
    data['verification_expires'] = datetime.utcnow() + timedelta(days=30)
    data['total_ap'] = 100
    data['total_mined'] = 50.5
    return data


@pytest.fixture
def sample_mining_event(sample_wallet):
    """Generate sample mining event data."""
    return {
        'wallet_address': sample_wallet,
        'amount': 1.5,
        'pool_id': 'pool_1',
        'timestamp': datetime.utcnow(),
        'block_hash': fake.sha256(),
    }


@pytest.fixture
def sample_pool_snapshot():
    """Generate sample pool snapshot data."""
    return {
        'pool_id': 'pool_1',
        'total_hashrate': 1000000000,
        'active_miners': 50,
        'last_block': fake.sha256(),
        'timestamp': datetime.utcnow(),
    }


@pytest.fixture
def sample_achievement():
    """Generate sample achievement data."""
    return {
        'id': 'first_mine',
        'name': 'First Steps',
        'description': 'Mine your first ALPH',
        'condition_type': 'total_mined',
        'condition_value': 1.0,
        'ap_reward': 10,
        'icon': 'pickaxe',
    }


@pytest.fixture
def mock_pool_response():
    """Generate mock pool API response."""
    return {
        'hashrate': 1000000000,
        'miners': 50,
        'blocks': [
            {
                'height': 12345,
                'hash': fake.sha256(),
                'timestamp': datetime.utcnow().isoformat(),
                'reward': 2.5,
                'miner': fake.sha256()[:42],
            }
        ],
        'payments': [
            {
                'address': fake.sha256()[:42],
                'amount': 1.5,
                'timestamp': datetime.utcnow().isoformat(),
                'txid': fake.sha256(),
            }
        ]
    }


@pytest.fixture
def mock_blockchain_response(sample_wallet):
    """Generate mock blockchain API response."""
    return {
        'address': sample_wallet,
        'balance': '1000000000000000000',  # 1 ALPH in wei
        'lockedBalance': '0',
        'txNumber': 10,
    }


@pytest.fixture
def multiple_players(sample_wallet):
    """Generate multiple sample players for leaderboard testing."""
    players = []
    for i in range(10):
        players.append({
            'wallet_address': f"1{fake.sha256()[:42]}",
            'username': fake.user_name(),
            'total_ap': (10 - i) * 100,  # Descending AP scores
            'daily_ap': (10 - i) * 10,
            'weekly_ap': (10 - i) * 50,
            'monthly_ap': (10 - i) * 80,
            'total_mined': (10 - i) * 10.5,
            'verified': True,
            'verification_expires': datetime.utcnow() + timedelta(days=30),
        })
    return players


@pytest.fixture
def mock_socketio():
    """Create a mock SocketIO instance."""
    socketio = MagicMock()
    socketio.emit = Mock()
    return socketio


@pytest.fixture(autouse=True)
def reset_db(db, session):
    """Automatically reset database between tests."""
    yield
    session.rollback()
    # Clean up all tables
    # This will be implemented when actual models are available


@pytest.fixture
def auth_headers(sample_wallet):
    """Generate authentication headers for API requests."""
    return {
        'X-Wallet-Address': sample_wallet,
        'Content-Type': 'application/json',
    }


@pytest.fixture
def mock_web3():
    """Create a mock Web3 instance for blockchain interactions."""
    web3 = MagicMock()
    web3.is_connected = Mock(return_value=True)
    web3.eth.get_balance = Mock(return_value=1000000000000000000)
    return web3


@pytest.fixture(scope='session')
def test_config():
    """Provide test configuration."""
    return {
        'TESTING': True,
        'DEBUG': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'SECRET_KEY': 'test-secret-key',
        'POOL_POLLING_INTERVAL': 1,  # Fast polling for tests
        'VERIFICATION_DURATION_DAYS': 30,
        'MIN_BALANCE_FOR_VERIFICATION': 1.0,
        'ACHIEVEMENTS_ENABLED': True,
    }


@pytest.fixture
def temp_db_file():
    """Create a temporary database file for integration tests."""
    fd, path = tempfile.mkstemp(suffix='.db')
    yield path
    os.close(fd)
    os.unlink(path)


# Async fixtures for async tests
@pytest.fixture
async def async_client(app):
    """Create an async test client."""
    async with app.test_client() as client:
        yield client


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
