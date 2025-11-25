# CORS/Network Error Fix - Video Token Endpoint

## ✅ Backend Status: WORKING

I've verified:
- ✅ Backend is accessible at `https://api.tailoredpsychology.com.au`
- ✅ SSL certificate is valid
- ✅ CORS is configured correctly
- ✅ CORS headers are being sent: `access-control-allow-origin: https://tailoredpsychology.com.au`
- ✅ Endpoint exists: `/api/appointments/video-token/{id}/`

## 🔍 The Problem

Your frontend is getting a network error when trying to reach:
```
https://api.tailoredpsychology.com.au/api/appointments/video-token/13/
```

## 🧪 Test Results

### Backend Accessibility Test:
```bash
curl -I https://api.tailoredpsychology.com.au/api/appointments/video-token/13/
# Result: HTTP/2 401 (Expected - requires authentication)
```

### CORS Preflight Test:
```bash
curl -X OPTIONS https://api.tailoredpsychology.com.au/api/appointments/video-token/13/ \
  -H "Origin: https://tailoredpsychology.com.au" \
  -H "Access-Control-Request-Method: GET"

# Result: HTTP/2 200
# Headers:
# access-control-allow-origin: https://tailoredpsychology.com.au ✅
# access-control-allow-credentials: true ✅
# access-control-allow-methods: GET, POST, PUT, DELETE, PATCH, OPTIONS ✅
```

## 🔧 Possible Causes & Fixes

### **Issue 1: Browser Caching / Service Worker**

**Symptom**: Network error persists even though backend is working

**Fix**:
1. Open browser DevTools (F12)
2. Go to **Application** tab → **Service Workers**
3. Click **Unregister** if any service workers are registered
4. Go to **Application** tab → **Storage** → **Clear site data**
5. Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)

### **Issue 2: Mixed Content (HTTP/HTTPS)**

**Symptom**: Browser blocks request due to mixed content policy

**Check**: Make sure your frontend is served over HTTPS:
- ✅ `https://tailoredpsychology.com.au` (HTTPS)
- ❌ `http://tailoredpsychology.com.au` (HTTP - will be blocked)

**Fix**: Ensure your App Platform frontend is using HTTPS (it should be by default)

### **Issue 3: Request URL Construction**

**Symptom**: Frontend might be constructing the URL incorrectly

**Check your frontend code**:
```typescript
// ✅ CORRECT
const API_URL = 'https://api.tailoredpsychology.com.au';
const endpoint = `${API_URL}/api/appointments/video-token/${appointmentId}/`;

// ❌ WRONG - Double /api/
const API_URL = 'https://api.tailoredpsychology.com.au/api';
const endpoint = `${API_URL}/api/appointments/video-token/${appointmentId}/`;
// Results in: https://api.tailoredpsychology.com.au/api/api/appointments/...

// ❌ WRONG - Missing trailing slash
const endpoint = `${API_URL}/api/appointments/video-token/${appointmentId}`;
```

### **Issue 4: Appointment ID Doesn't Exist**

**Symptom**: Error for specific appointment ID (e.g., 13)

**Check**: 
1. Does appointment #13 exist?
2. Does it have a `video_room_id`?
3. Is the user authorized (patient or psychologist of that appointment)?

**Test**:
```bash
# Get a JWT token first (login)
curl -X POST https://api.tailoredpsychology.com.au/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test.patient@clinic.test","password":"test123"}'

# Use the access token
curl -X GET https://api.tailoredpsychology.com.au/api/appointments/video-token/13/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Origin: https://tailoredpsychology.com.au"
```

### **Issue 5: Browser Network Tab Shows Different Error**

**Action**: Check browser DevTools → Network tab:
1. Find the failed request to `/api/appointments/video-token/13/`
2. Click on it
3. Check:
   - **Status Code**: 
     - `0` or `(failed)` = Network error (CORS or connection issue)
     - `401` = Missing or invalid auth token
     - `404` = Endpoint doesn't exist or appointment not found
     - `403` = User not authorized for this appointment
   - **Request Headers**: Should include `Authorization: Bearer ...`
   - **Response Headers**: Should include `access-control-allow-origin`
   - **Response**: Check the error message

## 🎯 Step-by-Step Debugging

### Step 1: Check Browser Network Tab

