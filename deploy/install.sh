#!/bin/bash

# Installation script for Pool Monitoring Service
# This script should be run as root or with sudo

set -e

echo "=== Pool Monitoring Service Installation ==="

# Configuration
INSTALL_DIR="/opt/m2p"
SERVICE_USER="m2p"
SERVICE_GROUP="m2p"
VENV_DIR="$INSTALL_DIR/venv"

# Create service user if it doesn't exist
if ! id "$SERVICE_USER" &>/dev/null; then
    echo "Creating service user: $SERVICE_USER"
    useradd -r -s /bin/false -d "$INSTALL_DIR" -m "$SERVICE_USER"
fi

# Create installation directory
echo "Creating installation directory: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/logs"

# Copy application files
echo "Copying application files..."
cp -r ../server "$INSTALL_DIR/"
cp -r ../config.py "$INSTALL_DIR/"
cp -r ../requirements.txt "$INSTALL_DIR/"
cp -r ../.env.example "$INSTALL_DIR/"

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"

# Install dependencies
echo "Installing Python dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# Set up .env file if it doesn't exist
if [ ! -f "$INSTALL_DIR/.env" ]; then
    echo "Creating .env file from template..."
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
    echo "IMPORTANT: Edit $INSTALL_DIR/.env with your configuration!"
fi

# Set permissions
echo "Setting permissions..."
chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"
chmod 750 "$INSTALL_DIR"
chmod 640 "$INSTALL_DIR/.env"

# Install systemd service
echo "Installing systemd service..."
cp pool-poller.service /etc/systemd/system/
systemctl daemon-reload

# Initialize database (optional - requires database to be set up)
echo ""
echo "=== Installation Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit $INSTALL_DIR/.env with your configuration"
echo "2. Set up your PostgreSQL database"
echo "3. Initialize the database: cd $INSTALL_DIR && $VENV_DIR/bin/python -c 'from server.database import init_db; init_db()'"
echo "4. Enable the service: systemctl enable pool-poller"
echo "5. Start the service: systemctl start pool-poller"
echo "6. Check status: systemctl status pool-poller"
echo "7. View logs: journalctl -u pool-poller -f"
echo ""
