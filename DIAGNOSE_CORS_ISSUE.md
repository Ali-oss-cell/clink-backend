# Diagnose CORS Issue - Step by Step

## 🔍 Step 1: Check Browser Network Tab

**This is the most important step!**

1. Open your browser on `https://tailoredpsychology.com.au`
2. Open DevTools (F12) → **Network** tab
3. **Clear the network log** (🚫 icon)
4. Try to join the video call
5. Find the request to `video-token/13/` (or whatever appointment ID)
6. **Click on it** and check:

### Check the Status Column:
- **`(blocked)` or `CORS`** → CORS headers missing
- **`Failed` or `ERR_`** → Network/SSL issue  
- **`0` or blank** → Request never sent
- **`401`** → Auth issue (token missing/invalid)
- **`404`** → Endpoint not found

### Check Request Headers:
- Should include: `Origin: https://tailoredpsychology.com.au`
- Should include: `Authorization: Bearer ...`

### Check Response Headers:
- **Do you see `access-control-allow-origin`?**
  - ✅ **YES** → CORS is working, issue is elsewhere
  - ❌ **NO** → CORS headers not being sent (Nginx issue)

### Check Response Body:
- What error message does it show?

**📸 Take a screenshot of the Network tab and share it!**

---

## 🔍 Step 2: Verify Nginx Config is Deployed

**On your Droplet, run:**

```bash
# Check if the new config is in place
grep -A 5 "Handle OPTIONS preflight" /etc/nginx/sites-available/psychology_clinic
```

**Expected output:**
```
        # Handle OPTIONS preflight requests
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' 'https://tailoredpsychology.com.au' always;
```

**If you see nothing**, the config hasn't been deployed yet.

---

## 🔍 Step 3: Test CORS Headers with curl

**On your Droplet or local machine:**

```bash
# Test OPTIONS preflight
curl -X OPTIONS https://api.tailoredpsychology.com.au/api/appointments/video-token/13/ \
  -H "Origin: https://tailoredpsychology.com.au" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: authorization,content-type" \
  -v 2>&1 | grep -i "access-control"
```

**Expected output:**
```
< access-control-allow-origin: https://tailoredpsychology.com.au
< access-control-allow-credentials: true
< access-control-allow-methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
```

**If you don't see these headers**, Nginx isn't adding them.

---

## 🔍 Step 4: Check Nginx Error Logs

**On your Droplet:**

```bash
# Check for errors
sudo tail -50 /var/log/nginx/error.log

# Check access log for the request
sudo tail -50 /var/log/nginx/psychology_clinic_api_access.log | grep video-token
```

Look for any errors related to CORS or the `if` statement.

---

## 🔍 Step 5: Verify Django CORS Settings

**On your Droplet:**

```bash
cd /var/www/clink-backend
source venv/bin/activate
python manage.py shell
```

Then in the shell:
```python
from django.conf import settings
print("CORS_ALLOWED_ORIGINS:", settings.CORS_ALLOWED_ORIGINS)
print("CORS_ALLOW_CREDENTIALS:", settings.CORS_ALLOW_CREDENTIALS)
```

**Expected output:**
```
CORS_ALLOWED_ORIGINS: ['https://tailoredpsychology.com.au', ...]
CORS_ALLOW_CREDENTIALS: True
```

---

## 🛠️ Quick Fix: Deploy Nginx Config (if not deployed)

**If Step 2 showed the config isn't deployed:**

```bash
cd /var/www/clink-backend
git pull origin main
sudo cp deployment/nginx.conf /etc/nginx/sites-available/psychology_clinic
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🛠️ Alternative: Let Django Handle CORS Completely

If Nginx is causing issues, we can remove CORS handling from Nginx and let Django do it all:

**Update Nginx config to remove CORS handling:**

```nginx
location / {
    proxy_pass http://unix:/var/www/clink-backend/gunicorn.sock;
    proxy_set_header Host $http_host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;
    proxy_set_header X-Forwarded-Host $server_name;
    proxy_redirect off;
    
    # WebSocket support
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    
    # Don't hide CORS headers - let Django handle it
}
```

Django's `django-cors-headers` middleware should handle CORS automatically if configured correctly.

---

## 📋 What to Share

Please share:

1. **Browser Network tab screenshot** (most important!)
   - Show the failed request
   - Show Request Headers
   - Show Response Headers
   - Show Response body

2. **Output of Step 2** (check if config is deployed)

3. **Output of Step 3** (curl test for CORS headers)

4. **Any errors from Step 4** (Nginx logs)

This will help identify exactly what's wrong!

