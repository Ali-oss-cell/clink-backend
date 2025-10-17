#!/bin/bash

# Video Calls & Notifications Setup Script
# Run this script to set up all services

echo "═══════════════════════════════════════════════════════════════"
echo "   Video Calls & Notifications Setup"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

echo -e "${GREEN}✓${NC} Virtual environment activated"
echo ""

# Check Redis
echo -e "${YELLOW}Checking Redis...${NC}"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Redis is running"
else
    echo -e "${RED}✗${NC} Redis is not running"
    echo "  Start Redis with: redis-server"
    echo "  Or install with:"
    echo "    Ubuntu/Debian: sudo apt install redis-server"
    echo "    macOS: brew install redis"
    echo ""
fi

# Check environment variables
echo -e "${YELLOW}Checking environment variables...${NC}"

if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    
    # Check required variables
    REQUIRED_VARS="TWILIO_ACCOUNT_SID TWILIO_AUTH_TOKEN TWILIO_API_KEY TWILIO_API_SECRET"
    MISSING_VARS=""
    
    for var in $REQUIRED_VARS; do
        if grep -q "^${var}=" .env; then
            value=$(grep "^${var}=" .env | cut -d '=' -f 2)
            if [ -z "$value" ] || [ "$value" == "your_*" ]; then
                MISSING_VARS="$MISSING_VARS $var"
            fi
        else
            MISSING_VARS="$MISSING_VARS $var"
        fi
    done
    
    if [ -z "$MISSING_VARS" ]; then
        echo -e "${GREEN}✓${NC} All required Twilio variables configured"
    else
        echo -e "${YELLOW}⚠${NC} Missing or incomplete variables:$MISSING_VARS"
        echo "  Please configure these in .env file"
    fi
else
    echo -e "${RED}✗${NC} .env file not found"
    echo "  Creating template .env file..."
    
    cat > .env << 'EOF'
# Twilio Video & Messaging
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_API_KEY=your_api_key
TWILIO_API_SECRET=your_api_secret
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Redis
REDIS_URL=redis://localhost:6379/0

# Frontend URL
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
EOF
    
    echo -e "${GREEN}✓${NC} Created .env template"
    echo "  Please fill in your credentials in .env file"
fi

echo ""

# Check if Celery processes are running
echo -e "${YELLOW}Checking Celery processes...${NC}"

if pgrep -f "celery.*worker" > /dev/null; then
    echo -e "${GREEN}✓${NC} Celery worker is running"
else
    echo -e "${YELLOW}⚠${NC} Celery worker is not running"
    echo "  Start with: celery -A psychology_clinic worker -l info"
fi

if pgrep -f "celery.*beat" > /dev/null; then
    echo -e "${GREEN}✓${NC} Celery beat is running"
else
    echo -e "${YELLOW}⚠${NC} Celery beat is not running"
    echo "  Start with: celery -A psychology_clinic beat -l info"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "   Quick Start Commands"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. Start Redis:"
echo "   redis-server"
echo ""
echo "2. Start Celery Worker (in new terminal):"
echo "   celery -A psychology_clinic worker -l info"
echo ""
echo "3. Start Celery Beat (in new terminal):"
echo "   celery -A psychology_clinic beat -l info"
echo ""
echo "4. Test Email Configuration:"
echo "   python manage.py shell -c \"from core.email_service import test_email_configuration; print(test_email_configuration())\""
echo ""
echo "5. Test Video Service:"
echo "   curl -X POST http://localhost:8000/api/appointments/video-room/1/ \\"
echo "     -H 'Authorization: Bearer YOUR_TOKEN'"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "📚 For detailed documentation, see:"
echo "   - VIDEO_NOTIFICATIONS_COMPLETE_IMPLEMENTATION.md"
echo "   - VIDEO_AND_NOTIFICATIONS_IMPLEMENTATION.md"
echo ""

