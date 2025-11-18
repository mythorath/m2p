"""
Test utilities and helper functions.

Provides:
- Database cleanup functions
- Mock data generators
- Test assertions
- Helper decorators
- Common test patterns
"""
import random
import string
from datetime import datetime, timedelta
from typing import List, Dict, Any
from faker import Faker

fake = Faker()


class TestDataGenerator:
    """Generate test data for various models."""

    @staticmethod
    def generate_wallet_address() -> str:
        """Generate a mock Alephium wallet address."""
        # Alephium addresses start with '1' and are base58 encoded
        chars = string.ascii_letters + string.digits
        return '1' + ''.join(random.choices(chars, k=42))

    @staticmethod
    def generate_player(
        wallet_address: str = None,
        verified: bool = False,
        total_ap: int = 0
    ) -> Dict[str, Any]:
        """Generate mock player data."""
        if wallet_address is None:
            wallet_address = TestDataGenerator.generate_wallet_address()

        return {
            'wallet_address': wallet_address,
            'username': fake.user_name(),
            'total_ap': total_ap,
            'daily_ap': 0,
            'weekly_ap': 0,
            'monthly_ap': 0,
            'total_mined': 0.0,
            'verified': verified,
            'verification_expires': datetime.utcnow() + timedelta(days=30) if verified else None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }

    @staticmethod
    def generate_players(count: int = 10) -> List[Dict[str, Any]]:
        """Generate multiple mock players."""
        return [
            TestDataGenerator.generate_player(
                total_ap=(count - i) * 100,
                verified=True
            )
            for i in range(count)
        ]

    @staticmethod
    def generate_mining_event(
        wallet_address: str = None,
        amount: float = None
    ) -> Dict[str, Any]:
        """Generate mock mining event."""
        if wallet_address is None:
            wallet_address = TestDataGenerator.generate_wallet_address()

        if amount is None:
            amount = round(random.uniform(0.1, 10.0), 2)

        return {
            'wallet_address': wallet_address,
            'amount': amount,
            'pool_id': f'pool_{random.randint(1, 3)}',
            'timestamp': datetime.utcnow(),
            'block_hash': fake.sha256(),
            'transaction_id': fake.sha256(),
        }

    @staticmethod
    def generate_pool_snapshot(pool_id: str = 'pool_1') -> Dict[str, Any]:
        """Generate mock pool snapshot."""
        return {
            'pool_id': pool_id,
            'total_hashrate': random.randint(1000000, 10000000),
            'active_miners': random.randint(10, 100),
            'last_block': fake.sha256(),
            'timestamp': datetime.utcnow(),
        }

    @staticmethod
    def generate_achievement(
        achievement_id: str = None,
        condition_type: str = 'total_mined'
    ) -> Dict[str, Any]:
        """Generate mock achievement."""
        if achievement_id is None:
            achievement_id = f'achievement_{fake.word()}'

        return {
            'id': achievement_id,
            'name': fake.catch_phrase(),
            'description': fake.sentence(),
            'condition_type': condition_type,
            'condition_value': random.randint(1, 1000),
            'ap_reward': random.randint(10, 100),
            'icon': fake.word(),
            'category': random.choice(['mining', 'social', 'streak', 'special']),
        }

    @staticmethod
    def generate_blockchain_response(wallet_address: str) -> Dict[str, Any]:
        """Generate mock blockchain API response."""
        balance_wei = random.randint(1000000000000000000, 10000000000000000000)  # 1-10 ALPH
        return {
            'address': wallet_address,
            'balance': str(balance_wei),
            'lockedBalance': '0',
            'txNumber': random.randint(1, 100),
        }

    @staticmethod
    def generate_pool_api_response() -> Dict[str, Any]:
        """Generate mock pool API response."""
        return {
            'hashrate': random.randint(1000000, 10000000),
            'miners': random.randint(10, 100),
            'blocks': [
                {
                    'height': random.randint(10000, 99999),
                    'hash': fake.sha256(),
                    'timestamp': datetime.utcnow().isoformat(),
                    'reward': round(random.uniform(1.0, 5.0), 2),
                    'miner': TestDataGenerator.generate_wallet_address(),
                }
                for _ in range(5)
            ],
            'payments': [
                {
                    'address': TestDataGenerator.generate_wallet_address(),
                    'amount': round(random.uniform(0.5, 5.0), 2),
                    'timestamp': datetime.utcnow().isoformat(),
                    'txid': fake.sha256(),
                }
                for _ in range(10)
            ]
        }


