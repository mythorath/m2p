#!/bin/bash
# M2P Wallet Verification System - Setup Script

set -e

echo "=========================================="
echo "M2P Wallet Verification System Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your configuration!"
    echo "   Required settings:"
    echo "   - DEV_WALLET_ADDRESS"
    echo "   - ADMIN_API_KEY"
    echo "   - SECRET_KEY"
    echo ""
else
    echo ".env file already exists"
fi

# Create logs directory
echo "Creating logs directory..."
mkdir -p logs

# Initialize database
echo ""
read -p "Initialize database? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Initializing database..."
    python init_db.py
fi

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run the application: python -m server.app"
echo "3. Or install as systemd service (see DEPLOYMENT.md)"
echo ""
