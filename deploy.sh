#!/bin/bash
# Production deployment script for Ubuntu VPS

echo "========================================="
echo "PRODUCTION DEPLOYMENT SCRIPT"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
PROJECT_PATH="/var/www/jndroid.store/backend"  # Change this to your actual path
PYTHON_VERSION="python3"
VENV_NAME="venv"

echo -e "${YELLOW}[Step 1] Navigating to project directory...${NC}"
cd $PROJECT_PATH || { echo "Project directory not found!"; exit 1; }
echo -e "${GREEN}✓ Project path: $PROJECT_PATH${NC}"

echo -e "${YELLOW}[Step 2] Creating/Activating virtual environment...${NC}"
if [ ! -d "$VENV_NAME" ]; then
    $PYTHON_VERSION -m venv $VENV_NAME
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

source $VENV_NAME/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

echo -e "${YELLOW}[Step 3] Upgrading pip...${NC}"
$PYTHON_VERSION -m pip install --upgrade pip
echo -e "${GREEN}✓ Pip upgraded${NC}"

echo -e "${YELLOW}[Step 4] Installing Django 6.0.2...${NC}"
pip install Django==6.0.2 --upgrade
echo -e "${GREEN}✓ Django 6.0.2 installed${NC}"

echo -e "${YELLOW}[Step 5] Installing all requirements...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}✓ All requirements installed${NC}"

echo -e "${YELLOW}[Step 6] Running migrations...${NC}"
$PYTHON_VERSION manage.py migrate --noinput
echo -e "${GREEN}✓ Migrations completed${NC}"

echo -e "${YELLOW}[Step 7] Collecting static files...${NC}"
$PYTHON_VERSION manage.py collectstatic --noinput
echo -e "${GREEN}✓ Static files collected${NC}"

echo -e "${YELLOW}[Step 8] Verifying installation...${NC}"
$PYTHON_VERSION archived-scripts/final_verify.py
echo -e "${GREEN}✓ Installation verified${NC}"

echo ""
echo "========================================="
echo -e "${GREEN}✓ DEPLOYMENT COMPLETED!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Setup Gunicorn service (systemd)"
echo "2. Setup Nginx reverse proxy"
echo "3. Setup SSL certificate (Let's Encrypt)"
echo "4. Start services: systemctl start gunicorn"
echo ""
