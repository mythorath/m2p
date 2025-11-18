"""
Seed script for dungeon system data.

Creates initial dungeons, monsters, and starter gear for the M2P dungeon system.
Run this script once to populate the database with dungeon content.
"""

import json
from app import app
from models import db, Dungeon, Monster, Gear

def seed_dungeons():
    """Create initial dungeons with balanced progression."""

    print("Seeding dungeons...")

    dungeons_data = [
        {
            'name': 'Crystal Mines',
            'description': 'Ancient mining caverns filled with crystalline formations and territorial slimes. A perfect starting point for new adventurers.',
            'difficulty': 1,
            'min_level_required': 1,
            'ap_cost_per_run': 50,
            'max_floors': 10,
            'base_loot_multiplier': 1.0,
            'active': True,
            'theme': 'mines',
            'unlock_requirements': json.dumps({}),  # Always available
        },
        {
            'name': 'Abandoned Laboratory',
            'description': 'A high-tech facility overrun by rogue AI and malfunctioning security systems. Strange experiments left behind dangerous creations.',
            'difficulty': 3,
            'min_level_required': 10,
            'ap_cost_per_run': 100,
            'max_floors': 15,
            'base_loot_multiplier': 1.3,
            'active': True,
            'theme': 'laboratory',
            'unlock_requirements': json.dumps({'min_level': 10}),
        },
        {
            'name': 'Blockchain Abyss',
            'description': 'A dimensional rift where corrupted data manifests as deadly entities. Only the bravest dare venture into these cryptographic depths.',
            'difficulty': 5,
            'min_level_required': 25,
            'ap_cost_per_run': 200,
            'max_floors': 25,
            'base_loot_multiplier': 1.8,
            'active': True,
            'theme': 'abyss',
            'unlock_requirements': json.dumps({'min_level': 25}),
        },
    ]

    created_dungeons = []
    for dungeon_data in dungeons_data:
        # Check if dungeon already exists
        existing = Dungeon.query.filter_by(name=dungeon_data['name']).first()
        if existing:
            print(f"  - Dungeon '{dungeon_data['name']}' already exists, skipping...")
            created_dungeons.append(existing)
            continue

        dungeon = Dungeon(**dungeon_data)
        db.session.add(dungeon)
        db.session.flush()  # Get ID
        created_dungeons.append(dungeon)
        print(f"  ✓ Created dungeon: {dungeon.name}")

    db.session.commit()
    return created_dungeons


