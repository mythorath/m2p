"""
Achievement definitions for M2P (Mine to Play)
Contains all achievement data including conditions and rewards
"""

ACHIEVEMENTS = [
    # ===== MINING MILESTONES =====
    {
        'id': 'first_block',
        'name': 'Genesis Miner',
        'description': 'Mine your first ADVC reward',
        'icon': '⛏️',
        'ap_reward': 100,
        'condition_type': 'total_mined',
        'condition_value': 0.0001,
        'category': 'mining',
        'sort_order': 1
    },
    {
        'id': 'ten_club',
        'name': 'Double Digits',
        'description': 'Mine 10 ADVC total',
        'icon': '🔟',
        'ap_reward': 200,
        'condition_type': 'total_mined',
        'condition_value': 10.0,
        'category': 'mining',
        'sort_order': 2
    },
    {
        'id': 'hundred_club',
        'name': 'Century Mark',
        'description': 'Mine 100 ADVC total',
        'icon': '💯',
        'ap_reward': 500,
        'condition_type': 'total_mined',
        'condition_value': 100.0,
        'category': 'mining',
        'sort_order': 3
    },
    {
        'id': 'thousand_club',
        'name': 'Millennium Miner',
        'description': 'Mine 1,000 ADVC total',
        'icon': '🎯',
        'ap_reward': 2000,
        'condition_type': 'total_mined',
        'condition_value': 1000.0,
        'category': 'mining',
        'sort_order': 4
    },
    {
        'id': 'whale',
        'name': 'Mining Whale',
        'description': 'Mine 10,000 ADVC total',
        'icon': '🐋',
        'ap_reward': 5000,
        'condition_type': 'total_mined',
        'condition_value': 10000.0,
        'category': 'mining',
        'sort_order': 5
    },
    {
        'id': 'legend',
        'name': 'Legendary Miner',
        'description': 'Mine 100,000 ADVC total',
        'icon': '👑',
        'ap_reward': 10000,
        'condition_type': 'total_mined',
        'condition_value': 100000.0,
        'category': 'mining',
        'sort_order': 6,
        'is_hidden': True
    },

    # ===== STREAK ACHIEVEMENTS =====
    {
        'id': 'daily_habit',
        'name': 'Daily Habit',
        'description': 'Mine for 3 consecutive days',
        'icon': '📅',
        'ap_reward': 250,
        'condition_type': 'consecutive_days',
        'condition_value': 3,
        'category': 'streaks',
        'sort_order': 10
    },
    {
        'id': 'marathon',
        'name': 'Marathon Miner',
        'description': 'Mine for 7 consecutive days',
        'icon': '🏃',
        'ap_reward': 1000,
        'condition_type': 'consecutive_days',
        'condition_value': 7,
        'category': 'streaks',
        'sort_order': 11
    },
    {
        'id': 'commitment',
        'name': 'Committed Miner',
        'description': 'Mine for 30 consecutive days',
        'icon': '🔥',
        'ap_reward': 5000,
        'condition_type': 'consecutive_days',
        'condition_value': 30,
        'category': 'streaks',
        'sort_order': 12
    },
    {
        'id': 'unstoppable',
        'name': 'Unstoppable Force',
        'description': 'Mine for 100 consecutive days',
        'icon': '💪',
        'ap_reward': 20000,
        'condition_type': 'consecutive_days',
        'condition_value': 100,
        'category': 'streaks',
        'sort_order': 13,
        'is_hidden': True
    },

    # ===== DAILY PERFORMANCE =====
    {
        'id': 'productive_day',
        'name': 'Productive Day',
        'description': 'Mine 5 ADVC in one day',
        'icon': '🌟',
        'ap_reward': 150,
        'condition_type': 'daily_mined',
        'condition_value': 5.0,
        'category': 'daily',
        'sort_order': 20
    },
    {
        'id': 'speed_demon',
        'name': 'Speed Demon',
        'description': 'Mine 10 ADVC in one day',
        'icon': '⚡',
        'ap_reward': 300,
        'condition_type': 'daily_mined',
        'condition_value': 10.0,
        'category': 'daily',
        'sort_order': 21
    },
    {
        'id': 'power_miner',
        'name': 'Power Miner',
        'description': 'Mine 50 ADVC in one day',
        'icon': '💥',
        'ap_reward': 1000,
        'condition_type': 'daily_mined',
        'condition_value': 50.0,
        'category': 'daily',
        'sort_order': 22
    },
    {
        'id': 'daily_legend',
        'name': 'Daily Legend',
        'description': 'Mine 100 ADVC in one day',
        'icon': '🌠',
        'ap_reward': 3000,
        'condition_type': 'daily_mined',
        'condition_value': 100.0,
        'category': 'daily',
        'sort_order': 23,
        'is_hidden': True
    },

    # ===== POOL DIVERSITY =====
    {
        'id': 'explorer',
        'name': 'Pool Explorer',
        'description': 'Mine on 2 different pools',
        'icon': '🗺️',
        'ap_reward': 100,
        'condition_type': 'unique_pools',
        'condition_value': 2,
        'category': 'pools',
        'sort_order': 30
    },
    {
        'id': 'diversified',
        'name': 'Pool Hopper',
        'description': 'Mine on 3 different pools',
        'icon': '🔀',
        'ap_reward': 200,
        'condition_type': 'unique_pools',
        'condition_value': 3,
        'category': 'pools',
        'sort_order': 31
    },
    {
        'id': 'nomad',
        'name': 'Pool Nomad',
        'description': 'Mine on 5 different pools',
        'icon': '🌐',
        'ap_reward': 400,
        'condition_type': 'unique_pools',
        'condition_value': 5,
        'category': 'pools',
        'sort_order': 32
    },
    {
        'id': 'pool_master',
        'name': 'Pool Master',
        'description': 'Mine on 10 different pools',
        'icon': '🎓',
        'ap_reward': 1000,
        'condition_type': 'unique_pools',
        'condition_value': 10,
        'category': 'pools',
        'sort_order': 33
    },

    # ===== MINING EVENTS =====
    {
        'id': 'active_miner',
        'name': 'Active Miner',
        'description': 'Complete 10 mining events',
        'icon': '🎬',
        'ap_reward': 150,
        'condition_type': 'mining_events',
        'condition_value': 10,
        'category': 'events',
        'sort_order': 40
    },
    {
        'id': 'dedicated_miner',
        'name': 'Dedicated Miner',
        'description': 'Complete 100 mining events',
        'icon': '🎪',
        'ap_reward': 500,
        'condition_type': 'mining_events',
        'condition_value': 100,
        'category': 'events',
        'sort_order': 41
    },
    {
        'id': 'veteran_miner',
        'name': 'Veteran Miner',
        'description': 'Complete 1,000 mining events',
        'icon': '🎖️',
        'ap_reward': 2500,
        'condition_type': 'mining_events',
        'condition_value': 1000,
        'category': 'events',
        'sort_order': 42
    },
    {
        'id': 'eternal_miner',
        'name': 'Eternal Miner',
        'description': 'Complete 10,000 mining events',
        'icon': '♾️',
        'ap_reward': 10000,
        'condition_type': 'mining_events',
        'condition_value': 10000,
        'category': 'events',
        'sort_order': 43,
        'is_hidden': True
    },

    # ===== LEADERBOARD =====
    {
        'id': 'top_100',
        'name': 'Rising Star',
        'description': 'Reach top 100 on the leaderboard',
        'icon': '⭐',
        'ap_reward': 500,
        'condition_type': 'leaderboard_rank',
        'condition_value': 100,
        'category': 'leaderboard',
        'sort_order': 50
    },
    {
        'id': 'top_50',
        'name': 'Elite Miner',
        'description': 'Reach top 50 on the leaderboard',
        'icon': '🌟',
        'ap_reward': 1000,
        'condition_type': 'leaderboard_rank',
        'condition_value': 50,
        'category': 'leaderboard',
        'sort_order': 51
    },
    {
        'id': 'top_10',
        'name': 'Top Ten',
        'description': 'Reach top 10 on the leaderboard',
        'icon': '🏆',
        'ap_reward': 2500,
        'condition_type': 'leaderboard_rank',
        'condition_value': 10,
        'category': 'leaderboard',
        'sort_order': 52
    },
    {
        'id': 'champion',
        'name': 'Champion',
        'description': 'Reach #1 on the leaderboard',
        'icon': '👑',
        'ap_reward': 10000,
        'condition_type': 'leaderboard_rank',
        'condition_value': 1,
        'category': 'leaderboard',
        'sort_order': 53,
        'is_hidden': True
    },

    # ===== SPECIAL/HIDDEN =====
    {
        'id': 'early_adopter',
        'name': 'Early Adopter',
        'description': 'Join M2P in the first month',
        'icon': '🚀',
        'ap_reward': 1000,
        'condition_type': 'special',
        'condition_value': 1,
        'category': 'special',
        'sort_order': 60,
        'is_hidden': True
    },
]


def get_achievement_by_id(achievement_id: str) -> dict:
    """Get a specific achievement by its ID"""
    for achievement in ACHIEVEMENTS:
        if achievement['id'] == achievement_id:
            return achievement
    return None


def get_achievements_by_category(category: str) -> list:
    """Get all achievements in a specific category"""
    return [a for a in ACHIEVEMENTS if a.get('category') == category]


def get_achievements_count() -> int:
    """Get total number of achievements"""
    return len(ACHIEVEMENTS)
