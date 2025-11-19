#!/bin/bash
#
# M2P (Mine to Play) - Restart Script
# Restart all M2P services
#

echo "============================================================"
echo "M2P (Mine to Play) - Restarting System"
echo "============================================================"
echo

# Stop services
./stop.sh

echo
echo "Waiting 2 seconds..."
sleep 2
echo

# Start services
./start.sh
