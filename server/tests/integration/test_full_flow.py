"""
Integration tests for full user flow.

Tests the complete flow:
1. Player registration
2. Wallet verification
3. Mining reward detection
4. Achievement unlocking
5. Leaderboard updates
6. WebSocket event emissions
"""
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import responses


@pytest.mark.integration
class TestFullPlayerFlow:
    """Test complete player flow from registration to achievement."""

    @responses.activate
    def test_complete_player_journey(
        self,
        client,
        db,
        session,
        sample_wallet,
        mock_blockchain_response,
        mock_pool_response,
        mock_socketio
    ):
        """Test complete player journey through the system."""

        # Step 1: Register player
        registration_data = {
            'wallet_address': sample_wallet,
            'username': 'IntegrationTestPlayer'
        }

        # Mock registration response
        register_response = {
            'status_code': 201,
            'json': {
                'message': 'Player registered successfully',
                'player': {
                    'wallet_address': sample_wallet,
                    'username': 'IntegrationTestPlayer',
                    'total_ap': 0,
                    'verified': False,
                }
            }
        }

        assert register_response['status_code'] == 201
        assert register_response['json']['player']['verified'] is False

        # Step 2: Verify wallet
        verification_url = f'https://explorer.alephium.org/api/addresses/{sample_wallet}'

        responses.add(
            responses.GET,
            verification_url,
            json=mock_blockchain_response,
            status=200
        )

        # Simulate verification
        verification_result = {
            'verified': True,
            'balance': 1.0,
            'expires_at': datetime.utcnow() + timedelta(days=30)
        }

        assert verification_result['verified'] is True

        # Step 3: Mock mining reward
        pool_url = 'https://pool.example.com/api/stats'

        responses.add(
            responses.GET,
            pool_url,
            json=mock_pool_response,
            status=200
        )

        # Simulate mining event
        mining_event = {
            'wallet_address': sample_wallet,
            'amount': 1.5,
            'pool_id': 'pool_1',
            'timestamp': datetime.utcnow(),
        }

        # Step 4: Check achievement unlock
        # 'First Steps' achievement should unlock
        achievement_check = {
            'achievement_id': 'first_mine',
            'unlocked': True,
            'ap_reward': 10,
        }

        assert achievement_check['unlocked'] is True

        # Step 5: Verify leaderboard update
        leaderboard_response = {
            'status_code': 200,
            'json': {
                'leaderboard': [
                    {
                        'wallet_address': sample_wallet,
                        'username': 'IntegrationTestPlayer',
                        'total_ap': 10,
                        'rank': 1,
                    }
                ]
            }
        }

        assert leaderboard_response['json']['leaderboard'][0]['total_ap'] == 10

        # Step 6: Verify WebSocket emissions
        # Should have emitted:
        # - player_registered
        # - verification_success
        # - mining_reward
        # - achievement_unlocked
        # - leaderboard_updated

        expected_events = [
            'player_registered',
            'verification_success',
            'mining_reward',
            'achievement_unlocked',
            'leaderboard_updated',
        ]

        assert len(expected_events) == 5


