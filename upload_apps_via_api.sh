#!/bin/bash
#
# Script to upload 5 sample Android apps via HTTP API
# Usage: bash upload_apps_via_api.sh [BASE_URL] [USERNAME] [PASSWORD]
# Example: bash upload_apps_via_api.sh http://localhost:8000 appuploader TestPassword123!
#

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${1:-http://localhost:8000}"
USERNAME="${2:-appuploader}"
PASSWORD="${3:-TestPassword123!}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}📱 Android App Upload via API${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Base URL: ${BLUE}${BASE_URL}${NC}"
echo -e "Username: ${BLUE}${USERNAME}${NC}"
echo ""

# Function to upload single app
upload_app() {
    local app_title="$1"
    local category="$2"
    local version="$3"
    local short_desc="$4"
    local description="$5"
    local download_link="$6"
    local price="$7"
    local is_free="$8"
    
    echo -e "${YELLOW}⏳ Uploading: ${app_title}${NC}"
    
    local response=$(curl -s -X POST "${BASE_URL}/apps/upload/" \
        -F "title=${app_title}" \
        -F "category=${category}" \
        -F "version=${version}" \
        -F "short_description=${short_desc}" \
        -F "description=${description}" \
        -F "download_link=${download_link}" \
        -F "is_free=${is_free}" \
        -F "price=${price}" \
        -F "developer_name=JnDroid Developer" \
        -F "developer_email=dev@jndroid.store" \
        -F "support_email=support@jndroid.store" \
        -F "website_url=https://jndroid.store" \
        -F "min_api_level=21" \
        -F "target_api_level=34" \
        -F "min_android_version=5.0" \
        -F "target_android_version=14.0" \
        -F "size_mb=15.5" \
        -F "age_rating=3+" \
        -F "is_original_content=on" \
        --user "${USERNAME}:${PASSWORD}" 2>&1)
    
    if echo "$response" | grep -q "success\|added\|created\|uploaded"; then
        echo -e "${GREEN}✅ Successfully uploaded: ${app_title}${NC}"
    else
        echo -e "${RED}❌ Failed to upload: ${app_title}${NC}"
        echo "   Response: $response"
    fi
    echo ""
}

# App upload data
echo -e "${BLUE}📋 Apps to upload:${NC}\n"

# App 1: Game Master Pro
upload_app \
    "Game Master Pro" \
    "games" \
    "1.0.0" \
    "Ultimate casual gaming experience" \
    "A fast-paced, addictive game with amazing graphics and engaging gameplay. Compete with friends and climb the leaderboards." \
    "https://example.com/gamemaster.apk" \
    "" \
    "true"

# App 2: File Manager Plus
upload_app \
    "File Manager Plus" \
    "tools" \
    "2.1.5" \
    "Fast and powerful file management tool" \
    "Organize your files efficiently with a modern interface. Features include cloud sync, compression, and secure deletion." \
    "https://example.com/filemgr.apk" \
    "" \
    "true"

# App 3: Invoice Maker Business
upload_app \
    "Invoice Maker Business" \
    "business" \
    "3.2.1" \
    "Create professional invoices on the go" \
    "Generate, send, and manage invoices from anywhere. Track payments, create estimates, and grow your business with ease." \
    "https://example.com/invoice.apk" \
    "4.99" \
    "false"

# App 4: Movie Streaming Hub
upload_app \
    "Movie Streaming Hub" \
    "entertainment" \
    "1.5.3" \
    "Watch movies and TV shows anywhere" \
    "Stream thousands of movies and shows in HD and 4K. Download for offline viewing and enjoy entertainment wherever you are." \
    "https://example.com/moviehub.apk" \
    "" \
    "true"

# App 5: Productivity Timer
upload_app \
    "Productivity Timer" \
    "productivity" \
    "4.0.2" \
    "Master time management and focus" \
    "Use the Pomodoro technique to boost productivity. Track your tasks, set goals, and achieve more with effective time blocking." \
    "https://example.com/prodtimer.apk" \
    "" \
    "true"

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Upload process completed!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "📊 View apps at: ${BLUE}${BASE_URL}/apps/${NC}"
echo -e "💼 Your dashboard: ${BLUE}${BASE_URL}/apps/my-apps/${NC}"