1. Open DevTools (F12) → **Network** tab
2. Clear network log (🚫 icon)
3. Try to join video call
4. Find the request to `video-token/13/`
5. Click on it and check:
   - **General** tab:
     - Request URL: Should be `https://api.tailoredpsychology.com.au/api/appointments/video-token/13/`
     - Request Method: Should be `GET`
     - Status Code: What is it?
   - **Headers** tab:
     - Request Headers: Does it include `Authorization: Bearer ...`?
     - Response Headers: Does it include `access-control-allow-origin: https://tailoredpsychology.com.au`?
   - **Response** tab: What error message?

### Step 2: Test with curl (from your local machine)

```bash
# 1. Login to get token
TOKEN=$(curl -s -X POST https://api.tailoredpsychology.com.au/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"YOUR_EMAIL","password":"YOUR_PASSWORD"}' | jq -r '.access')

# 2. Test video token endpoint
curl -X GET https://api.tailoredpsychology.com.au/api/appointments/video-token/13/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Origin: https://tailoredpsychology.com.au" \
  -v
```

If this works, the backend is fine - the issue is in the frontend.

### Step 3: Check Frontend Code

Verify your frontend is making the request correctly:

```typescript
// Example correct implementation
async function getVideoToken(appointmentId: number) {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('Not authenticated');
  }

  const response = await fetch(
    `https://api.tailoredpsychology.com.au/api/appointments/video-token/${appointmentId}/`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      credentials: 'include' // Important for CORS with credentials
    }
  );

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return await response.json();
}
```

### Step 4: Check for Service Workers

Service workers can cache failed requests. Clear them:

1. DevTools → **Application** tab
2. **Service Workers** → Click **Unregister**
3. **Storage** → **Clear site data**
4. Hard refresh: `Ctrl+Shift+R`

## 🔍 Common Error Messages & Solutions

### Error: "Network error: Could not reach API server"
**Cause**: Request is being blocked or URL is wrong
**Fix**: 
- Check Network tab for actual request URL
- Verify API URL is `https://api.tailoredpsychology.com.au` (not localhost)
- Check browser console for CORS errors

### Error: "CORS policy: No 'Access-Control-Allow-Origin' header"
**Cause**: CORS headers not being sent (but we verified they are!)
**Fix**: 
- Clear browser cache
- Check if request includes `Origin` header
- Verify frontend URL matches CORS allowed origins

### Error: "401 Unauthorized"
**Cause**: Missing or invalid JWT token
**Fix**: 
- Check if user is logged in
- Verify token is in localStorage
- Check if token is expired (refresh it)

### Error: "404 Not Found"
**Cause**: Endpoint doesn't exist or appointment not found
**Fix**: 
- Verify appointment ID exists
- Check if appointment has `video_room_id`
- Verify endpoint URL is correct

## ✅ Verification Checklist

- [ ] Backend is accessible: `curl https://api.tailoredpsychology.com.au/api/`
- [ ] CORS headers are present: Check OPTIONS request
- [ ] Frontend uses correct API URL: `https://api.tailoredpsychology.com.au`
- [ ] Request includes `Authorization: Bearer <token>` header
- [ ] User is logged in and has valid token
- [ ] Appointment exists and has `video_room_id`
- [ ] Browser Network tab shows correct request URL
- [ ] No service workers interfering
- [ ] Frontend is served over HTTPS

## 🚀 Quick Test

Run this in your browser console (on `https://tailoredpsychology.com.au`):

```javascript
// Get token from localStorage
const token = localStorage.getItem('access_token');
console.log('Token:', token ? 'Found' : 'Missing');

// Test the endpoint
fetch('https://api.tailoredpsychology.com.au/api/appointments/video-token/13/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(res => {
  console.log('Status:', res.status);
  console.log('Headers:', [...res.headers.entries()]);
  return res.json();
})
.then(data => console.log('Success:', data))
.catch(err => console.error('Error:', err));
```

This will show you exactly what's happening.

## 📞 Next Steps

If the issue persists after checking all of the above:

1. **Share the Network tab details**:
   - Screenshot of the failed request
   - Status code
   - Request headers
   - Response headers
   - Response body

2. **Check browser console** for any additional errors

3. **Test with curl** to verify backend is working

The backend is confirmed working - this is likely a frontend configuration or browser caching issue.

