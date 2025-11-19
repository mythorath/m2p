# M2P (Mine to Play) - Quick Start Guide

## 🚀 Starting the System

### Simple Start (Recommended)
```bash
cd /home/mytho/m2p
./start.sh
```

This will:
- Stop any existing instances
- Start backend server on port 5000
- Start frontend server on port 3000
- Display status and log locations

### Access the Application
- **Frontend UI:** http://localhost:3000
- **Backend API:** http://localhost:5000
- **API Docs:** `/home/mytho/m2p/API_DOCUMENTATION.md`

---

## 🛠️ Management Commands

### Start Services
```bash
./start.sh          # Start all services
```

### Stop Services
```bash
./stop.sh           # Stop all services
```

### Restart Services
```bash
./restart.sh        # Restart all services
```

### Check Status
```bash
./status.sh         # View system status
```

---

## 📊 Monitoring & Logs

### View Backend Logs (Real-time)
```bash
tail -f /tmp/m2p_backend.log
```

### View Frontend Logs (Real-time)
```bash
tail -f /tmp/m2p_frontend.log
```

### View Recent Errors
```bash
tail -50 /tmp/m2p_backend.log | grep -i error
```

---

## 🗄️ Database Management

### Database Location
```
/home/mytho/m2p/server/instance/m2p.db
```

### View Database Stats
```bash
cd /home/mytho/m2p/server
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('instance/m2p.db')
cursor = conn.cursor()

tables = ['players', 'player_characters', 'dungeons', 'monsters', 
          'gear', 'achievements', 'mining_events', 'dungeon_runs']
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"{table}: {cursor.fetchone()[0]}")
conn.close()
EOF
```

### Reset Database (⚠️ DESTRUCTIVE)
```bash
cd /home/mytho/m2p/server
rm -f instance/m2p.db
python3 << 'EOF'
from app import app, db
with app.app_context():
    db.create_all()
print("✓ Database recreated")
EOF

# Re-seed game data
python3 seed_dungeons.py
python3 seed_dungeon_achievements.py
```

---

## 🔧 Common Tasks

### Test a Player Account
```bash
# Replace with your wallet address
WALLET="AcDmzPS41vJR8UG8m43ruSLZkeVCALudcG"

# Get player info
curl -s "http://localhost:5000/api/player/$WALLET" | python3 -m json.tool

# Get character stats
curl -s "http://localhost:5000/api/character?wallet=$WALLET" | python3 -m json.tool

# Get active dungeon run
curl -s "http://localhost:5000/api/dungeon/current?wallet=$WALLET" | python3 -m json.tool
```

### Give Player AP (Testing)
```bash
cd /home/mytho/m2p/server
python3 << 'EOF'
from app import app, db
from models import Player

WALLET = "AcDmzPS41vJR8UG8m43ruSLZkeVCALudcG"
AMOUNT = 1000

with app.app_context():
    player = Player.query.filter_by(wallet_address=WALLET).first()
    if player:
        player.total_ap += AMOUNT
        db.session.commit()
        print(f"✓ Gave {AMOUNT} AP to {player.display_name}")
        print(f"  New total: {player.total_ap} AP")
    else:
        print("✗ Player not found")
EOF
```

### Check Pending Verifications
```bash
curl -s http://localhost:5000/api/pending_verifications | python3 -m json.tool
```

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check if port is in use
lsof -ti:5000

# View error logs
tail -50 /tmp/m2p_backend.log

# Check Python environment
cd /home/mytho/m2p
source venv/bin/activate
python3 -c "import flask, flask_socketio, sqlalchemy, aiohttp; print('✓ All modules installed')"
```

### Frontend Won't Start
```bash
# Check if port is in use
lsof -ti:3000

# View error logs
tail -50 /tmp/m2p_frontend.log

