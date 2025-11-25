# Debug Video Token Request Error

## Error
```
Network error: Could not connect to API server
at dA.getVideoToken
```

This means the frontend is failing to call the backend API to get the video token.

## Quick Diagnostic Script

**Run this in your browser console on `https://tailoredpsychology.com.au`:**

```javascript
(async function debugVideoToken() {
  console.log('🔍 Debugging Video Token Request');
  console.log('='.repeat(60));
  
  // Step 1: Check axiosInstance config
  console.log('\n1. Checking axiosInstance configuration...');
  if (typeof axiosInstance !== 'undefined') {
    console.log('✅ axiosInstance found');
    console.log('   baseURL:', axiosInstance.defaults?.baseURL);
    console.log('   timeout:', axiosInstance.defaults?.timeout);
    console.log('   headers:', axiosInstance.defaults?.headers);
  } else {
    console.log('❌ axiosInstance not found');
  }
  
  // Step 2: Check environment variables
  console.log('\n2. Checking environment variables...');
  if (typeof import !== 'undefined' && import.meta) {
    console.log('   PROD:', import.meta.env?.PROD);
    console.log('   VITE_API_BASE_URL:', import.meta.env?.VITE_API_BASE_URL);
    console.log('   VITE_API_URL:', import.meta.env?.VITE_API_URL);
  } else {
    console.log('   (Environment variables not accessible)');
  }
  
  // Step 3: Check auth token
  console.log('\n3. Checking authentication...');
  const token = localStorage.getItem('access_token');
  if (token) {
    console.log('✅ Auth token found');
    console.log('   Token preview:', token.substring(0, 20) + '...');
    console.log('   Token length:', token.length);
  } else {
    console.log('❌ No auth token found in localStorage');
    console.log('   You need to log in first!');
    return;
  }
  
  // Step 4: Test direct fetch (bypass axios)
  console.log('\n4. Testing direct fetch to API...');
  const appointmentId = 13; // Change this to your appointment ID
  const apiUrl = 'https://api.tailoredpsychology.com.au';
  const endpoint = `${apiUrl}/api/appointments/video-token/${appointmentId}/`;
  
  console.log('   URL:', endpoint);
  console.log('   Method: GET');
  console.log('   Headers: Authorization: Bearer ...');
  
  try {
    const response = await fetch(endpoint, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    console.log('   ✅ Request sent successfully');
    console.log('   Status:', response.status);
    console.log('   Status Text:', response.statusText);
    console.log('   Response Headers:');
    
    // Check CORS headers
    const corsOrigin = response.headers.get('access-control-allow-origin');
    if (corsOrigin) {
      console.log('      ✅ access-control-allow-origin:', corsOrigin);
    } else {
      console.log('      ❌ access-control-allow-origin: MISSING');
    }
    
    if (response.ok) {
      const data = await response.json();
      console.log('   ✅ Success! Token received:');
      console.log('      Room:', data.room_name);
      console.log('      Expires in:', data.expires_in, 'seconds');
      console.log('      Access token:', data.access_token.substring(0, 30) + '...');
    } else {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      console.log('   ❌ Error response:', errorData);
      console.log('   Status:', response.status);
      
      if (response.status === 401) {
        console.log('   ⚠️  Authentication failed - token might be expired');
      } else if (response.status === 403) {
        console.log('   ⚠️  Permission denied - you may not be authorized for this appointment');
      } else if (response.status === 404) {
        console.log('   ⚠️  Appointment or video room not found');
      }
    }
    
  } catch (error) {
    console.error('   ❌ Fetch failed:', error);
    console.error('   Error name:', error.name);
    console.error('   Error message:', error.message);
    
    if (error.message.includes('Failed to fetch') || error.message.includes('network')) {
      console.error('\n   🔍 This is a network error. Possible causes:');
      console.error('      1. Backend server is down');
      console.error('      2. Wrong API URL');
      console.error('      3. CORS blocking the request');
      console.error('      4. Network/firewall blocking the request');
    }
  }
  
  // Step 5: Check Network tab
  console.log('\n5. Network Tab Check');
  console.log('   📋 Open DevTools → Network tab');
  console.log('   📋 Try joining video call again');
  console.log('   📋 Find request to "video-token"');
  console.log('   📋 Check:');
  console.log('      - Request URL (should be: https://api.tailoredpsychology.com.au/api/appointments/video-token/...)');
  console.log('      - Status code (200 = success, 0 = failed, blocked = CORS)');
  console.log('      - Request Headers (should include Authorization)');
  console.log('      - Response Headers (should include access-control-allow-origin)');
  
  console.log('\n' + '='.repeat(60));
  console.log('Diagnostic complete!');
})();
```

