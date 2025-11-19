# Quick Fix: 404 Error on Data Access Endpoint

## The Problem

Django is returning 404 for `/api/auth/data-access-request/` even though it's registered.

## Root Cause

The Django server process was started **before** the URL was added, so it doesn't know about the new endpoint.

## Solution

### Step 1: Kill ALL Django Processes

```bash
# Kill all Django runserver processes
pkill -9 -f "manage.py runserver"

# Verify they're gone
ps aux | grep "manage.py runserver"
# Should show nothing
```

### Step 2: Restart Server

```bash
cd /home/ali/Desktop/projects/clink-backend
source venv/bin/activate
python manage.py runserver
```

### Step 3: Test

After restart, the endpoint should work:
- ✅ `/api/auth/data-access-request/` - JSON
- ✅ `/api/auth/data-access-request/?format=pdf` - PDF
- ✅ `/api/auth/data-access-request/?format=csv` - CSV

---

## Verification

The endpoint is correctly configured:
- ✅ URL registered: `/api/auth/data-access-request/`
- ✅ View exists: `DataAccessRequestView`
- ✅ Can be imported: Working
- ✅ URL reverse works: `/api/auth/data-access-request/`

**The only issue is the server needs to be restarted!**

---

## After Restart

Check Django logs - you should see:
```
INFO "GET /api/auth/data-access-request/ HTTP/1.1" 200 ...
```

Instead of:
```
WARNING "GET /api/auth/data-access-request/ HTTP/1.1" 404 ...
```

**Kill the server and restart it now!** 🚀

