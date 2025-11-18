# M2P Game - Complete Setup and Testing Guide

This guide will take you from a fresh clone to a fully tested, running M2P (Mining to Play) game system with dungeon exploration.

## System Overview
M2P is a cryptocurrency mining rewards platform with an integrated dungeon crawler RPG. Players earn AP (Action Points) by mining ADVC cryptocurrency, then spend AP on dungeon runs to battle monsters, collect loot, and level up their character.

---

## Phase 1: Environment Setup

### 1.1 Verify Repository Structure
```bash
cd /home/user/m2p
ls -la
```

**Expected structure:**
- `server/` - Flask backend with WebSocket support
- `client/` - React frontend
- `requirements.txt` - Python dependencies
- `README.md` - Project documentation

### 1.2 Check Python Version
```bash
python --version  # Should be 3.8+
```

### 1.3 Check Node.js Version
```bash
node --version  # Should be 16+
npm --version   # Should be 8+
```

---

## Phase 2: Backend Setup

### 2.1 Install Python Dependencies
```bash
cd /home/user/m2p
pip install -r requirements.txt
```

**Verify key packages installed:**
- Flask 3.0.0
- flask-socketio 5.3.5
- Flask-SQLAlchemy 3.1.1
- flask-cors 4.0.0
- aiohttp 3.9.1

### 2.2 Set Up Environment Variables
```bash
cd server
cp .env.example .env
```

**Edit `.env` if needed (optional for development):**
- `SECRET_KEY` - Flask secret (default is fine for dev)
- `DATABASE_URL` - SQLite by default, or set PostgreSQL URL for production

### 2.3 Initialize Database
```bash
cd /home/user/m2p/server
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✓ Database tables created')"
```

**Expected output:** "✓ Database tables created"

**Verify database file created:**
```bash
ls -lh m2p.db  # Should exist and be ~100KB
```

### 2.4 Seed Dungeon Data
```bash
# Seed dungeons, monsters, and starter gear
python seed_dungeons.py

# Seed dungeon achievements
python seed_dungeon_achievements.py

# Seed original achievements (if exists)
python seed_achievements.py 2>/dev/null || echo "Original achievements seed script not found (OK)"
```

**Expected output:**
- 3 dungeons created (Crystal Mines, Abandoned Laboratory, Blockchain Abyss)
- 9 monsters created (levels 1-35)
- 6 starter gear items
- 20+ achievements created

### 2.5 Verify Database Seeding
```bash
python -c "
from app import app, db
from models import Dungeon, Monster, Gear, Achievement
with app.app_context():
    print(f'Dungeons: {Dungeon.query.count()}')
    print(f'Monsters: {Monster.query.count()}')
    print(f'Gear: {Gear.query.count()}')
    print(f'Achievements: {Achievement.query.count()}')
"
```

**Expected output:**
- Dungeons: 3
- Monsters: 9
- Gear: 6
- Achievements: 20+ (depends on original seeds)

---

## Phase 3: Frontend Setup

### 3.1 Install Node Dependencies
```bash
cd /home/user/m2p/client
npm install
```

**Verify key packages installed:**
- react 18.0+
- react-router-dom
- socket.io-client
- axios

### 3.2 Verify Environment Configuration
```bash
cat .env.example  # Check if exists
```

**If `.env` is needed, create it:**
```bash
echo "REACT_APP_API_URL=http://localhost:5000" > .env
```

---

## Phase 4: Launch Servers

### 4.1 Start Backend Server
```bash
# In terminal 1
cd /home/user/m2p/server
python app.py
```

**Expected output:**
- "Database tables created successfully"
- "Running on http://127.0.0.1:5000"
- WebSocket initialized

**Leave this running and open a new terminal**

### 4.2 Start Frontend Dev Server
```bash
# In terminal 2
cd /home/user/m2p/client
npm start
```

**Expected output:**
- "webpack compiled successfully"
- "Local: http://localhost:3000"

**Application should open in browser automatically**

---

## Phase 5: Comprehensive Feature Testing

### TEST CHECKLIST - Mark each as you complete

#### 5.1 User Registration & Authentication
- [ ] Navigate to http://localhost:3000
- [ ] Click "Register" link
- [ ] Register new account with wallet address: `A` + 33 random alphanumeric characters
  - Example: `ATestWallet123456789012345678901234`