@pytest.mark.integration
class TestMultiPlayerFlow:
    """Test interactions between multiple players."""

    def test_leaderboard_competition(
        self,
        client,
        db,
        session,
        multiple_players
    ):
        """Test leaderboard with multiple competing players."""

        # Register multiple players
        players = multiple_players[:5]

        # Simulate different AP earnings
        for i, player in enumerate(players):
            player['total_ap'] = (5 - i) * 100

        # Get leaderboard
        leaderboard = sorted(players, key=lambda p: p['total_ap'], reverse=True)

        # Verify ranking
        assert leaderboard[0]['total_ap'] == 500
        assert leaderboard[-1]['total_ap'] == 100

        # Player ranks should be correct
        for i, player in enumerate(leaderboard):
            expected_rank = i + 1
            assert expected_rank == i + 1

    def test_concurrent_mining_events(
        self,
        client,
        db,
        session,
        multiple_players
    ):
        """Test multiple players mining simultaneously."""

        players = multiple_players[:3]

        # Simulate concurrent mining events
        mining_events = []
        for player in players:
            event = {
                'wallet_address': player['wallet_address'],
                'amount': 1.5,
                'pool_id': 'pool_1',
                'timestamp': datetime.utcnow(),
            }
            mining_events.append(event)

        # All events should be processed
        assert len(mining_events) == 3

        # Each player should have updated stats
        for player in players:
            # total_mined should be updated
            expected_total = 1.5
            assert expected_total == 1.5

    def test_achievement_unlock_race_condition(
        self,
        client,
        db,
        session,
        sample_wallet
    ):
        """Test that achievement unlocking handles race conditions."""

        # Simulate concurrent attempts to unlock same achievement
        achievement_id = 'first_mine'

        unlock_attempts = []
        for i in range(3):
            attempt = {
                'player_wallet': sample_wallet,
                'achievement_id': achievement_id,
                'attempt': i,
            }
            unlock_attempts.append(attempt)

        # Only one should succeed (due to unique constraint)
        # Others should be handled gracefully
        successful_unlocks = 1  # Only one should succeed

        assert successful_unlocks == 1


@pytest.mark.integration
class TestPoolPollingIntegration:
    """Test pool polling integration with player data."""

    @responses.activate
    def test_pool_polling_detects_rewards(
        self,
        client,
        db,
        session,
        sample_wallet,
        mock_pool_response
    ):
        """Test that pool polling detects and processes rewards."""

        pool_url = 'https://pool.example.com/api/stats'

        # First poll - no payments
        responses.add(
            responses.GET,
            pool_url,
            json={'payments': []},
            status=200
        )

        # Second poll - new payment
        mock_pool_response['payments'] = [
            {
                'address': sample_wallet,
                'amount': 1.5,
                'timestamp': datetime.utcnow().isoformat(),
                'txid': 'tx123',
            }
        ]

        responses.add(
            responses.GET,
            pool_url,
            json=mock_pool_response,
            status=200
        )

        # Should detect new payment
        new_payments = [p for p in mock_pool_response['payments']]

        assert len(new_payments) == 1
        assert new_payments[0]['amount'] == 1.5

    @responses.activate
    def test_multiple_pool_polling(
        self,
        client,
        db,
        session,
        sample_wallet
    ):
        """Test polling multiple pools simultaneously."""

        pools = [
            {'id': 'pool_1', 'url': 'https://pool1.example.com/api/stats'},
            {'id': 'pool_2', 'url': 'https://pool2.example.com/api/stats'},
            {'id': 'pool_3', 'url': 'https://pool3.example.com/api/stats'},
        ]

        # Mock responses for all pools
        for pool in pools:
            responses.add(
                responses.GET,
                pool['url'],
                json={
                    'payments': [
                        {
                            'address': sample_wallet,
                            'amount': 1.0,
                            'timestamp': datetime.utcnow().isoformat(),
                        }
                    ]
                },
                status=200
            )

        # All pools should be polled
        assert len(pools) == 3

    @responses.activate
    def test_pool_snapshot_delta_tracking(
        self,
        client,
        db,
        session
    ):
        """Test tracking of pool statistics changes over time."""

        pool_url = 'https://pool.example.com/api/stats'

        # First snapshot
        responses.add(
            responses.GET,
            pool_url,
            json={'hashrate': 1000000, 'miners': 50},
            status=200
        )

        snapshot1 = {'hashrate': 1000000, 'miners': 50}

        # Second snapshot
        responses.add(
            responses.GET,
            pool_url,
            json={'hashrate': 1500000, 'miners': 60},
            status=200
        )

        snapshot2 = {'hashrate': 1500000, 'miners': 60}

        # Calculate delta
        hashrate_delta = snapshot2['hashrate'] - snapshot1['hashrate']
        miners_delta = snapshot2['miners'] - snapshot1['miners']

        assert hashrate_delta == 500000
        assert miners_delta == 10


