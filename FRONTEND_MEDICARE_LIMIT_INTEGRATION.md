# Frontend Integration: Medicare Session Limits

## What You Need to Update

### 1. Show Session Limit When Booking

**Update your booking form/component:**

```typescript
// When user selects a service, check Medicare limit
const checkMedicareLimit = async (serviceId: number) => {
  try {
    const response = await axios.get(
      `/api/appointments/medicare-limit-check/?service_id=${serviceId}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    return response.data; // { sessions_used, sessions_remaining, max_sessions }
  } catch (error) {
    console.error('Error checking Medicare limit:', error);
  }
};

// Display in UI
{sessionsRemaining !== null && (
  <div className="medicare-info">
    <p>Medicare Sessions: {sessionsUsed}/{maxSessions} used</p>
    <p>Sessions Remaining: {sessionsRemaining}</p>
    {sessionsRemaining <= 2 && (
      <p className="warning">⚠️ Only {sessionsRemaining} Medicare sessions remaining this year</p>
    )}
  </div>
)}
```

### 2. Handle Booking Errors

**Update your booking error handling:**

```typescript
try {
  const response = await axios.post('/api/appointments/book-enhanced/', bookingData);
  // Success
} catch (error: any) {
  if (error.response?.data?.error?.includes('Medicare session limit')) {
    // Show Medicare limit error
    setError({
      message: error.response.data.error,
      medicareLimit: error.response.data.medicare_limit_info
    });
  } else if (error.response?.data?.error?.includes('GP referral')) {
    // Show referral requirement error
    setError({
      message: error.response.data.error,
      requiresReferral: true
    });
  } else {
    // Other errors
    setError({ message: error.response?.data?.error || 'Booking failed' });
  }
}
```

### 3. Show Limit in Patient Dashboard

**Add to patient dashboard:**

```typescript
// Fetch Medicare session info
const getMedicareSessionInfo = async () => {
  try {
    const response = await axios.get('/api/appointments/medicare-session-info/');
    return response.data;
  } catch (error) {
    console.error('Error fetching Medicare info:', error);
  }
};

// Display component
<div className="medicare-sessions-card">
  <h3>Medicare Sessions This Year</h3>
  <div className="progress-bar">
    <div 
      className="progress-fill" 
      style={{ width: `${(sessionsUsed / 10) * 100}%` }}
    />
  </div>
  <p>{sessionsUsed} / 10 sessions used</p>
  <p>{sessionsRemaining} sessions remaining</p>
  {sessionsRemaining === 0 && (
    <p className="alert">
      Medicare limit reached. You can still book private sessions.
    </p>
  )}
</div>
```

### 4. Show Warning When Approaching Limit

```typescript
// In booking component
useEffect(() => {
  if (sessionsRemaining !== null && sessionsRemaining <= 2) {
    setWarning(
      `⚠️ You have only ${sessionsRemaining} Medicare sessions remaining this year. 
       After this, you'll need to pay full price or wait until next year.`
    );
  }
}, [sessionsRemaining]);
```

---

## API Endpoints Available

### 1. Check Medicare Limit (Before Booking)
**Endpoint:** `GET /api/appointments/medicare-limit-check/?service_id=1`

**Response:**
```json
{
  "service_id": 1,
  "service_name": "Individual Therapy",
  "medicare_item_number": "80110",
  "is_allowed": true,
  "sessions_used": 7,
  "sessions_remaining": 3,
  "max_sessions": 10,
  "current_year": 2025
}
```

**When limit reached:**
```json
{
  "service_id": 1,
  "service_name": "Individual Therapy",
  "medicare_item_number": "80110",
  "is_allowed": false,
  "sessions_used": 10,
  "sessions_remaining": 0,
  "max_sessions": 10,
  "current_year": 2025,
  "error": "Medicare session limit reached (10 sessions per calendar year)..."
}
```

### 2. Get Patient's Medicare Session Info (Dashboard)
**Endpoint:** `GET /api/appointments/medicare-session-info/`

**Response:**
```json
{
  "current_year": 2025,
  "sessions_used": 7,
  "sessions_remaining": 3,
  "max_sessions": 10,
  "limit_reached": false,
  "services": [
    {
      "service_id": 1,
      "service_name": "Individual Therapy",
      "item_number": "80110",
      "sessions_used": 5,
      "sessions_remaining": 5,
      "max_sessions": 10
    },
    {
      "service_id": 2,
      "service_name": "Group Therapy",
      "item_number": "80115",
      "sessions_used": 2,
      "sessions_remaining": 8,
      "max_sessions": 10
    }
  ]
}
```

---

## Quick Summary

**What to add:**
1. ✅ Show Medicare session count when booking
2. ✅ Display remaining sessions
3. ✅ Handle "limit reached" error message
4. ✅ Show warning when approaching limit (8+ used)
5. ✅ Add Medicare info to patient dashboard

**Error messages to handle:**
- "Medicare session limit reached"
- "GP referral is required"
- "Invalid Medicare item number"

That's it! The backend already handles everything - you just need to display the information to users.

