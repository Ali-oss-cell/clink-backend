# Fix: 404 Error on Data Access Request Endpoint

## The Problem

You're getting `404 Not Found` for `/api/auth/data-access-request/` even though the URL is registered.

## The Solution

**You MUST restart your Django development server** for the new URL to be recognized.

---

## Steps to Fix

### 1. Stop the Current Django Server

In your terminal where Django is running:
- Press `Ctrl+C` to stop the server

### 2. Restart the Server

```bash
cd /home/ali/Desktop/projects/clink-backend
source venv/bin/activate  # If using virtual environment
python manage.py runserver
```

### 3. Verify the Endpoint

After restarting, test the endpoint:

```bash
# Test with curl (replace YOUR_TOKEN with actual token)
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

Or check in browser (if logged in):
```
http://127.0.0.1:8000/api/auth/data-access-request/
```

---

## Why This Happens

Django's development server loads URL patterns when it starts. When you add a new URL pattern, the server doesn't automatically reload it - you need to restart.

---

## After Restart

Once the server is restarted, the endpoint should work:
- ✅ `/api/auth/data-access-request/` - JSON format
- ✅ `/api/auth/data-access-request/?format=pdf` - PDF format  
- ✅ `/api/auth/data-access-request/?format=csv` - CSV format

---

## Still Getting 404?

If you still get 404 after restarting:

1. **Check the URL is registered:**
   ```bash
   python manage.py show_urls | grep data-access
   ```
   Should show: `/api/auth/data-access-request/`

2. **Check the view exists:**
   ```bash
   python manage.py shell -c "from users.views import DataAccessRequestView; print('OK')"
   ```

3. **Check for syntax errors:**
   ```bash
   python manage.py check
   ```

4. **Clear Python cache:**
   ```bash
   find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
   find . -name "*.pyc" -delete
   ```

---

## Quick Test

After restarting, you should see in Django logs when you access the endpoint:
```
INFO "GET /api/auth/data-access-request/ HTTP/1.1" 200 ...
```

Instead of:
```
WARNING "GET /api/auth/data-access-request/ HTTP/1.1" 404 ...
```

**Restart the server and try again!** 🚀