def seed_monsters(dungeons):
    """Create monsters for each dungeon."""

    print("\nSeeding monsters...")

    # Crystal Mines Monsters (Tier 1)
    crystal_mines = dungeons[0]
    crystal_mines_monsters = [
        {
            'name': 'Crystal Slime',
            'description': 'A gelatinous creature formed from liquid crystal. Slow but resilient.',
            'dungeon_id': crystal_mines.id,
            'dungeon_tier': 1,
            'level': 1,
            'health': 40,
            'attack': 8,
            'defense': 3,
            'speed': 8,
            'exp_reward': 20,
            'loot_table': json.dumps([
                {'gear_type': 'weapon', 'drop_chance': 0.3},
                {'gear_type': 'armor', 'drop_chance': 0.3},
            ]),
        },
        {
            'name': 'Cave Bat',
            'description': 'An aggressive flying creature with razor-sharp fangs.',
            'dungeon_id': crystal_mines.id,
            'dungeon_tier': 1,
            'level': 2,
            'health': 30,
            'attack': 12,
            'defense': 2,
            'speed': 15,
            'exp_reward': 25,
            'loot_table': json.dumps([
                {'gear_type': 'weapon', 'drop_chance': 0.35},
            ]),
        },
        {
            'name': 'Rock Golem',
            'description': 'A living statue of stone, slow but incredibly durable.',
            'dungeon_id': crystal_mines.id,
            'dungeon_tier': 1,
            'level': 4,
            'health': 80,
            'attack': 10,
            'defense': 8,
            'speed': 5,
            'exp_reward': 40,
            'loot_table': json.dumps([
                {'gear_type': 'armor', 'drop_chance': 0.5},
            ]),
        },
    ]

    # Abandoned Laboratory Monsters (Tier 3)
    laboratory = dungeons[1]
    laboratory_monsters = [
        {
            'name': 'Rogue AI',
            'description': 'A sentient program that has gained physical form through holographic projectors.',
            'dungeon_id': laboratory.id,
            'dungeon_tier': 3,
            'level': 10,
            'health': 120,
            'attack': 20,
            'defense': 10,
            'speed': 18,
            'exp_reward': 100,
            'loot_table': json.dumps([
                {'gear_type': 'weapon', 'drop_chance': 0.4},
                {'gear_type': 'armor', 'drop_chance': 0.3},
            ]),
            'special_abilities': json.dumps(['System Overload: 20% chance to deal double damage']),
        },
        {
            'name': 'Security Drone',
            'description': 'An automated defense unit programmed to eliminate intruders.',
            'dungeon_id': laboratory.id,
            'dungeon_tier': 3,
            'level': 12,
            'health': 150,
            'attack': 25,
            'defense': 15,
            'speed': 16,
            'exp_reward': 120,
            'loot_table': json.dumps([
                {'gear_type': 'weapon', 'drop_chance': 0.45},
            ]),
            'special_abilities': json.dumps(['Targeting Lock: Increased accuracy']),
        },
        {
            'name': 'Experimental Hybrid',
            'description': 'A grotesque fusion of organic and mechanical components gone wrong.',
            'dungeon_id': laboratory.id,
            'dungeon_tier': 3,
            'level': 16,
            'health': 200,
            'attack': 28,
            'defense': 12,
            'speed': 14,
            'exp_reward': 160,
            'loot_table': json.dumps([
                {'gear_type': 'weapon', 'drop_chance': 0.5},
                {'gear_type': 'armor', 'drop_chance': 0.5},
            ]),
            'special_abilities': json.dumps(['Regeneration: Heals 10 HP per turn']),
        },
    ]

    # Blockchain Abyss Monsters (Tier 5)
    abyss = dungeons[2]
    abyss_monsters = [
        {
            'name': 'Hash Demon',
            'description': 'A corrupted cryptographic entity that feeds on computational power.',
            'dungeon_id': abyss.id,
            'dungeon_tier': 5,
            'level': 25,
            'health': 300,
            'attack': 45,
            'defense': 25,
            'speed': 22,
            'exp_reward': 250,
            'loot_table': json.dumps([
                {'gear_type': 'weapon', 'drop_chance': 0.6},
                {'gear_type': 'armor', 'drop_chance': 0.5},
            ]),
            'special_abilities': json.dumps([
                'Hash Attack: Ignores 50% of defense',
                'Cryptographic Shield: Reduces damage taken'
            ]),
        },
        {
            'name': 'Proof-of-Work Titan',
            'description': 'A massive construct of pure blockchain energy, relentless and powerful.',
            'dungeon_id': abyss.id,
            'dungeon_tier': 5,
            'level': 30,
            'health': 400,
            'attack': 50,
            'defense': 30,
            'speed': 20,
            'exp_reward': 300,
            'loot_table': json.dumps([
                {'gear_type': 'weapon', 'drop_chance': 0.7},
                {'gear_type': 'armor', 'drop_chance': 0.6},
            ]),
            'special_abilities': json.dumps([
                'Consensus Strike: Multiple attacks per turn',
                'Block Generation: Creates defensive barriers'
            ]),
        },
        {
            'name': 'The Satoshi',
            'description': 'LEGENDARY BOSS: The mysterious entity at the core of the abyss. Defeating it grants incredible rewards.',
            'dungeon_id': abyss.id,
            'dungeon_tier': 5,
            'level': 35,
            'health': 1000,
            'attack': 60,
            'defense': 40,
            'speed': 25,
            'exp_reward': 1000,
            'loot_table': json.dumps([
                {'gear_type': 'weapon', 'drop_chance': 1.0, 'rarity_boost': 'legendary'},
                {'gear_type': 'armor', 'drop_chance': 1.0, 'rarity_boost': 'legendary'},
            ]),
            'special_abilities': json.dumps([
                'Genesis Block: Massive area attack',
                'Nakamoto Consensus: Becomes stronger over time',
                'Digital Gold: Drops legendary loot guaranteed'
            ]),
        },
    ]

    all_monsters = crystal_mines_monsters + laboratory_monsters + abyss_monsters

    for monster_data in all_monsters:
        # Check if monster already exists
        existing = Monster.query.filter_by(
            name=monster_data['name'],
            dungeon_id=monster_data['dungeon_id']
        ).first()

        if existing:
            print(f"  - Monster '{monster_data['name']}' already exists, skipping...")
            continue

        monster = Monster(**monster_data)
        db.session.add(monster)
        print(f"  ✓ Created monster: {monster.name} (Lv{monster.level})")

    db.session.commit()


