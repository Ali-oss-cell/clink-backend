# Video Token Network Error - Troubleshooting Guide

## Problem
Frontend is getting "Network Error: No response from server" when trying to get video token.

## Root Cause
The endpoint `/api/appointments/video-token/{id}/` requires authentication, but the frontend request is not including the `Authorization` header.

## Solution

### 1. Check Frontend Axios Configuration

Make sure your axios instance includes the Authorization header:

```typescript
// src/services/api/videoCall.ts or similar
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

// Create axios instance
const axiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/appointments`,
  timeout: 10000,
});

// Add request interceptor to include auth token
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
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const getVideoToken = async (appointmentId: number) => {
  try {
    const response = await axiosInstance.get(`/video-token/${appointmentId}/`);
    return response.data;
  } catch (error: any) {
    if (error.response) {
      // Server responded with error
      throw new Error(error.response.data.detail || 'Failed to get video token');
    } else if (error.request) {
      // Request made but no response
      throw new Error('Network error: No response from server. Please check your connection.');
    } else {
      // Error in request setup
      throw new Error('Failed to get video token: ' + error.message);
    }
  }
};
```

### 2. Verify Token is Stored

Check if the token exists in localStorage:

```typescript
// In your component or service
const token = localStorage.getItem('access_token');
console.log('Token exists:', !!token);
console.log('Token value:', token ? token.substring(0, 20) + '...' : 'None');
```

### 3. Check Token Format

The token should be a JWT string. Verify it's stored correctly:

```typescript
// After login
const loginResponse = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email, password })
});

const data = await loginResponse.json();
console.log('Login response:', data);

// Store token
if (data.access) {
  localStorage.setItem('access_token', data.access);
  console.log('Token stored successfully');
} else {
  console.error('No access token in response!');
}
```

### 4. Test the Endpoint Manually

Test if the endpoint works with a valid token:

```bash
# Get token from browser console after login
# Then test:
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://127.0.0.1:8000/api/appointments/video-token/50/
```

### 5. Check Browser Network Tab

1. Open browser DevTools (F12)
2. Go to Network tab
3. Try to join video session
4. Find the request to `/api/appointments/video-token/50/`
5. Check:
   - **Request Headers**: Should include `Authorization: Bearer ...`
   - **Status Code**: Should be 200 (not 401)
   - **Response**: Should contain `access_token` and `room_name`

### 6. Common Issues

#### Issue: Token Not in Request Headers
**Symptom**: Network tab shows request without `Authorization` header

**Fix**: Ensure axios interceptor is configured (see step 1)

#### Issue: 401 Unauthorized
**Symptom**: Status code 401 in network tab

**Possible Causes**:
- Token expired (JWT tokens expire after 60 minutes)
- Token not valid
- User not logged in

**Fix**:
```typescript
// Refresh token if expired
if (error.response?.status === 401) {
  const refreshToken = localStorage.getItem('refresh_token');
  if (refreshToken) {
    try {
      const refreshResponse = await axios.post(
        `${API_BASE_URL}/api/auth/refresh/`,
        { refresh: refreshToken }
      );
      localStorage.setItem('access_token', refreshResponse.data.access);
      // Retry original request
      return axiosInstance.request(error.config);
    } catch (refreshError) {
      // Refresh failed, redirect to login
      window.location.href = '/login';
    }
  }
}
```

#### Issue: CORS Error
**Symptom**: Browser console shows CORS error

**Fix**: Backend CORS is already configured. If you see CORS errors:
1. Check Django server is running
2. Verify CORS settings in `settings.py` include your frontend URL
3. Restart Django server after CORS changes

#### Issue: Network Error (No Response)
**Symptom**: "Network Error: No response from server"

**Possible Causes**:
1. Django server not running
2. Wrong URL/port
3. Request timeout
4. Missing Authorization header (most common)

**Fix**:
1. Verify Django server is running: `python manage.py runserver`
2. Check API base URL matches server URL
3. Increase timeout if needed
4. Ensure Authorization header is included (see step 1)

### 7. Complete Working Example

```typescript
// src/services/api/videoCall.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const axiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/appointments`,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - adds auth token to every request
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    } else {
      console.warn('No access token found in localStorage');
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handles errors
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and we haven't tried to refresh yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(
            `${API_BASE_URL}/api/auth/refresh/`,
            { refresh: refreshToken }
          );
          
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          
          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return axiosInstance(originalRequest);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export const VideoCallService = {
  /**
   * Get video access token for an appointment
   */
  getVideoToken: async (appointmentId: number) => {
    try {
      console.log(`[VideoCallService] Requesting token for appointment ${appointmentId}`);
      
      const response = await axiosInstance.get(`/video-token/${appointmentId}/`);
      
      console.log('[VideoCallService] Token received:', {
        room: response.data.room_name,
        expiresIn: response.data.expires_in,
      });
      
      return response.data;
    } catch (error: any) {
      console.error('[VideoCallService] Error getting token:', error);
      
      if (error.response) {
        // Server responded with error status
        const message = error.response.data?.detail || error.response.data?.error || 'Failed to get video token';
        throw new Error(message);
      } else if (error.request) {
        // Request made but no response received
        throw new Error('Network error: No response from server. Please check your connection and ensure the server is running.');
      } else {
        // Error in request setup
        throw new Error(`Failed to get video token: ${error.message}`);
      }
    }
  },

  /**
   * Refresh video token
   */
  refreshVideoToken: async (appointmentId: number) => {
    try {
      const response = await axiosInstance.post(`/video-token-refresh/${appointmentId}/`);
      return response.data;
    } catch (error: any) {
      console.error('[VideoCallService] Error refreshing token:', error);
      throw error;
    }
  },

  /**
   * Get room status
   */
  getRoomStatus: async (appointmentId: number) => {
    try {
      const response = await axiosInstance.get(`/video-status/${appointmentId}/`);
      return response.data;
    } catch (error: any) {
      console.error('[VideoCallService] Error getting room status:', error);
      throw error;
    }
  },
};
```

### 8. Usage in Component

```typescript
// src/pages/video/VideoCallPage.tsx
import { VideoCallService } from '@/services/api/videoCall';
import Video from 'twilio-video';