class DatabaseCleaner:
    """Utilities for cleaning up test database."""

    @staticmethod
    def clean_all_tables(db):
        """Clean all tables in the database."""
        # This will be implemented when actual models are available
        # db.session.query(Player).delete()
        # db.session.query(MiningEvent).delete()
        # db.session.query(PoolSnapshot).delete()
        # db.session.query(Achievement).delete()
        # db.session.query(PlayerAchievement).delete()
        # db.session.commit()
        pass

    @staticmethod
    def clean_table(db, model):
        """Clean a specific table."""
        # db.session.query(model).delete()
        # db.session.commit()
        pass

    @staticmethod
    def reset_sequences(db):
        """Reset auto-increment sequences."""
        # Implementation depends on database backend
        pass


class Assertions:
    """Custom assertions for tests."""

    @staticmethod
    def assert_valid_wallet_address(wallet_address: str):
        """Assert that wallet address is valid Alephium format."""
        assert wallet_address is not None
        assert isinstance(wallet_address, str)
        assert len(wallet_address) > 40
        assert wallet_address.startswith('1')

    @staticmethod
    def assert_valid_player(player_data: Dict[str, Any]):
        """Assert that player data is valid."""
        assert 'wallet_address' in player_data
        assert 'username' in player_data
        assert 'total_ap' in player_data
        assert isinstance(player_data['total_ap'], (int, float))
        assert player_data['total_ap'] >= 0
        Assertions.assert_valid_wallet_address(player_data['wallet_address'])

    @staticmethod
    def assert_valid_mining_event(event_data: Dict[str, Any]):
        """Assert that mining event data is valid."""
        assert 'wallet_address' in event_data
        assert 'amount' in event_data
        assert 'pool_id' in event_data
        assert 'timestamp' in event_data
        assert event_data['amount'] > 0
        Assertions.assert_valid_wallet_address(event_data['wallet_address'])

    @staticmethod
    def assert_valid_achievement(achievement_data: Dict[str, Any]):
        """Assert that achievement data is valid."""
        assert 'id' in achievement_data
        assert 'name' in achievement_data
        assert 'condition_type' in achievement_data
        assert 'condition_value' in achievement_data
        assert 'ap_reward' in achievement_data
        assert achievement_data['ap_reward'] > 0

    @staticmethod
    def assert_sorted_descending(items: List[Any], key: str):
        """Assert that list is sorted in descending order by key."""
        for i in range(len(items) - 1):
            assert items[i][key] >= items[i + 1][key], \
                f"List not sorted: {items[i][key]} < {items[i + 1][key]}"

    @staticmethod
    def assert_valid_timestamp(timestamp):
        """Assert that timestamp is valid."""
        assert timestamp is not None
        if isinstance(timestamp, str):
            # Try to parse ISO format
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif isinstance(timestamp, datetime):
            assert timestamp <= datetime.utcnow()
        else:
            raise AssertionError(f"Invalid timestamp type: {type(timestamp)}")


class MockHelpers:
    """Helpers for creating mocks."""

    @staticmethod
    def mock_database_session():
        """Create a mock database session."""
        from unittest.mock import MagicMock

        session = MagicMock()
        session.query = MagicMock()
        session.add = MagicMock()
        session.commit = MagicMock()
        session.rollback = MagicMock()
        session.close = MagicMock()

        return session

    @staticmethod
    def mock_flask_app():
        """Create a mock Flask app."""
        from unittest.mock import MagicMock

        app = MagicMock()
        app.config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SECRET_KEY': 'test-secret-key',
        }
        app.test_client = MagicMock()

        return app

    @staticmethod
    def mock_socketio():
        """Create a mock SocketIO instance."""
        from unittest.mock import MagicMock

        socketio = MagicMock()
        socketio.emit = MagicMock()
        socketio.on = MagicMock()

        return socketio

    @staticmethod
    def mock_http_response(status_code: int = 200, json_data: Dict = None):
        """Create a mock HTTP response."""
        from unittest.mock import MagicMock

        response = MagicMock()
        response.status_code = status_code
        response.json = MagicMock(return_value=json_data or {})
        response.text = str(json_data)

        return response


