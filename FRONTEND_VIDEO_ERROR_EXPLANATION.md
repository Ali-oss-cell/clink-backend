# Frontend Video Call Error Explanation

## 🔴 Error You're Seeing

```
❌ Failed to connect to video room: Error: Network error: No response from server. 
Please check:
1. Django server is running: python manage.py runserver
2. Server is accessible at: http://127.0.0.1:8000
3. Check browser Network tab for the actual request URL
```

## 🔍 What This Error Means

Your **frontend** is trying to call the backend API to get a video token, but it's **failing** for one of these reasons:

### **Problem 1: Wrong API URL** ⚠️ **MOST LIKELY**

The error message mentions `http://127.0.0.1:8000`, which means your frontend is configured to use **localhost** instead of your **production API URL**.

**Your production API URL should be:**
```
https://api.tailoredpsychology.com.au
```

**NOT:**
```
http://127.0.0.1:8000  ❌ (localhost - only works on your local machine)
```

### **Problem 2: Missing Authentication** ⚠️ **ALSO LIKELY**

The video token endpoint requires a **JWT Bearer token** in the request headers. If your frontend isn't sending the `Authorization` header, the request will fail.

### **Problem 3: CORS or Network Issue** ⚠️ **LESS LIKELY**

If the API URL is correct and auth is included, it might be a CORS or network connectivity issue.

---

## ✅ How to Fix

### **Step 1: Check Your Frontend API URL Configuration**

In your **frontend project** (React/Next.js), check your environment variables:

**For Next.js:**
```bash
# .env.local or .env.production
NEXT_PUBLIC_API_URL=https://api.tailoredpsychology.com.au
```

**For React/Vite:**
```bash
# .env.production
VITE_API_URL=https://api.tailoredpsychology.com.au
```

**For React/CRA:**
```bash
# .env.production
REACT_APP_API_URL=https://api.tailoredpsychology.com.au
```

### **Step 2: Verify Your Frontend Code Uses the Environment Variable**

Check where you're making the video token request. It should look like this:

```typescript
// ✅ CORRECT - Uses environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.tailoredpsychology.com.au';
const response = await fetch(`${API_URL}/api/appointments/video-token/${appointmentId}/`, {
  headers: {
    'Authorization': `Bearer ${userToken}`,
    'Content-Type': 'application/json'
  }
});

// ❌ WRONG - Hardcoded localhost
const response = await fetch(`http://127.0.0.1:8000/api/appointments/video-token/${appointmentId}/`, {
  // ...
});
```

### **Step 3: Ensure Authorization Header is Included**

The endpoint **requires authentication**. Make sure your request includes the JWT token:

```typescript
// Get token from localStorage (after user logs in)
const token = localStorage.getItem('access_token');

// Include in request
const response = await fetch(
  `${API_URL}/api/appointments/video-token/${appointmentId}/`,
  {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,  // ← REQUIRED!
      'Content-Type': 'application/json'
    }
  }
);
```

### **Step 4: Check Browser Network Tab**

1. Open browser **DevTools** (F12)
2. Go to **Network** tab
3. Try to join the video call
4. Find the request to `/api/appointments/video-token/...`
5. Check:
   - **Request URL**: Should be `https://api.tailoredpsychology.com.au/api/appointments/video-token/...`
   - **Request Headers**: Should include `Authorization: Bearer ...`
   - **Status Code**: 
     - `200` = ✅ Success
     - `401` = ❌ Missing or invalid token
     - `404` = ❌ Wrong URL or endpoint doesn't exist
     - `0` or `ERR_FAILED` = ❌ Network error (wrong URL or server down)

---

## 🧪 Test the Endpoint Manually

To verify the backend is working, test it directly:

```bash
# 1. Get a JWT token first (login)
curl -X POST https://api.tailoredpsychology.com.au/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test.patient@clinic.test","password":"test123"}'

# Response will include:
# {
#   "access": "eyJhbGciOiJIUzI1NiIs...",
#   "refresh": "eyJhbGciOiJIUzI1NiIs..."
# }

# 2. Use the access token to get video token
curl -X GET https://api.tailoredpsychology.com.au/api/appointments/video-token/12/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

If this works, the backend is fine - the issue is in your frontend configuration.

---

## 📋 Complete Frontend Fix Example

Here's a complete example of how your frontend should call the video token endpoint:

```typescript
// src/services/videoCall.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.tailoredpsychology.com.au';

export async function getVideoToken(appointmentId: number) {
  // Get JWT token from localStorage (stored after login)
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('Not authenticated. Please log in first.');
  }

  try {
    const response = await fetch(
      `${API_URL}/api/appointments/video-token/${appointmentId}/`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Authentication failed. Please log in again.');
      }
      if (response.status === 404) {
        throw new Error('Video room not found for this appointment.');
      }
      throw new Error(`Failed to get video token: ${response.statusText}`);
    }

    const data = await response.json();
    return data; // { access_token, room_name, user_identity, ... }
  } catch (error: any) {
    if (error.message.includes('fetch')) {
      throw new Error('Network error: Could not reach the server. Check your internet connection.');
    }
    throw error;
  }
}
```

---

## 🎯 Quick Checklist

- [ ] Frontend environment variable is set to `https://api.tailoredpsychology.com.au`
- [ ] Frontend code uses the environment variable (not hardcoded localhost)
- [ ] User is logged in and has a valid JWT token
- [ ] Request includes `Authorization: Bearer <token>` header
- [ ] Browser Network tab shows correct URL and headers
- [ ] Backend is accessible (test with curl)

---

## 🔗 Related Files

- Backend endpoint: `appointments/views.py` → `GetVideoAccessTokenView`
- URL route: `appointments/urls.py` → `video-token/<int:appointment_id>/`
- Full guide: `VIDEO_TOKEN_NETWORK_ERROR_FIX.md`
- Frontend flow: `FRONTEND_VIDEO_CALL_FLOW.md`

---

## 💡 Summary

**The error means:**
- Your frontend is trying to call `http://127.0.0.1:8000` (localhost)
- But your backend is at `https://api.tailoredpsychology.com.au` (production)

**Fix:**
1. Set `NEXT_PUBLIC_API_URL=https://api.tailoredpsychology.com.au` in your frontend `.env`
2. Make sure your frontend code uses this environment variable
3. Ensure the request includes the `Authorization` header with a valid JWT token
4. Rebuild and redeploy your frontend

The backend is working fine - this is a **frontend configuration issue**.