def seed_starter_gear():
    """Create some basic starter gear for new players."""

    print("\nSeeding starter gear...")

    starter_gear = [
        {
            'name': 'Rusty Iron Sword',
            'description': 'A simple sword that has seen better days.',
            'type': 'weapon',
            'rarity': 'common',
            'stat_bonuses': json.dumps({'attack': 5}),
            'level_requirement': 1,
            'sell_value': 10,
        },
        {
            'name': 'Leather Chestplate',
            'description': 'Basic leather armor for protection.',
            'type': 'armor',
            'rarity': 'common',
            'stat_bonuses': json.dumps({'defense': 3, 'max_health': 10}),
            'level_requirement': 1,
            'sell_value': 10,
        },
        {
            'name': 'Steel Longsword',
            'description': 'A well-crafted blade for intermediate fighters.',
            'type': 'weapon',
            'rarity': 'uncommon',
            'stat_bonuses': json.dumps({'attack': 12}),
            'level_requirement': 5,
            'sell_value': 25,
        },
        {
            'name': 'Chainmail Armor',
            'description': 'Interlocked metal rings provide solid protection.',
            'type': 'armor',
            'rarity': 'uncommon',
            'stat_bonuses': json.dumps({'defense': 8, 'max_health': 20}),
            'level_requirement': 5,
            'sell_value': 25,
        },
        {
            'name': 'Plasma Blade',
            'description': 'A high-tech weapon that cuts through anything.',
            'type': 'weapon',
            'rarity': 'rare',
            'stat_bonuses': json.dumps({'attack': 25}),
            'level_requirement': 15,
            'sell_value': 50,
        },
        {
            'name': 'Nano-weave Suit',
            'description': 'Advanced defensive technology in fabric form.',
            'type': 'armor',
            'rarity': 'rare',
            'stat_bonuses': json.dumps({'defense': 18, 'max_health': 40}),
            'level_requirement': 15,
            'sell_value': 50,
        },
    ]

    for gear_data in starter_gear:
        # Check if gear already exists
        existing = Gear.query.filter_by(name=gear_data['name']).first()
        if existing:
            print(f"  - Gear '{gear_data['name']}' already exists, skipping...")
            continue

        gear = Gear(**gear_data)
        db.session.add(gear)
        print(f"  ✓ Created gear: {gear.name} ({gear.rarity})")

    db.session.commit()


def main():
    """Main seeding function."""
    with app.app_context():
        print("=" * 60)
        print("  M2P DUNGEON SYSTEM - DATABASE SEEDING")
        print("=" * 60)
        print()

        # Seed dungeons first
        dungeons = seed_dungeons()

        # Seed monsters for each dungeon
        seed_monsters(dungeons)

        # Seed starter gear
        seed_starter_gear()

        print()
        print("=" * 60)
        print("  ✓ DUNGEON SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print(f"Created dungeons: {len(dungeons)}")
        print(f"Total monsters: {Monster.query.count()}")
        print(f"Total gear: {Gear.query.count()}")
        print()


if __name__ == '__main__':
    main()
