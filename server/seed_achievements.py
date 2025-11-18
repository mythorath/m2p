"""
Achievement Seeding Script for M2P

This script populates the database with a comprehensive set of achievements
across different tiers and categories.
"""

import json
from app import app, db
from models import Achievement
from decimal import Decimal


def decimal_default(obj):
    """JSON encoder for Decimal objects."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def seed_achievements():
    """Seed the database with achievements."""

    achievements = [
        # ====================
        # BEGINNER TIER (Bronze) - Easy to achieve
        # ====================
        {
            'name': 'First Steps',
            'description': 'Start your mining journey - Register your wallet',
            'tier': 'Bronze',
            'ap_reward': 10,
            'icon': '🎯',
            'criteria': {'type': 'registration', 'count': 1},
            'category': 'onboarding'
        },
        {
            'name': 'First Blood',
            'description': 'Receive your first mining reward',
            'tier': 'Bronze',
            'ap_reward': 25,
            'icon': '💰',
            'criteria': {'type': 'mining_events', 'count': 1},
            'category': 'mining'
        },
        {
            'name': 'Penny Pincher',
            'description': 'Mine a total of 1 ADVC',
            'tier': 'Bronze',
            'ap_reward': 15,
            'icon': '🪙',
            'criteria': {'type': 'total_advc', 'amount': Decimal('1')},
            'category': 'mining'
        },
        {
            'name': 'Getting Started',
            'description': 'Earn 50 total AP',
            'tier': 'Bronze',
            'ap_reward': 10,
            'icon': '⭐',
            'criteria': {'type': 'total_ap', 'amount': 50},
            'category': 'progression'
        },
        {
            'name': 'Verified Miner',
            'description': 'Complete wallet verification',
            'tier': 'Bronze',
            'ap_reward': 50,
            'icon': '✅',
            'criteria': {'type': 'verified', 'value': True},
            'category': 'verification'
        },

        # ====================
        # INTERMEDIATE TIER (Silver) - Moderate effort
        # ====================
        {
            'name': 'Consistent Miner',
            'description': 'Receive 10 mining rewards',
            'tier': 'Silver',
            'ap_reward': 50,
            'icon': '⛏️',
            'criteria': {'type': 'mining_events', 'count': 10},
            'category': 'mining'
        },
        {
            'name': 'Silver Striker',
            'description': 'Mine a total of 10 ADVC',
            'tier': 'Silver',
            'ap_reward': 75,
            'icon': '🥈',
            'criteria': {'type': 'total_advc', 'amount': Decimal('10')},
            'category': 'mining'
        },
        {
            'name': 'Rising Star',
            'description': 'Earn 250 total AP',
            'tier': 'Silver',
            'ap_reward': 50,
            'icon': '🌟',
            'criteria': {'type': 'total_ap', 'amount': 250},
            'category': 'progression'
        },
        {
            'name': 'Big Spender',
            'description': 'Spend 100 AP on rewards',
            'tier': 'Silver',
            'ap_reward': 30,
            'icon': '💸',
            'criteria': {'type': 'spent_ap', 'amount': 100},
            'category': 'economy'
        },
        {
            'name': 'Week Warrior',
            'description': 'Receive rewards for 7 consecutive days',
            'tier': 'Silver',
            'ap_reward': 100,
            'icon': '📅',
            'criteria': {'type': 'consecutive_days', 'count': 7},
            'category': 'dedication'
        },

        # ====================
        # ADVANCED TIER (Gold) - Significant commitment
        # ====================
        {
            'name': 'Gold Digger',
            'description': 'Mine a total of 50 ADVC',
            'tier': 'Gold',
            'ap_reward': 150,
            'icon': '🥇',
            'criteria': {'type': 'total_advc', 'amount': Decimal('50')},
            'category': 'mining'
        },
        {
            'name': 'Century Club',
            'description': 'Receive 100 mining rewards',
            'tier': 'Gold',
            'ap_reward': 200,
            'icon': '💯',
            'criteria': {'type': 'mining_events', 'count': 100},
            'category': 'mining'
        },
        {
            'name': 'AP Millionaire',
            'description': 'Earn 1,000 total AP',
            'tier': 'Gold',
            'ap_reward': 100,
            'icon': '👑',
            'criteria': {'type': 'total_ap', 'amount': 1000},
            'category': 'progression'
        },
        {
            'name': 'Dedication',
            'description': 'Mine for 30 consecutive days',
            'tier': 'Gold',
            'ap_reward': 300,
            'icon': '🔥',
            'criteria': {'type': 'consecutive_days', 'count': 30},
            'category': 'dedication'
        },
        {
            'name': 'Top 10',
            'description': 'Reach Top 10 on the leaderboard',
            'tier': 'Gold',
            'ap_reward': 250,
            'icon': '🏆',
            'criteria': {'type': 'leaderboard_rank', 'max_rank': 10},
            'category': 'competitive'
        },

        # ====================
        # EXPERT TIER (Platinum) - Serious dedication
        # ====================
        {
            'name': 'Platinum Producer',
            'description': 'Mine a total of 250 ADVC',
            'tier': 'Platinum',
            'ap_reward': 500,
            'icon': '💎',
            'criteria': {'type': 'total_advc', 'amount': Decimal('250')},
            'category': 'mining'
        },
        {
            'name': 'Mining Mogul',
            'description': 'Receive 500 mining rewards',
            'tier': 'Platinum',
            'ap_reward': 750,
            'icon': '🏭',
            'criteria': {'type': 'mining_events', 'count': 500},
            'category': 'mining'
        },
        {
            'name': 'AP Overlord',
            'description': 'Earn 5,000 total AP',
            'tier': 'Platinum',
            'ap_reward': 500,
            'icon': '👹',
            'criteria': {'type': 'total_ap', 'amount': 5000},
            'category': 'progression'
        },
        {
            'name': 'Iron Will',
            'description': 'Mine for 90 consecutive days',
            'tier': 'Platinum',
            'ap_reward': 1000,
            'icon': '🛡️',
            'criteria': {'type': 'consecutive_days', 'count': 90},
            'category': 'dedication'
        },
        {
            'name': 'Big Fish',
            'description': 'Earn 100 ADVC in a single payout',
            'tier': 'Platinum',
            'ap_reward': 400,
            'icon': '🐋',
            'criteria': {'type': 'single_payout', 'amount': Decimal('100')},
            'category': 'mining'
        },

        # ====================
        # LEGENDARY TIER (Diamond) - Ultimate achievements
        # ====================
        {
            'name': 'Diamond Hands',
            'description': 'Mine a total of 1,000 ADVC',
            'tier': 'Diamond',
            'ap_reward': 2000,
            'icon': '💠',
            'criteria': {'type': 'total_advc', 'amount': Decimal('1000')},
            'category': 'mining'
        },
        {
            'name': 'Mining Legend',
            'description': 'Receive 1,000 mining rewards',
            'tier': 'Diamond',
            'ap_reward': 2500,
            'icon': '🌌',
            'criteria': {'type': 'mining_events', 'count': 1000},
            'category': 'mining'
        },
        {
            'name': 'AP God',
            'description': 'Earn 10,000 total AP',
            'tier': 'Diamond',
            'ap_reward': 1000,
            'icon': '⚡',
            'criteria': {'type': 'total_ap', 'amount': 10000},
            'category': 'progression'
        },
        {
            'name': 'Year One',
            'description': 'Mine for 365 consecutive days',
            'tier': 'Diamond',
            'ap_reward': 5000,
            'icon': '🎆',
            'criteria': {'type': 'consecutive_days', 'count': 365},
            'category': 'dedication'
        },
        {
            'name': '#1 Miner',
            'description': 'Reach #1 on the all-time leaderboard',
            'tier': 'Diamond',
            'ap_reward': 3000,
            'icon': '👑',
            'criteria': {'type': 'leaderboard_rank', 'max_rank': 1},
            'category': 'competitive'
        },

        # ====================
        # SPECIAL ACHIEVEMENTS - Unique conditions
        # ====================
        {
            'name': 'Early Adopter',
            'description': 'Join M2P in the first month',
            'tier': 'Gold',
            'ap_reward': 500,
            'icon': '🚀',
            'criteria': {'type': 'registration_date', 'before': '2025-12-18'},
            'category': 'special'
        },
        {
            'name': 'Treasure Hunter',
            'description': 'Find a rare block (0.1% chance)',
            'tier': 'Platinum',
            'ap_reward': 1000,
            'icon': '🗺️',
            'criteria': {'type': 'rare_block', 'rarity': 0.001},
            'category': 'special'
        },
        {
            'name': 'Lucky Strike',
            'description': 'Receive exactly 777 ADVC in total',
            'tier': 'Gold',
            'ap_reward': 777,
            'icon': '🎰',
            'criteria': {'type': 'exact_advc', 'amount': Decimal('777')},
            'category': 'special'
        },
        {
            'name': 'Generous Soul',
            'description': 'Spend 1,000 AP on the community',
            'tier': 'Silver',
            'ap_reward': 200,
            'icon': '❤️',
            'criteria': {'type': 'community_spending', 'amount': 1000},
            'category': 'social'
        },
        {
            'name': 'Night Owl',
            'description': 'Receive 50 rewards between midnight and 6 AM',
            'tier': 'Silver',
            'ap_reward': 100,
            'icon': '🦉',
            'criteria': {'type': 'time_based', 'timeframe': 'night', 'count': 50},
            'category': 'special'
        }
    ]

    with app.app_context():
        # Clear existing achievements (optional - comment out in production)
        # Achievement.query.delete()

        for ach_data in achievements:
            # Check if achievement already exists
            existing = Achievement.query.filter_by(name=ach_data['name']).first()

            if not existing:
                achievement = Achievement(
                    name=ach_data['name'],
                    description=ach_data['description'],
                    tier=ach_data['tier'],
                    ap_reward=ach_data['ap_reward'],
                    icon=ach_data['icon'],
                    criteria=json.dumps(ach_data['criteria'], default=decimal_default),  # Store as JSON string
                    category=ach_data.get('category', 'general')
                )
                db.session.add(achievement)
                print(f"✓ Created: {ach_data['name']} ({ach_data['tier']})")
            else:
                print(f"⊘ Skipped: {ach_data['name']} (already exists)")

        db.session.commit()
        print(f"\n✅ Achievement seeding complete! Total: {len(achievements)} achievements")


if __name__ == '__main__':
    print("🎮 Mine to Play - Achievement Seeding")
    print("=" * 50)
    seed_achievements()
