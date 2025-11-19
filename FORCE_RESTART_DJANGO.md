# Force Restart Django Server - Fix 404 Error

## The Problem

You're getting 404 even though the endpoint is registered. This usually means:
1. Multiple Django processes running
2. Server didn't restart properly
3. Old process still running

## Solution: Force Kill and Restart

### Step 1: Kill ALL Django Processes

```bash
# Find all Django processes
ps aux | grep "manage.py runserver"

# Kill all of them
pkill -9 -f "manage.py runserver"
pkill -9 -f "python.*runserver"

# Verify they're gone
ps aux | grep "manage.py runserver"
# Should show nothing
```

### Step 2: Clear Python Cache

```bash
cd /home/ali/Desktop/projects/clink-backend

# Remove all __pycache__ directories
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null

# Remove all .pyc files
find . -name "*.pyc" -delete

# Remove .pyo files
find . -name "*.pyo" -delete
```

### Step 3: Restart Server

```bash
cd /home/ali/Desktop/projects/clink-backend
source venv/bin/activate
python manage.py runserver
```

### Step 4: Test Endpoint

```bash
# Test with curl (replace YOUR_TOKEN)
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -v
```

You should see:
- `HTTP/1.1 200 OK` (if authenticated as patient)
- `HTTP/1.1 401 Unauthorized` (if token invalid)
- `HTTP/1.1 403 Forbidden` (if not a patient)

**NOT** `HTTP/1.1 404 Not Found`

---

## Quick One-Liner

```bash
pkill -9 -f "manage.py runserver" && \
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null && \
find . -name "*.pyc" -delete && \
python manage.py runserver
```

---

## After Restart

The endpoint should work:
- ✅ `/api/auth/data-access-request/` - JSON
- ✅ `/api/auth/data-access-request/?format=pdf` - PDF
- ✅ `/api/auth/data-access-request/?format=csv` - CSV

