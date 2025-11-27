# 🚀 Quick Deployment Guide - Step by Step

## How Everything Works Together

```
User Request
    ↓
[Nginx] → Receives request on port 80
    ↓
[Gunicorn] → Runs Django via WSGI
    ↓
[Django] → Your application code
    ↓
[PostgreSQL] → Database
```

**You need ALL services:**
- ✅ Nginx (web server)
- ✅ Gunicorn (runs Django)
- ✅ PostgreSQL (database)
- ✅ Redis (for Celery)
- ✅ Celery Worker (background tasks)
- ✅ Celery Beat (scheduled tasks)

## Local Database Setup (For Testing)

### Step 1: Install PostgreSQL

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib -y
```

### Step 2: Create Database

```bash
sudo -u postgres psql

# Run these commands:
CREATE DATABASE psychology_clinic;
CREATE USER psychology_clinic_user WITH PASSWORD 'your_secure_password';
ALTER ROLE psychology_clinic_user SET client_encoding TO 'utf8';
ALTER ROLE psychology_clinic_user SET timezone TO 'Australia/Sydney';
GRANT ALL PRIVILEGES ON DATABASE psychology_clinic TO psychology_clinic_user;
\q
```

### Step 3: Update .env File

```bash
# In your .env file:
DATABASE_URL=postgresql://psychology_clinic_user:your_secure_password@localhost:5432/psychology_clinic
```

## Complete Deployment Process

### 1. Upload Code to Droplet

```bash
# SSH into your Droplet
ssh user@209.38.89.74

# Clone or upload your code
cd /var/www
sudo git clone YOUR_REPO_URL clink-backend
# OR upload via SCP from your local machine
```

### 2. Run Deployment Script

```bash
cd /var/www/clink-backend
chmod +x deploy.sh
./deploy.sh
```

The script will:
- Install all dependencies
- Setup PostgreSQL (if local)
- Configure Nginx
- Setup Gunicorn
- Setup Celery
- Configure services

### 3. Configure Environment

```bash
# Edit .env file
sudo nano /var/www/clink-backend/.env

# Set these values:
DEBUG=False
SECRET_KEY=your-strong-secret-key-here
ALLOWED_HOSTS=209.38.89.74,api.tailoredpsychology.com.au
DATABASE_URL=postgresql://psychology_clinic_user:password@localhost:5432/psychology_clinic
REDIS_URL=redis://localhost:6379/0
# ... add all other API keys
```

### 4. Setup Local Database (if using local)

```bash
# Create database (if not done by deploy script)
sudo -u postgres psql
CREATE DATABASE psychology_clinic;
CREATE USER psychology_clinic_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE psychology_clinic TO psychology_clinic_user;
\q
```

### 5. Run Migrations

```bash
cd /var/www/clink-backend
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

### 6. Create Superuser

```bash
sudo -u www-data /var/www/clink-backend/venv/bin/python \
  /var/www/clink-backend/manage.py createsuperuser
```

### 7. Restart All Services

```bash
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celery-beat
sudo systemctl restart nginx
```

### 8. Test Everything

```bash
# Test health endpoint
curl http://209.38.89.74/health/

# Test API
curl http://209.38.89.74/api/auth/login/

# Check services
sudo systemctl status gunicorn celery celery-beat nginx redis postgresql
```

## What Each Service Does

| Service | Purpose | Required? |
|---------|---------|-----------|
| **Nginx** | Web server, handles HTTP/HTTPS, serves static files | ✅ Yes |
| **Gunicorn** | Runs Django application via WSGI | ✅ Yes |
| **PostgreSQL** | Database for storing data | ✅ Yes |
| **Redis** | Message broker for Celery | ✅ Yes |
| **Celery Worker** | Processes background tasks | ✅ Yes |
| **Celery Beat** | Schedules periodic tasks | ✅ Yes |

## Configuration Files

- `nginx.conf` → Tells Nginx how to handle requests
- `gunicorn.service` → Systemd service for Gunicorn
- `celery.service` → Systemd service for Celery Worker
- `celery-beat.service` → Systemd service for Celery Beat
- `.env` → Environment variables (secrets, config)

## Summary

**Before deploying:**
1. ✅ Code ready
2. ✅ `.env` file configured
3. ✅ Database setup (local or managed)
4. ✅ All API keys ready

**Deploy:**
1. Upload code
2. Run `./deploy.sh`
3. Configure `.env`
4. Run migrations
5. Create superuser
6. Test!

**All services work together** - you can't skip any of them!

