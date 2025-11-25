# Twilio WebSocket Connection Error Fix

## Error

```
WebSocket connection to 'wss://sdkgw.us1.twilio.com/v1/VideoEvents' failed
```

## What This Means

The Twilio Video SDK is trying to establish a WebSocket connection to Twilio's servers but failing. This is **not a backend issue** - the backend is generating tokens correctly. This is a **frontend/browser/network issue**.

## Common Causes & Fixes

### 1. **Invalid or Expired Token** ⚠️ **MOST COMMON**

**Symptom**: WebSocket fails immediately after getting token

**Check**:
```javascript
// In browser console, after getting token
const tokenData = await videoCallService.getVideoToken(13);
console.log('Token:', tokenData.access_token);
console.log('Token expires in:', tokenData.expires_in, 'seconds');

// Decode token to check expiration (JWT)
const parts = tokenData.access_token.split('.');
const payload = JSON.parse(atob(parts[1]));
console.log('Token expires at:', new Date(payload.exp * 1000));
console.log('Current time:', new Date());
```

**Fix**: 
- Make sure token is fresh (not expired)
- Check if token generation is working on backend
- Verify token is being passed correctly to Twilio SDK

### 2. **Network/Firewall Blocking WebSocket** ⚠️ **COMMON**

**Symptom**: WebSocket connection fails immediately

**Check**:
```javascript
// Test WebSocket connectivity
const ws = new WebSocket('wss://sdkgw.us1.twilio.com/v1/VideoEvents');
ws.onopen = () => console.log('✅ WebSocket connection successful');
ws.onerror = (err) => console.error('❌ WebSocket error:', err);
ws.onclose = (event) => console.log('WebSocket closed:', event.code, event.reason);
```

**Fix**:
- Check if firewall is blocking WebSocket connections
- Check if corporate network blocks WebSocket
- Try from different network (mobile hotspot)
- Check browser console for CORS/network errors

### 3. **Browser WebSocket Support** ⚠️ **RARE**

**Symptom**: WebSocket fails in specific browsers

**Check**:
```javascript
// Check WebSocket support
if (typeof WebSocket === 'undefined') {
  console.error('❌ WebSocket not supported in this browser');
} else {
  console.log('✅ WebSocket is supported');
}
```

**Fix**: 
- Use modern browser (Chrome, Firefox, Safari, Edge)
- Update browser to latest version
- Disable browser extensions that might block WebSocket

### 4. **Twilio SDK Configuration Issue** ⚠️ **POSSIBLE**

**Symptom**: WebSocket fails but token is valid

**Check your frontend Twilio Video connection code**:

```typescript
// ❌ WRONG - Missing error handling
const room = await Video.connect(token);

// ✅ CORRECT - With proper error handling
try {
  const room = await Video.connect(token, {
    name: roomName,
    audio: true,
    video: true,
    // Add logging
    logLevel: 'info'
  });
  
  console.log('✅ Connected to room:', room.name);
  
  // Handle connection events
  room.on('disconnected', (room, error) => {
    console.error('Room disconnected:', error);
  });
  
  room.on('reconnecting', (error) => {
    console.warn('Reconnecting:', error);
  });
  
  room.on('reconnected', () => {
    console.log('✅ Reconnected to room');
  });
  
} catch (error) {
  console.error('❌ Failed to connect:', error);
  // Check error type
  if (error.message.includes('WebSocket')) {
    console.error('WebSocket connection failed');
  }
}
```

### 5. **Token Region Mismatch** ⚠️ **POSSIBLE**

**Symptom**: Token generated with `region='au1'` but SDK trying to connect to `us1`

**Check**: Your backend is generating tokens with `region='au1'` (Australia), but Twilio SDK might be defaulting to `us1`.

**Fix**: In your frontend, explicitly set the region when connecting:

```typescript
import Video from 'twilio-video';

// Set region explicitly
Video.connect(token, {
  name: roomName,
  region: 'au1',  // Match backend token region
  audio: true,
  video: true
});
```

## Step-by-Step Debugging

### Step 1: Verify Token is Valid

```javascript
// Get token from backend
const tokenData = await fetch('https://api.tailoredpsychology.com.au/api/appointments/video-token/13/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
}).then(r => r.json());

console.log('Token received:', tokenData);
console.log('Room name:', tokenData.room_name);

// Try to decode token (JWT)
try {
  const parts = tokenData.access_token.split('.');
  const payload = JSON.parse(atob(parts[1]));
  console.log('Token payload:', payload);
  console.log('Token expires:', new Date(payload.exp * 1000));
} catch (e) {
  console.error('Could not decode token:', e);
}
```

### Step 2: Test WebSocket Connection

```javascript
// Test direct WebSocket connection to Twilio
const testWs = new WebSocket('wss://sdkgw.us1.twilio.com/v1/VideoEvents');

testWs.onopen = () => {
  console.log('✅ WebSocket connection successful');
  testWs.close();
};

testWs.onerror = (error) => {
  console.error('❌ WebSocket connection failed:', error);
  console.error('This means your network/firewall is blocking WebSocket connections');
};

testWs.onclose = (event) => {
  console.log('WebSocket closed:', event.code, event.reason);
};
```

