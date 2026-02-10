#!/bin/bash
# Generate production credentials for .env.production file

echo "========================================"
echo "PRODUCTION CREDENTIALS GENERATOR"
echo "========================================"
echo ""

# Generate Django SECRET_KEY
echo "Step 1: Generating Django SECRET_KEY..."
echo "-----------------------------------------"
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
echo "SECRET_KEY: $SECRET_KEY"
echo ""

# Instructions for other credentials
echo "Step 2: Other Credentials Needed"
echo "-----------------------------------------"
echo "1. PostgreSQL Password:"
echo "   - Generate a strong password (min 16 characters)"
echo "   - Use uppercase, lowercase, numbers, and symbols"
echo "   - Example: MyStr0ng!P@ssw0rd#2024"
echo ""

echo "2. Gmail App Password:"
echo "   - Visit: https://myaccount.google.com/apppasswords"
echo "   - Select 'Mail' and 'Windows Computer'"
echo "   - Copy the 16-character password"
echo ""

echo "3. VPS IP Address:"
echo "   - Your VPS IP for ALLOWED_HOSTS"
echo "   - Usually shown in VPS provider dashboard"
echo ""

echo "========================================"
echo "SAVE YOUR CREDENTIALS:"
echo "========================================"
echo ""
echo "Copy this to a SECURE location:"
echo ""
echo "SECRET_KEY=$SECRET_KEY"
echo ""

# Create a temporary file with the generated SECRET_KEY
CREDS_FILE="production_credentials.txt"
cat > "$CREDS_FILE" << EOF
# Save this file SECURELY - Delete after using!
# Generated: $(date)

SECRET_KEY=$SECRET_KEY

DATABASE_PASSWORD=[FILL_ME: Strong PostgreSQL password]
EMAIL_HOST_PASSWORD=[FILL_ME: Gmail App Password]
ALLOWED_HOSTS=[FILL_ME: Your VPS IP address]

# Use these values in .env.production file
EOF

echo "Credentials saved to: $CREDS_FILE"
echo "⚠️  IMPORTANT: Delete this file after copying values to .env.production"
echo ""
echo "========================================"
