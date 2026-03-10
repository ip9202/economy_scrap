#!/bin/bash
# RateStance Nginx Configuration Fix Script
# Purpose: Fix 404 errors for /economy/_next/static/* resources

set -e

# Server configuration
SERVER_HOST="ip9202.site"
SERVER_USER="irons_server"
NGINX_CONF="/opt/homebrew/etc/nginx/nginx.conf"
BACKUP_SUFFIX=$(date +%Y%m%d_%H%M%S)

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== RateStance Nginx Configuration Fix ===${NC}"
echo ""
echo "This script will fix the 404 errors for /economy/_next/static/* resources"
echo ""

# Step 1: Backup current config
echo -e "${YELLOW}[Step 1/5] Backing up current Nginx configuration...${NC}"
ssh "${SERVER_USER}@${SERVER_HOST}" "echo '${DEPLOY_PASS}' | sudo -S cp ${NGINX_CONF} ${NGINX_CONF}.backup.${BACKUP_SUFFIX}"
echo -e "${GREEN}✓ Backup created: ${NGINX_CONF}.backup.${BACKUP_SUFFIX}${NC}"

# Step 2: Read the updated config
echo ""
echo -e "${YELLOW}[Step 2/5] Reading updated Nginx configuration...${NC}"
UPDATED_CONFIG=$(cat "$(dirname "$0")/nginx-economy-updated.conf")

# Step 3: Apply the new config
echo ""
echo -e "${YELLOW}[Step 3/5] Applying new Nginx configuration...${NC}"
echo "${UPDATED_CONFIG}" | ssh "${SERVER_USER}@${SERVER_HOST}" "cat > /tmp/nginx-economy.conf && echo '${DEPLOY_PASS}' | sudo -S tee ${NGINX_CONF} > /dev/null && rm /tmp/nginx-economy.conf"
echo -e "${GREEN}✓ New configuration applied${NC}"

# Step 4: Test configuration
echo ""
echo -e "${YELLOW}[Step 4/5] Testing Nginx configuration...${NC}"
ssh "${SERVER_USER}@${SERVER_HOST}" "echo '${DEPLOY_PASS}' | sudo -S nginx -t"
echo -e "${GREEN}✓ Configuration test passed${NC}"

# Step 5: Reload Nginx
echo ""
echo -e "${YELLOW}[Step 5/5] Reloading Nginx...${NC}"
ssh "${SERVER_USER}@${SERVER_HOST}" "echo '${DEPLOY_PASS}' | sudo -S nginx -s reload"
echo -e "${GREEN}✓ Nginx reloaded${NC}"

# Step 6: Restart PM2
echo ""
echo -e "${YELLOW}[Step 6/6] Restarting PM2 ratestance process...${NC}"
ssh "${SERVER_USER}@${SERVER_HOST}" "pm2 restart ratestance"
echo -e "${GREEN}✓ PM2 ratestance restarted${NC}"

# Verification
echo ""
echo -e "${GREEN}=== Configuration Fix Complete ===${NC}"
echo ""
echo "Verification steps:"
echo "1. Check PM2 status:"
echo "   ssh ${SERVER_USER}@${SERVER_HOST} 'pm2 list'"
echo ""
echo "2. Check PM2 logs:"
echo "   ssh ${SERVER_USER}@${SERVER_HOST} 'pm2 logs ratestance --lines 20'"
echo ""
echo "3. Test static resource:"
echo "   curl -I https://${SERVER_HOST}/economy/_next/static/media/manifest.json"
echo ""
echo -e "${GREEN}✓ Fix complete! Please verify the dashboard is working correctly.${NC}"
