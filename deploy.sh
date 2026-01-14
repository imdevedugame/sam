#!/bin/bash

# Deployment Script for Distributed Flask App
# Run this on your VPS server

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/var/www/sam"
APP_USER="www-data"
PYTHON_VERSION="3.11"

# Step 1: Update system packages
echo -e "${BLUE}📦 Updating system packages...${NC}"
apt-get update
apt-get upgrade -y

# Step 2: Install Python and dependencies
echo -e "${BLUE}🐍 Installing Python $PYTHON_VERSION...${NC}"
apt-get install -y python$PYTHON_VERSION python$PYTHON_VERSION-venv python$PYTHON_VERSION-dev
apt-get install -y python3-pip nginx supervisor

# Step 3: Create virtual environment
echo -e "${BLUE}🔧 Creating virtual environment...${NC}"
cd $APP_DIR
python$PYTHON_VERSION -m venv venv

# Step 4: Activate venv and install requirements
echo -e "${BLUE}📥 Installing Python packages...${NC}"
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Step 5: Create systemd service
echo -e "${BLUE}⚙️  Creating systemd service...${NC}"
cat > /etc/systemd/system/distributed-flask.service << 'EOF'
[Unit]
Description=Distributed Flask Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/sam
Environment="PATH=/var/www/sam/venv/bin"
Environment="CONSISTENCY_MODE=eventual"
Environment="REPLICATION_DELAY=3"
Environment="QUORUM_SIZE=2"
Environment="PORT=5001"
ExecStart=/var/www/sam/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5001 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Step 6: Configure Nginx
echo -e "${BLUE}🌐 Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/distributed-flask << 'EOF'
server {
    listen 80;
    server_name _;  # Replace with your domain if you have one

    # Increase timeout for long-running requests
    proxy_read_timeout 300;
    proxy_connect_timeout 300;
    proxy_send_timeout 300;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Dashboard specific
    location /dashboard {
        proxy_pass http://127.0.0.1:5001/dashboard;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API endpoints
    location /api {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
    }
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/distributed-flask /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default  # Remove default site

# Test Nginx configuration
nginx -t

# Step 7: Set permissions
echo -e "${BLUE}🔐 Setting permissions...${NC}"
chown -R $APP_USER:$APP_USER $APP_DIR
chmod -R 755 $APP_DIR

# Step 8: Enable and start services
echo -e "${BLUE}🚀 Starting services...${NC}"
systemctl daemon-reload
systemctl enable distributed-flask
systemctl start distributed-flask
systemctl restart nginx

# Step 9: Check status
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo -e "${BLUE}📊 Service Status:${NC}"
systemctl status distributed-flask --no-pager || true

echo ""
echo -e "${GREEN}🎉 Application deployed successfully!${NC}"
echo ""
echo -e "${BLUE}Access your app at:${NC}"
echo "  - API: http://$(hostname -I | awk '{print $1}')"
echo "  - Dashboard: http://$(hostname -I | awk '{print $1}')/dashboard"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  - Check logs: journalctl -u distributed-flask -f"
echo "  - Restart app: systemctl restart distributed-flask"
echo "  - Stop app: systemctl stop distributed-flask"
echo "  - Start app: systemctl start distributed-flask"
echo ""
