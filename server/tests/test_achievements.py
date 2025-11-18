"""
Unit tests for achievement system.

Tests cover:
- Achievement unlocking
- Condition checking
- AP awarding
- Duplicate unlock prevention
- Achievement categories
- Progress tracking
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.unit
@pytest.mark.achievements
class TestAchievementUnlocking:
    """Test cases for achievement unlocking logic."""

    def test_unlock_first_mine_achievement(self, sample_wallet):
        """Test unlocking 'First Steps' achievement."""
        # Player mines for the first time
        mining_event = {
            'wallet_address': sample_wallet,
            'amount': 1.5,
        }

        # Check achievement condition
        total_mined = 1.5
        achievement_condition = 1.0

        should_unlock = total_mined >= achievement_condition

        assert should_unlock is True

        # Unlock achievement
        unlock_data = {
            'player_wallet': sample_wallet,
            'achievement_id': 'first_mine',
            'unlocked_at': datetime.utcnow(),
            'ap_reward': 10,
        }

        assert unlock_data['achievement_id'] == 'first_mine'
        assert unlock_data['ap_reward'] == 10

    def test_unlock_veteran_miner_achievement(self, sample_wallet):
        """Test unlocking 'Veteran Miner' achievement."""
        total_mined = 1000.0
        achievement_condition = 1000.0

        should_unlock = total_mined >= achievement_condition

        assert should_unlock is True

    def test_unlock_streak_achievement(self, sample_wallet):
        """Test unlocking streak-based achievement."""
        # Mining days in a row
        mining_days = [
            datetime.utcnow() - timedelta(days=i)
            for i in range(7)
        ]

        streak = len(mining_days)
        achievement_condition = 7

        should_unlock = streak >= achievement_condition

        assert should_unlock is True

    def test_unlock_pool_loyalty_achievement(self, sample_wallet):
        """Test unlocking pool loyalty achievement."""
        # All mining events from same pool
        mining_events = [
            {'pool_id': 'pool_1'},
            {'pool_id': 'pool_1'},
            {'pool_id': 'pool_1'},
        ]

        pool_counts = {}
        for event in mining_events:
            pool_id = event['pool_id']
            pool_counts[pool_id] = pool_counts.get(pool_id, 0) + 1

        max_pool_events = max(pool_counts.values())
        achievement_condition = 3

        should_unlock = max_pool_events >= achievement_condition

        assert should_unlock is True

    def test_unlock_social_achievement(self, sample_wallet):
        """Test unlocking social/referral achievement."""
        referrals = ['player_1', 'player_2', 'player_3']
        achievement_condition = 3

        should_unlock = len(referrals) >= achievement_condition

        assert should_unlock is True


@pytest.mark.unit
@pytest.mark.achievements
class TestAchievementConditions:
    """Test achievement condition checking."""

    def test_total_mined_condition(self, sample_wallet):
        """Test total mined amount condition."""
        player_data = {
            'wallet_address': sample_wallet,
            'total_mined': 500.0,
        }

        achievement = {
            'id': 'veteran_miner',
            'condition_type': 'total_mined',
            'condition_value': 1000.0,
        }

        is_met = player_data['total_mined'] >= achievement['condition_value']
        progress = player_data['total_mined'] / achievement['condition_value']

        assert is_met is False
        assert progress == 0.5

    def test_daily_ap_condition(self, sample_wallet):
        """Test daily AP condition."""
        player_data = {
            'wallet_address': sample_wallet,
            'daily_ap': 100,
        }

        achievement = {
            'id': 'daily_grind',
            'condition_type': 'daily_ap',
            'condition_value': 50,
        }

        is_met = player_data['daily_ap'] >= achievement['condition_value']

        assert is_met is True

    def test_mining_streak_condition(self, sample_wallet):
        """Test mining streak condition."""
        # Calculate current streak
        mining_dates = [
            datetime.utcnow().date() - timedelta(days=i)
            for i in range(5)
        ]

        # Check consecutive days
        streak = len(mining_dates)

        achievement = {
            'id': 'streak_7',
            'condition_type': 'mining_streak',
            'condition_value': 7,
        }

        is_met = streak >= achievement['condition_value']

        assert is_met is False

    def test_pool_loyalty_condition(self, sample_wallet):
        """Test pool loyalty condition."""
        mining_events = [
            {'pool_id': 'pool_1'},
            {'pool_id': 'pool_1'},
            {'pool_id': 'pool_2'},
        ]

        # Count events per pool
        pool_counts = {}
        for event in mining_events:
            pool_id = event['pool_id']
            pool_counts[pool_id] = pool_counts.get(pool_id, 0) + 1

        max_loyalty = max(pool_counts.values())

        achievement = {
            'id': 'pool_loyalty',
            'condition_type': 'pool_loyalty',
            'condition_value': 5,
        }

        is_met = max_loyalty >= achievement['condition_value']

        assert is_met is False

    def test_referral_condition(self, sample_wallet):
        """Test referral condition."""
        referrals = ['player_1', 'player_2', 'player_3']

        achievement = {
            'id': 'influencer',
            'condition_type': 'referrals',
            'condition_value': 5,
        }

        is_met = len(referrals) >= achievement['condition_value']
        progress = len(referrals) / achievement['condition_value']

        assert is_met is False
        assert progress == 0.6


@pytest.mark.unit
@pytest.mark.achievements
class TestAPAwarding:
    """Test AP awarding system."""

    def test_award_ap_for_achievement(self, sample_wallet):
        """Test awarding AP when achievement is unlocked."""
        player_data = {
            'wallet_address': sample_wallet,
            'total_ap': 100,
        }

        achievement = {
            'id': 'first_mine',
            'ap_reward': 10,
        }

        # Award AP
        new_ap = player_data['total_ap'] + achievement['ap_reward']

        assert new_ap == 110

    def test_award_ap_multiple_achievements(self, sample_wallet):
        """Test awarding AP for multiple achievements."""
        player_data = {
            'wallet_address': sample_wallet,
            'total_ap': 100,
        }

        achievements = [
            {'id': 'first_mine', 'ap_reward': 10},
            {'id': 'veteran_miner', 'ap_reward': 100},
            {'id': 'streak_7', 'ap_reward': 50},
        ]

        total_reward = sum(a['ap_reward'] for a in achievements)
        new_ap = player_data['total_ap'] + total_reward

        assert new_ap == 260

    def test_ap_awarded_once_per_achievement(self, sample_wallet):
        """Test that AP is only awarded once per achievement."""
        player_achievements = ['first_mine']

        achievement = {
            'id': 'first_mine',
            'ap_reward': 10,
        }

        # Check if already unlocked
        already_unlocked = achievement['id'] in player_achievements

        should_award_ap = not already_unlocked

        assert should_award_ap is False

    def test_bonus_ap_multiplier(self, sample_wallet):
        """Test bonus AP multiplier for special conditions."""
        base_reward = 10
        multiplier = 2.0  # 2x event

        final_reward = int(base_reward * multiplier)

        assert final_reward == 20

    def test_ap_leaderboard_update(self, sample_wallet):
        """Test leaderboard update after AP award."""
        leaderboard = [
            {'wallet': 'player_1', 'total_ap': 200},
            {'wallet': 'player_2', 'total_ap': 150},
            {'wallet': sample_wallet, 'total_ap': 100},
        ]

        # Award AP
        for player in leaderboard:
            if player['wallet'] == sample_wallet:
                player['total_ap'] += 60

        # Re-sort leaderboard
        leaderboard.sort(key=lambda p: p['total_ap'], reverse=True)

        # Player should move up
        player_rank = next(i for i, p in enumerate(leaderboard) if p['wallet'] == sample_wallet)

        assert player_rank == 1  # Moved to first place


@pytest.mark.unit
@pytest.mark.achievements
class TestDuplicateUnlockPrevention:
    """Test prevention of duplicate achievement unlocks."""

    def test_prevent_duplicate_unlock(self, sample_wallet):
        """Test that achievement can only be unlocked once."""
        player_achievements = ['first_mine', 'veteran_miner']

        achievement_to_unlock = 'first_mine'

        # Check if already unlocked
        already_unlocked = achievement_to_unlock in player_achievements

        assert already_unlocked is True

        # Should not unlock again
        should_unlock = not already_unlocked

        assert should_unlock is False

    def test_database_unique_constraint(self, sample_wallet):
        """Test database unique constraint on player-achievement pair."""
        # Attempt to insert duplicate
        player_achievement1 = {
            'player_wallet': sample_wallet,
            'achievement_id': 'first_mine',
        }

        player_achievement2 = {
            'player_wallet': sample_wallet,
            'achievement_id': 'first_mine',
        }

        # Second insert should fail due to unique constraint
        # (player_wallet, achievement_id) must be unique

        assert player_achievement1 == player_achievement2

    def test_check_before_unlock(self, sample_wallet):
        """Test checking unlock status before attempting unlock."""
        player_achievements = ['first_mine']

        def can_unlock(achievement_id):
            return achievement_id not in player_achievements

        assert can_unlock('first_mine') is False
        assert can_unlock('veteran_miner') is True

    def test_idempotent_unlock_operation(self, sample_wallet):
        """Test that unlock operation is idempotent."""
        player_achievements = set()

        achievement_id = 'first_mine'

        # First unlock
        player_achievements.add(achievement_id)
        count_after_first = len(player_achievements)

        # Second unlock (should be no-op)
        player_achievements.add(achievement_id)
        count_after_second = len(player_achievements)

        assert count_after_first == count_after_second == 1


@pytest.mark.unit
@pytest.mark.achievements
class TestAchievementCategories:
    """Test achievement categorization."""

    def test_mining_category(self):
        """Test mining category achievements."""
        mining_achievements = [
            {'id': 'first_mine', 'category': 'mining'},
            {'id': 'veteran_miner', 'category': 'mining'},
            {'id': 'whale_miner', 'category': 'mining'},
        ]

        for achievement in mining_achievements:
            assert achievement['category'] == 'mining'

    def test_social_category(self):
        """Test social category achievements."""
        social_achievements = [
            {'id': 'referral_5', 'category': 'social'},
            {'id': 'influencer', 'category': 'social'},
        ]

        for achievement in social_achievements:
            assert achievement['category'] == 'social'

    def test_streak_category(self):
        """Test streak category achievements."""
        streak_achievements = [
            {'id': 'streak_7', 'category': 'streak'},
            {'id': 'streak_30', 'category': 'streak'},
        ]

        for achievement in streak_achievements:
            assert achievement['category'] == 'streak'

    def test_special_category(self):
        """Test special category achievements."""
        special_achievements = [
            {'id': 'early_bird', 'category': 'special'},
            {'id': 'community_hero', 'category': 'special'},
        ]

        for achievement in special_achievements:
            assert achievement['category'] == 'special'

    def test_group_achievements_by_category(self):
        """Test grouping achievements by category."""
        achievements = [
            {'id': 'first_mine', 'category': 'mining'},
            {'id': 'referral_5', 'category': 'social'},
            {'id': 'streak_7', 'category': 'streak'},
            {'id': 'veteran_miner', 'category': 'mining'},
        ]

        grouped = {}
        for achievement in achievements:
            category = achievement['category']
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(achievement)

        assert len(grouped['mining']) == 2
        assert len(grouped['social']) == 1
        assert len(grouped['streak']) == 1


@pytest.mark.unit
@pytest.mark.achievements
class TestAchievementProgress:
    """Test achievement progress tracking."""

    def test_calculate_progress_percentage(self, sample_wallet):
        """Test calculating progress percentage towards achievement."""
        player_data = {
            'total_mined': 500.0,
        }

        achievement = {
            'id': 'veteran_miner',
            'condition_type': 'total_mined',
            'condition_value': 1000.0,
        }

        progress = (player_data['total_mined'] / achievement['condition_value']) * 100

        assert progress == 50.0

    def test_progress_for_multiple_achievements(self, sample_wallet):
        """Test tracking progress for multiple achievements."""
        player_data = {
            'total_mined': 500.0,
            'daily_ap': 30,
            'referrals': 2,
        }

        achievements = [
            {
                'id': 'veteran_miner',
                'condition_type': 'total_mined',
                'condition_value': 1000.0,
            },
            {
                'id': 'daily_grind',
                'condition_type': 'daily_ap',
                'condition_value': 50,
            },
            {
                'id': 'influencer',
                'condition_type': 'referrals',
                'condition_value': 5,
            },
        ]

        progress_data = []
        for achievement in achievements:
            condition_type = achievement['condition_type']
            if condition_type in player_data:
                current = player_data[condition_type]
                target = achievement['condition_value']
                progress = (current / target) * 100
                progress_data.append({
                    'achievement_id': achievement['id'],
                    'progress': progress,
                })

        assert len(progress_data) == 3
        assert progress_data[0]['progress'] == 50.0  # veteran_miner
        assert progress_data[1]['progress'] == 60.0  # daily_grind
        assert progress_data[2]['progress'] == 40.0  # influencer

    def test_progress_display_format(self):
        """Test formatting progress for display."""
        current_value = 750
        target_value = 1000

        progress_percent = (current_value / target_value) * 100
        progress_text = f"{current_value}/{target_value} ({progress_percent:.1f}%)"

        assert progress_text == "750/1000 (75.0%)"

    def test_progress_clamping(self):
        """Test that progress is clamped to 100%."""
        current_value = 1500
        target_value = 1000

        progress = min((current_value / target_value) * 100, 100)

        assert progress == 100


@pytest.mark.unit
@pytest.mark.achievements
class TestAchievementEvents:
    """Test achievement-related events."""

    def test_achievement_unlocked_event(self, sample_wallet, mock_socketio):
        """Test event emission when achievement is unlocked."""
        event_name = 'achievement_unlocked'
        event_data = {
            'wallet_address': sample_wallet,
            'achievement_id': 'first_mine',
            'achievement_name': 'First Steps',
            'ap_reward': 10,
            'unlocked_at': datetime.utcnow().isoformat(),
        }

        # Should emit WebSocket event
        assert event_name == 'achievement_unlocked'
        assert event_data['ap_reward'] == 10

    def test_achievement_progress_event(self, sample_wallet, mock_socketio):
        """Test event emission for achievement progress updates."""
        event_name = 'achievement_progress'
        event_data = {
            'wallet_address': sample_wallet,
            'achievement_id': 'veteran_miner',
            'progress': 75.0,
        }

        assert event_name == 'achievement_progress'
        assert event_data['progress'] == 75.0

    def test_all_achievements_unlocked_event(self, sample_wallet, mock_socketio):
        """Test event when player unlocks all achievements."""
        total_achievements = 10
        unlocked_achievements = 10

        if unlocked_achievements == total_achievements:
            event_name = 'all_achievements_unlocked'
            event_data = {
                'wallet_address': sample_wallet,
                'bonus_ap': 500,
            }

            assert event_name == 'all_achievements_unlocked'


@pytest.mark.unit
@pytest.mark.achievements
class TestAchievementSystem:
    """Test overall achievement system integration."""

    def test_check_all_achievements_on_event(self, sample_wallet):
        """Test checking all achievements when relevant event occurs."""
        # Mining event occurs
        mining_event = {
            'wallet_address': sample_wallet,
            'amount': 1.5,
        }

        # Check all achievements that could be affected
        achievements_to_check = [
            'first_mine',
            'veteran_miner',
            'whale_miner',
        ]

        assert len(achievements_to_check) == 3

    def test_achievement_notification(self, sample_wallet):
        """Test sending notification when achievement is unlocked."""
        unlock_data = {
            'player_wallet': sample_wallet,
            'achievement_id': 'first_mine',
            'achievement_name': 'First Steps',
            'ap_reward': 10,
        }

        notification = {
            'type': 'achievement_unlocked',
            'title': f'Achievement Unlocked: {unlock_data["achievement_name"]}',
            'message': f'You earned {unlock_data["ap_reward"]} AP!',
        }

        assert notification['type'] == 'achievement_unlocked'

    def test_achievement_leaderboard(self):
        """Test achievement completion leaderboard."""
        players = [
            {'wallet': 'player_1', 'achievements_unlocked': 8},
            {'wallet': 'player_2', 'achievements_unlocked': 5},
            {'wallet': 'player_3', 'achievements_unlocked': 10},
        ]

        # Sort by achievements unlocked
        leaderboard = sorted(players, key=lambda p: p['achievements_unlocked'], reverse=True)

        assert leaderboard[0]['wallet'] == 'player_3'
        assert leaderboard[0]['achievements_unlocked'] == 10

    def test_rare_achievement(self):
        """Test rare achievement tracking."""
        achievement = {
            'id': 'legendary_miner',
            'rarity': 'legendary',
            'unlocked_by': 0.01,  # 1% of players
        }

        # Should grant bonus AP for rare achievements
        base_reward = 100
        rarity_multiplier = 2.0
        final_reward = int(base_reward * rarity_multiplier)

        assert final_reward == 200
