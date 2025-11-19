#!/bin/bash
#
# M2P (Mine to Play) - Startup Script
# Starts backend and frontend servers with proper cleanup
#

set -e

PROJECT_DIR="/home/mytho/m2p"
BACKEND_LOG="/tmp/m2p_backend.log"
FRONTEND_LOG="/tmp/m2p_frontend.log"
BACKEND_PORT=5000
FRONTEND_PORT=3000

echo "============================================================"
echo "M2P (Mine to Play) - Starting System"
echo "============================================================"
echo

# Stop any existing instances
echo "1. Stopping existing instances..."
lsof -ti:$BACKEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null && echo "  ✓ Stopped backend on port $BACKEND_PORT" || echo "  • No backend running"
lsof -ti:$FRONTEND_PORT 2>/dev/null | xargs kill -9 2>/dev/null && echo "  ✓ Stopped frontend on port $FRONTEND_PORT" || echo "  • No frontend running"
echo

# Start backend
echo "2. Starting backend server..."
cd "$PROJECT_DIR"
source venv/bin/activate
cd server

# Clear old logs
> "$BACKEND_LOG"

# Start backend in background
nohup python3 app.py > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
echo "  ✓ Backend started (PID: $BACKEND_PID)"
echo "  • Log: $BACKEND_LOG"
echo

# Wait for backend to be ready
echo "3. Waiting for backend to start..."
for i in {1..10}; do
    if curl -s http://localhost:$BACKEND_PORT/api/leaderboard > /dev/null 2>&1; then
        echo "  ✓ Backend ready on http://localhost:$BACKEND_PORT"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "  ✗ Backend failed to start. Check logs: tail -f $BACKEND_LOG"
        exit 1
    fi
    sleep 1
done
echo

# Start frontend
echo "4. Starting frontend server..."
cd "$PROJECT_DIR/client"

# Clear old logs
> "$FRONTEND_LOG"

# Start frontend in background
nohup npm start > "$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!
echo "  ✓ Frontend started (PID: $FRONTEND_PID)"
echo "  • Log: $FRONTEND_LOG"
echo

# Wait for frontend to be ready
echo "5. Waiting for frontend to start..."
for i in {1..30}; do
    if lsof -ti:$FRONTEND_PORT > /dev/null 2>&1; then
        echo "  ✓ Frontend ready on http://localhost:$FRONTEND_PORT"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "  ✗ Frontend failed to start. Check logs: tail -f $FRONTEND_LOG"
        exit 1
    fi
    sleep 1
done
echo

# Show system status
echo "============================================================"
echo "✓ M2P System Started Successfully"
echo "============================================================"
echo
echo "Services:"
echo "  Backend:  http://localhost:$BACKEND_PORT (PID: $BACKEND_PID)"
echo "  Frontend: http://localhost:$FRONTEND_PORT (PID: $FRONTEND_PID)"
echo
echo "Logs:"
echo "  Backend:  tail -f $BACKEND_LOG"
echo "  Frontend: tail -f $FRONTEND_LOG"
echo
echo "Quick Commands:"
echo "  ./stop.sh           - Stop all services"
echo "  ./status.sh         - Check system status"
echo "  ./restart.sh        - Restart all services"
echo
echo "Database:"
echo "  $PROJECT_DIR/server/instance/m2p.db"
echo
echo "============================================================"
