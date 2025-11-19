# Psychologist Video Session Endpoints

## Overview

Psychologists can access video sessions through multiple endpoints. All video endpoints check if the user is either the patient OR the psychologist of the appointment, so they work for both roles.

---

## Primary Video Endpoints for Psychologists

### 1. **Get Video Access Token** (Main Endpoint)
**Endpoint:** `GET /api/appointments/video-token/<appointment_id>/`

**Description:** Get Twilio access token to join a video session. This is the main endpoint psychologists use to get video access.

**Authentication:** Bearer Token (JWT) - Must be the psychologist of the appointment

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "room_name": "apt-47-1763138954-46eb915c",
  "user_identity": "19-sarah@example.com",
  "expires_in": 5400,
  "expires_at": "2025-11-16T10:30:00Z",
  "appointment_id": 47,
  "appointment_duration_minutes": 60,
  "token_valid_until": "90 minutes (1 hours)"
}
```

**Usage Example:**
```typescript
// Get video token for appointment #47
const response = await fetch('/api/appointments/video-token/47/', {
  headers: {
    'Authorization': `Bearer ${psychologistToken}`
  }
});

const tokenData = await response.json();
// Use tokenData.access_token to connect to Twilio Video
```

---

### 2. **Refresh Video Token**
**Endpoint:** `GET /api/appointments/video-token-refresh/<appointment_id>/`

**Description:** Get a new access token before the current one expires. Use this for long sessions.

**Authentication:** Bearer Token (JWT) - Must be the psychologist of the appointment

**Response:** Same format as video-token endpoint, with additional `refreshed_at` field

**Usage:**
```typescript
// Refresh token when it's about to expire
const response = await fetch('/api/appointments/video-token-refresh/47/', {
  headers: {
    'Authorization': `Bearer ${psychologistToken}`
  }
});
```

---

### 3. **Get Video Room Status**
**Endpoint:** `GET /api/appointments/video-status/<appointment_id>/`

**Description:** Check video room status, participant count, and connection information.

**Authentication:** Bearer Token (JWT) - Must be the psychologist of the appointment

**Response:**
```json
{
  "room_name": "apt-47-abc",
  "room_sid": "RM...",
  "status": "in-progress",
  "participants_count": 2,
  "participants": [
    {
      "sid": "PA...",
      "identity": "19-sarah@example.com",
      "status": "connected",
      "duration": 1200,
      "connected_at": "2025-11-16T08:00:00Z"
    },
    {
      "sid": "PA...",
      "identity": "2-jane@example.com",
      "status": "connected",
      "duration": 1200,
      "connected_at": "2025-11-16T08:00:00Z"
    }
  ],
  "duration": 1200,
  "created_at": "2025-11-16T08:00:00Z",
  "appointment_id": 47
}
```

---

## Getting Appointment List with Video Info

### 4. **Psychologist Schedule** (Recommended for Schedule View)
**Endpoint:** `GET /api/appointments/psychologist/schedule/`

**Description:** Get all appointments for the logged-in psychologist with formatted data including video room info and timer fields.

**Authentication:** Bearer Token (JWT) - Must be a psychologist

**Query Parameters:**
- `start_date` - Filter from date (YYYY-MM-DD)
- `end_date` - Filter to date (YYYY-MM-DD)
- `month` - Filter by month (YYYY-MM)
- `year` - Filter by year (YYYY)
- `status` - Filter by status (scheduled, confirmed, completed, cancelled, all)
- `page` - Page number (default: 1)
- `page_size` - Results per page (default: 50)

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 47,
      "patient_name": "Jane Doe",
      "service_name": "Individual Therapy",
      "appointment_date": "2025-11-16T08:00:00Z",
      "formatted_date": "Sat, 16 Nov 2025",
      "formatted_time": "08:00 AM",
      "duration_minutes": 60,
      "status": "confirmed",
      "session_type": "telehealth",
      "video_room_id": "apt-47-abc",
      "meeting_url": "https://yourwebsite.com/video-session/apt-47-abc",
      "session_start_time": "2025-11-16T08:00:00Z",
      "session_end_time": "2025-11-16T09:00:00Z",
      "time_until_start_seconds": 3600,
      "time_remaining_seconds": null,
      "session_status": "upcoming",
      "can_join_session": false
    }
  ]
}
```

**Usage:**
```typescript
// Get psychologist's schedule with video info
const response = await fetch('/api/appointments/psychologist/schedule/?status=confirmed', {
  headers: {
    'Authorization': `Bearer ${psychologistToken}`
  }
});

const schedule = await response.json();
// schedule.results contains appointments with video_room_id and timer fields
```

---

### 5. **Main Appointments List**
**Endpoint:** `GET /api/appointments/`

**Description:** Returns all appointments for the logged-in psychologist. Automatically filters to show only psychologist's appointments.

**Authentication:** Bearer Token (JWT) - Must be a psychologist

**Query Parameters:**
- `status` - Filter by status
- `date_from` - Filter from date (YYYY-MM-DD)
- `date_to` - Filter to date (YYYY-MM-DD)
- `page` - Page number
- `page_size` - Results per page (default: 100)

**Response:** Same format as psychologist schedule, but uses `AppointmentListSerializer`

---

## Complete Video Session Flow for Psychologists

### **Step 1: Get Appointments List**
```typescript
// Get upcoming appointments
const appointments = await fetch('/api/appointments/psychologist/schedule/?status=confirmed', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());
```

### **Step 2: Select Appointment and Get Video Token**
```typescript
// Get video token for selected appointment
const appointmentId = 47;
const tokenData = await fetch(`/api/appointments/video-token/${appointmentId}/`, {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());
```

### **Step 3: Connect to Twilio Video**
```typescript
import Video from 'twilio-video';

const room = await Video.connect(tokenData.access_token, {
  name: tokenData.room_name,
  audio: true,
  video: true
});
```

### **Step 4: Monitor Token Expiration (Optional)**
```typescript
// Check if token is about to expire
const expiresAt = new Date(tokenData.expires_at);
const timeUntilExpiry = expiresAt.getTime() - Date.now();

// Refresh token 5 minutes before expiration
if (timeUntilExpiry < 5 * 60 * 1000) {
  const newToken = await fetch(`/api/appointments/video-token-refresh/${appointmentId}/`, {
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(r => r.json());
  
  // Reconnect with new token
  await reconnectWithNewToken(newToken.access_token);
}
```

### **Step 5: Check Room Status (Optional)**
```typescript
// Check who's in the room
const status = await fetch(`/api/appointments/video-status/${appointmentId}/`, {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

console.log(`Participants: ${status.participants_count}`);
console.log(`Room status: ${status.status}`);
```

---

## Summary

**Main Video Endpoint for Psychologists:**
```
GET /api/appointments/video-token/<appointment_id>/
```

**Get Appointments with Video Info:**
```
GET /api/appointments/psychologist/schedule/
```

**All Video Endpoints:**
1. `GET /api/appointments/video-token/<id>/` - Get access token
2. `GET /api/appointments/video-token-refresh/<id>/` - Refresh token
3. `GET /api/appointments/video-status/<id>/` - Check room status
4. `GET /api/appointments/psychologist/schedule/` - Get schedule with video info
5. `GET /api/appointments/` - Get appointments list (auto-filtered for psychologist)

**Important Notes:**
- All endpoints require authentication (Bearer Token)
- Psychologists can only access video sessions for their own appointments
- Token expiration is calculated based on appointment duration + 30 minutes buffer
- Use the refresh endpoint for long sessions to prevent disconnection

