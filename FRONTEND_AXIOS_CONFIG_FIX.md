# Frontend Axios Configuration Fix

## Your Code Analysis

Your `VideoCallService` code looks good! The issue is likely one of these:

1. **`axiosInstance` baseURL not configured correctly**
2. **Nginx CORS fix not deployed yet**
3. **Environment variable not set**

## Step 1: Check Your `axiosInstance` Configuration

Find where you create `axiosInstance` (usually in `src/services/api/axiosInstance.ts` or similar):

```typescript
// ✅ CORRECT Configuration
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.PROD 
    ? 'https://api.tailoredpsychology.com.au/api' 
    : 'http://127.0.0.1:8000/api');

export const axiosInstance = axios.create({
  baseURL: API_BASE_URL,  // Should be: https://api.tailoredpsychology.com.au/api
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth interceptor
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

### Common Issues:

#### Issue 1: Wrong baseURL
```typescript
// ❌ WRONG - Missing /api
baseURL: 'https://api.tailoredpsychology.com.au'

// ✅ CORRECT
baseURL: 'https://api.tailoredpsychology.com.au/api'
```

#### Issue 2: baseURL includes /appointments
```typescript
// ❌ WRONG - Too specific
baseURL: 'https://api.tailoredpsychology.com.au/api/appointments'

// ✅ CORRECT - Generic API base
baseURL: 'https://api.tailoredpsychology.com.au/api'
```

#### Issue 3: Environment variable not set
```typescript
// Check in browser console:
console.log('VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL);
console.log('PROD:', import.meta.env.PROD);
console.log('axiosInstance baseURL:', axiosInstance.defaults.baseURL);
```

## Step 2: Verify Environment Variable

In your frontend project, check `.env.production` or `.env`:

```bash
# Should be:
VITE_API_BASE_URL=https://api.tailoredpsychology.com.au/api
```

**Or if using Vite with different variable name:**
```bash
VITE_API_URL=https://api.tailoredpsychology.com.au
# Then in code:
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://api.tailoredpsychology.com.au';
const axiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api`,
});
```

## Step 3: Deploy Nginx CORS Fix

**On your Droplet, run:**

```bash
cd /var/www/clink-backend && \
git pull origin main && \
sudo cp deployment/nginx.conf /etc/nginx/sites-available/psychology_clinic && \
sudo nginx -t && \
sudo systemctl reload nginx
```

This ensures CORS headers are passed through from Django.

## Step 4: Test in Browser Console

Run this in your browser console on `https://tailoredpsychology.com.au`:

```javascript
// Test 1: Check axiosInstance config
console.log('axiosInstance baseURL:', axiosInstance.defaults.baseURL);
console.log('Environment:', import.meta.env.PROD ? 'PRODUCTION' : 'DEVELOPMENT');
console.log('VITE_API_BASE_URL:', import.meta.env.VITE_API_BASE_URL);

// Test 2: Use your test method
await videoCallService.testVideoToken(13);

// Test 3: Direct fetch test
const token = localStorage.getItem('access_token');
const response = await fetch('https://api.tailoredpsychology.com.au/api/appointments/video-token/13/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  }
});
console.log('Status:', response.status);
console.log('Headers:', [...response.headers.entries()]);
const data = await response.json();
console.log('Response:', data);
```

## Step 5: Check Browser Network Tab

1. Open DevTools (F12) → **Network** tab
2. Clear log (🚫 icon)
3. Try to join video call
4. Find request to `video-token/13/`
5. Check:
   - **Request URL**: Should be `https://api.tailoredpsychology.com.au/api/appointments/video-token/13/`
   - **Status**: What is it? (blocked, CORS, 401, 404, 200?)
   - **Request Headers**: Should include `Authorization: Bearer ...`
   - **Response Headers**: Should include `access-control-allow-origin: https://tailoredpsychology.com.au`

## Quick Fix: Update Your axiosInstance

If your `axiosInstance` is not configured correctly, update it:

```typescript
// src/services/api/axiosInstance.ts
import axios from 'axios';

const getApiBaseUrl = () => {
  // Check environment variable first
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  // Fallback based on environment
  if (import.meta.env.PROD) {
    return 'https://api.tailoredpsychology.com.au/api';
  }
  
  return 'http://127.0.0.1:8000/api';
};

export const axiosInstance = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for auth
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh or redirect to login
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## Summary

Your `VideoCallService` code is good! The issues are likely:

1. ✅ **Deploy Nginx CORS fix** (Step 3 above)
2. ✅ **Verify `axiosInstance` baseURL** (Step 1 above)
3. ✅ **Set environment variable** (Step 2 above)
4. ✅ **Test in browser console** (Step 4 above)

After deploying the Nginx fix and verifying the axiosInstance config, the video calls should work!