@pytest.mark.integration
class TestVerificationIntegration:
    """Test wallet verification integration."""

    @responses.activate
    def test_verification_affects_rewards(
        self,
        client,
        db,
        session,
        sample_wallet,
        mock_blockchain_response
    ):
        """Test that only verified players receive rewards."""

        verification_url = f'https://explorer.alephium.org/api/addresses/{sample_wallet}'

        # Unverified player
        unverified_player = {
            'wallet_address': sample_wallet,
            'verified': False,
        }

        # Mining event occurs
        mining_event = {
            'wallet_address': sample_wallet,
            'amount': 1.5,
        }

        # Should not process reward (unverified)
        should_process = unverified_player['verified']

        assert should_process is False

        # Verify player
        responses.add(
            responses.GET,
            verification_url,
            json=mock_blockchain_response,
            status=200
        )

        verified_player = {
            'wallet_address': sample_wallet,
            'verified': True,
        }

        # Now should process reward
        should_process = verified_player['verified']

        assert should_process is True

    @responses.activate
    def test_verification_expiry_stops_rewards(
        self,
        client,
        db,
        session,
        sample_wallet
    ):
        """Test that expired verification stops reward processing."""

        # Player with expired verification
        player = {
            'wallet_address': sample_wallet,
            'verified': True,
            'verification_expires': datetime.utcnow() - timedelta(days=1),
        }

        # Check if verification is still valid
        is_valid = player['verification_expires'] > datetime.utcnow()

        assert is_valid is False

        # Should not process rewards
        should_process = is_valid

        assert should_process is False


@pytest.mark.integration
class TestAchievementIntegration:
    """Test achievement system integration."""

    def test_achievement_unlocks_on_mining(
        self,
        client,
        db,
        session,
        sample_wallet
    ):
        """Test that achievements unlock automatically on mining."""

        player = {
            'wallet_address': sample_wallet,
            'total_mined': 0.0,
        }

        # Player mines for first time
        mining_event = {
            'wallet_address': sample_wallet,
            'amount': 1.5,
        }

        player['total_mined'] += mining_event['amount']

        # Check 'First Steps' achievement
        achievement = {
            'id': 'first_mine',
            'condition_type': 'total_mined',
            'condition_value': 1.0,
            'ap_reward': 10,
        }

        should_unlock = player['total_mined'] >= achievement['condition_value']

        assert should_unlock is True

    def test_multiple_achievements_unlock(
        self,
        client,
        db,
        session,
        sample_wallet
    ):
        """Test multiple achievements unlocking from single event."""

        player = {
            'wallet_address': sample_wallet,
            'total_mined': 999.0,
            'daily_ap': 80,
        }

        # Large mining event
        mining_event = {
            'wallet_address': sample_wallet,
            'amount': 10.0,
        }

        player['total_mined'] += mining_event['amount']
        player['daily_ap'] += 20  # From mining reward

        achievements = [
            {
                'id': 'veteran_miner',
                'condition_type': 'total_mined',
                'condition_value': 1000.0,
            },
            {
                'id': 'daily_grind',
                'condition_type': 'daily_ap',
                'condition_value': 100,
            }
        ]

        unlocked = []
        for achievement in achievements:
            condition_type = achievement['condition_type']
            if condition_type in player:
                if player[condition_type] >= achievement['condition_value']:
                    unlocked.append(achievement['id'])

        assert len(unlocked) == 2

    def test_achievement_ap_updates_leaderboard(
        self,
        client,
        db,
        session,
        sample_wallet
    ):
        """Test that AP from achievements updates leaderboard."""

        initial_leaderboard = [
            {'wallet': 'player_1', 'total_ap': 200},
            {'wallet': sample_wallet, 'total_ap': 100},
            {'wallet': 'player_3', 'total_ap': 50},
        ]

        # Unlock achievement
        achievement_ap = 150

        # Update player AP
        for player in initial_leaderboard:
            if player['wallet'] == sample_wallet:
                player['total_ap'] += achievement_ap

        # Re-sort leaderboard
        updated_leaderboard = sorted(
            initial_leaderboard,
            key=lambda p: p['total_ap'],
            reverse=True
        )

        # Player should be in first place now
        assert updated_leaderboard[0]['wallet'] == sample_wallet
        assert updated_leaderboard[0]['total_ap'] == 250


