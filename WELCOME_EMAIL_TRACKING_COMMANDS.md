# 📧 Welcome Email Tracking - Deployment Commands

## What Was Added

✅ Database fields to track welcome email status:
- `welcome_email_sent` - Boolean (was email sent successfully?)
- `welcome_email_sent_at` - DateTime (when was it sent?)  
- `welcome_email_attempts` - Integer (how many attempts?)
- `welcome_email_last_error` - Text (last error message if failed)

✅ Automatic tracking when user registers
✅ API response includes email status
✅ Logs saved to database for debugging

---

## Commands for Production Server

### 1. Pull Latest Code

```bash
ssh root@your-server-ip
cd /var/www/clink-backend
git pull origin main
```

### 2. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 3. Apply Database Migration

**Option A: Using Django (if drf_yasg is installed)**
```bash
python manage.py migrate
```

**Option B: Manual SQL (if drf_yasg error occurs)**
```bash
# Connect to your database
sqlite3 db.sqlite3  # If using SQLite

# Or for PostgreSQL:
# psql $DATABASE_URL

# Run this SQL:
ALTER TABLE users_user ADD COLUMN welcome_email_sent BOOLEAN DEFAULT FALSE;
ALTER TABLE users_user ADD COLUMN welcome_email_sent_at TIMESTAMP NULL;
ALTER TABLE users_user ADD COLUMN welcome_email_attempts INTEGER DEFAULT 0;
ALTER TABLE users_user ADD COLUMN welcome_email_last_error TEXT NULL;

# Mark migration as applied
INSERT INTO django_migrations (app, name, applied) 
VALUES ('users', '0003_add_welcome_email_tracking', datetime('now'));
```

### 4. Restart Services

```bash
sudo systemctl restart gunicorn
sudo systemctl restart celery
```

### 5. Verify It's Working

```bash
# Check database has new fields
python manage.py dbshell
# Then run:
# .schema users_user  (SQLite)
# \d users_user       (PostgreSQL)
```

---

## Testing Commands

### Test 1: Check Email Configuration

```bash
cd /var/www/clink-backend
python check_email_config.py
```

**Expected Output:**
```
✅ SendGrid is configured - emails should work!
```

### Test 2: Create a New User and Check Tracking

```bash
# Option A: Via API (from your machine)
curl -X POST https://your-backend-url/api/auth/register/patient/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "phone_number": "+61412345678",
    "date_of_birth": "1990-01-01"
  }'

# Check the response - should include:
# "welcome_email_sent": true or false
# "welcome_email_sent_at": "2025-11-28T..."
```

### Test 3: Check Database Directly

```bash
# On server:
python manage.py shell
```

```python
from users.models import User

# Get latest user
user = User.objects.latest('date_joined')

# Check welcome email status
print(f"Email: {user.email}")
print(f"Welcome email sent: {user.welcome_email_sent}")
print(f"Sent at: {user.welcome_email_sent_at}")
print(f"Attempts: {user.welcome_email_attempts}")
print(f"Last error: {user.welcome_email_last_error}")
```

### Test 4: Check Server Logs

```bash
# Watch logs in real-time
sudo journalctl -u gunicorn -f

# Or check recent logs
sudo journalctl -u gunicorn -n 100

# Look for:
# "Attempting to send welcome email to..."
# "Welcome email sent successfully to..." 
# "Welcome email failed for..."
```

### Test 5: Check SendGrid Dashboard

1. Go to: https://app.sendgrid.com/
2. Click: Activity → Email Activity
3. Search for the test user's email
4. Check delivery status

---

## Verification Checklist

After deploying, verify:

- [ ] Code pulled from GitHub
- [ ] Database migration applied (new fields exist)
- [ ] Services restarted (gunicorn + celery)
- [ ] Email configuration still valid (`python check_email_config.py`)
- [ ] Created test user account
- [ ] API response includes `welcome_email_sent` and `welcome_email_sent_at`
- [ ] Welcome email arrived in inbox (or spam)
- [ ] Database shows `welcome_email_sent=True` for new user
- [ ] Server logs show "Welcome email sent successfully"
- [ ] SendGrid dashboard shows email delivered

---

## Troubleshooting

### Issue: Migration fails with drf_yasg error

**Solution:** Use manual SQL migration (see Option B above)

### Issue: welcome_email_sent is always False

**Check:**
1. SendGrid configuration: `python check_email_config.py`
2. Server logs: `sudo journalctl -u gunicorn -n 100 | grep welcome`
3. Database field `welcome_email_last_error` for error message

### Issue: Email sent but user doesn't receive it

**Check:**
1. Spam/Junk folder
2. SendGrid dashboard for delivery status
3. Domain verification in SendGrid
4. Email address is correct

### Issue: API doesn't show welcome_email_sent in response

**Check:**
1. Did you restart gunicorn? `sudo systemctl restart gunicorn`
2. Pull latest code? `git pull origin main`
3. Check API response structure

---

## Files Changed

### Modified Files:
1. `users/models.py` - Added 4 new fields to User model
2. `users/serializers.py` - Added tracking in registration (2 places)
3. `users/views.py` - Added tracking in admin user creation + API response

### New Files:
1. `users/migrations/0003_add_welcome_email_tracking.py` - Database migration
2. `WELCOME_EMAIL_TRACKING_COMMANDS.md` - This file
3. `WELCOME_EMAIL_FLOW_EXPLANATION.md` - Technical explanation

---

## Quick Commands Summary

```bash
# On production server:
cd /var/www/clink-backend
source venv/bin/activate
git pull origin main

# Apply migration (try Django first)
python manage.py migrate

# If that fails, use manual SQL (see Option B above)

# Restart services
sudo systemctl restart gunicorn
sudo systemctl restart celery

# Test
python check_email_config.py

# Watch logs
sudo journalctl -u gunicorn -f
```

---

## What the User Will See

### Before (Old Response):
```json
{
  "message": "Patient registered successfully",
  "user": { ... },
  "tokens": { ... }
}
```

### After (New Response):
```json
{
  "message": "Patient registered successfully",
  "user": { ... },
  "tokens": { ... },
  "welcome_email_sent": true,
  "welcome_email_sent_at": "2025-11-28T10:30:45.123456Z"
}
```

---

## Next Steps

1. **Deploy to production** (commands above)
2. **Test with a new registration**
3. **Check welcome email arrives**
4. **Verify database tracking works**
5. **Monitor logs for any errors**

---

**Ready to deploy!** 🚀


