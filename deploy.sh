#!/bin/bash
set -e

echo "🚀 Starting Psychology Clinic Backend Deployment..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ Please do not run this script as root. Run as regular user with sudo privileges.${NC}"
    exit 1
fi

# Variables
APP_DIR="/var/www/clink-backend"
APP_USER="www-data"
DOMAIN="tailoredpsychology.com.au"
DROPLET_IP="209.38.89.74"

echo -e "${GREEN}✓ Running as user: $(whoami)${NC}"

# 1. Update system
echo -e "\n${YELLOW}[1/15] Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
echo -e "\n${YELLOW}[2/15] Installing system dependencies...${NC}"
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    redis-server \
    certbot \
    python3-certbot-nginx \
    git \
    build-essential \
    libpq-dev \
    python3-dev

# 3. Create application directory
echo -e "\n${YELLOW}[3/15] Creating application directory...${NC}"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# 4. Copy application files (assuming you're running from project root)
echo -e "\n${YELLOW}[4/15] Copying application files...${NC}"
if [ -d "$APP_DIR/.git" ]; then
    echo "Application already exists. Pulling latest changes..."
    cd $APP_DIR
    git pull
else
    echo "Copying files from current directory..."
    cp -r . $APP_DIR/ 2>/dev/null || {
        echo -e "${YELLOW}⚠ Could not copy files. Please ensure you're in the project root directory.${NC}"
        echo "You may need to manually copy files or clone from git repository."
        read -p "Press Enter to continue after copying files manually..."
    }
fi

cd $APP_DIR

# 5. Create virtual environment
echo -e "\n${YELLOW}[5/15] Creating Python virtual environment...${NC}"
python3.11 -m venv venv
source venv/bin/activate

# 6. Install Python packages
echo -e "\n${YELLOW}[6/15] Installing Python packages...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# 7. Create .env file if it doesn't exist
echo -e "\n${YELLOW}[7/15] Setting up environment file...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    if [ -f "$APP_DIR/env_template.txt" ]; then
        cp env_template.txt .env
        # Update ALLOWED_HOSTS to include IP and domain
        if grep -q "ALLOWED_HOSTS=" "$APP_DIR/.env"; then
            sed -i "s|ALLOWED_HOSTS=.*|ALLOWED_HOSTS=$DROPLET_IP,$DOMAIN,www.$DOMAIN|" "$APP_DIR/.env"
        else
            echo "ALLOWED_HOSTS=$DROPLET_IP,$DOMAIN,www.$DOMAIN" >> "$APP_DIR/.env"
        fi
        echo -e "${GREEN}✓ Created .env file with IP and domain in ALLOWED_HOSTS${NC}"
        echo -e "${YELLOW}⚠ Please edit .env file with production values!${NC}"
        echo "Edit: sudo nano $APP_DIR/.env"
    else
        echo -e "${RED}❌ env_template.txt not found. Please create .env file manually.${NC}"
        exit 1
    fi
else
    # Update ALLOWED_HOSTS in existing .env if IP is not present
    if ! grep -q "$DROPLET_IP" "$APP_DIR/.env"; then
        if grep -q "ALLOWED_HOSTS=" "$APP_DIR/.env"; then
            CURRENT_HOSTS=$(grep "ALLOWED_HOSTS=" "$APP_DIR/.env" | cut -d'=' -f2)
            sed -i "s|ALLOWED_HOSTS=.*|ALLOWED_HOSTS=$CURRENT_HOSTS,$DROPLET_IP|" "$APP_DIR/.env"
            echo -e "${GREEN}✓ Added IP to existing ALLOWED_HOSTS${NC}"
        fi
    fi
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# 8. Create necessary directories
echo -e "\n${YELLOW}[8/15] Creating necessary directories...${NC}"
sudo mkdir -p /var/log/celery /var/run/celery
sudo chown -R $APP_USER:$APP_USER /var/log/celery /var/run/celery

# 9. Set permissions
echo -e "\n${YELLOW}[9/15] Setting file permissions...${NC}"
sudo chown -R $APP_USER:$APP_USER $APP_DIR
sudo chmod -R 755 $APP_DIR
sudo chmod 600 $APP_DIR/.env 2>/dev/null || true

# 10. Run migrations
echo -e "\n${YELLOW}[10/15] Running database migrations...${NC}"
sudo -u $APP_USER $APP_DIR/venv/bin/python $APP_DIR/manage.py migrate --noinput

