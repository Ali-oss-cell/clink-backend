# 🔧 Celery Troubleshooting Guide

## Current Status

✅ **Gunicorn**: Working fine (3 workers started)  
❌ **Celery**: Failed to start

---

## Quick Diagnosis

### 1. Check Celery Status

```bash
sudo systemctl status celery
```

### 2. Check Celery Logs

```bash
# Recent logs
sudo journalctl -u celery -n 50

# Full logs
sudo journalctl -u celery --no-pager
```

### 3. Check Celery Service File

```bash
# View service configuration
cat /etc/systemd/system/celery.service
```

---

## Common Issues & Fixes

### Issue 1: Redis Connection Problem

**Check:**
```bash
redis-cli ping
# Should return: PONG
```

**Fix if not running:**
```bash
sudo systemctl start redis
sudo systemctl enable redis
```

### Issue 2: Wrong Working Directory

**Check service file:**
```bash
cat /etc/systemd/system/celery.service | grep WorkingDirectory
```

**Should be:**
```
WorkingDirectory=/var/www/clink-backend
```

### Issue 3: Wrong Python/Virtual Environment

**Check service file:**
```bash
cat /etc/systemd/system/celery.service | grep ExecStart
```

**Should use venv:**
```
ExecStart=/var/www/clink-backend/venv/bin/celery -A psychology_clinic worker --loglevel=info
```

### Issue 4: Missing Environment Variables

**Check if .env is loaded:**
```bash
cat /etc/systemd/system/celery.service | grep EnvironmentFile
```

**Should have:**
```
EnvironmentFile=/var/www/clink-backend/.env
```

---

## Fix Celery Service

### Option 1: Check Current Service File

```bash
cat /etc/systemd/system/celery.service
```

### Option 2: Create/Update Service File

```bash
sudo nano /etc/systemd/system/celery.service
```

**Correct service file should look like:**

```ini
[Unit]
Description=Celery Service
After=network.target redis.service

[Service]
Type=forking
User=root
Group=root
EnvironmentFile=/var/www/clink-backend/.env
WorkingDirectory=/var/www/clink-backend
ExecStart=/var/www/clink-backend/venv/bin/celery -A psychology_clinic worker --loglevel=info --logfile=/var/log/celery/worker.log --pidfile=/var/run/celery/worker.pid
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

**Then:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Start Celery
sudo systemctl start celery

# Enable on boot
sudo systemctl enable celery

# Check status
sudo systemctl status celery
```

---

## Test Celery Manually

```bash
cd /var/www/clink-backend
source venv/bin/activate

# Test if Celery can start
celery -A psychology_clinic worker --loglevel=info
```

**If this works**, the issue is with the systemd service file.  
**If this fails**, check the error message for the real problem.

---

## Quick Fix Commands

```bash
# 1. Check Redis
redis-cli ping

# 2. Check Celery logs
sudo journalctl -u celery -n 50

# 3. Test Celery manually
cd /var/www/clink-backend
source venv/bin/activate
celery -A psychology_clinic worker --loglevel=info

# 4. If manual test works, fix service file (see above)

# 5. Reload and restart
sudo systemctl daemon-reload
sudo systemctl restart celery
sudo systemctl status celery
```

---

## What the Warnings Mean

The `pkg_resources is deprecated` warnings are **NOT errors** - just deprecation warnings from `rest_framework_simplejwt`. They won't break anything, but you can ignore them for now.

---

**Run the diagnosis commands above to find the exact issue!** 🔍


