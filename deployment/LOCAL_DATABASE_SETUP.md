# 🗄️ Local PostgreSQL Database Setup for Testing

## Overview

Instead of using DigitalOcean Managed Database, you can install PostgreSQL directly on your Droplet for testing. This is cheaper and good for development/testing.

## Installation Steps

### 1. Install PostgreSQL on Droplet

```bash
# Update system
sudo apt update

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Check version
psql --version
```

### 2. Create Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt, run:
CREATE DATABASE psychology_clinic;
CREATE USER psychology_clinic_user WITH PASSWORD 'your_secure_password_here';
ALTER ROLE psychology_clinic_user SET client_encoding TO 'utf8';
ALTER ROLE psychology_clinic_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE psychology_clinic_user SET timezone TO 'Australia/Sydney';
GRANT ALL PRIVILEGES ON DATABASE psychology_clinic TO psychology_clinic_user;
\q
```

### 3. Configure PostgreSQL for Remote Access (Optional)

If you want to connect from your local machine:

```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/14/main/postgresql.conf

# Find and uncomment:
listen_addresses = 'localhost'

# Edit pg_hba.conf
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Add line:
host    psychology_clinic    psychology_clinic_user    127.0.0.1/32    md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 4. Update .env File

In your `.env` file on the Droplet:

```bash
# Local PostgreSQL Database
DATABASE_URL=postgresql://psychology_clinic_user:your_secure_password_here@localhost:5432/psychology_clinic
```

### 5. Test Connection

```bash
# Test from command line
psql -U psychology_clinic_user -d psychology_clinic -h localhost

# If it works, you'll see:
# psychology_clinic=>
```

## Database URL Format

```
postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME
```

For local database:
```
postgresql://psychology_clinic_user:password@localhost:5432/psychology_clinic
```

## Advantages of Local Database

✅ **Free** - No additional cost
✅ **Fast** - No network latency
✅ **Simple** - Everything on one server
✅ **Good for testing** - Easy to reset/backup

## Disadvantages

❌ **Single point of failure** - If Droplet goes down, database is down
❌ **No automatic backups** - You need to set up backups manually
❌ **Limited resources** - Shares Droplet resources with app
❌ **Not ideal for production** - Managed database is better for production

## Backup Local Database

```bash
# Create backup
sudo -u postgres pg_dump psychology_clinic > /backup/psychology_clinic_$(date +%Y%m%d).sql

# Restore backup
sudo -u postgres psql psychology_clinic < /backup/psychology_clinic_20250123.sql
```

## Migration from SQLite to PostgreSQL

If you're currently using SQLite:

```bash
# 1. Update .env with PostgreSQL DATABASE_URL
# 2. Install psycopg2
pip install psycopg2-binary

# 3. Run migrations
python manage.py migrate

# 4. (Optional) Migrate data from SQLite
python manage.py dumpdata > data.json
# Change DATABASE_URL to PostgreSQL
python manage.py loaddata data.json
```

## Recommended for Testing

✅ **Use local PostgreSQL for:**
- Development
- Testing
- Staging environments
- Learning

❌ **Use Managed Database for:**
- Production
- High availability needs
- Automatic backups
- Scaling requirements