- [ ] Enter display name: "TestPlayer"
- [ ] Verify challenge amount is shown (1.5000-1.9999 ADVC)
- [ ] Note the challenge amount for verification

**Test wallet verification:**
- [ ] Go back to login
- [ ] Login with wallet address
- [ ] Click "Verify Wallet" (if verification is required)
- [ ] Simulate transaction with the exact challenge amount
- [ ] Verify account becomes verified
- [ ] Check that AP is credited for verification

#### 5.2 Mining Rewards System
**Create test mining events via backend:**
```bash
# In terminal 3
cd /home/user/m2p/server
python -c "
from app import app, db
from models import Player, MiningEvent
from datetime import datetime
import random

with app.app_context():
    # Get test player
    player = Player.query.first()
    if not player:
        print('ERROR: No players found. Register a player first.')
        exit(1)

    # Create test mining events
    for i in range(5):
        event = MiningEvent(
            wallet_address=player.wallet_address,
            amount_advc=round(random.uniform(1.0, 10.0), 8),
            ap_awarded=random.randint(50, 200),
            pool='test_pool',
            timestamp=datetime.utcnow()
        )
        db.session.add(event)
        player.total_ap += event.ap_awarded
        player.total_mined_advc += event.amount_advc

    db.session.commit()
    print(f'✓ Created 5 test mining events for {player.display_name}')
    print(f'  Total AP: {player.total_ap}')
    print(f'  Total ADVC: {float(player.total_mined_advc)}')
"
```

**Verify in UI:**
- [ ] Refresh the game view
- [ ] Check AP counter shows updated total
- [ ] View "Recent Activity" shows mining events
- [ ] Check stats page shows correct totals

#### 5.3 Achievement System
- [ ] Navigate to Achievements page
- [ ] Verify achievements are displayed with:
  - [ ] Name, description, tier, AP reward
  - [ ] Icons are visible
  - [ ] Locked/unlocked status
  - [ ] Unlock date for unlocked achievements
- [ ] Check that "First Mine" achievement unlocked (if applicable)
- [ ] Verify achievement categories work

#### 5.4 Leaderboard System
- [ ] Navigate to Leaderboard page
- [ ] Verify rankings are displayed
- [ ] Check filters work: All Time / Week / Day
- [ ] Verify your test player appears in rankings
- [ ] Check that stats are accurate (AP, ADVC mined)

#### 5.5 Dungeon System - Hub View
- [ ] Click "🏰 Dungeons" navigation link
- [ ] Verify dungeon hub loads with all 3 dungeons:
  - [ ] Crystal Mines (⭐, 50 AP, Level 1 required)
  - [ ] Abandoned Laboratory (⭐⭐⭐, 100 AP, Level 10 required)
  - [ ] Blockchain Abyss (⭐⭐⭐⭐⭐, 200 AP, Level 25 required)
- [ ] Check character summary displays:
  - [ ] Level, HP, ATK, DEF, AP
- [ ] Verify requirement checks:
  - [ ] "Can enter" shows green for level 1 player
  - [ ] "Can afford" shows based on AP balance
  - [ ] Higher level dungeons show red "requires level X"

#### 5.6 Character System
- [ ] Click "👤 Character" tab in dungeon view
- [ ] Verify character stats display:
  - [ ] Level (starts at 1)
  - [ ] Experience (0 / 100 for level 1)
  - [ ] Health (100/100)
  - [ ] Attack (10)
  - [ ] Defense (5)
  - [ ] Speed (10)
- [ ] Check equipment slots:
  - [ ] Weapon slot (empty initially)
  - [ ] Armor slot (empty initially)

#### 5.7 Inventory System
- [ ] Click "🎒 Inventory" tab
- [ ] Initially should be empty
- [ ] Verify message: "No items in inventory"

#### 5.8 Starting a Dungeon Run
**Prerequisites:** Ensure you have at least 50 AP

- [ ] Return to "🏰 Dungeons" tab
- [ ] Click "Enter Dungeon" on Crystal Mines
- [ ] Verify:
  - [ ] AP is deducted (50 AP)
  - [ ] View switches to "⚔️ Active Run" tab
  - [ ] Floor indicator shows "Floor: 1/10"
  - [ ] Character HP is displayed
  - [ ] Combat log is empty/shows entrance message

