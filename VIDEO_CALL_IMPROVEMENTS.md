# Video Call Experience Improvements

## Current Token Validity

**Token Expiration:** 2 hours (7200 seconds)

**Current Implementation:**
- Tokens are valid for 2 hours from generation
- No automatic refresh mechanism
- If a session runs longer than 2 hours, users will be disconnected

---

## Improvements Implemented

### 1. **Smart Token Expiration**

**Problem:** Fixed 2-hour expiration doesn't account for appointment duration

**Solution:** Calculate token expiration based on:
- Appointment duration (e.g., 60 minutes)
- Buffer time (15 minutes before + 15 minutes after)
- Maximum session time

**Result:** Token expires when appointment actually ends, not after arbitrary 2 hours

---

### 2. **Token Refresh Endpoint**

**New Endpoint:** `GET /api/appointments/video-token-refresh/<appointment_id>/`

**Purpose:** Get a new token before the current one expires

**Use Case:**
- Frontend detects token is about to expire (within 5 minutes)
- Automatically requests a new token
- Reconnects seamlessly without interrupting the call

---

### 3. **Token Expiration Timestamp**

**Added Field:** `expires_at` (ISO 8601 timestamp)

**Purpose:** Frontend can calculate exact time until expiration

**Frontend Usage:**
```typescript
const expiresAt = new Date(tokenData.expires_at);
const timeUntilExpiry = expiresAt.getTime() - Date.now();

// Refresh token 5 minutes before expiration
if (timeUntilExpiry < 5 * 60 * 1000) {
  await refreshToken();
}
```

---

### 4. **Better Room Timeout Settings**

**Current Settings:**
- `empty_room_timeout`: 5 minutes (room closes if empty)
- `unused_room_timeout`: 10 minutes (room closes if unused)

**Improved Settings:**
- `empty_room_timeout`: 15 minutes (allows late joiners)
- `unused_room_timeout`: Based on appointment duration + 30 minutes buffer

---

### 5. **Connection Status Endpoint**

**New Endpoint:** `GET /api/appointments/video-status/<appointment_id>/`

**Returns:**
- Room status (active, completed, not_found)
- Number of participants
- Room duration
- Connection quality indicators

---

## Token Validity Calculation

### **Formula:**
```
Token TTL = max(
  appointment_duration_minutes + 30 minutes (buffer),
  60 minutes (minimum),
  4 hours (maximum)
)
```

### **Examples:**

**30-minute appointment:**
- Token valid for: 60 minutes (minimum)
- Expires: 30 minutes after appointment end

**60-minute appointment:**
- Token valid for: 90 minutes (60 + 30 buffer)
- Expires: 30 minutes after appointment end

**120-minute appointment:**
- Token valid for: 150 minutes (120 + 30 buffer)
- Expires: 30 minutes after appointment end

---

## Frontend Implementation Guide

### **1. Monitor Token Expiration**

```typescript
useEffect(() => {
  if (!tokenData?.expires_at) return;

  const expiresAt = new Date(tokenData.expires_at);
  const checkInterval = setInterval(() => {
    const timeUntilExpiry = expiresAt.getTime() - Date.now();
    const fiveMinutes = 5 * 60 * 1000;

    // Refresh token 5 minutes before expiration
    if (timeUntilExpiry < fiveMinutes && timeUntilExpiry > 0) {
      refreshVideoToken();
    }
  }, 60000); // Check every minute

  return () => clearInterval(checkInterval);
}, [tokenData]);
```

### **2. Auto-Refresh Token**

```typescript
async function refreshVideoToken() {
  try {
    const response = await fetch(
      `/api/appointments/video-token-refresh/${appointmentId}/`,
      {
        headers: {
          'Authorization': `Bearer ${userToken}`
        }
      }
    );

    const newTokenData = await response.json();
    
    // Reconnect with new token
    await reconnectWithNewToken(newTokenData.access_token);
  } catch (error) {
    console.error('Failed to refresh token:', error);
    // Show warning to user
  }
}
```

### **3. Show Token Expiration Warning**

```typescript
const [timeUntilExpiry, setTimeUntilExpiry] = useState<number | null>(null);

useEffect(() => {
  if (!tokenData?.expires_at) return;

  const interval = setInterval(() => {
    const expiresAt = new Date(tokenData.expires_at);
    const remaining = expiresAt.getTime() - Date.now();
    setTimeUntilExpiry(remaining);

    // Show warning when less than 10 minutes remain
    if (remaining < 10 * 60 * 1000 && remaining > 0) {
      showWarning('Your session will expire soon. Refreshing...');
    }
  }, 1000);

  return () => clearInterval(interval);
}, [tokenData]);
```

---

## API Response Changes

### **Before:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "room_name": "apt-47-abc",
  "user_identity": "2-jane@example.com",
  "expires_in": 7200,
  "appointment_id": 47
}
```

### **After:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "room_name": "apt-47-abc",
  "user_identity": "2-jane@example.com",
  "expires_in": 5400,
  "expires_at": "2025-11-16T10:30:00Z",
  "appointment_id": 47,
  "appointment_duration_minutes": 60,
  "token_valid_until": "30 minutes after appointment end"
}
```

---

## Benefits

1. **No Unexpected Disconnections:** Token expires after appointment ends, not during
2. **Seamless Long Sessions:** Auto-refresh prevents interruptions
3. **Better User Experience:** Users see expiration warnings
4. **Flexible Duration:** Works for any appointment length
5. **Connection Reliability:** Better room timeout settings

---

## Testing

### **Test Scenarios:**

1. **Short Appointment (30 min):**
   - Token should be valid for at least 60 minutes
   - Should not expire during session

2. **Long Appointment (120 min):**
   - Token should be valid for 150 minutes
   - Should not expire during session

3. **Token Refresh:**
   - Request new token 5 minutes before expiration
   - Should get new token successfully
   - Should be able to reconnect seamlessly

4. **Expiration Warning:**
   - Frontend should show warning 10 minutes before expiration
   - Auto-refresh should happen 5 minutes before expiration

---

## Summary

**Token Validity:** Now calculated based on appointment duration + buffer

**Minimum:** 60 minutes
**Maximum:** 4 hours
**Typical:** Appointment duration + 30 minutes buffer

**New Features:**
- Token refresh endpoint
- Expiration timestamp in response
- Smart expiration calculation
- Better room timeout settings
- Connection status endpoint

**Frontend Requirements:**
- Monitor token expiration
- Auto-refresh before expiration
- Show expiration warnings
- Handle reconnection gracefully