### Step 3: Test Twilio Video Connection

```javascript
import Video from 'twilio-video';

// Get token
const tokenData = await videoCallService.getVideoToken(13);

// Try to connect with explicit region
try {
  const room = await Video.connect(tokenData.access_token, {
    name: tokenData.room_name,
    region: 'au1',  // Match backend region
    audio: true,
    video: true,
    logLevel: 'info'  // Enable logging
  });
  
  console.log('✅ Successfully connected to room:', room.name);
  console.log('Room SID:', room.sid);
  console.log('Local participant:', room.localParticipant.identity);
  
  // Disconnect after test
  room.disconnect();
  
} catch (error) {
  console.error('❌ Connection failed:', error);
  console.error('Error name:', error.name);
  console.error('Error message:', error.message);
  
  // Check specific error types
  if (error.message.includes('WebSocket')) {
    console.error('WebSocket connection issue');
  } else if (error.message.includes('token')) {
    console.error('Token issue - check if token is valid');
  } else if (error.message.includes('room')) {
    console.error('Room issue - check if room exists');
  }
}
```

## Quick Fixes

### Fix 1: Add Region to Video.connect()

```typescript
// In your video call component
const room = await Video.connect(token, {
  name: roomName,
  region: 'au1',  // Add this to match backend
  audio: true,
  video: true
});
```

### Fix 2: Add Error Handling

```typescript
try {
  const room = await Video.connect(token, {
    name: roomName,
    region: 'au1',
    audio: true,
    video: true
  });
} catch (error) {
  if (error.message.includes('WebSocket')) {
    // WebSocket connection failed
    alert('Network error: Could not connect to video service. Please check your internet connection.');
  } else {
    // Other error
    alert('Failed to join video call: ' + error.message);
  }
}
```

### Fix 3: Check Network/Firewall

If WebSocket test fails:
1. **Check firewall settings** - Allow WebSocket connections
2. **Check corporate network** - May block WebSocket
3. **Try different network** - Mobile hotspot to test
4. **Check browser extensions** - Disable ad blockers/privacy extensions

## Most Likely Solution

Based on the error, the most likely issue is:

1. **Missing region in Video.connect()** - Add `region: 'au1'` to match backend
2. **Network blocking WebSocket** - Check firewall/network settings
3. **Invalid token** - Verify token is being generated correctly

## Test Script

Run this in your browser console to diagnose:

```javascript
(async function testTwilioConnection() {
  console.log('🧪 Testing Twilio Video Connection');
  console.log('='.repeat(60));
  
  // Step 1: Get token
  console.log('Step 1: Getting video token...');
  const token = localStorage.getItem('access_token');
  if (!token) {
    console.error('❌ No auth token found');
    return;
  }
  
  const tokenData = await fetch('https://api.tailoredpsychology.com.au/api/appointments/video-token/13/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }).then(r => r.json());
  
  console.log('✅ Token received');
  console.log('Room name:', tokenData.room_name);
  console.log('Token expires in:', tokenData.expires_in, 'seconds');
  
  // Step 2: Test WebSocket
  console.log('\nStep 2: Testing WebSocket connection...');
  const wsTest = new Promise((resolve, reject) => {
    const ws = new WebSocket('wss://sdkgw.us1.twilio.com/v1/VideoEvents');
    ws.onopen = () => {
      console.log('✅ WebSocket connection successful');
      ws.close();
      resolve(true);
    };
    ws.onerror = (error) => {
      console.error('❌ WebSocket connection failed');
      reject(error);
    };
    setTimeout(() => reject(new Error('Timeout')), 5000);
  });
  
  try {
    await wsTest;
  } catch (error) {
    console.error('❌ WebSocket test failed:', error);
    console.error('This means your network is blocking WebSocket connections');
    return;
  }
  
  // Step 3: Test Video connection
  console.log('\nStep 3: Testing Twilio Video connection...');
  try {
    const Video = (await import('twilio-video')).default;
    const room = await Video.connect(tokenData.access_token, {
      name: tokenData.room_name,
      region: 'au1',
      audio: true,
      video: true,
      logLevel: 'info'
    });
    
    console.log('✅ Successfully connected to Twilio room!');
    console.log('Room SID:', room.sid);
    console.log('Local participant:', room.localParticipant.identity);
    
    // Disconnect
    room.disconnect();
    console.log('✅ Test complete - connection successful!');
    
  } catch (error) {
    console.error('❌ Video connection failed:', error);
    console.error('Error details:', {
      name: error.name,
      message: error.message,
      code: error.code
    });
  }
})();
```

## Summary

The WebSocket error is a **frontend/network issue**, not a backend issue. Most likely fixes:

1. ✅ Add `region: 'au1'` to `Video.connect()` call
2. ✅ Check network/firewall isn't blocking WebSocket
3. ✅ Verify token is valid and not expired
4. ✅ Add proper error handling

The backend is working correctly - this is a frontend Twilio SDK configuration issue.