const connectToRoom = async (appointmentId: number) => {
  try {
    setConnecting(true);
    setError(null);

    // Get video token
    const tokenData = await VideoCallService.getVideoToken(appointmentId);
    
    // Connect to Twilio room
    const room = await Video.connect(tokenData.access_token, {
      name: tokenData.room_name,
      audio: true,
      video: { width: 640, height: 480 },
    });

    setRoom(room);
    setConnecting(false);
    
    // Handle room events...
  } catch (err: any) {
    console.error('Failed to connect to video room:', err);
    setError(err.message || 'Failed to connect to video session');
    setConnecting(false);
  }
};
```

## Quick Checklist

- [ ] Axios instance has request interceptor that adds `Authorization` header
- [ ] Token is stored in `localStorage` as `access_token`
- [ ] Token is valid (not expired)
- [ ] User is logged in
- [ ] Django server is running on port 8000
- [ ] API base URL is correct
- [ ] CORS is configured (already done in backend)
- [ ] Network tab shows `Authorization` header in request

## Testing

1. **Login first**:
```typescript
const loginResponse = await fetch('http://127.0.0.1:8000/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'jane.doe@example.com',
    password: 'your_password'
  })
});
const { access, refresh } = await loginResponse.json();
localStorage.setItem('access_token', access);
localStorage.setItem('refresh_token', refresh);
```

2. **Then get video token**:
```typescript
const tokenData = await VideoCallService.getVideoToken(50);
console.log('Token:', tokenData);
```

## Backend Status

✅ **Backend is working correctly!**

- Endpoint exists: `/api/appointments/video-token/{id}/`
- Authentication required: Yes (JWT Bearer token)
- CORS configured: Yes
- Server running: Yes (port 8000)

The issue is **frontend not sending the Authorization header**.

## Next Steps

1. Update your frontend axios configuration (see step 1)
2. Verify token is stored after login
3. Check browser Network tab to confirm Authorization header is sent
4. Test again

If you still have issues after following these steps, check:
- Browser console for errors
- Network tab for request/response details
- Django server logs for any errors

