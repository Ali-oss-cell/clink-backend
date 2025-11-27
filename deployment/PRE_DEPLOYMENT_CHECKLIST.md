# ✅ Pre-Deployment Checklist

## 📋 Before You Deploy - Complete This Checklist

### 1. **Code Preparation** ✅

- [ ] All code committed to git
- [ ] `requirements.txt` is up to date
- [ ] `psycopg2-binary` is uncommented in requirements.txt
- [ ] No hardcoded secrets in code
- [ ] `.env` file is ready (or `env_template.txt` exists)

### 2. **Environment Variables** ✅

Create `.env` file with:

- [ ] `DEBUG=False` (production mode)
- [ ] `SECRET_KEY` (strong, unique key)
- [ ] `ALLOWED_HOSTS` includes: `209.38.89.74,api.tailoredpsychology.com.au`
- [ ] `DATABASE_URL` for PostgreSQL (local or managed)
- [ ] `REDIS_URL=redis://localhost:6379/0`
- [ ] Twilio credentials (production keys)
- [ ] Stripe credentials (production keys)
- [ ] Email configuration (SendGrid or SMTP)

### 3. **Database Setup** ✅

**Option A: Local PostgreSQL (for testing)**
- [ ] PostgreSQL installed on Droplet
- [ ] Database created: `psychology_clinic`
- [ ] User created with password
- [ ] `DATABASE_URL` in `.env` points to local database

**Option B: Managed Database**
- [ ] DigitalOcean Managed PostgreSQL created
- [ ] Connection details saved
- [ ] `DATABASE_URL` in `.env` points to managed database

### 4. **Server Requirements** ✅

- [ ] Droplet created (2GB or 4GB recommended)
- [ ] SSH access working
- [ ] Domain DNS configured (if using domain)
- [ ] Firewall allows ports 22, 80, 443

### 5. **Configuration Files** ✅

- [ ] `deployment/gunicorn.service` exists
- [ ] `deployment/celery.service` exists
- [ ] `deployment/celery-beat.service` exists
- [ ] `deployment/nginx.conf` exists
- [ ] `deploy.sh` is executable

### 6. **Services You Need** ✅

All of these will be installed/configured by `deploy.sh`:

- [x] **Nginx** - Web server (handles HTTP/HTTPS)
- [x] **Gunicorn** - WSGI server (runs Django)
- [x] **PostgreSQL** - Database (local or managed)
- [x] **Redis** - Task queue for Celery
- [x] **Celery Worker** - Background tasks
- [x] **Celery Beat** - Scheduled tasks

**You need ALL of them!** They work together.

## 🚀 Deployment Steps

### Step 1: Upload Code to Droplet

```bash
# Option A: Clone from Git
cd /var/www
sudo git clone YOUR_REPO_URL clink-backend
cd clink-backend

# Option B: Upload via SCP
scp -r . user@209.38.89.74:/var/www/clink-backend
```

### Step 2: Run Deployment Script

```bash
cd /var/www/clink-backend
chmod +x deploy.sh
./deploy.sh
```

### Step 3: Configure Environment

```bash
# Edit .env file
sudo nano /var/www/clink-backend/.env

# Make sure to set:
# - DEBUG=False
# - SECRET_KEY (generate new one)
# - DATABASE_URL (local or managed)
# - ALLOWED_HOSTS (includes your IP)
# - All API keys
```

### Step 4: Setup Database (if local)

```bash
# Create database and user
sudo -u postgres psql

# In PostgreSQL:
CREATE DATABASE psychology_clinic;
CREATE USER psychology_clinic_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE psychology_clinic TO psychology_clinic_user;
\q

# Update .env with:
# DATABASE_URL=postgresql://psychology_clinic_user:your_password@localhost:5432/psychology_clinic
```

### Step 5: Run Migrations

```bash
cd /var/www/clink-backend
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

### Step 6: Create Superuser

```bash
sudo -u www-data /var/www/clink-backend/venv/bin/python \
  /var/www/clink-backend/manage.py createsuperuser
```

### Step 7: Restart Services

```bash
sudo systemctl restart gunicorn
sudo systemctl restart celery
sudo systemctl restart celery-beat
sudo systemctl restart nginx
```

## 🔍 Verification

### Check Services Status

```bash
sudo systemctl status gunicorn
sudo systemctl status celery
sudo systemctl status celery-beat
sudo systemctl status nginx
sudo systemctl status redis
sudo systemctl status postgresql
```

All should show "active (running)".

### Test API

```bash
# Test health endpoint
curl http://209.38.89.74/health/

# Test API endpoint
curl http://209.38.89.74/api/auth/login/
```

### Check Logs

```bash
# Gunicorn logs
sudo journalctl -u gunicorn -f

# Nginx logs
sudo tail -f /var/log/nginx/psychology_clinic_ip_error.log

# Celery logs
sudo tail -f /var/log/celery/worker.log
```

## ⚠️ Common Issues

### Issue 1: Gunicorn won't start
- Check: `sudo journalctl -u gunicorn -n 50`
- Fix: Verify `.env` file exists and has correct values
- Fix: Check file permissions: `sudo chown -R www-data:www-data /var/www/clink-backend`

### Issue 2: Database connection error
- Check: PostgreSQL is running: `sudo systemctl status postgresql`
- Check: `DATABASE_URL` in `.env` is correct
- Fix: Test connection: `psql -U username -d database_name -h localhost`

### Issue 3: 502 Bad Gateway
- Check: Gunicorn is running: `sudo systemctl status gunicorn`
- Check: Socket file exists: `ls -la /var/www/clink-backend/gunicorn.sock`
- Fix: Restart Gunicorn: `sudo systemctl restart gunicorn`

### Issue 4: Static files not loading
- Fix: Run: `python manage.py collectstatic --noinput`
- Check: Nginx can access static files: `ls -la /var/www/clink-backend/staticfiles/`

## 📝 Quick Reference

### Service Management

```bash
# Start services
sudo systemctl start gunicorn celery celery-beat nginx redis postgresql

# Stop services
sudo systemctl stop gunicorn celery celery-beat nginx

# Restart services
sudo systemctl restart gunicorn celery celery-beat nginx

# Check status
sudo systemctl status gunicorn
```

### Important Paths

- Application: `/var/www/clink-backend`
- Logs: `/var/log/nginx/`, `/var/log/celery/`
- Static files: `/var/www/clink-backend/staticfiles/`
- Media files: `/var/www/clink-backend/media/`
- Environment: `/var/www/clink-backend/.env`

## ✅ Ready to Deploy?

Once you've completed the checklist above, you're ready to deploy!

Run: `./deploy.sh` and follow the prompts.