#### 5.9 Dungeon Exploration
- [ ] Click "🔍 Explore Room" button
- [ ] Verify one of three encounters occurs:

  **If Monster Encounter (70% chance):**
  - [ ] Combat log shows "💀 Encountered: [Monster Name] (Lv[X])"
  - [ ] Combat interface appears
  - [ ] Enemy HP bar is shown
  - [ ] Player HP bar is shown
  - [ ] Combat action buttons appear: ⚔️ Attack, 🛡️ Defend, 🏃 Flee

  **If Treasure Room (20% chance):**
  - [ ] Combat log shows "💰 Found a treasure room!"
  - [ ] Loot is added to unclaimed loot

  **If Rest Area (10% chance):**
  - [ ] Combat log shows "💚 Rest area - Healed [X] HP"
  - [ ] Character HP increases

#### 5.10 Combat System
**Assuming you encountered a monster:**

**Test Attack:**
- [ ] Click "⚔️ Attack" button
- [ ] Verify combat log shows:
  - [ ] "⚔️ You dealt [X] damage!"
  - [ ] "🩸 You took [X] damage!" (monster counterattack)
- [ ] Check HP values update
- [ ] Verify damage numbers are realistic (based on ATK/DEF)

**Test Defend:**
- [ ] Click "🛡️ Defend" button (in next combat)
- [ ] Verify damage taken is reduced (~50% less)

**Test Flee:**
- [ ] Click "🏃 Flee" button (in next combat)
- [ ] Verify either:
  - [ ] "🏃 Successfully fled from combat!" (60% chance)
  - [ ] "❌ Failed to escape!" + damage taken (40% chance)

**Test Victory:**
- [ ] Continue attacking until monster defeated
- [ ] Verify combat log shows:
  - [ ] "🎉 Victory! +[X] EXP"
  - [ ] Loot notifications if items dropped
  - [ ] Level up message if threshold reached
- [ ] Check unclaimed loot counter increases

**Test Defeat:**
- [ ] (Optional) Let monster defeat you by defending/fleeing until HP = 0
- [ ] Verify:
  - [ ] "💀 You were defeated! Lost all unclaimed loot."
  - [ ] Returns to dungeon hub after 2 seconds
  - [ ] Experience is kept, loot is lost

#### 5.11 Floor Progression
- [ ] After clearing rooms, click "📈 Next Floor"
- [ ] Verify:
  - [ ] Floor counter increments (Floor: 2/10)
  - [ ] Combat log shows progression message
  - [ ] Can continue exploring

#### 5.12 Loot and Rewards
- [ ] Defeat several monsters to collect loot
- [ ] Verify unclaimed loot counter shows: "💰 Unclaimed Loot: [X] items"
- [ ] Click "🏆 Complete & Claim Loot" button
- [ ] Verify:
  - [ ] Success message appears
  - [ ] Run status changes to "completed"
  - [ ] View returns to dungeon hub

#### 5.13 Inventory Management
- [ ] Navigate to "🎒 Inventory" tab
- [ ] Verify collected loot appears with:
  - [ ] Gear name
  - [ ] Rarity badge (color-coded)
  - [ ] Type (weapon/armor)
  - [ ] Stat bonuses (+X ATK, +X DEF)
  - [ ] Sell value in AP

**Test Equip Gear:**
- [ ] Click "Equip" on a weapon
- [ ] Verify:
  - [ ] Button changes to "✓ Equipped"
  - [ ] Character stats update (total attack increases)
  - [ ] Weapon appears in Character tab equipment slot
- [ ] Repeat for armor

**Test Sell Gear:**
- [ ] Click "Sell" on an unequipped item
- [ ] Confirm the sale
- [ ] Verify:
  - [ ] Item removed from inventory
  - [ ] AP balance increases by sell value
  - [ ] Cannot sell equipped items

#### 5.14 Leveling and Progression
**Create high-EXP scenario:**
```bash
# Give player enough EXP to level up
python -c "
from app import app, db
from models import Player, PlayerCharacter

with app.app_context():
    player = Player.query.first()
    char = PlayerCharacter.query.filter_by(player_id=player.wallet_address).first()

    if char:
        # Add enough EXP for 3 level ups
        levels_gained = char.add_exp(350)
        db.session.commit()
        print(f'✓ Added 350 EXP to character')
        print(f'  Levels gained: {levels_gained}')
        print(f'  New level: {char.level}')
        print(f'  New stats - HP: {char.max_health}, ATK: {char.attack}, DEF: {char.defense}')
    else:
        print('No character found. Enter a dungeon first to create character.')
"
```

