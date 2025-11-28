# 🚀 Deployment Commands - Welcome Email Tracking

## ✅ Changes Pushed to GitHub

Everything is committed and pushed! Now deploy to your production server.

---

## 📋 Production Server Commands

### Step 1: Connect to Server

```bash
ssh root@your-server-ip
```

### Step 2: Navigate to Project & Pull Code

```bash
cd /var/www/clink-backend
git pull origin main
```

**Expected output:**
```
Updating 57de56a..796a3a8
Fast-forward
 users/models.py             | 4 ++++
 users/serializers.py        | ...
 users/views.py              | ...
 ...
```

### Step 3: Activate Virtual Environment

```bash
source venv/bin/activate
```

### Step 4: Apply Database Migration

```bash
# Add the new fields to database
python manage.py sqlmigrate users 0003 > /tmp/migration.sql

# Apply manually (since drf_yasg might cause issues)
sqlite3 db.sqlite3 < /tmp/migration.sql
```

**OR use manual SQL:**

```sql
sqlite3 db.sqlite3

-- Add the fields
ALTER TABLE users_user ADD COLUMN welcome_email_sent BOOLEAN DEFAULT 0;
ALTER TABLE users_user ADD COLUMN welcome_email_sent_at TIMESTAMP NULL;
ALTER TABLE users_user ADD COLUMN welcome_email_attempts INTEGER DEFAULT 0;
ALTER TABLE users_user ADD COLUMN welcome_email_last_error TEXT NULL;

-- Mark migration as applied
INSERT INTO django_migrations (app, name, applied) 
VALUES ('users', '0003_add_welcome_email_tracking', datetime('now'));

-- Exit
.exit
```

### Step 5: Restart Services

```bash
sudo systemctl restart gunicorn
sudo systemctl restart celery
```

**Verify restart:**
```bash
sudo systemctl status gunicorn
sudo systemctl status celery
```

---

## ✅ Verification Commands

### Test 1: Check Database Fields Were Added

```bash
sqlite3 db.sqlite3

.schema users_user

-- Should show new fields:
-- welcome_email_sent BOOLEAN DEFAULT 0
-- welcome_email_sent_at TIMESTAMP
-- welcome_email_attempts INTEGER DEFAULT 0  
-- welcome_email_last_error TEXT

.exit
```

### Test 2: Check Email Configuration

```bash
python check_email_config.py
```

**Expected:**
```
✅ SendGrid is configured - emails should work!
   Method: SendGrid API
```

### Test 3: Create a Test User (API Test)

From your **local machine**, run:

```bash
curl -X POST https://your-backend-url/api/auth/register/patient/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test123@example.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "+61412345678",
    "date_of_birth": "1990-01-01"
  }'
```

**Check the response for:**
```json
{
  "message": "Patient registered successfully",
  "user": { ... },
  "tokens": { ... },
  "welcome_email_sent": true,    ← Should be true
  "welcome_email_sent_at": "2025-11-28T..." ← Should have timestamp
}
```

### Test 4: Check Database

```bash
# On server
python manage.py shell
```

```python
from users.models import User

# Get latest user
user = User.objects.latest('date_joined')

print(f"Email: {user.email}")
print(f"Welcome email sent: {user.welcome_email_sent}")
print(f"Sent at: {user.welcome_email_sent_at}")
print(f"Attempts: {user.welcome_email_attempts}")
print(f"Last error: {user.welcome_email_last_error}")

# Should show:
# Welcome email sent: True
# Sent at: 2025-11-28 10:30:45...
# Attempts: 1
# Last error: None
```

### Test 5: Check Server Logs

```bash
# Watch live logs
sudo journalctl -u gunicorn -f

# Or check recent logs
sudo journalctl -u gunicorn -n 100 | grep "welcome"
```

**Look for:**
```
Attempting to send welcome email to test123@example.com
Welcome email sent successfully to test123@example.com (status: 202)
```

### Test 6: Check SendGrid Dashboard

1. Go to: https://app.sendgrid.com/
2. Login with your Twilio credentials
3. Click: **Activity** → **Email Activity**
4. Search for: `test123@example.com`
5. Check status: Should show "Delivered"

### Test 7: Check Actual Email

1. Check the inbox of test email
2. Check spam/junk folder
3. Verify welcome email arrived

---

## 🔍 Debugging Commands

### If Email Not Sent

```bash
# Check SendGrid config
python check_email_config.py

# Check last user's error
python manage.py shell
```

```python
from users.models import User
user = User.objects.latest('date_joined')
print(f"Error: {user.welcome_email_last_error}")
```

### If Migration Fails

```bash
# Check current migrations
python manage.py showmigrations users

# If 0003 is not applied, run manual SQL (see Step 4 above)
```

### Check Gunicorn is Running

```bash
sudo systemctl status gunicorn

# If stopped, start it
sudo systemctl start gunicorn
```

### Check Celery is Running

```bash
sudo systemctl status celery

# If stopped, start it
sudo systemctl start celery
```

---

## 📊 Complete Verification Checklist

Run through this checklist to ensure everything works:

- [ ] SSH into server
- [ ] Navigate to `/var/www/clink-backend`
- [ ] Pull latest code: `git pull origin main`
- [ ] Activate venv: `source venv/bin/activate`
- [ ] Apply migration (manual SQL)
- [ ] Verify fields exist in database
- [ ] Restart gunicorn: `sudo systemctl restart gunicorn`
- [ ] Restart celery: `sudo systemctl restart celery`
- [ ] Check email config: `python check_email_config.py` (should show ✅)
- [ ] Create test user via API
- [ ] API response includes `welcome_email_sent: true`
- [ ] Check database shows `welcome_email_sent=True`
- [ ] Check server logs show "Welcome email sent successfully"
- [ ] Check SendGrid dashboard shows email delivered
- [ ] Check email inbox (welcome email arrived)

---

## 🎯 Quick Command Summary

```bash
# 1. SSH to server
ssh root@your-server-ip

# 2. Pull & Update
cd /var/www/clink-backend
git pull origin main
source venv/bin/activate

# 3. Apply Migration (manual SQL)
sqlite3 db.sqlite3 <<EOF
ALTER TABLE users_user ADD COLUMN welcome_email_sent BOOLEAN DEFAULT 0;
ALTER TABLE users_user ADD COLUMN welcome_email_sent_at TIMESTAMP NULL;
ALTER TABLE users_user ADD COLUMN welcome_email_attempts INTEGER DEFAULT 0;
ALTER TABLE users_user ADD COLUMN welcome_email_last_error TEXT NULL;
INSERT INTO django_migrations (app, name, applied) 
VALUES ('users', '0003_add_welcome_email_tracking', datetime('now'));
EOF

# 4. Restart
sudo systemctl restart gunicorn
sudo systemctl restart celery

# 5. Verify
python check_email_config.py

# 6. Test (watch logs)
sudo journalctl -u gunicorn -f
```

Then create a new user from your app and check the results!

---

## 📧 What Changed

### Database:
- Added `welcome_email_sent` field (boolean)
- Added `welcome_email_sent_at` field (datetime)
- Added `welcome_email_attempts` field (integer)
- Added `welcome_email_last_error` field (text)

### API Response:
- Registration now returns email status
- Frontend can show "Email sent" message

### Tracking:
- Every registration attempt is tracked
- Errors are saved to database
- Logs show success/failure

---

## 🚀 Ready!

Everything is deployed and ready to test. Create a new user and watch the magic happen! ✨