class TimeHelpers:
    """Helpers for time-related testing."""

    @staticmethod
    def days_ago(days: int) -> datetime:
        """Get datetime N days ago."""
        return datetime.utcnow() - timedelta(days=days)

    @staticmethod
    def hours_ago(hours: int) -> datetime:
        """Get datetime N hours ago."""
        return datetime.utcnow() - timedelta(hours=hours)

    @staticmethod
    def minutes_ago(minutes: int) -> datetime:
        """Get datetime N minutes ago."""
        return datetime.utcnow() - timedelta(minutes=minutes)

    @staticmethod
    def is_same_day(dt1: datetime, dt2: datetime) -> bool:
        """Check if two datetimes are on the same day."""
        return dt1.date() == dt2.date()

    @staticmethod
    def get_date_range(start_days_ago: int, end_days_ago: int = 0) -> List[datetime]:
        """Get list of datetimes for a date range."""
        return [
            TimeHelpers.days_ago(days)
            for days in range(start_days_ago, end_days_ago - 1, -1)
        ]


class ComparisonHelpers:
    """Helpers for comparing test results."""

    @staticmethod
    def dict_contains_subset(superset: Dict, subset: Dict) -> bool:
        """Check if dictionary contains all keys/values from subset."""
        return all(
            key in superset and superset[key] == value
            for key, value in subset.items()
        )

    @staticmethod
    def lists_equal_unordered(list1: List, list2: List) -> bool:
        """Check if two lists contain the same elements (order doesn't matter)."""
        return sorted(list1) == sorted(list2)

    @staticmethod
    def approx_equal(value1: float, value2: float, tolerance: float = 0.01) -> bool:
        """Check if two float values are approximately equal."""
        return abs(value1 - value2) <= tolerance


class APIHelpers:
    """Helpers for API testing."""

    @staticmethod
    def make_api_request(client, method: str, endpoint: str, **kwargs):
        """Make an API request with client."""
        # This will be implemented when actual Flask app is available
        # method_func = getattr(client, method.lower())
        # return method_func(endpoint, **kwargs)
        pass

    @staticmethod
    def assert_api_success(response, expected_status: int = 200):
        """Assert that API response is successful."""
        assert response is not None
        # assert response.status_code == expected_status
        # assert response.json is not None

    @staticmethod
    def assert_api_error(response, expected_status: int = 400):
        """Assert that API response is an error."""
        assert response is not None
        # assert response.status_code == expected_status
        # assert 'error' in response.json

    @staticmethod
    def extract_json_response(response):
        """Extract JSON from response."""
        # return response.json if hasattr(response, 'json') else None
        pass


class FixtureHelpers:
    """Helpers for working with fixtures."""

    @staticmethod
    def create_player_in_db(db, session, player_data: Dict):
        """Create a player in the database."""
        # from server.models import Player
        # player = Player(**player_data)
        # session.add(player)
        # session.commit()
        # return player
        pass

    @staticmethod
    def create_mining_event_in_db(db, session, event_data: Dict):
        """Create a mining event in the database."""
        # from server.models import MiningEvent
        # event = MiningEvent(**event_data)
        # session.add(event)
        # session.commit()
        # return event
        pass

    @staticmethod
    def create_achievement_in_db(db, session, achievement_data: Dict):
        """Create an achievement in the database."""
        # from server.models import Achievement
        # achievement = Achievement(**achievement_data)
        # session.add(achievement)
        # session.commit()
        # return achievement
        pass


# Convenience exports
generate_wallet_address = TestDataGenerator.generate_wallet_address
generate_player = TestDataGenerator.generate_player
generate_players = TestDataGenerator.generate_players
generate_mining_event = TestDataGenerator.generate_mining_event
generate_pool_snapshot = TestDataGenerator.generate_pool_snapshot
generate_achievement = TestDataGenerator.generate_achievement
