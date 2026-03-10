#!/bin/bash

# ============================================
# RateStance Dashboard Deployment Script
# ============================================
# One-click deployment script for the economy dashboard
# Following the same pattern as hanyang project
#
# Usage:
#   cd dashboard
#   ../deploy/deploy.sh
# ============================================

# Configuration
SERVER="irons_server@ip9202.site"
PASS="rkdcjfIP00!"
PROJECT_PATH="~/projects/economy"
APP_PORT="3004"
PM2_NAME="ratestance"
SERVICE_URL="https://ip9202.site/economy"
BASE_PATH="/economy"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Change to dashboard directory (script is in deploy/, dashboard is ../)
cd "$(dirname "$0")/../dashboard" || exit 1

echo "=========================================="
echo "  RateStance Dashboard Deployment"
echo "  Target: $SERVICE_URL"
echo "=========================================="
echo ""

# Step 1: Build
log_info "Step 1: Building Next.js application..."
npm run build || { log_error "Build failed"; exit 1; }
log_success "Build completed"

# Step 2: Clear server cache
log_info "Step 2: Clearing server cache..."
expect -c "
set timeout 60
spawn ssh $SERVER \"rm -rf $PROJECT_PATH/.next && mkdir -p $PROJECT_PATH/.next\"
expect {
    \"Password:\" { send \"$PASS\r\"; exp_continue }
    \"password:\" { send \"$PASS\r\"; exp_continue }
    eof
}
"
log_success "Server cache cleared"

# Step 3: Deploy .next
log_info "Step 3: Deploying .next folder..."
expect -c "
set timeout 120
spawn scp -r .next/standalone/.next/. $SERVER:$PROJECT_PATH/.next/
expect {
    \"Password:\" { send \"$PASS\r\"; exp_continue }
    \"password:\" { send \"$PASS\r\"; exp_continue }
    eof
}
"
log_success ".next folder deployed"

# Step 4: Deploy static folder
log_info "Step 4: Deploying static folder..."
expect -c "
set timeout 120
spawn scp -r .next/static $SERVER:$PROJECT_PATH/.next/
expect {
    \"Password:\" { send \"$PASS\r\"; exp_continue }
    \"password:\" { send \"$PASS\r\"; exp_continue }
    eof
}
"
log_success "Static folder deployed"

# Step 5: Restart PM2
log_info "Step 5: Restarting PM2 process..."
expect -c "
set timeout 60
spawn ssh $SERVER \"bash -l -c 'pm2 restart $PM2_NAME'\"
expect {
    \"Password:\" { send \"$PASS\r\"; exp_continue }
    \"password:\" { send \"$PASS\r\"; exp_continue }
    eof
}
"
log_success "PM2 process restarted"

# Step 6: Check logs
log_info "Step 6: Checking PM2 logs..."
expect -c "
set timeout 30
spawn ssh $SERVER \"bash -l -c 'pm2 logs $PM2_NAME --lines 10 --nostream'\"
expect {
    \"Password:\" { send \"$PASS\r\"; exp_continue }
    \"password:\" { send \"$PASS\r\"; exp_continue }
    eof
}
"

echo ""
echo "=========================================="
log_success "Deployment Complete!"
echo "=========================================="
echo ""
echo "Access URL: $SERVICE_URL"
echo "PM2 Name: $PM2_NAME"
echo "Port: $APP_PORT"
echo ""
echo "Nginx Configuration Required:"
echo "  Add to /opt/homebrew/etc/nginx/nginx.conf:"
echo ""
echo "  # RateStance static resources"
echo "  location /_next/ {"
echo "      proxy_pass http://127.0.0.1:$APP_PORT;"
echo "      proxy_http_version 1.1;"
echo "      proxy_set_header Host \$host;"
echo "      proxy_set_header X-Real-IP \$remote_addr;"
echo "      proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;"
echo "      proxy_set_header X-Forwarded-Proto \$scheme;"
echo "  }"
echo ""
echo "  # RateStance main page"
echo "  location $BASE_PATH {"
echo "      proxy_pass http://127.0.0.1:$APP_PORT/;"
echo "      rewrite ^$BASE_PATH(/.*)\$ \$1 break;"
echo "      proxy_http_version 1.1;"
echo "      proxy_set_header Upgrade \$http_upgrade;"
echo "      proxy_set_header Connection \"upgrade\";"
echo "      proxy_set_header Host \$host;"
echo "      proxy_set_header X-Real-IP \$remote_addr;"
echo "      proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;"
echo "      proxy_set_header X-Forwarded-Proto \$scheme;"
echo "  }"
echo ""
