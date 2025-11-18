"""
Seed script for dungeon-specific achievements.

Creates achievements related to the dungeon exploration system.
"""

import json
from app import app
from models import db, Achievement

def seed_dungeon_achievements():
    """Create dungeon-specific achievements."""

    print("Seeding dungeon achievements...")

    achievements_data = [
        {
            'name': 'First Blood',
            'description': 'Defeat your first monster in a dungeon',
            'tier': 'Bronze',
            'ap_reward': 10,
            'icon': '⚔️',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'dungeon_monsters_defeated',
                'count': 1
            }),
        },
        {
            'name': 'Monster Slayer',
            'description': 'Defeat 10 monsters',
            'tier': 'Silver',
            'ap_reward': 25,
            'icon': '🗡️',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'dungeon_monsters_defeated',
                'count': 10
            }),
        },
        {
            'name': 'Monster Hunter',
            'description': 'Defeat 50 monsters',
            'tier': 'Gold',
            'ap_reward': 50,
            'icon': '⚔️',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'dungeon_monsters_defeated',
                'count': 50
            }),
        },
        {
            'name': 'Treasure Hunter',
            'description': 'Collect 100 loot items from dungeons',
            'tier': 'Silver',
            'ap_reward': 50,
            'icon': '💰',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'loot_collected',
                'count': 100
            }),
        },
        {
            'name': 'Dungeon Master',
            'description': 'Complete any dungeon 10 times',
            'tier': 'Gold',
            'ap_reward': 100,
            'icon': '🏰',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'dungeons_completed',
                'count': 10
            }),
        },
        {
            'name': 'Glass Cannon',
            'description': 'Complete a floor with less than 10% HP remaining',
            'tier': 'Gold',
            'ap_reward': 150,
            'icon': '💔',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'low_health_floor_clear',
                'health_percent': 10
            }),
        },
        {
            'name': 'Legendary Collector',
            'description': 'Own 5 legendary items',
            'tier': 'Diamond',
            'ap_reward': 500,
            'icon': '✨',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'legendary_items_owned',
                'count': 5
            }),
        },
        {
            'name': 'First Steps',
            'description': 'Complete your first dungeon run',
            'tier': 'Bronze',
            'ap_reward': 25,
            'icon': '🚪',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'dungeons_completed',
                'count': 1
            }),
        },
        {
            'name': 'Deep Delver',
            'description': 'Reach floor 20 in any dungeon',
            'tier': 'Platinum',
            'ap_reward': 200,
            'icon': '🕳️',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'deepest_floor',
                'floor': 20
            }),
        },
        {
            'name': 'Speed Runner',
            'description': 'Complete a dungeon in under 10 minutes',
            'tier': 'Gold',
            'ap_reward': 100,
            'icon': '⚡',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'dungeon_time',
                'max_minutes': 10
            }),
        },
        {
            'name': 'Survivor',
            'description': 'Complete a dungeon without fleeing from combat',
            'tier': 'Silver',
            'ap_reward': 75,
            'icon': '🛡️',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'no_flee_completion',
            }),
        },
        {
            'name': 'Equipment Master',
            'description': 'Equip a full set of rare or better gear',
            'tier': 'Gold',
            'ap_reward': 100,
            'icon': '🎭',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'full_rare_set',
            }),
        },
        {
            'name': 'Crystal Conqueror',
            'description': 'Complete Crystal Mines 5 times',
            'tier': 'Bronze',
            'ap_reward': 50,
            'icon': '💎',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'specific_dungeon_completions',
                'dungeon_name': 'Crystal Mines',
                'count': 5
            }),
        },
        {
            'name': 'Lab Technician',
            'description': 'Complete Abandoned Laboratory 5 times',
            'tier': 'Silver',
            'ap_reward': 100,
            'icon': '🔬',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'specific_dungeon_completions',
                'dungeon_name': 'Abandoned Laboratory',
                'count': 5
            }),
        },
        {
            'name': 'Abyss Walker',
            'description': 'Complete Blockchain Abyss once',
            'tier': 'Platinum',
            'ap_reward': 250,
            'icon': '🌌',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'specific_dungeon_completions',
                'dungeon_name': 'Blockchain Abyss',
                'count': 1
            }),
        },
        {
            'name': 'Boss Slayer',
            'description': 'Defeat The Satoshi',
            'tier': 'Diamond',
            'ap_reward': 1000,
            'icon': '👑',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'boss_defeated',
                'monster_name': 'The Satoshi'
            }),
        },
        {
            'name': 'Level 10',
            'description': 'Reach character level 10',
            'tier': 'Bronze',
            'ap_reward': 50,
            'icon': '⬆️',
            'category': 'progression',
            'criteria': json.dumps({
                'type': 'character_level',
                'level': 10
            }),
        },
        {
            'name': 'Level 25',
            'description': 'Reach character level 25',
            'tier': 'Gold',
            'ap_reward': 150,
            'icon': '⬆️',
            'category': 'progression',
            'criteria': json.dumps({
                'type': 'character_level',
                'level': 25
            }),
        },
        {
            'name': 'Merchant',
            'description': 'Sell 50 items for AP',
            'tier': 'Silver',
            'ap_reward': 50,
            'icon': '🏪',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'items_sold',
                'count': 50
            }),
        },
        {
            'name': 'Flawless Victory',
            'description': 'Complete a dungeon without taking damage',
            'tier': 'Diamond',
            'ap_reward': 500,
            'icon': '🏆',
            'category': 'dungeon',
            'criteria': json.dumps({
                'type': 'no_damage_completion',
            }),
        },
    ]

    created_count = 0
    skipped_count = 0

    for achievement_data in achievements_data:
        # Check if achievement already exists
        existing = Achievement.query.filter_by(name=achievement_data['name']).first()
        if existing:
            print(f"  - Achievement '{achievement_data['name']}' already exists, skipping...")
            skipped_count += 1
            continue

        achievement = Achievement(**achievement_data)
        db.session.add(achievement)
        created_count += 1
        print(f"  ✓ Created achievement: {achievement.name} ({achievement.tier}) - {achievement.ap_reward} AP")

    db.session.commit()

    print(f"\n  Created: {created_count} achievements")
    print(f"  Skipped: {skipped_count} achievements (already exist)")


def main():
    """Main seeding function."""
    with app.app_context():
        print("=" * 60)
        print("  M2P DUNGEON ACHIEVEMENTS - DATABASE SEEDING")
        print("=" * 60)
        print()

        seed_dungeon_achievements()

        print()
        print("=" * 60)
        print("  ✓ ACHIEVEMENT SEEDING COMPLETED!")
        print("=" * 60)
        print()


if __name__ == '__main__':
    main()