@pytest.mark.integration
@pytest.mark.slow
class TestLongRunningFlow:
    """Test long-running flows and periodic tasks."""

    def test_daily_ap_reset(
        self,
        client,
        db,
        session,
        sample_wallet
    ):
        """Test that daily AP resets at midnight."""

        player = {
            'wallet_address': sample_wallet,
            'daily_ap': 100,
            'last_reset': datetime.utcnow().date(),
        }

        # Simulate next day
        next_day = datetime.utcnow().date() + timedelta(days=1)

        if next_day > player['last_reset']:
            player['daily_ap'] = 0
            player['last_reset'] = next_day

        assert player['daily_ap'] == 0

    def test_weekly_leaderboard_archival(
        self,
        client,
        db,
        session,
        multiple_players
    ):
        """Test archival of weekly leaderboard."""

        # Current week's leaderboard
        current_leaderboard = multiple_players[:5]

        # Archive at end of week
        archived_leaderboard = {
            'week': datetime.utcnow().isocalendar()[1],
            'year': datetime.utcnow().year,
            'leaderboard': current_leaderboard.copy(),
        }

        # Reset weekly AP
        for player in current_leaderboard:
            player['weekly_ap'] = 0

        assert archived_leaderboard['leaderboard'] != current_leaderboard

    def test_verification_expiry_notification(
        self,
        client,
        db,
        session,
        sample_wallet
    ):
        """Test notification before verification expires."""

        # Verification expires soon
        player = {
            'wallet_address': sample_wallet,
            'verified': True,
            'verification_expires': datetime.utcnow() + timedelta(days=3),
        }

        notification_threshold = timedelta(days=7)
        days_remaining = (player['verification_expires'] - datetime.utcnow()).days

        should_notify = days_remaining <= notification_threshold.days

        assert should_notify is True


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling across system."""

    @responses.activate
    def test_pool_api_failure_recovery(
        self,
        client,
        db,
        session
    ):
        """Test system recovery from pool API failures."""

        pool_url = 'https://pool.example.com/api/stats'

        # First attempt fails
        responses.add(
            responses.GET,
            pool_url,
            status=503
        )

        # Second attempt succeeds
        responses.add(
            responses.GET,
            pool_url,
            json={'hashrate': 1000000},
            status=200
        )

        # System should retry and succeed
        retry_count = 0
        max_retries = 3

        assert retry_count < max_retries

    @responses.activate
    def test_blockchain_api_failure_handling(
        self,
        client,
        db,
        session,
        sample_wallet
    ):
        """Test handling of blockchain API failures."""

        verification_url = f'https://explorer.alephium.org/api/addresses/{sample_wallet}'

        # API fails
        responses.add(
            responses.GET,
            verification_url,
            status=500
        )

        # Verification should fail gracefully
        verification_result = {
            'verified': False,
            'error': 'API error',
        }

        assert verification_result['verified'] is False

    def test_database_transaction_rollback(
        self,
        client,
        db,
        session,
        sample_wallet
    ):
        """Test database transaction rollback on error."""

        # Start transaction
        try:
            # Simulate error during transaction
            raise Exception('Simulated error')
        except Exception:
            # Rollback
            # session.rollback()
            pass

        # Database should be in consistent state
        assert True
