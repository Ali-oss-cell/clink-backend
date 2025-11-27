# Deploy CORS Fix V2 - Step by Step

## ⚠️ Important: Test Before Reloading

The Nginx config uses an `if` statement which can be tricky. We need to test it first!

## Step-by-Step Deployment

### 1. Pull Latest Code

```bash
cd /var/www/clink-backend
git pull origin main
```

### 2. Test Nginx Configuration

**CRITICAL**: Test the config before reloading to catch any syntax errors:

```bash
sudo nginx -t
```

**Expected output:**
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

**If you see errors**, DO NOT reload. Share the error message.

### 3. Backup Current Config (Safety First)

```bash
sudo cp /etc/nginx/sites-available/psychology_clinic /etc/nginx/sites-available/psychology_clinic.backup
```

### 4. Update Nginx Config

```bash
sudo cp /var/www/clink-backend/deployment/nginx.conf /etc/nginx/sites-available/psychology_clinic
```

### 5. Test Again

```bash
sudo nginx -t
```

**Must pass before continuing!**

### 6. Reload Nginx

```bash
sudo systemctl reload nginx
```

### 7. Check Status

```bash
sudo systemctl status nginx
```

Should show: `Active: active (running)`

## Test CORS Headers

### Test 1: OPTIONS Preflight

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
```

### Test 2: Actual Request (with auth)

```bash
# First, get a token (login)
TOKEN=$(curl -s -X POST https://api.tailoredpsychology.com.au/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test.patient@clinic.test","password":"test123"}' | jq -r '.access')

# Then test the endpoint
curl -X GET https://api.tailoredpsychology.com.au/api/appointments/video-token/13/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Origin: https://tailoredpsychology.com.au" \
  -v 2>&1 | grep -i "access-control"
```

**Expected output:**
```
< access-control-allow-origin: https://tailoredpsychology.com.au
< access-control-allow-credentials: true
```

## If Nginx Test Fails

### Error: "unknown directive 'if'"

This shouldn't happen - `if` is a standard Nginx directive. But if it does:

```bash
# Check Nginx version
nginx -v

# Should be 1.18+ (Ubuntu 24.04 has 1.24)
```

### Error: "unexpected '}'"

Check for syntax errors:

```bash
# View the config
sudo nano /etc/nginx/sites-available/psychology_clinic

# Look for the location / block around line 134
# Make sure all { } are balanced
```

### Error: "test failed" but no specific error

Check Nginx error log:

```bash
sudo tail -20 /var/log/nginx/error.log
```

## If CORS Still Doesn't Work

### Check 1: Verify Headers Are Being Sent

```bash
curl -I https://api.tailoredpsychology.com.au/api/appointments/video-token/13/ \
  -H "Origin: https://tailoredpsychology.com.au" \
  -H "Authorization: Bearer YOUR_TOKEN" 2>&1 | grep -i "access-control"
```

If you don't see `access-control-allow-origin`, the headers aren't being added.

### Check 2: Browser Network Tab

1. Open DevTools (F12) → Network tab
2. Try to join video call
3. Find request to `video-token/13/`
4. Click it → Headers tab
5. Check **Response Headers**:
   - Should see `access-control-allow-origin: https://tailoredpsychology.com.au`
   - Should see `access-control-allow-credentials: true`

### Check 3: Nginx Logs

```bash
# Check access log
sudo tail -f /var/log/nginx/psychology_clinic_api_access.log

# Check error log
sudo tail -f /var/log/nginx/psychology_clinic_api_error.log
```

## Quick Deploy Script

Copy and paste this entire block:

```bash
cd /var/www/clink-backend && \
git pull origin main && \
sudo cp /etc/nginx/sites-available/psychology_clinic /etc/nginx/sites-available/psychology_clinic.backup && \
sudo cp deployment/nginx.conf /etc/nginx/sites-available/psychology_clinic && \
sudo nginx -t && \
sudo systemctl reload nginx && \
echo "✅ CORS fix deployed! Test with:" && \
echo "curl -X OPTIONS https://api.tailoredpsychology.com.au/api/appointments/video-token/13/ -H 'Origin: https://tailoredpsychology.com.au' -v"
```

## What Changed

### Before:
- Nginx was passing requests to Django
- Django added CORS headers
- **Nginx might have been stripping them** ❌

### After:
- Nginx handles OPTIONS preflight directly
- Nginx adds CORS headers to all responses
- Django also adds CORS headers (backup)
- **Browser receives CORS headers** ✅

## Still Not Working?

If after deploying you still get CORS errors:

1. **Share the output of:**
   ```bash
   sudo nginx -t
   curl -X OPTIONS https://api.tailoredpsychology.com.au/api/appointments/video-token/13/ \
     -H "Origin: https://tailoredpsychology.com.au" -v
   ```

2. **Check browser Network tab:**
   - Screenshot of the failed request
   - Status code
   - Response headers

3. **Clear browser cache:**
   - Hard refresh: `Ctrl+Shift+R`
   - Or: DevTools → Application → Clear storage

The fix is deployed - we just need to make sure it's active on your Droplet!

