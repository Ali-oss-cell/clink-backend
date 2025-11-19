# Frontend Network Error Diagnosis

## Problem
Frontend getting "Network Error: No response from server" when calling video token endpoint.

## Server Status: ✅ RUNNING
- Django server is running on port 8000
- Server responds to requests (tested with curl)
- Endpoint exists and works (returns 401 without auth, which is correct)

## The Issue
The frontend cannot reach the backend server. This is a **connectivity issue**, not a CORS or authentication issue.

---

## Diagnostic Steps

### 1. Check Frontend API Base URL

**Check your frontend code** - What URL is it using?

```typescript
// Check these files:
// - src/services/api/videoCall.ts
// - src/services/api/axiosInstance.ts
// - .env or .env.local

// Common issues:
const API_BASE_URL = 'http://localhost:8000';  // ✅ Correct
const API_BASE_URL = 'http://127.0.0.1:8000';  // ✅ Also correct
const API_BASE_URL = 'https://localhost:8000';  // ❌ Wrong (HTTPS)
const API_BASE_URL = 'http://localhost:3000';   // ❌ Wrong port
const API_BASE_URL = '/api';                    // ❌ Relative URL (won't work)
```

**Action**: Verify your frontend is using `http://127.0.0.1:8000` or `http://localhost:8000`

---

### 2. Check Browser Network Tab

1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Try to join video session
4. Look for the request to `/api/appointments/video-token/50/`
5. Check:
   - **Request URL**: What's the full URL?
   - **Status**: What status code? (If it shows "failed" or "pending", that's the issue)
   - **Type**: Should be "xhr" or "fetch"
   - **Time**: Does it timeout or fail immediately?

**What to look for**:
- If URL is `http://localhost:5173/api/...` → Wrong! Should be `http://127.0.0.1:8000/api/...`
- If request shows "pending" forever → Server not reachable
- If request shows "failed" immediately → Network issue

---

### 3. Test from Browser Console

Open browser console and run:

```javascript
// Test 1: Check if server is reachable
fetch('http://127.0.0.1:8000/api/appointments/video-token/50/', {
  method: 'GET',
  headers: {
    'Authorization': 'Bearer YOUR_TOKEN_HERE'
  }
})
.then(r => r.json())
.then(data => console.log('✅ Server reachable:', data))
.catch(err => console.error('❌ Server NOT reachable:', err));

// Test 2: Check without auth (should get 401)
fetch('http://127.0.0.1:8000/api/appointments/video-token/50/')
.then(r => {
  console.log('Status:', r.status);
  return r.json();
})
.then(data => console.log('Response:', data))
.catch(err => console.error('Error:', err));
```

**Expected Results**:
- Test 1: Should return video token (if token is valid)
- Test 2: Should return 401 Unauthorized (proves server is reachable)

---

### 4. Check Axios Configuration

**Find your axios instance** (usually in `src/services/api/axiosInstance.ts` or similar):

```typescript
// ❌ WRONG - Relative URL
const axiosInstance = axios.create({
  baseURL: '/api/appointments',  // This won't work!
});

// ❌ WRONG - Wrong port
const axiosInstance = axios.create({
  baseURL: 'http://localhost:5173/api/appointments',  // Frontend port!
});

// ✅ CORRECT - Full URL with backend port
const axiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/appointments',
  // or
  baseURL: 'http://localhost:8000/api/appointments',
});
```

**Action**: Make sure baseURL points to port **8000** (Django), not **5173** (Vite)

---

### 5. Check Environment Variables

**Check your frontend `.env` or `.env.local` file**:

```bash
# ✅ CORRECT
VITE_API_URL=http://127.0.0.1:8000
# or
REACT_APP_API_URL=http://127.0.0.1:8000

# ❌ WRONG
VITE_API_URL=http://localhost:5173
VITE_API_URL=/api
```

**Then in your code**:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
// or for Create React App:
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
```

**Action**: Verify environment variable is set correctly

---

### 6. Check for Proxy Configuration

**If using Vite**, check `vite.config.ts`:

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',  // ✅ Backend URL
        changeOrigin: true,
      }
    }
  }
});
```

**If proxy is configured**, you can use relative URLs:
```typescript
// With proxy, this works:
const axiosInstance = axios.create({
  baseURL: '/api/appointments',  // ✅ Works with proxy
});
```

**Action**: Either configure proxy OR use full URL

---

### 7. Check Firewall/Security

**Possible issues**:
- Firewall blocking connection
- Antivirus blocking localhost connections
- Browser security settings

**Test**: Try accessing `http://127.0.0.1:8000/api/appointments/video-token/50/` directly in browser (should get 401 JSON response)

---

## Quick Fix Checklist

- [ ] **Verify Django server is running**: `python manage.py runserver`
- [ ] **Check frontend baseURL**: Should be `http://127.0.0.1:8000` or `http://localhost:8000`
- [ ] **Check port**: Should be **8000** (Django), not 5173 (Vite)
- [ ] **Check browser Network tab**: See actual request URL
- [ ] **Test with browser console**: Use fetch() to test connectivity
- [ ] **Check environment variables**: Verify API_URL is set correctly
- [ ] **Check proxy config**: If using Vite proxy, verify it's configured
- [ ] **Restart both servers**: Sometimes helps with connection issues

---

## Common Solutions

### Solution 1: Fix Base URL

```typescript
// src/services/api/videoCall.ts
import axios from 'axios';

// ✅ CORRECT - Use full URL
const API_BASE_URL = 'http://127.0.0.1:8000';

const axiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/appointments`,
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

export const getVideoToken = async (appointmentId: number) => {
  try {
    const response = await axiosInstance.get(`/video-token/${appointmentId}/`);
    return response.data;
  } catch (error: any) {
    console.error('[VideoCallService] Error:', error);
    throw error;
  }
};
```

### Solution 2: Use Environment Variable

```typescript
// .env.local (in frontend root)
VITE_API_URL=http://127.0.0.1:8000

// src/services/api/videoCall.ts
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
```

### Solution 3: Configure Vite Proxy

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      }
    }
  }
});
```

Then use relative URLs:
```typescript
const axiosInstance = axios.create({
  baseURL: '/api/appointments',  // Works with proxy
});
```

---

## Debugging Commands

### Test Server from Terminal

```bash
# Test 1: Check if server is running
curl http://127.0.0.1:8000/api/appointments/video-token/50/

# Should return: {"detail":"Authentication credentials were not provided."}

# Test 2: Check with auth token
TOKEN="your_token_here"
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/appointments/video-token/50/

# Should return video token JSON
```

### Check What Ports Are Listening

```bash
# Linux/Mac
netstat -tlnp | grep :8000
# or
ss -tlnp | grep :8000

# Should show: 127.0.0.1:8000 LISTEN
```

---

## Most Likely Issues (In Order)

1. **Wrong baseURL** - Frontend using wrong port (5173 instead of 8000)
2. **Relative URL without proxy** - Using `/api` without Vite proxy configured
3. **Environment variable not set** - API_URL not configured
4. **Server not running** - Django server stopped (but we verified it's running)
5. **Network/firewall** - Blocking localhost connections

---

## Next Steps

1. **Check browser Network tab** - See the actual request URL
2. **Check your axios baseURL** - Verify it's `http://127.0.0.1:8000`
3. **Test with browser console** - Use fetch() to test connectivity
4. **Share the Network tab screenshot** - So we can see the exact error

The server is working fine - the issue is the frontend can't reach it. Check the URL configuration!