- [ ] Refresh character view
- [ ] Verify level increased (should be level 4)
- [ ] Check stat increases:
  - [ ] HP increased by +15 (5 per level)
  - [ ] Attack increased by +6 (2 per level)
  - [ ] Defense increased by +3 (1 per level)
- [ ] Verify experience bar resets

#### 5.15 Multiple Dungeons Testing
**Unlock higher-level dungeons:**
```bash
# Level up character to 15 for mid-tier dungeon
python -c "
from app import app, db
from models import PlayerCharacter

with app.app_context():
    char = PlayerCharacter.query.first()
    if char:
        char.add_exp(1500)  # Level to 15+
        char.health = char.max_health  # Full heal
        db.session.commit()
        print(f'✓ Character leveled to {char.level}')
"
```

- [ ] Return to dungeon hub
- [ ] Verify "Abandoned Laboratory" is now accessible
- [ ] Start a run in the Laboratory
- [ ] Verify:
  - [ ] Higher AP cost (100 AP)
  - [ ] Stronger monsters (Level 10-16)
  - [ ] Better loot (more rare items)

#### 5.16 Dungeon Leaderboard
- [ ] Complete at least one full dungeon run
- [ ] Navigate to a dungeon's details
- [ ] Check leaderboard shows:
  - [ ] Player rankings
  - [ ] Floors cleared
  - [ ] Monsters defeated
  - [ ] Completion dates

#### 5.17 Dungeon Achievements
**Trigger achievement unlocks:**
```bash
# Check dungeon achievements
python -c "
from app import app
from achievement_service import AchievementService

with app.app_context():
    service = AchievementService(app)
    # Check achievements for test player
    from models import Player
    player = Player.query.first()
    if player:
        unlocked = service.check_player_achievements(player.wallet_address)
        print(f'✓ Checked achievements for {player.display_name}')
        print(f'  Newly unlocked: {len(unlocked)}')
        for ach in unlocked:
            print(f'    - {ach[\"name\"]} (+{ach[\"ap_reward\"]} AP)')
"
```

- [ ] Navigate to Achievements page
- [ ] Verify dungeon achievements appear:
  - [ ] "First Blood" - Defeat first monster
  - [ ] "First Steps" - Complete first dungeon
  - [ ] "Monster Slayer" - Defeat 10 monsters
  - [ ] Others as applicable
- [ ] Check AP rewards were credited

#### 5.18 WebSocket Real-Time Updates
**Test in two browser windows:**
- [ ] Open http://localhost:3000 in two different browser windows
- [ ] Login as same player in both
- [ ] In window 1: Start a dungeon run
- [ ] In window 2: Verify events appear in real-time:
  - [ ] `dungeon_started` event
  - [ ] `combat_hit` during battles
  - [ ] `monster_defeated` on kills
  - [ ] `floor_cleared` on progression
  - [ ] `dungeon_completed` on completion

