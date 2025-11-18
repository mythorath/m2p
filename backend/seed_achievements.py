"""Seed initial achievement data."""
import json
from database import SessionLocal, init_db
from models.achievement import Achievement

# Leaderboard achievements
LEADERBOARD_ACHIEVEMENTS = [
    {
        "code": "top_10_all_time",
        "name": "Elite Miner",
        "description": "Reach top 10 in all-time leaderboard",
        "category": "leaderboard",
        "requirement_type": "rank",
        "requirement_value": json.dumps({"period": "all_time", "max_rank": 10}),
        "ap_reward": 1000,
        "icon": "trophy-gold",
    },
    {
        "code": "top_10_weekly",
        "name": "Weekly Champion",
        "description": "Reach top 10 in weekly leaderboard",
        "category": "leaderboard",
        "requirement_type": "rank",
        "requirement_value": json.dumps({"period": "this_week", "max_rank": 10}),
        "ap_reward": 500,
        "icon": "trophy-silver",
    },
    {
        "code": "top_10_daily",
        "name": "Daily Dominator",
        "description": "Reach top 10 in daily leaderboard",
        "category": "leaderboard",
        "requirement_type": "rank",
        "requirement_value": json.dumps({"period": "today", "max_rank": 10}),
        "ap_reward": 250,
        "icon": "trophy-bronze",
    },
    {
        "code": "top_100_all_time",
        "name": "Legendary Miner",
        "description": "Reach top 100 in all-time leaderboard",
        "category": "leaderboard",
        "requirement_type": "rank",
        "requirement_value": json.dumps({"period": "all_time", "max_rank": 100}),
        "ap_reward": 500,
        "icon": "star-gold",
    },
    {
        "code": "biggest_climber_week",
        "name": "Rising Star",
        "description": "Climb the most positions in the weekly leaderboard",
        "category": "leaderboard",
        "requirement_type": "rank_change",
        "requirement_value": json.dumps({"period": "this_week", "min_climb": 50}),
        "ap_reward": 750,
        "icon": "arrow-up",
    },
    {
        "code": "efficiency_master",
        "name": "Efficiency Master",
        "description": "Reach top 10 in efficiency leaderboard",
        "category": "leaderboard",
        "requirement_type": "rank",
        "requirement_value": json.dumps({"period": "efficiency", "max_rank": 10}),
        "ap_reward": 800,
        "icon": "lightning",
    },
    {
        "code": "top_3_all_time",
        "name": "Podium Legend",
        "description": "Reach top 3 in all-time leaderboard",
        "category": "leaderboard",
        "requirement_type": "rank",
        "requirement_value": json.dumps({"period": "all_time", "max_rank": 3}),
        "ap_reward": 2500,
        "icon": "crown",
    },
    {
        "code": "rank_1_any_period",
        "name": "Number One",
        "description": "Reach rank #1 in any leaderboard period",
        "category": "leaderboard",
        "requirement_type": "rank",
        "requirement_value": json.dumps({"period": "any", "max_rank": 1}),
        "ap_reward": 5000,
        "icon": "crown-gold",
    },
]


def seed_achievements():
    """Seed achievement data into database."""
    db = SessionLocal()

    try:
        print("Seeding leaderboard achievements...")

        for achievement_data in LEADERBOARD_ACHIEVEMENTS:
            # Check if achievement already exists
            existing = db.query(Achievement).filter(
                Achievement.code == achievement_data["code"]
            ).first()

            if existing:
                print(f"  Skipping {achievement_data['code']} (already exists)")
                continue

            # Create new achievement
            achievement = Achievement(**achievement_data)
            db.add(achievement)
            print(f"  Created {achievement_data['code']}")

        db.commit()
        print(f"\nSuccessfully seeded {len(LEADERBOARD_ACHIEVEMENTS)} achievements!")

    except Exception as e:
        print(f"Error seeding achievements: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database
    init_db()

    # Seed achievements
    seed_achievements()
