# Setup and Test M2P Game - Complete Instructions

You are tasked with setting up and comprehensively testing the M2P (Mining to Play) game system from a freshly cloned repository.

## Your Mission

1. **Install all dependencies** (Python and Node.js)
2. **Initialize the database** with all tables
3. **Seed all game data** (dungeons, monsters, gear, achievements)
4. **Launch both servers** (Flask backend + React frontend)
5. **Test every feature thoroughly** following the comprehensive checklist
6. **Report all findings** with detailed test results

## Primary Resource

Follow the **complete step-by-step guide** in `/home/user/m2p/SETUP_AND_TEST_GUIDE.md`

This guide contains:
- 10 detailed phases covering setup to production readiness
- 100+ specific test checkboxes
- Code snippets for verification
- Expected outputs for each step
- Troubleshooting section
- Success criteria

## System Overview

M2P is a cryptocurrency mining rewards platform with integrated dungeon crawler RPG:
- Players earn AP (Action Points) from mining ADVC cryptocurrency
- Spend AP to enter dungeons and battle monsters
- Turn-based combat system
- Loot collection and character progression
- Equipment management and leveling system
- Achievement system with WebSocket real-time updates

## Key Features to Test

### Core Systems:
1. **User Registration & Authentication** - Wallet-based login with verification
2. **Mining Rewards** - AP earning from mining events
3. **Achievement System** - 20+ achievements with AP rewards
4. **Dungeon Exploration** - 3 dungeons with 10-25 floors each
5. **Combat System** - Turn-based battles (attack/defend/flee)
6. **Character Progression** - Leveling, stats, and equipment
7. **Inventory Management** - Collect, equip, and sell gear
8. **Loot System** - 5 rarity tiers (common to legendary)
9. **WebSocket Events** - Real-time combat and notifications
10. **Leaderboards** - Rankings and statistics

### Database Schema:
- **11 database tables** including 6 new dungeon system tables
- **3 dungeons**: Crystal Mines (Lv1), Abandoned Laboratory (Lv10), Blockchain Abyss (Lv25)
- **9 monsters**: Levels 1-35 including "The Satoshi" boss
- **6 starter gear items**: Common to rare equipment
- **20+ achievements**: Dungeon-specific achievements

## Your Workflow

### Phase 1: Setup (30 minutes)
- Install Python dependencies from `requirements.txt`
- Install Node.js dependencies with `npm install`
- Create database with `db.create_all()`
- Run 3 seed scripts:
  - `seed_dungeons.py` → dungeons, monsters, gear
  - `seed_dungeon_achievements.py` → achievements
  - `seed_achievements.py` → original achievements (if exists)

### Phase 2: Launch (5 minutes)
- Terminal 1: `python server/app.py` (Flask backend on port 5000)
- Terminal 2: `npm start` from client folder (React on port 3000)
- Verify both servers are running without errors

### Phase 3: Comprehensive Testing (2-3 hours)
Follow **SETUP_AND_TEST_GUIDE.md** sections 5.1 through 5.20:

**Critical test flows:**
1. Register account → Get AP → Enter dungeon
2. Battle monsters → Collect loot → Level up
3. Equip gear → Enhanced combat → Sell items
4. Complete dungeon → Unlock achievements → Check leaderboard
5. Test all edge cases and error handling

### Phase 4: Validation (30 minutes)
- Run API endpoint tests (curl commands provided)
- Verify database integrity with Python scripts
- Check WebSocket connections
- Generate final test report

### Phase 5: Report Back (15 minutes)
Create a summary including:
- ✅ All completed test items
- 🐛 Any bugs or issues found
- 📊 Database statistics (player count, runs, etc.)
- ⚡ Performance metrics
- 💡 Improvement suggestions

## Success Criteria

**Required for success:**
- All 100+ test checkboxes completed
- Zero server errors during testing
- All dungeon features working (combat, loot, progression)
- WebSocket real-time updates functioning
- Database integrity verified
- Performance within targets (< 2s page load, < 200ms API)

## Important Notes

- **Follow the guide sequentially** - Don't skip steps
- **Mark each checkbox** as you complete it
- **Document any deviations** from expected behavior
- **Test thoroughly** - This is a complete game system
- **Use the provided Python scripts** for data verification
- **Create test players and play the game** - Experience it firsthand

## Files You'll Work With

**Backend:**
- `server/app.py` - Main Flask application (1500+ lines)
- `server/models.py` - Database models (11 tables)
- `server/dungeon_service.py` - Game logic (900+ lines)
- `server/seed_*.py` - Data seeding scripts

**Frontend:**
- `client/src/App.js` - React router setup
- `client/src/components/DungeonView.js` - Main dungeon UI (500+ lines)
- `client/src/components/DungeonView.css` - Styling (600+ lines)

**Database:**
- `server/m2p.db` - SQLite database (created during setup)

## Troubleshooting Quick Reference

```bash
# Reset database
rm server/m2p.db && cd server && python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Kill stuck server
lsof -i :5000 && kill -9 [PID]

# Clear npm cache
rm -rf client/node_modules client/package-lock.json && cd client && npm install
```

## Expected Timeline

- Setup & Installation: 30 minutes
- Server Launch: 5 minutes
- Feature Testing: 2-3 hours
- API & Performance Testing: 30 minutes
- Final Validation: 30 minutes
- **Total: 4-5 hours for complete testing**

## Your Deliverable

A comprehensive test report showing:
1. All 100+ checkboxes marked complete ✅
2. List of any bugs found 🐛
3. Performance metrics 📊
4. Database statistics summary
5. Screenshots of key features working
6. Overall assessment: PASS/FAIL with notes

---

**Start with:** `cat /home/user/m2p/SETUP_AND_TEST_GUIDE.md`

Then work through each phase methodically. Good luck! 🚀
