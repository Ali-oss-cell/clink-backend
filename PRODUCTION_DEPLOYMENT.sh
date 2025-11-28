#!/bin/bash
# Production Server Deployment Script
# Run this on your production server at /var/www/clink-backend

echo "🚀 Welcome Email Tracking - Production Deployment"
echo "================================================"
echo ""

# Step 1: Pull latest code
echo "📥 Step 1: Pulling latest code from GitHub..."
cd /var/www/clink-backend
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to pull code"
    exit 1
fi

echo "✅ Code pulled successfully"
echo ""

# Step 2: Activate virtual environment
echo "🐍 Step 2: Activating virtual environment..."
source venv/bin/activate

# Step 3: Apply database migration
echo "🗄️  Step 3: Applying database migration..."
echo ""

# Check if using SQLite or PostgreSQL
if [ -f "db.sqlite3" ]; then
    echo "   Using SQLite database..."
    sqlite3 db.sqlite3 <<EOF
-- Add welcome email tracking fields
ALTER TABLE users_user ADD COLUMN welcome_email_sent BOOLEAN DEFAULT 0;
ALTER TABLE users_user ADD COLUMN welcome_email_sent_at TIMESTAMP NULL;
ALTER TABLE users_user ADD COLUMN welcome_email_attempts INTEGER DEFAULT 0;
ALTER TABLE users_user ADD COLUMN welcome_email_last_error TEXT NULL;

-- Mark migration as applied
INSERT INTO django_migrations (app, name, applied) 
VALUES ('users', '0003_add_welcome_email_tracking', datetime('now'));
EOF
    echo "✅ SQLite migration applied"
else
    echo "   Using PostgreSQL database..."
    echo "   Please run this SQL manually:"
    echo ""
    echo "   ALTER TABLE users_user ADD COLUMN welcome_email_sent BOOLEAN DEFAULT FALSE;"
    echo "   ALTER TABLE users_user ADD COLUMN welcome_email_sent_at TIMESTAMP NULL;"
    echo "   ALTER TABLE users_user ADD COLUMN welcome_email_attempts INTEGER DEFAULT 0;"
    echo "   ALTER TABLE users_user ADD COLUMN welcome_email_last_error TEXT NULL;"
    echo ""
    echo "   INSERT INTO django_migrations (app, name, applied) VALUES ('users', '0003_add_welcome_email_tracking', NOW());"
    echo ""
    read -p "Press Enter after running the SQL commands..."
fi

echo ""

# Step 4: Restart services
echo "🔄 Step 4: Restarting services..."
sudo systemctl restart gunicorn
sudo systemctl restart celery

echo "✅ Services restarted"
echo ""

# Step 5: Verify
echo "✅ Step 5: Verification"
echo "   Checking email configuration..."
python check_email_config.py

echo ""
echo "================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "📋 Next Steps:"
echo "   1. Create a test user account"
echo "   2. Check API response includes 'welcome_email_sent'"
echo "   3. Check email inbox"
echo "   4. Check SendGrid dashboard"
echo ""
echo "📊 To watch logs:"
echo "   sudo journalctl -u gunicorn -f"
echo ""
echo "🔍 To check database:"
echo "   python manage.py shell"
echo "   >>> from users.models import User"
echo "   >>> user = User.objects.latest('date_joined')"
echo "   >>> print(user.welcome_email_sent)"
echo ""