# 11. Collect static files
echo -e "\n${YELLOW}[11/15] Collecting static files...${NC}"
sudo -u $APP_USER $APP_DIR/venv/bin/python $APP_DIR/manage.py collectstatic --noinput

# 12. Setup Gunicorn
echo -e "\n${YELLOW}[12/15] Setting up Gunicorn service...${NC}"
sudo cp $APP_DIR/deployment/gunicorn.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn
echo -e "${GREEN}✓ Gunicorn service configured${NC}"

# 13. Setup Celery
echo -e "\n${YELLOW}[13/15] Setting up Celery services...${NC}"
sudo cp $APP_DIR/deployment/celery.service /etc/systemd/system/
sudo cp $APP_DIR/deployment/celery-beat.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable celery
sudo systemctl enable celery-beat
sudo systemctl restart celery
sudo systemctl restart celery-beat
echo -e "${GREEN}✓ Celery services configured${NC}"

# 14. Configure Nginx
echo -e "\n${YELLOW}[14/15] Configuring Nginx...${NC}"
sudo cp $APP_DIR/deployment/nginx.conf /etc/nginx/sites-available/psychology_clinic
sudo ln -sf /etc/nginx/sites-available/psychology_clinic /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
if sudo nginx -t; then
    sudo systemctl restart nginx
    echo -e "${GREEN}✓ Nginx configured and restarted${NC}"
else
    echo -e "${RED}❌ Nginx configuration test failed!${NC}"
    exit 1
fi

# 15. Setup SSL (optional - will prompt)
echo -e "\n${YELLOW}[15/15] SSL Certificate Setup...${NC}"
echo -e "${YELLOW}⚠ SSL certificate setup requires domain DNS to be configured first.${NC}"
read -p "Do you want to set up SSL certificate now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN || {
        echo -e "${YELLOW}⚠ SSL setup failed. You can run this later:${NC}"
        echo "sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
    }
else
    echo -e "${YELLOW}⚠ Skipping SSL setup. Run this later:${NC}"
    echo "sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN"
fi

# 16. Setup firewall
echo -e "\n${YELLOW}[16/16] Configuring firewall...${NC}"
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
echo "y" | sudo ufw enable
echo -e "${GREEN}✓ Firewall configured${NC}"

# 17. Setup automatic security updates
echo -e "\n${YELLOW}[17/17] Setting up automatic security updates...${NC}"
sudo apt install -y unattended-upgrades
echo 'Unattended-Upgrade::Automatic-Reboot "false";' | sudo tee -a /etc/apt/apt.conf.d/50unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades <<< "yes" || true
echo -e "${GREEN}✓ Automatic security updates configured${NC}"

# Final status check
echo -e "\n${GREEN}=================================================="
echo "✅ Deployment Complete!"
echo "==================================================${NC}\n"

echo "Service Status:"
sudo systemctl is-active gunicorn > /dev/null && echo -e "${GREEN}✓ Gunicorn: Running${NC}" || echo -e "${RED}✗ Gunicorn: Not Running${NC}"
sudo systemctl is-active celery > /dev/null && echo -e "${GREEN}✓ Celery: Running${NC}" || echo -e "${RED}✗ Celery: Not Running${NC}"
sudo systemctl is-active celery-beat > /dev/null && echo -e "${GREEN}✓ Celery Beat: Running${NC}" || echo -e "${RED}✗ Celery Beat: Not Running${NC}"
sudo systemctl is-active nginx > /dev/null && echo -e "${GREEN}✓ Nginx: Running${NC}" || echo -e "${RED}✗ Nginx: Not Running${NC}"
sudo systemctl is-active redis > /dev/null && echo -e "${GREEN}✓ Redis: Running${NC}" || echo -e "${RED}✗ Redis: Not Running${NC}"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Edit production .env file: sudo nano $APP_DIR/.env"
echo "2. Create superuser: sudo -u $APP_USER $APP_DIR/venv/bin/python $APP_DIR/manage.py createsuperuser"
echo "3. Test your API:"
echo "   - Via IP: http://$DROPLET_IP/api/"
echo "   - Via Domain: https://$DOMAIN/api/"
echo "4. Check logs: sudo journalctl -u gunicorn -f"
echo "5. Monitor services: sudo systemctl status gunicorn celery celery-beat nginx"

echo -e "\n${GREEN}🌐 Your API is accessible at:${NC}"
echo -e "   ${GREEN}• IP (HTTP): http://$DROPLET_IP${NC}"
echo -e "   ${GREEN}• Domain (HTTPS): https://$DOMAIN${NC}\n"

