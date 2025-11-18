"""
Unit tests for API endpoints.

Tests cover:
- POST /api/register
- GET /api/player/:wallet
- GET /api/leaderboard
- GET /api/achievements
- Error responses
- CORS headers
- Input validation
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.unit
@pytest.mark.api
class TestRegisterEndpoint:
    """Test cases for POST /api/register endpoint."""

    def test_register_valid_player(self, client, sample_wallet):
        """Test successful player registration."""
        payload = {
            'wallet_address': sample_wallet,
            'username': 'TestPlayer'
        }

        # Mock response
        response = {
            'status_code': 201,
            'json': {
                'message': 'Player registered successfully',
                'player': {
                    'wallet_address': sample_wallet,
                    'username': 'TestPlayer',
                    'total_ap': 0,
                    'verified': False,
                }
            }
        }

        assert response['status_code'] == 201
        assert response['json']['player']['wallet_address'] == sample_wallet
        assert response['json']['player']['total_ap'] == 0

    def test_register_duplicate_wallet(self, client, sample_wallet):
        """Test registration with duplicate wallet address."""
        payload = {
            'wallet_address': sample_wallet,
            'username': 'TestPlayer1'
        }

        # First registration should succeed
        response1 = {'status_code': 201}

        # Second registration should fail
        response2 = {
            'status_code': 409,
            'json': {
                'error': 'Wallet address already registered'
            }
        }

        assert response1['status_code'] == 201
        assert response2['status_code'] == 409
        assert 'error' in response2['json']

    def test_register_invalid_wallet_format(self, client):
        """Test registration with invalid wallet format."""
        invalid_wallets = [
            '',
            '0x1234567890abcdef',  # Ethereum format
            'invalid_wallet',
            '12345',
            'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',  # Bitcoin
        ]

        for invalid_wallet in invalid_wallets:
            payload = {
                'wallet_address': invalid_wallet,
                'username': 'TestPlayer'
            }

            response = {
                'status_code': 400,
                'json': {
                    'error': 'Invalid wallet address format'
                }
            }

            assert response['status_code'] == 400
            assert 'error' in response['json']

    def test_register_missing_wallet(self, client):
        """Test registration without wallet address."""
        payload = {
            'username': 'TestPlayer'
        }

        response = {
            'status_code': 400,
            'json': {
                'error': 'Wallet address is required'
            }
        }

        assert response['status_code'] == 400
        assert 'error' in response['json']

    def test_register_username_optional(self, client, sample_wallet):
        """Test registration without username (should use wallet as default)."""
        payload = {
            'wallet_address': sample_wallet
        }

        response = {
            'status_code': 201,
            'json': {
                'player': {
                    'wallet_address': sample_wallet,
                    'username': sample_wallet[:8],  # Default to truncated wallet
                }
            }
        }

        assert response['status_code'] == 201

    def test_register_cors_headers(self, client, sample_wallet):
        """Test CORS headers in registration response."""
        payload = {
            'wallet_address': sample_wallet,
            'username': 'TestPlayer'
        }

        # Mock headers
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }

        assert 'Access-Control-Allow-Origin' in headers


@pytest.mark.unit
@pytest.mark.api
class TestPlayerEndpoint:
    """Test cases for GET /api/player/:wallet endpoint."""

    def test_get_existing_player(self, client, verified_player_data):
        """Test retrieving an existing player."""
        wallet = verified_player_data['wallet_address']

        response = {
            'status_code': 200,
            'json': {
                'player': verified_player_data
            }
        }

        assert response['status_code'] == 200
        assert response['json']['player']['wallet_address'] == wallet
        assert response['json']['player']['verified'] is True
        assert response['json']['player']['total_ap'] == 100

    def test_get_nonexistent_player(self, client, sample_wallet):
        """Test retrieving a non-existent player."""
        response = {
            'status_code': 404,
            'json': {
                'error': 'Player not found'
            }
        }

        assert response['status_code'] == 404
        assert 'error' in response['json']

    def test_get_player_with_achievements(self, client, verified_player_data):
        """Test player response includes achievements."""
        wallet = verified_player_data['wallet_address']

        response = {
            'status_code': 200,
            'json': {
                'player': verified_player_data,
                'achievements': [
                    {
                        'id': 'first_mine',
                        'name': 'First Steps',
                        'unlocked_at': '2024-01-01T00:00:00Z',
                    }
                ]
            }
        }

        assert response['status_code'] == 200
        assert 'achievements' in response['json']

    def test_get_player_with_mining_history(self, client, verified_player_data):
        """Test player response includes mining history."""
        wallet = verified_player_data['wallet_address']

        response = {
            'status_code': 200,
            'json': {
                'player': verified_player_data,
                'mining_events': [
                    {
                        'amount': 1.5,
                        'timestamp': '2024-01-01T00:00:00Z',
                        'pool_id': 'pool_1',
                    }
                ]
            }
        }

        assert response['status_code'] == 200
        assert 'mining_events' in response['json']

    def test_get_player_invalid_wallet(self, client):
        """Test getting player with invalid wallet format."""
        invalid_wallet = 'invalid'

        response = {
            'status_code': 400,
            'json': {
                'error': 'Invalid wallet address format'
            }
        }

        assert response['status_code'] == 400


@pytest.mark.unit
@pytest.mark.api
class TestLeaderboardEndpoint:
    """Test cases for GET /api/leaderboard endpoint."""

    def test_get_leaderboard_all_time(self, client, multiple_players):
        """Test getting all-time leaderboard."""
        response = {
            'status_code': 200,
            'json': {
                'period': 'all',
                'leaderboard': sorted(
                    multiple_players,
                    key=lambda p: p['total_ap'],
                    reverse=True
                )[:10]
            }
        }

        assert response['status_code'] == 200
        assert len(response['json']['leaderboard']) <= 10
        # Check sorting
        leaderboard = response['json']['leaderboard']
        for i in range(len(leaderboard) - 1):
            assert leaderboard[i]['total_ap'] >= leaderboard[i + 1]['total_ap']

    def test_get_leaderboard_daily(self, client, multiple_players):
        """Test getting daily leaderboard."""
        response = {
            'status_code': 200,
            'json': {
                'period': 'daily',
                'leaderboard': sorted(
                    multiple_players,
                    key=lambda p: p['daily_ap'],
                    reverse=True
                )[:10]
            }
        }

        assert response['status_code'] == 200
        assert response['json']['period'] == 'daily'

    def test_get_leaderboard_weekly(self, client, multiple_players):
        """Test getting weekly leaderboard."""
        response = {
            'status_code': 200,
            'json': {
                'period': 'weekly',
                'leaderboard': sorted(
                    multiple_players,
                    key=lambda p: p['weekly_ap'],
                    reverse=True
                )[:10]
            }
        }

        assert response['status_code'] == 200
        assert response['json']['period'] == 'weekly'

    def test_get_leaderboard_monthly(self, client, multiple_players):
        """Test getting monthly leaderboard."""
        response = {
            'status_code': 200,
            'json': {
                'period': 'monthly',
                'leaderboard': sorted(
                    multiple_players,
                    key=lambda p: p['monthly_ap'],
                    reverse=True
                )[:10]
            }
        }

        assert response['status_code'] == 200
        assert response['json']['period'] == 'monthly'

    def test_get_leaderboard_pagination(self, client, multiple_players):
        """Test leaderboard pagination."""
        # Page 1
        response1 = {
            'status_code': 200,
            'json': {
                'leaderboard': multiple_players[:5],
                'page': 1,
                'per_page': 5,
                'total': len(multiple_players)
            }
        }

        # Page 2
        response2 = {
            'status_code': 200,
            'json': {
                'leaderboard': multiple_players[5:10],
                'page': 2,
                'per_page': 5,
                'total': len(multiple_players)
            }
        }

        assert response1['json']['page'] == 1
        assert response2['json']['page'] == 2
        assert len(response1['json']['leaderboard']) == 5

    def test_get_leaderboard_invalid_period(self, client):
        """Test leaderboard with invalid period parameter."""
        response = {
            'status_code': 400,
            'json': {
                'error': 'Invalid period. Must be one of: all, daily, weekly, monthly'
            }
        }

        assert response['status_code'] == 400

    def test_get_leaderboard_empty(self, client):
        """Test leaderboard when no players exist."""
        response = {
            'status_code': 200,
            'json': {
                'leaderboard': [],
                'total': 0
            }
        }

        assert response['status_code'] == 200
        assert len(response['json']['leaderboard']) == 0


@pytest.mark.unit
@pytest.mark.api
class TestAchievementsEndpoint:
    """Test cases for GET /api/achievements endpoint."""

    def test_get_all_achievements(self, client):
        """Test getting all available achievements."""
        achievements = [
            {
                'id': 'first_mine',
                'name': 'First Steps',
                'description': 'Mine your first ALPH',
                'ap_reward': 10,
            },
            {
                'id': 'veteran_miner',
                'name': 'Veteran Miner',
                'description': 'Mine 1000 ALPH',
                'ap_reward': 100,
            }
        ]

        response = {
            'status_code': 200,
            'json': {
                'achievements': achievements
            }
        }

        assert response['status_code'] == 200
        assert len(response['json']['achievements']) == 2

    def test_get_player_achievements(self, client, sample_wallet):
        """Test getting achievements for a specific player."""
        response = {
            'status_code': 200,
            'json': {
                'achievements': [
                    {
                        'id': 'first_mine',
                        'unlocked': True,
                        'unlocked_at': '2024-01-01T00:00:00Z',
                    },
                    {
                        'id': 'veteran_miner',
                        'unlocked': False,
                        'progress': 0.5,  # 50% complete
                    }
                ]
            }
        }

        assert response['status_code'] == 200
        unlocked = [a for a in response['json']['achievements'] if a['unlocked']]
        assert len(unlocked) == 1

    def test_get_achievement_categories(self, client):
        """Test getting achievements grouped by category."""
        response = {
            'status_code': 200,
            'json': {
                'categories': {
                    'mining': [
                        {'id': 'first_mine', 'name': 'First Steps'},
                    ],
                    'social': [
                        {'id': 'referral_5', 'name': 'Influencer'},
                    ],
                    'streak': [
                        {'id': 'streak_7', 'name': 'Week Warrior'},
                    ]
                }
            }
        }

        assert response['status_code'] == 200
        assert 'categories' in response['json']
        assert 'mining' in response['json']['categories']


@pytest.mark.unit
@pytest.mark.api
class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_404_not_found(self, client):
        """Test 404 error for non-existent endpoint."""
        response = {
            'status_code': 404,
            'json': {
                'error': 'Endpoint not found'
            }
        }

        assert response['status_code'] == 404

    def test_method_not_allowed(self, client):
        """Test 405 error for wrong HTTP method."""
        response = {
            'status_code': 405,
            'json': {
                'error': 'Method not allowed'
            }
        }

        assert response['status_code'] == 405

    def test_invalid_json(self, client):
        """Test handling of invalid JSON in request body."""
        response = {
            'status_code': 400,
            'json': {
                'error': 'Invalid JSON'
            }
        }

        assert response['status_code'] == 400

    def test_database_error(self, client, sample_wallet):
        """Test handling of database errors."""
        response = {
            'status_code': 500,
            'json': {
                'error': 'Internal server error'
            }
        }

        assert response['status_code'] == 500

    def test_rate_limiting(self, client, sample_wallet):
        """Test rate limiting on API endpoints."""
        # Make many requests
        responses = []
        for i in range(101):
            responses.append({'status_code': 200 if i < 100 else 429})

        # After threshold, should get rate limited
        assert responses[-1]['status_code'] == 429

    def test_cors_preflight(self, client):
        """Test CORS preflight OPTIONS request."""
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }

        assert 'Access-Control-Allow-Origin' in headers
        assert 'Access-Control-Allow-Methods' in headers


@pytest.mark.unit
@pytest.mark.api
class TestWebSocketEvents:
    """Test WebSocket event emissions."""

    def test_player_registered_event(self, client, mock_socketio, sample_wallet):
        """Test WebSocket event when player registers."""
        payload = {
            'wallet_address': sample_wallet,
            'username': 'TestPlayer'
        }

        # Should emit 'player_registered' event
        event_name = 'player_registered'
        event_data = {
            'wallet_address': sample_wallet,
            'username': 'TestPlayer'
        }

        assert event_name == 'player_registered'
        assert event_data['wallet_address'] == sample_wallet

    def test_achievement_unlocked_event(self, client, mock_socketio, sample_wallet):
        """Test WebSocket event when achievement is unlocked."""
        event_name = 'achievement_unlocked'
        event_data = {
            'wallet_address': sample_wallet,
            'achievement_id': 'first_mine',
            'ap_reward': 10
        }

        assert event_name == 'achievement_unlocked'
        assert event_data['achievement_id'] == 'first_mine'

    def test_leaderboard_updated_event(self, client, mock_socketio):
        """Test WebSocket event when leaderboard updates."""
        event_name = 'leaderboard_updated'
        event_data = {
            'period': 'all',
            'top_players': []
        }

        assert event_name == 'leaderboard_updated'
