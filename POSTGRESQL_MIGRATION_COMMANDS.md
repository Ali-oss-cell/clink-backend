# 🐘 PostgreSQL Migration Commands

## For Production Server (PostgreSQL)

### Option 1: Use Django Migrate (Recommended)

```bash
# On production server:
cd /var/www/clink-backend
source venv/bin/activate
git pull origin main

# Run migration
python manage.py migrate
```

### Option 2: Manual SQL (If Django fails)

If `python manage.py migrate` fails, you can apply the migration manually:

```bash
# Connect to PostgreSQL
psql $DATABASE_URL

# Or if DATABASE_URL is not set:
psql -h localhost -U your_user -d your_database
```

Then run this SQL:

```sql
-- Add welcome email tracking fields
ALTER TABLE users_user ADD COLUMN welcome_email_sent BOOLEAN DEFAULT FALSE;
ALTER TABLE users_user ADD COLUMN welcome_email_sent_at TIMESTAMP NULL;
ALTER TABLE users_user ADD COLUMN welcome_email_attempts INTEGER DEFAULT 0;
ALTER TABLE users_user ADD COLUMN welcome_email_last_error TEXT NULL;

-- Mark migration as applied
INSERT INTO django_migrations (app, name, applied) 
VALUES ('users', '0010_add_welcome_email_tracking', NOW());

-- Exit
\q
```

### Option 3: Fix Migration Conflict First

If you see "Conflicting migrations detected", run:

```bash
# Merge migrations
python manage.py makemigrations --merge

# Then migrate
python manage.py migrate
```

---

## Verify Migration Applied

### Check in Django Shell

```bash
python manage.py shell
```

```python
from users.models import User
from django.db import connection

# Check if fields exist
cursor = connection.cursor()
cursor.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name='users_user' 
    AND column_name LIKE 'welcome_email%'
""")
columns = [row[0] for row in cursor.fetchall()]
print("Welcome email fields:", columns)

# Should show:
# ['welcome_email_sent', 'welcome_email_sent_at', 'welcome_email_attempts', 'welcome_email_last_error']
```

### Check in PostgreSQL Directly

```bash
psql $DATABASE_URL
```

```sql
-- Check columns
\d users_user

-- Or query columns
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'users_user' 
AND column_name LIKE 'welcome_email%';

-- Check migration was applied
SELECT * FROM django_migrations 
WHERE app = 'users' 
AND name = '0010_add_welcome_email_tracking';
```

---

## Complete Deployment Steps

```bash
# 1. Pull latest code
cd /var/www/clink-backend
git pull origin main

# 2. Activate venv
source venv/bin/activate

# 3. Try Django migrate first
python manage.py migrate

# 4. If conflict, merge
python manage.py makemigrations --merge
python manage.py migrate

# 5. If still fails, use manual SQL (see Option 2 above)

# 6. Restart services
sudo systemctl restart gunicorn
sudo systemctl restart celery

# 7. Verify
python manage.py shell
# Then run the verification code above
```

---

## Troubleshooting

### Issue: "Conflicting migrations detected"

**Solution:**
```bash
python manage.py makemigrations --merge
python manage.py migrate
```

### Issue: "Migration already applied"

**Check:**
```sql
SELECT * FROM django_migrations 
WHERE app = 'users' 
AND name LIKE '%welcome_email%';
```

If it exists, the migration is already applied!

### Issue: "Column already exists"

**Check:**
```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'users_user' 
AND column_name = 'welcome_email_sent';
```

If it returns a row, the field already exists. You can skip the migration.

---

## Quick PostgreSQL Commands

```bash
# Connect to database
psql $DATABASE_URL

# List all tables
\dt

# Describe users_user table
\d users_user

# Check migrations
SELECT app, name, applied FROM django_migrations WHERE app = 'users' ORDER BY applied DESC LIMIT 10;

# Exit
\q
```

---

**Ready to deploy!** 🚀


