# Frontend 404 Fix - Data Access Endpoint

## Problem

Frontend is getting `404 Not Found` errors when accessing `/api/auth/data-access-request/`, but **the backend endpoint works perfectly** when tested with curl.

## Backend Status: ✅ WORKING

### Confirmed Working

```bash
# 1. URL is registered
/api/auth/data-access-request/  ✅ (with trailing slash)
/api/auth/data-access-request   ✅ (without trailing slash)

# 2. Server is running
python manage.py runserver      ✅ (PID: 66658)

# 3. Endpoint responds correctly
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/" \
  -H "Authorization: Bearer TOKEN"
# Returns: 200 OK with full data ✅
```

---

## Root Cause: Frontend Configuration Issue

The backend is working. The problem is in the frontend's API call configuration.

### Common Frontend Issues

1. **Wrong Base URL**
   ```typescript
   // ❌ Wrong
   const baseURL = 'http://127.0.0.1:8000/api/'
   
   // ✅ Correct
   const baseURL = 'http://127.0.0.1:8000/api/auth'
   ```

2. **Double Slashes**
   ```typescript
   // ❌ Creates: /api/auth//data-access-request/
   axios.get('/data-access-request/')
   
   // ✅ Creates: /api/auth/data-access-request/
   axios.get('data-access-request/')
   ```

3. **Missing Authorization Header**
   ```typescript
   // ❌ No token
   axios.get('data-access-request/')
   
   // ✅ With token
   axios.get('data-access-request/', {
     headers: { Authorization: `Bearer ${token}` }
   })
   ```

4. **CORS Issues** (would show CORS error, not 404)

---

## Fix Your Frontend

### Step 1: Check Your Auth Service

In `src/services/api/auth.ts` (or similar):

```typescript
// Check the baseURL
const API_BASE_URL = 'http://127.0.0.1:8000/api/auth';

// Check the endpoint path
async requestDataAccess(format: string = 'json') {
  // Should be one of these:
  const response = await axios.get('data-access-request/', {  // ✅ No leading slash
    params: { format },
    headers: { Authorization: `Bearer ${token}` }
  });
  
  // OR
  const response = await axios.get('/data-access-request/', {  // ✅ With leading slash
    params: { format },
    headers: { Authorization: `Bearer ${token}` }
  });
}
```

### Step 2: Check Your Axios Instance

```typescript
// In axiosInstance.ts or similar
const axiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/auth',  // Correct base
  timeout: 10000,
});

// Add interceptor to include token
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Step 3: Test in Browser Console

Open browser console and run:

```javascript
// Get your token from localStorage
const token = localStorage.getItem('access_token');
console.log('Token:', token);

// Test the endpoint
fetch('http://127.0.0.1:8000/api/auth/data-access-request/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(r => r.json())
.then(d => console.log('Success:', d))
.catch(e => console.error('Error:', e));
```

If this works in the console but not in your app, the issue is in your frontend code configuration.

---

## Testing Guide

### Test Account
- **Email:** `testpatient@example.com`
- **Password:** `testpass123`

### Manual Backend Test

```bash
# 1. Login
curl -X POST "http://127.0.0.1:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email": "testpatient@example.com", "password": "testpass123"}'

# Copy the access token from response

# 2. Test JSON format
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Test PDF format
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/?format=pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o test-data.pdf

# 4. Test CSV format
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/?format=csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o test-data.csv
```

---

## Common URL Path Issues

### Check What URL is Actually Being Called

In your browser's Network tab:
1. Try to download the data
2. Check the **failed request** in Network tab
3. Look at the **Request URL**

Common problems:
- `http://127.0.0.1:8000/api/auth//data-access-request/` (double slash) ❌
- `http://127.0.0.1:8000/api/data-access-request/` (missing /auth/) ❌
- `http://127.0.0.1:8000/data-access-request/` (missing /api/auth/) ❌
- `http://127.0.0.1:8000/api/auth/data-access-request/` (correct) ✅

---

## Debug Checklist

- [ ] Backend server is running (`python manage.py runserver`)
- [ ] Test endpoint with curl - should return 200 OK
- [ ] Check browser Network tab for actual URL being called
- [ ] Verify Authorization header is being sent
- [ ] Check token is valid (not expired)
- [ ] Verify baseURL in frontend axios config
- [ ] Check for double slashes in URL path
- [ ] Test in browser console with fetch()

---

## Need More Help?

If you're still seeing 404 errors:

1. Share the **exact URL** from your browser's Network tab
2. Share your `auth.ts` service file
3. Share your `axiosInstance.ts` configuration

The backend is confirmed working. The issue is 100% in the frontend configuration.

