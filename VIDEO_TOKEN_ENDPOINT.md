# Video Token Endpoint - Complete Guide

## Endpoint for Getting Video Access Token

### **Full Endpoint URL:**
```
GET /api/appointments/video-token/<appointment_id>/
```

### **Example:**
```
GET /api/appointments/video-token/47/
```

---

## Authentication Required

**Method:** `GET`  
**Authentication:** Bearer Token (JWT)  
**Permission:** Must be the patient OR psychologist of the appointment

---

## Request

### **URL Parameters:**
- `appointment_id` (integer) - The ID of the appointment

### **Headers:**
```http
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

### **Example Request:**
```bash
curl -X GET http://localhost:8000/api/appointments/video-token/47/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json"
```

---

## Response

### **Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsImN0eSI6InR3aWxpby1mcGE7dj0xIiwidHlwIjoiSldUIiwiYWxnIjoiSFMyNTYifQ...",
  "room_name": "apt-47-1763138954-46eb915c",
  "user_identity": "2-jane.doe@example.com",
  "expires_in": 5400,
  "expires_at": "2025-11-16T10:30:00Z",
  "appointment_id": 47,
  "appointment_duration_minutes": 60,
  "token_valid_until": "90 minutes (1 hours)"
}
```

### **Response Fields:**
- `access_token` (string) - Twilio JWT token for joining the video room
- `room_name` (string) - The Twilio room name to connect to
- `user_identity` (string) - User identifier (format: `{user_id}-{email}`)
- `expires_in` (integer) - Token expiration time in seconds (calculated based on appointment duration)
- `expires_at` (string) - ISO 8601 timestamp when token expires
- `appointment_id` (integer) - The appointment ID
- `appointment_duration_minutes` (integer) - Duration of the appointment
- `token_valid_until` (string) - Human-readable description of token validity

**Token Validity Calculation:**
- Minimum: 60 minutes (1 hour)
- Maximum: 240 minutes (4 hours)
- Typical: Appointment duration + 30 minutes buffer
- Example: 60-minute appointment = 90-minute token validity

---

## ❌ **Error Responses**

### **403 Forbidden - Permission Denied**
```json
{
  "error": "Permission denied"
}
```
**Cause:** User is not the patient or psychologist of this appointment

### **404 Not Found - Appointment Not Found**
```json
{
  "error": "Appointment not found"
}
```
**Cause:** Appointment ID doesn't exist

### **404 Not Found - No Video Room**
```json
{
  "error": "No video room found for this appointment"
}
```
**Cause:** Appointment doesn't have a `video_room_id` set

### **500 Internal Server Error**
```json
{
  "error": "Failed to generate access token: <error_message>"
}
```
**Cause:** Server error (e.g., Twilio configuration issue)

---

## 💻 **Frontend Usage Example**

### **React/TypeScript:**
```typescript
async function getVideoToken(appointmentId: number, userToken: string) {
  try {
    const response = await fetch(
      `http://localhost:8000/api/appointments/video-token/${appointmentId}/`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json'
        }
      }
    );

    if (!response.ok) {
      throw new Error('Failed to get video token');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error getting video token:', error);
    throw error;
  }
}

// Usage
const tokenData = await getVideoToken(47, userJwtToken);
console.log('Access Token:', tokenData.access_token);
console.log('Room Name:', tokenData.room_name);
```

### **JavaScript:**
```javascript
async function getVideoToken(appointmentId, userToken) {
  const response = await fetch(
    `/api/appointments/video-token/${appointmentId}/`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${userToken}`,
        'Content-Type': 'application/json'
      }
    }
  );

  if (!response.ok) {
    throw new Error('Failed to get video token');
  }

  return await response.json();
}

// Usage
const tokenData = await getVideoToken(47, userJwtToken);
// Use tokenData.access_token to connect to Twilio
```

---

## 🎯 **Complete Flow Example**

### **Step 1: Get Access Token**
```typescript
// In your video call component
const appointmentId = 47; // From your appointment data
const userToken = localStorage.getItem('jwt_token'); // Your JWT token

const tokenData = await fetch(
  `/api/appointments/video-token/${appointmentId}/`,
  {
    headers: {
      'Authorization': `Bearer ${userToken}`
    }
  }
).then(res => res.json());

// tokenData contains:
// - access_token: Use this to connect to Twilio
// - room_name: The room to connect to
// - user_identity: Your user identifier
```

### **Step 2: Connect to Twilio Room**
```typescript
import Video from 'twilio-video';

// Use the token to connect
const room = await Video.connect(tokenData.access_token, {
  name: tokenData.room_name,
  audio: true,
  video: true
});

console.log('Connected to room:', room.name);
```

---

## 🔗 **Related Endpoints**

### **Create Video Room:**
```
POST /api/appointments/video-room/<appointment_id>/
```
Creates a video room for the appointment (if it doesn't exist)

### **Get Appointment Details:**
```
GET /api/appointments/<appointment_id>/
```
Returns appointment details including `video_room_id` if it exists

---

## ✅ **Test with Your Appointment**

For appointment #47 (Jane Doe with Dr. Sarah):

**Patient (Jane Doe):**
```bash
GET /api/appointments/video-token/47/
Authorization: Bearer <jane_doe_jwt_token>
```

**Psychologist (Dr. Sarah):**
```bash
GET /api/appointments/video-token/47/
Authorization: Bearer <sarah_jwt_token>
```

Both will get the same `room_name` but different `access_token` values.

---

## Notes

1. **Token Expiration:** Tokens expire based on appointment duration + 30 minutes buffer (minimum 1 hour, maximum 4 hours)
2. **Token Refresh:** Use `/api/appointments/video-token-refresh/<appointment_id>/` to get a new token before expiration
3. **Room Name:** Both users get the same `room_name` to join the same room
4. **User Identity:** Each user gets a unique `user_identity` based on their user ID and email
5. **Permissions:** Only the patient and psychologist can get tokens for their appointment
6. **Room Creation:** The room is automatically created in Twilio when the first user connects
7. **Expiration Timestamp:** Use `expires_at` field to monitor token expiration in frontend

---

## Related Endpoints

### **Refresh Video Token:**
```
GET /api/appointments/video-token-refresh/<appointment_id>/
```
Get a new access token before the current one expires. Use this for long sessions or when token is about to expire.

### **Get Video Room Status:**
```
GET /api/appointments/video-status/<appointment_id>/
```
Get current room status, participant count, and connection information.

---

## Quick Reference

| Method | Endpoint | Auth | Returns |
|--------|----------|------|---------|
| `GET` | `/api/appointments/video-token/<id>/` | Required | Access token + room info |
| `GET` | `/api/appointments/video-token-refresh/<id>/` | Required | New access token |
| `GET` | `/api/appointments/video-status/<id>/` | Required | Room status + participants |

**Full URL Example:**
```
http://localhost:8000/api/appointments/video-token/47/
```

