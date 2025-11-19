# Quick Fix: Privacy Policy Error

## The Error
```
[PrivacyService] Error getting Privacy Policy status:
```

## Most Common Causes & Quick Fixes

### 1. ✅ Check if Migration is Run (MOST COMMON)

**Fix:**
```bash
python manage.py migrate
```

**Verify:**
```bash
python manage.py showmigrations users | grep privacy
# Should show: [X] 0005_add_privacy_consent_fields
```

---

### 2. ✅ Check User Authentication

**Problem:** User is not logged in or token is expired.

**Fix in Frontend:**
```typescript
// Make sure token is set before calling the API
const token = localStorage.getItem('access_token');
if (!token) {
  // Redirect to login
  navigate('/login');
  return;
}

// Make sure axios instance has the token
axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

**Test:**
```bash
# Get token first
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"patient@example.com","password":"password"}'

# Then test endpoint with token
curl -X GET http://127.0.0.1:8000/api/auth/privacy-policy/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 3. ✅ Check User Role

**Problem:** User is not a patient (might be admin, psychologist, etc.)

**Fix:**
The endpoint only works for patients. Make sure you're logged in as a patient user.

**Check:**
```python
python manage.py shell
>>> from users.models import User
>>> user = User.objects.get(email='your-email@example.com')
>>> print(user.role)  # Should be 'patient'
```

---

### 4. ✅ Check API URL

**Problem:** Frontend is calling wrong URL.

**Fix:**
Make sure your axios instance is configured correctly:
```typescript
// src/services/api/axiosInstance.ts
import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000',  // Your Django backend URL
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token interceptor
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default axiosInstance;
```

---

### 5. ✅ Check CORS

**Problem:** CORS is blocking the request.

**Fix:**
Make sure your frontend URL is in `CORS_ALLOWED_ORIGINS` in `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite
    "http://127.0.0.1:5173",
]
```

**Test:**
Check browser console Network tab - if you see CORS error, this is the issue.

---

### 6. ✅ Check Django Server is Running

**Problem:** Backend server is not running.

**Fix:**
```bash
# Start Django server
python manage.py runserver
```

**Test:**
```bash
# Should return 401 (not authenticated, but server is responding)
curl http://127.0.0.1:8000/api/auth/privacy-policy/
```

---

## Quick Diagnostic Steps

1. **Check browser console** - What's the exact error message?
2. **Check Network tab** - What HTTP status code? (401, 403, 404, 500?)
3. **Check Django server logs** - Any errors in terminal?
4. **Test endpoint directly** - Use curl or Postman

---

## Test Endpoint Directly

```bash
# 1. Login and get token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"patient@example.com","password":"password"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")

# 2. Test Privacy Policy endpoint
curl -X GET http://127.0.0.1:8000/api/auth/privacy-policy/ \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**Expected Response:**
```json
{
  "accepted": false,
  "accepted_date": null,
  "version": "",
  "latest_version": "1.0",
  "needs_update": true,
  "privacy_policy_url": "https://yourclinic.com.au/privacy-policy"
}
```

---

## Still Not Working?

Share these details:
1. **Browser console error** (full error message)
2. **Network tab** (HTTP status code and response)
3. **Django server logs** (any errors in terminal)
4. **User role** (is the user a patient?)

Then we can debug further!

