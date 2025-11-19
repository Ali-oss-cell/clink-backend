# Video Token Error Solution: "Invalid Access Token issuer/subject"

## ✅ Good News: Your Backend is Working!

**Test Results:**
- ✅ Token generation works correctly
- ✅ API Key and Secret match Account SID
- ✅ Backend credentials are properly configured

**The error is happening in your FRONTEND, not the backend!**

---

## What's Happening

The error **"Invalid Access Token issuer/subject"** occurs when:

1. **Frontend is using an old/invalid token**
2. **Frontend is connecting to the wrong room**
3. **Token was generated for a different account**
4. **Frontend is using the token incorrectly**

---

## Frontend Checklist

### 1. **Make Sure You're Using the Token Correctly**

**Correct Way:**
```typescript
// Step 1: Get token from YOUR backend API
const response = await fetch('/api/appointments/video-token/47/', {
  headers: {
    'Authorization': `Bearer ${userToken}`
  }
});

const tokenData = await response.json();

// Step 2: Use the token from YOUR backend
const room = await Video.connect(tokenData.access_token, {
  name: tokenData.room_name,  // Use room_name from YOUR backend
  audio: true,
  video: true
});
```

**Common Mistakes:**
- ❌ Using a hardcoded token
- ❌ Using a token from a different source
- ❌ Using the wrong room name
- ❌ Using an expired token

---

### 2. **Check Token Expiration**

The token has an expiration time. Make sure you're not using an expired token:

```typescript
// Check if token is expired
const expiresAt = new Date(tokenData.expires_at);
const now = new Date();

if (now > expiresAt) {
  // Token expired - get a new one
  const newToken = await fetch('/api/appointments/video-token-refresh/47/', {
    headers: { 'Authorization': `Bearer ${userToken}` }
  }).then(r => r.json());
  
  // Use new token
  await Video.connect(newToken.access_token, {
    name: newToken.room_name,
    audio: true,
    video: true
  });
}
```

---

### 3. **Verify Room Name Matches**

Make sure you're using the `room_name` from the backend response:

```typescript
// ✅ CORRECT - Use room_name from backend
const room = await Video.connect(tokenData.access_token, {
  name: tokenData.room_name,  // This comes from your backend
  audio: true,
  video: true
});

// ❌ WRONG - Don't use a hardcoded or different room name
const room = await Video.connect(tokenData.access_token, {
  name: 'some-other-room',  // This will cause the error!
  audio: true,
  video: true
});
```

---

### 4. **Check for Token Refresh Issues**

If you're refreshing tokens, make sure you're using the new token:

```typescript
// Get fresh token
const tokenData = await fetch('/api/appointments/video-token/47/', {
  headers: { 'Authorization': `Bearer ${userToken}` }
}).then(r => r.json());

// Use it immediately - don't store it for too long
const room = await Video.connect(tokenData.access_token, {
  name: tokenData.room_name,
  audio: true,
  video: true
});
```

---

## Debugging Steps

### Step 1: Check What Token You're Getting

Add logging to see what token you're receiving:

```typescript
const response = await fetch('/api/appointments/video-token/47/', {
  headers: { 'Authorization': `Bearer ${userToken}` }
});

const tokenData = await response.json();

console.log('Token Data:', {
  hasToken: !!tokenData.access_token,
  tokenLength: tokenData.access_token?.length,
  roomName: tokenData.room_name,
  expiresAt: tokenData.expires_at,
  expiresIn: tokenData.expires_in
});

// Make sure token exists and is not empty
if (!tokenData.access_token || tokenData.access_token.length < 100) {
  console.error('Invalid token received!');
  return;
}
```

### Step 2: Test Token Connection

Try connecting with the token:

```typescript
try {
  const room = await Video.connect(tokenData.access_token, {
    name: tokenData.room_name,
    audio: true,
    video: true
  });
  
  console.log('✅ Connected successfully!', room.name);
} catch (error) {
  console.error('❌ Connection failed:', error);
  console.error('Token used:', tokenData.access_token.substring(0, 50) + '...');
  console.error('Room name used:', tokenData.room_name);
}
```