# Reinstall dependencies
cd /home/mytho/m2p/client
rm -rf node_modules package-lock.json
npm install
```

### Database Issues
```bash
# Verify database exists and is readable
ls -lh /home/mytho/m2p/server/instance/m2p.db

# Check database integrity
cd /home/mytho/m2p/server
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('instance/m2p.db')
cursor = conn.cursor()
cursor.execute("PRAGMA integrity_check")
print(cursor.fetchone()[0])
conn.close()
EOF
```

### Port Already in Use
```bash
# Find and kill process using port 5000
lsof -ti:5000 | xargs kill -9

# Find and kill process using port 3000
lsof -ti:3000 | xargs kill -9
```

---

## 🔐 Wallet Verification Flow

### 1. Register Wallet
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"wallet_address":"YOUR_WALLET","display_name":"YourName"}'
```

### 2. Get Challenge Amount
The response will include:
- `challenge_amount`: Unique amount to send (e.g., 1.7553 ADVC)
- `donation_address`: AKUg58E171GVJNw2RQzooQnuHs1zns2ecD
- `expires_at`: Expiration timestamp (24 hours)

### 3. Send Payment
Send the exact challenge amount from your wallet to the donation address.

### 4. Automatic Verification
The verification monitor checks every 60 seconds and will:
- Detect your payment
- Mark your account as verified
- Import your mining history
- Award AP for all past mining rewards (1 ADVC = 10 AP)

### 5. Check Status
```bash
curl -s "http://localhost:5000/api/player/YOUR_WALLET" | python3 -m json.tool
```

---

## 📦 System Architecture

```
M2P/
├── server/                  # Flask backend
│   ├── app.py              # Main application
│   ├── models.py           # Database models
│   ├── dungeon_service.py  # Game logic
│   ├── verification_monitor.py  # Wallet verification
│   ├── mining_history_service.py  # Mining history import
│   └── instance/
│       └── m2p.db          # SQLite database
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── context/        # State management
│   │   └── services/       # API integration
│   └── public/
├── venv/                   # Python virtual environment
├── start.sh               # Start script
├── stop.sh                # Stop script
├── restart.sh             # Restart script
└── status.sh              # Status check script
```

---

## 📝 Development Notes

### Key Conversion Rates
- **1 ADVC = 10 AP** (Action Points)
- Mining history automatically imported on verification

### Known Pool Address
- **ATBxmBJ9974wk3XVZU8my3gcJeYJe7TEkS** (Primary mining pool)

### Verification Donation Address
- **AKUg58E171GVJNw2RQzooQnuHs1zns2ecD**

### API Rate Limits
- Most endpoints: 100 requests/hour
- Write operations: 20 requests/hour

---

## 🎮 Game Mechanics

### Dungeons
- **Crystal Mines** (Lv1, 50 AP) - Beginner dungeon
- **Abandoned Laboratory** (Lv10, 100 AP) - Intermediate dungeon
- **Blockchain Abyss** (Lv25, 200 AP) - Advanced dungeon

### Character Progression
- Gain XP from defeating monsters
- Level up to increase stats
- Equip better gear for bonuses
- Unlock achievements for AP rewards

### Achievements
- **47 total achievements** across mining and dungeon categories
- Reward AP on completion
- Tracked automatically

---

## 📚 Additional Documentation

- **Full API Reference:** `/home/mytho/m2p/API_DOCUMENTATION.md`
- **Architecture Guide:** `/home/mytho/m2p/docs/ARCHITECTURE.md`
- **Testing Guide:** `/home/mytho/m2p/SETUP_AND_TEST_GUIDE.md`
- **Pool Integration:** `/home/mytho/m2p/docs/POOL_INTEGRATION.md`

---

## 🆘 Support

For issues or questions:
1. Check logs: `tail -f /tmp/m2p_backend.log`
2. Review status: `./status.sh`
3. Check documentation in `/home/mytho/m2p/docs/`

---

**Last Updated:** November 18, 2025
