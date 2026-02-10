#!/bin/bash
# Complete VPS Cleanup and Fresh Setup Script
# This will DELETE everything and reinstall from GitHub

set -e  # Exit on error

echo "======================================"
echo "COMPLETE VPS SETUP - JNDROID STORE"
echo "======================================"
echo ""

# Configuration
VPS_PATH="/var/www/jndroid.store"
REPO_URL="https://github.com/jndroid000/jndroid.store.git"
PYTHON_VERSION="python3.12"

# Step 1: Backup current state (optional but recommended)
echo "Step 1: Creating backup..."
if [ -d "$VPS_PATH" ]; then
    BACKUP_DIR="/var/www/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    echo "Backup location: $BACKUP_DIR"
else
    echo "No existing directory to backup"
fi

# Step 2: Remove everything
echo ""
echo "Step 2: Removing all files and directories..."
if [ -d "$VPS_PATH" ]; then
    cd "$VPS_PATH"
    # List what will be deleted
    echo "Deleting:"
    ls -la
    
    # Delete everything
    rm -rf ./*
    rm -rf ./.*
    
    echo "✓ All files deleted"
else
    echo "Creating directory..."
    mkdir -p "$VPS_PATH"
fi

# Step 3: Clone fresh repository
echo ""
echo "Step 3: Cloning from GitHub..."
cd "$VPS_PATH"
git clone "$REPO_URL" .
echo "✓ Repository cloned"

# Step 4: Create new virtual environment
echo ""
echo "Step 4: Creating new virtual environment..."
$PYTHON_VERSION -m venv venv
source venv/bin/activate
echo "✓ Virtual environment created and activated"

# Step 5: Upgrade pip
echo ""
echo "Step 5: Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo "✓ Pip upgraded"

# Step 6: Install requirements
echo ""
echo "Step 6: Installing requirements..."
pip install -r requirements.txt
echo "✓ Requirements installed"

# Step 7: Verify files
echo ""
echo "Step 7: Verifying setup..."
echo "Current directory: $(pwd)"
echo "Files present:"
ls -la | head -20

echo ""
echo "======================================"
echo "✓ FRESH SETUP COMPLETE!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Upload .env.production file via FileZilla"
echo "2. Run: cd $VPS_PATH && source venv/bin/activate"
echo "3. Run: python manage.py migrate --noinput"
echo "4. Run: python manage.py collectstatic --noinput"
echo "5. Run: sudo systemctl restart gunicorn nginx"
echo ""
