#!/bin/bash
#
# M2P (Mine to Play) - Stop Script
# Stops all running M2P services
#

BACKEND_PORT=5000
FRONTEND_PORT=3000

echo "============================================================"
echo "M2P (Mine to Play) - Stopping System"
echo "============================================================"
echo

# Stop backend
if lsof -ti:$BACKEND_PORT > /dev/null 2>&1; then
    echo "Stopping backend on port $BACKEND_PORT..."
    lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null
    echo "  ✓ Backend stopped"
else
    echo "  • No backend running on port $BACKEND_PORT"
fi

# Stop frontend
if lsof -ti:$FRONTEND_PORT > /dev/null 2>&1; then
    echo "Stopping frontend on port $FRONTEND_PORT..."
    lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null
    echo "  ✓ Frontend stopped"
else
    echo "  • No frontend running on port $FRONTEND_PORT"
fi

echo
echo "✓ All services stopped"
echo "============================================================"
