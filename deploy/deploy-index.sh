#!/bin/bash

# ============================================
# Root Index.html Deployment Script
# ============================================
# Deploys the root index.html to the webroot directory
#
# Usage:
#   ./deploy/deploy-index.sh              # Interactive (asks for password)
#   DEPLOY_PASS=xxx ./deploy/deploy-index.sh  # Non-interactive
# ============================================

# Configuration
SERVER="irons_server@ip9202.site"
WEBROOT_PATH="/Users/irons_server/webroot"
LOCAL_FILE="deploy/index.html"
REMOTE_FILE="$WEBROOT_PATH/index.html"

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

# Check if local file exists
if [ ! -f "$LOCAL_FILE" ]; then
    log_error "Local file not found: $LOCAL_FILE"
    log_info "Run this script from the project root directory"
    exit 1
fi

# Get password
if [ -z "$DEPLOY_PASS" ]; then
    echo -n "Enter server password: "
    read -s DEPLOY_PASS
    echo
fi

# Deploy
log_info "Deploying index.html to $SERVER:$REMOTE_FILE"

expect -c "
set timeout 30
spawn scp $LOCAL_FILE $SERVER:$REMOTE_FILE

expect {
    -exact \"Password:\" {
        send \"$DEPLOY_PASS\r\"
        exp_continue
    }
    -exact \"password:\" {
        send \"$DEPLOY_PASS\r\"
        exp_continue
    }
    timeout {
        puts stderr \"\n[ERROR] Connection timed out\"
        exit 1
    }
    eof {
        # Check exit status
        if {[lindex [wait] 3] == 0} {
            puts \"\n[SUCCESS] Deployment complete!\"
            puts \"Check: https://ip9202.site/\"
        } else {
            puts stderr \"\n[ERROR] Deployment failed\"
            exit 1
        }
    }
}
"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    log_success "Deployment complete!"
    echo ""
    echo "Access URL: https://ip9202.site/"
    echo ""
    echo "To add a new project, edit $LOCAL_FILE"
    echo "Then run this script again to deploy."
else
    log_error "Deployment failed with exit code $EXIT_CODE"
    exit $EXIT_CODE
fi