### Step 3: Verify Backend Response

Make sure your backend is returning the correct format:

```typescript
// Expected response format:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",  // Long JWT token
  "room_name": "apt-47-1763138954-46eb915c",  // Room name
  "user_identity": "19-sarah@example.com",
  "expires_in": 5400,
  "expires_at": "2025-11-16T10:30:00Z",
  "appointment_id": 47
}
```

---

## Common Frontend Issues

### Issue 1: Using Wrong Endpoint

**Wrong:**
```typescript
// Don't call Twilio directly
const token = await fetch('https://api.twilio.com/...');
```

**Correct:**
```typescript
// Call YOUR backend
const token = await fetch('/api/appointments/video-token/47/', {
  headers: { 'Authorization': `Bearer ${userToken}` }
});
```

### Issue 2: Not Waiting for Token

**Wrong:**
```typescript
let token;
fetch('/api/appointments/video-token/47/').then(r => {
  token = r.json();
});
// token is still undefined here!
Video.connect(token.access_token);  // Error!
```

**Correct:**
```typescript
const response = await fetch('/api/appointments/video-token/47/', {
  headers: { 'Authorization': `Bearer ${userToken}` }
});
const tokenData = await response.json();
// Now tokenData is ready
Video.connect(tokenData.access_token, { name: tokenData.room_name });
```

### Issue 3: Using Cached/Stale Token

**Wrong:**
```typescript
// Storing token in localStorage and reusing it
const oldToken = localStorage.getItem('video_token');
Video.connect(oldToken);  // Might be expired or invalid!
```

**Correct:**
```typescript
// Always get fresh token when connecting
const tokenData = await fetch('/api/appointments/video-token/47/', {
  headers: { 'Authorization': `Bearer ${userToken}` }
}).then(r => r.json());

Video.connect(tokenData.access_token, { name: tokenData.room_name });
```

---

## Quick Fix Checklist

Before connecting to video, make sure:

- [ ] You're calling `/api/appointments/video-token/<appointment_id>/`
- [ ] You're passing the correct `Authorization` header with JWT token
- [ ] You're using `tokenData.access_token` (not a hardcoded value)
- [ ] You're using `tokenData.room_name` (not a hardcoded value)
- [ ] The token is fresh (not expired, not cached)
- [ ] You're awaiting the fetch before using the token
- [ ] The appointment has a `video_room_id` set

---

## Test Your Frontend

Add this test function to your frontend:

```typescript
async function testVideoToken(appointmentId: number, userToken: string) {
  try {
    // Get token
    const response = await fetch(`/api/appointments/video-token/${appointmentId}/`, {
      headers: { 'Authorization': `Bearer ${userToken}` }
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`);
    }
    
    const tokenData = await response.json();
    
    console.log('✅ Token received:', {
      hasToken: !!tokenData.access_token,
      tokenLength: tokenData.access_token?.length,
      roomName: tokenData.room_name,
      expiresAt: tokenData.expires_at
    });
    
    // Try to connect
    const room = await Video.connect(tokenData.access_token, {
      name: tokenData.room_name,
      audio: true,
      video: true
    });
    
    console.log('✅ Connected to room:', room.name);
    room.disconnect();
    
    return true;
  } catch (error) {
    console.error('❌ Error:', error);
    return false;
  }
}

// Use it:
testVideoToken(47, userJWTToken);
```

---

## Summary

**Your backend is working correctly!** ✅

The error is in your **frontend implementation**. Most likely causes:

1. **Using wrong/expired token** - Always get fresh token from backend
2. **Using wrong room name** - Use `room_name` from backend response
3. **Not awaiting async calls** - Make sure you await the fetch before using token
4. **Token caching issues** - Don't cache tokens, get fresh ones each time

**Solution:** Review your frontend video connection code and make sure you're:
- Getting token from YOUR backend API
- Using the exact `access_token` and `room_name` from the response
- Not caching or reusing old tokens
- Handling errors properly

