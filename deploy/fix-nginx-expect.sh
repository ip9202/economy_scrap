#!/usr/bin/expect -f
# RateStance Nginx Configuration Fix Script (using expect)
# Purpose: Fix 404 errors for /economy/_next/static/* resources

set timeout 60

# Configuration
set SERVER_HOST "ip9202.site"
set SERVER_USER "irons_server"
set SERVER_PASS "rkdcjfIP00!"

spawn ssh ${SERVER_USER}@${SERVER_HOST}
expect {
    "password:" {
        send "${SERVER_PASS}\r"
        expect "~]#"
    }
    "~]#" {}
    timeout {
        send_user "Connection timeout\n"
        exit 1
    }
}

send_user "=== Connected to server ===\n"

# Backup nginx config
send_user "\n[Step 1/5] Backing up Nginx configuration...\n"
send "sudo cp /opt/homebrew/etc/nginx/nginx.conf /opt/homebrew/etc/nginx/nginx.conf.backup.[clock format [clock seconds] -format {%Y%m%d_%H%M%S}]\r"
expect {
    "Password for" {
        send "${SERVER_PASS}\r"
    }
}
expect "~]#"
send_user "Backup created\n"

# Create new location blocks file
send_user "\n[Step 2/5] Creating new location blocks...\n"
send "cat > /tmp/nginx-economy-blocks.conf << 'NGINX_EOF'\r"
expect ""

send "# RateStance static assets (more specific path first)\r"
expect ""
send "location /economy/_next/static/ {\r"
expect ""
send "    proxy_pass http://127.0.0.1:3004/_next/static/;\r"
expect ""
send "    proxy_http_version 1.1;\r"
expect ""
send "    proxy_set_header Host \$host;\r"
expect ""
send "    proxy_set_header X-Real-IP \$remote_addr;\r"
expect ""
send "    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\r"
expect ""
send "    proxy_set_header X-Forwarded-Proto \$scheme;\r"
expect ""
send "    expires 1y;\r"
expect ""
send "    add_header Cache-Control \"public, immutable\";\r"
expect ""
send "}\r"
expect ""
send "\r"
expect ""
send "# RateStance _next image resources\r"
expect ""
send "location /economy/_next/image/ {\r"
expect ""
send "    proxy_pass http://127.0.0.1:3004/_next/image/;\r"
expect ""
send "    proxy_http_version 1.1;\r"
expect ""
send "    proxy_set_header Host \$host;\r"
expect ""
send "    proxy_set_header X-Real-IP \$remote_addr;\r"
expect ""
send "    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\r"
expect ""
send "    proxy_set_header X-Forwarded-Proto \$scheme;\r"
expect ""
send "}\r"
expect ""
send "\r"
expect ""
send "# RateStance _next dynamic resources\r"
expect ""
send "location /economy/_next/ {\r"
expect ""
send "    proxy_pass http://127.0.0.1:3004/_next/;\r"
expect ""
send "    proxy_http_version 1.1;\r"
expect ""
send "    proxy_set_header Host \$host;\r"
expect ""
send "    proxy_set_header X-Real-IP \$remote_addr;\r"
expect ""
send "    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\r"
expect ""
send "    proxy_set_header X-Forwarded-Proto \$scheme;\r"
expect ""
send "}\r"
expect ""
send "\r"
expect ""
send "# RateStance main page\r"
expect ""
send "location /economy {\r"
expect ""
send "    proxy_pass http://127.0.0.1:3004/;\r"
expect ""
send "    rewrite ^/economy(/.*)\$ \$1 break;\r"
expect ""
send "    proxy_http_version 1.1;\r"
expect ""
send "    proxy_set_header Upgrade \$http_upgrade;\r"
expect ""
send "    proxy_set_header Connection \"upgrade\";\r"
expect ""
send "    proxy_set_header Host \$host;\r"
expect ""
send "    proxy_set_header X-Real-IP \$remote_addr;\r"
expect ""
send "    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\r"
expect ""
send "    proxy_set_header X-Forwarded-Proto \$scheme;\r"
expect ""
send "}\r"
expect ""
send "NGINX_EOF\r"
expect "~]#"
send_user "New location blocks created\n"

# Show current config for economy
send_user "\n[Step 3/5] Checking current configuration...\n"
send "grep -A 5 'location /economy' /opt/homebrew/etc/nginx/nginx.conf | head -20\r"
expect "~]#"

# Now apply using sed to replace the economy location blocks
send_user "\n[Step 4/5] Applying new configuration...\n"
send_user "Note: Using sed to replace economy location blocks\n"
send "sudo sed -i.bak '/^location.*economy/,/^}/d' /opt/homebrew/etc/nginx/nginx.conf\r"
expect {
    "Password for" {
        send "${SERVER_PASS}\r"
    }
}
expect "~]#"

# Append new blocks after /api/ location block
send "grep -n 'location /api/' /opt/homebrew/etc/nginx/nginx.conf | tail -1 | cut -d: -f1 > /tmp/api_line.txt\r"
expect "~]#"
send "API_LINE=\$(cat /tmp/api_line.txt)\r"
expect "~]#"
send "sudo sed -i \"\${API_LINE}r /tmp/nginx-economy-blocks.conf\" /opt/homebrew/etc/nginx/nginx.conf\r"
expect "~]#"
send_user "New configuration applied\n"

# Test nginx
send_user "\n[Step 5/5] Testing and reloading Nginx...\n"
send "sudo nginx -t\r"
expect "~]#"

send "sudo nginx -s reload\r"
expect "~]#"

# Restart PM2
send_user "\n[Step 6/6] Restarting PM2 ratestance...\n"
send "pm2 restart ratestance\r"
expect "~]#"

send "pm2 logs ratestance --lines 15\r"
expect "~]#"

send_user "\n=== Configuration Fix Complete ===\n"
send_user "\nPlease verify at: https://${SERVER_HOST}/economy\n"

send "exit\r"
expect eof