## What to Check

### 1. Browser Network Tab

**Most Important!**

1. Open DevTools (F12) → **Network** tab
2. Clear log (🚫 icon)
3. Try to join video call
4. Find the request to `video-token/...`
5. **Click on it** and check:

**Request Tab:**
- **Request URL**: What is the full URL?
  - ✅ Should be: `https://api.tailoredpsychology.com.au/api/appointments/video-token/13/`
  - ❌ Wrong: `http://127.0.0.1:8000/...` (localhost)
  - ❌ Wrong: `/api/appointments/...` (relative URL)

**Headers Tab:**
- **Request Headers**: Does it include `Authorization: Bearer ...`?
- **Response Headers**: Does it include `access-control-allow-origin`?

**Response Tab:**
- What error message does it show?

**Status Column:**
- `200` = ✅ Success
- `401` = ❌ Auth issue (token expired/invalid)
- `403` = ❌ Permission denied
- `404` = ❌ Endpoint not found
- `0` or `(failed)` = ❌ Network error (request not sent)
- `(blocked)` = ❌ CORS error

### 2. Check axiosInstance baseURL

Run in browser console:

```javascript
console.log('axiosInstance baseURL:', axiosInstance?.defaults?.baseURL);
```

**Should be:**
- ✅ `https://api.tailoredpsychology.com.au/api` (production)
- ❌ `http://127.0.0.1:8000/api` (localhost - won't work)
- ❌ `undefined` (not configured)

### 3. Test Direct Fetch

Run in browser console:

```javascript
const token = localStorage.getItem('access_token');
const response = await fetch('https://api.tailoredpsychology.com.au/api/appointments/video-token/13/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

console.log('Status:', response.status);
const data = await response.json();
console.log('Response:', data);
```

If this works but axios doesn't, the issue is with `axiosInstance` configuration.

## Common Fixes

### Fix 1: Update axiosInstance baseURL

If `axiosInstance.baseURL` is wrong, update it:

```typescript
// In your axiosInstance file
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 
  (import.meta.env.PROD 
    ? 'https://api.tailoredpsychology.com.au/api' 
    : 'http://127.0.0.1:8000/api');

export const axiosInstance = axios.create({
  baseURL: API_BASE_URL,  // Make sure this is correct!
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});
```

### Fix 2: Check Environment Variable

In your frontend `.env.production`:

```bash
VITE_API_BASE_URL=https://api.tailoredpsychology.com.au/api
```

Then rebuild your frontend.

### Fix 3: Use Direct Fetch as Fallback

In your `VideoCallService`, add a fallback:

```typescript
async getVideoToken(appointmentId: number): Promise<VideoTokenResponse> {
  try {
    // Try axios first
    return await axiosInstance.get(`/appointments/video-token/${appointmentId}/`);
  } catch (error) {
    // Fallback to direct fetch
    const token = localStorage.getItem('access_token');
    const response = await fetch(
      `https://api.tailoredpsychology.com.au/api/appointments/video-token/${appointmentId}/`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  }
}
```

## Summary

The error "Could not connect to API server" means:

1. **Request isn't reaching the server** - Check Network tab
2. **Wrong API URL** - Check axiosInstance baseURL
3. **Network blocking** - Check firewall/CORS

**Run the diagnostic script above** and share:
- What URL is being called?
- What status code do you see?
- What does the Network tab show?

This will tell us exactly what's wrong!