#### 5.19 Abandon Dungeon
- [ ] Start a new dungeon run
- [ ] Explore and collect some loot (don't claim)
- [ ] Click "🚪 Abandon" button
- [ ] Confirm the abandonment
- [ ] Verify:
  - [ ] Warning about losing loot
  - [ ] Run status changes to "abandoned"
  - [ ] Unclaimed loot is lost
  - [ ] Earned EXP is kept
  - [ ] Returns to hub

#### 5.20 Edge Cases and Error Handling

**Test insufficient AP:**
- [ ] Spend AP until balance < 50
- [ ] Try to enter Crystal Mines
- [ ] Verify error: "Insufficient AP"

**Test level requirements:**
- [ ] With level 1 character, try to enter Blockchain Abyss
- [ ] Verify error: "Requires level 25"

**Test active run restriction:**
- [ ] Start a dungeon run
- [ ] Try to start another dungeon (via API or second window)
- [ ] Verify error: "Already have an active dungeon run"

**Test combat state validation:**
- [ ] During combat, try to advance floor
- [ ] Verify error: "Cannot advance while in combat"
- [ ] Try to explore new room
- [ ] Verify error: "Already in combat"

**Test equip restrictions:**
- [ ] Try to equip gear above your level
- [ ] Verify error: "Requires level [X]"
- [ ] Try to sell equipped gear
- [ ] Verify error: "Cannot sell equipped gear"

---

## Phase 6: API Testing

### 6.1 Test All Dungeon Endpoints
```bash
# Get dungeons list
curl http://localhost:5000/api/dungeons | jq

# Get dungeon details
curl http://localhost:5000/api/dungeons/1 | jq

# Get character
curl "http://localhost:5000/api/character?wallet=ATestWallet123456789012345678901234" | jq

# Get inventory
curl "http://localhost:5000/api/inventory?wallet=ATestWallet123456789012345678901234" | jq

# Get current run
curl "http://localhost:5000/api/dungeon/current?wallet=ATestWallet123456789012345678901234" | jq
```

**Verify all endpoints return:**
- [ ] 200 status code
- [ ] Valid JSON
- [ ] Expected data structure
- [ ] No errors in console

### 6.2 Test WebSocket Connection
```bash
# Check WebSocket connection
curl http://localhost:5000/health | jq
```

- [ ] Verify WebSocket is initialized in server logs
- [ ] Check no connection errors

---

## Phase 7: Performance and Load Testing

### 7.1 Database Performance
```bash
# Check database size and query performance
python -c "
from app import app, db
from models import Dungeon, DungeonRun, Player, Monster
import time

with app.app_context():
    # Test query performance
    start = time.time()
    dungeons = Dungeon.query.all()
    query_time = (time.time() - start) * 1000
    print(f'✓ Dungeon query: {query_time:.2f}ms')

    start = time.time()
    monsters = Monster.query.all()
    query_time = (time.time() - start) * 1000
    print(f'✓ Monster query: {query_time:.2f}ms')

    # All queries should be < 50ms
"
```

### 7.2 Frontend Performance
- [ ] Open browser DevTools > Performance tab
- [ ] Record a dungeon run session
- [ ] Verify:
  - [ ] Page load < 2 seconds
  - [ ] Combat actions respond < 200ms
  - [ ] No memory leaks during extended play

---

## Phase 8: Data Validation

### 8.1 Verify Database Integrity
```bash
python -c "
from app import app, db
from models import *
import json

with app.app_context():
    print('=== DATABASE INTEGRITY CHECK ===')

    # Check all dungeons have monsters
    dungeons = Dungeon.query.all()
    for d in dungeons:
        monster_count = d.monsters.count()
        print(f'{d.name}: {monster_count} monsters')
        assert monster_count > 0, f'{d.name} has no monsters!'

    # Check all monsters have valid loot tables
    monsters = Monster.query.all()
    for m in monsters:
        if m.loot_table:
            loot = json.loads(m.loot_table)
            assert isinstance(loot, list), f'{m.name} invalid loot_table'

    # Check all gear has valid stat bonuses
    gear = Gear.query.all()
    for g in gear:
        if g.stat_bonuses:
            stats = json.loads(g.stat_bonuses)
            assert isinstance(stats, dict), f'{g.name} invalid stat_bonuses'

    # Check player relationships
    players = Player.query.all()
    for p in players:
        char = PlayerCharacter.query.filter_by(player_id=p.wallet_address).first()
        if char:
            print(f'{p.display_name}: Level {char.level}, {char.health}/{char.max_health} HP')

    print('✓ All integrity checks passed!')
"
```

---

## Phase 9: Production Readiness

### 9.1 Environment Variables Check
- [ ] Verify `.env` is NOT committed to git
- [ ] Check `.env.example` exists with sample values
- [ ] Ensure secret keys are randomized for production

### 9.2 Security Audit
- [ ] Verify rate limiting is active on API endpoints
- [ ] Check CORS is configured correctly
- [ ] Ensure wallet validation is working
- [ ] Verify no SQL injection vectors (all queries use ORM)

### 9.3 Error Handling
- [ ] Check all API endpoints have try-catch blocks
- [ ] Verify 404 handlers work
- [ ] Test 500 error recovery
- [ ] Check frontend error boundaries

---

## Phase 10: Final Verification

### 10.1 Complete Gameplay Flow Test
**Execute this end-to-end test:**

1. [ ] Register new account
2. [ ] Receive test mining rewards (500 AP)
3. [ ] Enter Crystal Mines dungeon
4. [ ] Battle through 3 floors
5. [ ] Collect loot from monsters
6. [ ] Advance to floor 4
7. [ ] Claim all loot and complete dungeon
8. [ ] Equip best weapon and armor
9. [ ] Check character level increased
10. [ ] Verify achievements unlocked
11. [ ] Check AP balance updated correctly
12. [ ] Enter dungeon again with equipped gear
13. [ ] Verify equipped gear bonuses work in combat
14. [ ] Sell unwanted gear
15. [ ] Check inventory updated
16. [ ] View leaderboard ranking
17. [ ] Check all stats are accurate

### 10.2 Create Test Report
```bash
# Generate test report
python -c "
from app import app, db
from models import *

with app.app_context():
    print('=' * 60)
    print('M2P GAME - TEST REPORT')
    print('=' * 60)
    print(f'Players: {Player.query.count()}')
    print(f'Verified Players: {Player.query.filter_by(verified=True).count()}')
    print(f'Dungeons: {Dungeon.query.count()}')
    print(f'Monsters: {Monster.query.count()}')
    print(f'Gear Types: {Gear.query.count()}')
    print(f'Achievements: {Achievement.query.count()}')
    print(f'Dungeon Runs: {DungeonRun.query.count()}')
    print(f'  - Active: {DungeonRun.query.filter_by(status=\"active\").count()}')
    print(f'  - Completed: {DungeonRun.query.filter_by(status=\"completed\").count()}')
    print(f'  - Abandoned: {DungeonRun.query.filter_by(status=\"abandoned\").count()}')
    print(f'  - Defeated: {DungeonRun.query.filter_by(status=\"defeated\").count()}')
    print(f'Characters: {PlayerCharacter.query.count()}')
    print(f'Inventory Items: {PlayerInventory.query.count()}')

    # Highest level character
    char = PlayerCharacter.query.order_by(PlayerCharacter.level.desc()).first()
    if char:
        print(f'\nHighest Level: {char.player.display_name} - Level {char.level}')

    # Most AP
    player = Player.query.order_by(Player.total_ap.desc()).first()
    if player:
        print(f'Most AP: {player.display_name} - {player.total_ap} AP')

    print('=' * 60)
"
```

---

## Success Criteria

### All tests must pass:
- [ ] Backend server runs without errors
- [ ] Frontend loads and renders correctly
- [ ] All 3 dungeons are accessible
- [ ] Combat system works (attack, defend, flee)
- [ ] Loot generation and collection works
- [ ] Character progression (levels, stats, equipment) works
- [ ] Inventory management (equip, sell) works
- [ ] Achievements unlock correctly
- [ ] WebSocket real-time updates work
- [ ] AP spending and earning works correctly
- [ ] No console errors in browser
- [ ] No server errors in terminal
- [ ] Database queries perform well (< 50ms)
- [ ] All API endpoints return expected data

---

## Troubleshooting

### Backend won't start:
```bash
# Check for port conflicts
lsof -i :5000
# Kill existing process
kill -9 [PID]
```

### Frontend won't start:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Database errors:
```bash
# Reset database
rm server/m2p.db
cd server
python -c "from app import app, db; app.app_context().push(); db.create_all()"
python seed_dungeons.py
python seed_dungeon_achievements.py
```

### WebSocket not connecting:
- Check CORS settings in server/app.py
- Verify both servers running
- Check browser console for connection errors

---

## Next Steps After Testing

1. [ ] Document any bugs found
2. [ ] Create GitHub issues for improvements
3. [ ] Update README with setup instructions
4. [ ] Deploy to staging environment
5. [ ] Run tests on staging
6. [ ] Deploy to production

---

## Additional Notes

**Expected Performance:**
- Page load: < 2s
- API response: < 200ms
- Combat action: < 100ms
- WebSocket latency: < 50ms

**Known Limitations:**
- Single player only (no multiplayer yet)
- No persistent WebSocket sessions across page reloads
- Limited to 3 dungeons initially (more can be added)

**Future Enhancements:**
- Co-op dungeons
- PvP arena
- Crafting system
- More dungeon tiers
- Special events

---

End of Setup and Testing Guide
