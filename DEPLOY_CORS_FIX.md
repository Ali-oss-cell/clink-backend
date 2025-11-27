# Deploy CORS Fix to Droplet

## What was the problem?

**Nginx was not passing CORS headers from Django to the browser.**

When your frontend (at `https://tailoredpsychology.com.au`) tries to call the API (at `https://api.tailoredpsychology.com.au`), the browser needs to see CORS headers that allow the cross-origin request.

Django was sending these headers, but **Nginx was blocking/stripping them** before they reached the browser, causing the "Network error: Could not reach API server" error.

## What was fixed?

Updated `deployment/nginx.conf` to:
1. **Handle OPTIONS preflight requests** - Nginx now responds directly to CORS preflight checks
2. **Add CORS headers** to all API responses
3. **Pass Origin header** from browser to Django
4. **Allow credentials** for authenticated requests

## Deploy to Droplet

Run these commands on your Droplet:

```bash
# 1. Pull the latest code
cd /var/www/clink-backend
git pull origin main

# 2. Update Nginx configuration
sudo cp deployment/nginx.conf /etc/nginx/sites-available/psychology_clinic

# 3. Test Nginx configuration (should say "syntax is ok")
sudo nginx -t

# 4. Reload Nginx to apply changes
sudo systemctl reload nginx

# 5. Check Nginx status (should be "active (running)")
sudo systemctl status nginx
```

## Verify the fix

### Test 1: Check CORS headers with curl

```bash
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
< access-control-allow-headers: Accept,Authorization,Cache-Control,Content-Type...
```

### Test 2: Try the video call in the frontend

1. Go to `https://tailoredpsychology.com.au`
2. Login as a patient or psychologist
3. Try to join a video call
4. **It should work now!** ✅

### Test 3: Check browser Network tab

1. Open DevTools (F12) → Network tab
2. Try to join video call
3. Find the request to `video-token/13/`
4. Click on it → **Headers** tab
5. **Response Headers** should include:
   ```
   access-control-allow-origin: https://tailoredpsychology.com.au
   access-control-allow-credentials: true
   ```

## What if it still doesn't work?

### Issue: "nginx: configuration file test failed"

**Symptom:**
```
nginx: [emerg] unexpected "}" in /etc/nginx/sites-available/psychology_clinic:XX
nginx: configuration file /etc/nginx/nginx.conf test failed
```

**Fix:**
```bash
# Check the exact error line
sudo nginx -t

# View the problematic section
sudo nano /etc/nginx/sites-available/psychology_clinic

# Make sure all { } are balanced
# Re-copy from deployment/nginx.conf if needed
```

### Issue: Still getting CORS error

**1. Clear browser cache:**
```
Ctrl+Shift+R (hard refresh)
Or: DevTools → Application → Clear storage
```

**2. Check Nginx logs:**
```bash
sudo tail -f /var/log/nginx/psychology_clinic_api_error.log
```

**3. Verify Nginx reloaded:**
```bash
sudo systemctl status nginx
# Should show: "Active: active (running)"
# Should show recent "Reloaded" timestamp
```

**4. Restart Nginx (if reload didn't work):**
```bash
sudo systemctl restart nginx
```

## Summary of changes

### Before (not working):
- Nginx passed requests to Django
- Django added CORS headers
- **Nginx didn't pass CORS headers to browser** ❌
- Browser blocked the request

### After (working):
- Nginx handles OPTIONS preflight directly
- Nginx adds CORS headers to all responses
- **Browser receives CORS headers** ✅
- Frontend can access the API

## Complete deployment command

Copy and paste this entire block:

```bash
cd /var/www/clink-backend && \
git pull origin main && \
sudo cp deployment/nginx.conf /etc/nginx/sites-available/psychology_clinic && \
sudo nginx -t && \
sudo systemctl reload nginx && \
echo "✅ CORS fix deployed successfully!"
```

Then test the video call in your frontend!

