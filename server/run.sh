#!/bin/bash

# M2P Flask Server Startup Script

# Load environment variables if .env exists
if [ -f .env ]; then
    echo "Loading environment variables from .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set defaults if not provided
export FLASK_HOST=${FLASK_HOST:-0.0.0.0}
export FLASK_PORT=${FLASK_PORT:-5000}
export FLASK_DEBUG=${FLASK_DEBUG:-False}

echo "========================================="
echo "Starting M2P Flask API Server"
echo "========================================="
echo "Host: $FLASK_HOST"
echo "Port: $FLASK_PORT"
echo "Debug: $FLASK_DEBUG"
echo "========================================="

# Check if running in production
if [ "$FLASK_DEBUG" = "False" ]; then
    echo "Running in PRODUCTION mode with Gunicorn"
    gunicorn --worker-class eventlet -w 1 --bind $FLASK_HOST:$FLASK_PORT app:app
else
    echo "Running in DEVELOPMENT mode"
    python app.py
fi
