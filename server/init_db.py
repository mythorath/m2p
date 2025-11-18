"""
Database initialization script for Mine-to-Play.

This script creates all database tables and optionally seeds initial data
such as default achievements.
"""

import sys
from datetime import datetime
from decimal import Decimal

from __init__ import create_app
from models import db, Achievement


def init_database(seed_data=True):
    """
    Initialize the database with tables and optional seed data.

    Args:
        seed_data: Whether to seed initial data (achievements, etc.)
    """
    app = create_app()

    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully")

        if seed_data:
            print("\nSeeding initial data...")
            seed_achievements()
            print("✓ Initial data seeded successfully")

        print("\n" + "="*50)
        print("Database initialization complete!")
        print("="*50)


def seed_achievements():
    """Seed the database with default achievements."""

    achievements = [
        # Mining milestones
        Achievement(
            id='first_mine',
            name='First Steps',
            description='Mine your first 0.1 ADVC',
            ap_reward=10,
            icon='⛏️',
            condition_type='total_mined',
            condition_value=0.1
        ),
        Achievement(
            id='miner_1',
            name='Casual Miner',
            description='Mine a total of 1 ADVC',
            ap_reward=50,
            icon='⚒️',
            condition_type='total_mined',
            condition_value=1.0
        ),
        Achievement(
            id='miner_10',
            name='Dedicated Miner',
            description='Mine a total of 10 ADVC',
            ap_reward=200,
            icon='⛏️',
            condition_type='total_mined',
            condition_value=10.0
        ),
        Achievement(
            id='miner_100',
            name='Expert Miner',
            description='Mine a total of 100 ADVC',
            ap_reward=1000,
            icon='💎',
            condition_type='total_mined',
            condition_value=100.0
        ),
        Achievement(
            id='whale_1000',
            name='Mining Whale',
            description='Mine a total of 1000 ADVC',
            ap_reward=5000,
            icon='🐋',
            condition_type='total_mined',
            condition_value=1000.0
        ),

        # Multi-pool achievements
        Achievement(
            id='multi_pool',
            name='Pool Hopper',
            description='Mine on at least 2 different pools',
            ap_reward=100,
            icon='🏊',
            condition_type='unique_pools',
            condition_value=2.0
        ),
        Achievement(
            id='all_pools',
            name='Pool Master',
            description='Mine on all 3 supported pools',
            ap_reward=300,
            icon='🎯',
            condition_type='unique_pools',
            condition_value=3.0
        ),

        # Consistency achievements
        Achievement(
            id='week_streak',
            name='Week Warrior',
            description='Mine for 7 consecutive days',
            ap_reward=250,
            icon='📅',
            condition_type='consecutive_days',
            condition_value=7.0
        ),
        Achievement(
            id='month_streak',
            name='Monthly Grinder',
            description='Mine for 30 consecutive days',
            ap_reward=1500,
            icon='🗓️',
            condition_type='consecutive_days',
            condition_value=30.0
        ),

        # Early adopter
        Achievement(
            id='early_adopter',
            name='Early Adopter',
            description='Join during the first month of launch',
            ap_reward=500,
            icon='🚀',
            condition_type='join_date',
            condition_value=30.0  # Days since launch
        ),

        # Verification
        Achievement(
            id='verified',
            name='Verified Miner',
            description='Verify your wallet address',
            ap_reward=25,
            icon='✓',
            condition_type='verified',
            condition_value=1.0
        ),
    ]

    for achievement in achievements:
        # Check if achievement already exists
        existing = Achievement.query.get(achievement.id)
        if not existing:
            db.session.add(achievement)
            print(f"  + Added achievement: {achievement.name}")
        else:
            print(f"  - Skipped existing achievement: {achievement.name}")

    db.session.commit()
    print(f"\n✓ Seeded {len(achievements)} achievements")


def drop_all_tables():
    """Drop all database tables. USE WITH CAUTION!"""
    app = create_app()

    with app.app_context():
        print("WARNING: This will delete all data!")
        confirm = input("Type 'DELETE' to confirm: ")

        if confirm == 'DELETE':
            print("Dropping all tables...")
            db.drop_all()
            print("✓ All tables dropped")
        else:
            print("Operation cancelled")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Initialize Mine-to-Play database')
    parser.add_argument(
        '--drop',
        action='store_true',
        help='Drop all tables before creating (DESTRUCTIVE!)'
    )
    parser.add_argument(
        '--no-seed',
        action='store_true',
        help='Skip seeding initial data'
    )

    args = parser.parse_args()

    if args.drop:
        drop_all_tables()

    init_database(seed_data=not args.no_seed)
