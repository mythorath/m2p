#!/bin/bash
#
# M2P (Mine to Play) - Status Script
# Check status of all M2P services
#

PROJECT_DIR="/home/mytho/m2p"
BACKEND_PORT=5000
FRONTEND_PORT=3000
BACKEND_LOG="/tmp/m2p_backend.log"
FRONTEND_LOG="/tmp/m2p_frontend.log"

echo "============================================================"
echo "M2P (Mine to Play) - System Status"
echo "============================================================"
echo

# Check backend
echo "Backend (Port $BACKEND_PORT):"
if lsof -ti:$BACKEND_PORT > /dev/null 2>&1; then
    PID=$(lsof -ti:$BACKEND_PORT)
    echo "  ✓ Running (PID: $PID)"
    
    # Test API
    if curl -s http://localhost:$BACKEND_PORT/api/leaderboard > /dev/null 2>&1; then
        echo "  ✓ API responding"
    else
        echo "  ✗ API not responding"
    fi
    
    # Show recent log
    if [ -f "$BACKEND_LOG" ]; then
        echo "  • Recent log:"
        tail -3 "$BACKEND_LOG" | sed 's/^/    /'
    fi
else
    echo "  ✗ Not running"
fi
echo

# Check frontend
echo "Frontend (Port $FRONTEND_PORT):"
if lsof -ti:$FRONTEND_PORT > /dev/null 2>&1; then
    PID=$(lsof -ti:$FRONTEND_PORT)
    echo "  ✓ Running (PID: $PID)"
    echo "  • URL: http://localhost:$FRONTEND_PORT"
else
    echo "  ✗ Not running"
fi
echo

# Check database
echo "Database:"
DB_PATH="$PROJECT_DIR/server/instance/m2p.db"
if [ -f "$DB_PATH" ]; then
    SIZE=$(du -h "$DB_PATH" | cut -f1)
    echo "  ✓ Found ($SIZE)"
    echo "  • Path: $DB_PATH"
    
    # Quick stats
    cd "$PROJECT_DIR/server" && python3 << 'EOF'
import sqlite3
try:
    conn = sqlite3.connect('instance/m2p.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM players")
    players = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM dungeon_runs WHERE completed_at IS NULL")
    active_runs = cursor.fetchone()[0]
    print(f"  • Players: {players}, Active runs: {active_runs}")
    conn.close()
except Exception as e:
    print(f"  • Error reading database: {e}")
EOF
else
    echo "  ✗ Database not found"
fi
echo

# Check virtual environment
echo "Virtual Environment:"
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "  ✓ Found"
    PYTHON_VERSION=$(source "$PROJECT_DIR/venv/bin/activate" && python3 --version 2>&1)
    echo "  • $PYTHON_VERSION"
else
    echo "  ✗ Not found (run: python3 -m venv venv)"
fi
echo

echo "============================================================"
