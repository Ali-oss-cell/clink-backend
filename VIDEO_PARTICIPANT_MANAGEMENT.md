# Video Room Participant Management

## Overview

Complete participant management for Twilio Video rooms, including listing, retrieving, and removing participants.

---

## API Endpoints

### 1. List Participants in a Room

**GET** `/api/appointments/video-participants/<appointment_id>/`

Get all participants in a video room for an appointment.

**Query Parameters:**
- `status` (optional): Filter by status
  - `connected` - Currently connected participants
  - `disconnected` - Participants who have left
  - `reconnecting` - Participants reconnecting

**Permissions:**
- Appointment patient
- Appointment psychologist
- Admin
- Practice Manager

**Example Request:**
```bash
GET /api/appointments/video-participants/48/?status=connected
Authorization: Bearer <token>
```

**Example Response:**
```json
{
  "appointment_id": 48,
  "room_name": "apt-48-1763195593-abc123",
  "room_sid": "RMxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "room_status": "in-progress",
  "participants_count": 2,
  "participants": [
    {
      "sid": "PAxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "identity": "2-jane.doe@example.com",
      "status": "connected",
      "duration": null,
      "connected_at": "2025-11-16T10:00:00Z",
      "disconnected_at": null,
      "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "room_sid": "RMxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "date_created": "2025-11-16T10:00:00Z",
      "date_updated": "2025-11-16T10:00:00Z"
    },
    {
      "sid": "PAyyyyyyyyyyyyyyyyyyyyyyyyyy",
      "identity": "19-sarah.johnson@example.com",
      "status": "connected",
      "duration": null,
      "connected_at": "2025-11-16T10:01:00Z",
      "disconnected_at": null,
      "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "room_sid": "RMxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "date_created": "2025-11-16T10:01:00Z",
      "date_updated": "2025-11-16T10:01:00Z"
    }
  ],
  "filter": {
    "status": "connected"
  }
}
```

---

### 2. Get Specific Participant

**GET** `/api/appointments/video-participant/<appointment_id>/<participant_identity_or_sid>/`

Get details of a specific participant by their identity or SID.

**Parameters:**
- `appointment_id`: Appointment ID
- `participant_identity_or_sid`: Participant identity (e.g., `2-jane.doe@example.com`) or SID (e.g., `PAxxxxxxxxxxxxxxxxxxxxxxxxxx`)

**Permissions:**
- Appointment patient
- Appointment psychologist
- Admin
- Practice Manager

**Example Request:**
```bash
GET /api/appointments/video-participant/48/2-jane.doe@example.com/
Authorization: Bearer <token>
```

**Example Response:**
```json
{
  "appointment_id": 48,
  "room_name": "apt-48-1763195593-abc123",
  "room_sid": "RMxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "participant": {
    "sid": "PAxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "identity": "2-jane.doe@example.com",
    "status": "connected",
    "duration": null,
    "connected_at": "2025-11-16T10:00:00Z",
    "disconnected_at": null,
    "account_sid": "ACxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "room_sid": "RMxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "date_created": "2025-11-16T10:00:00Z",
    "date_updated": "2025-11-16T10:00:00Z",
    "url": "https://video.twilio.com/v1/Rooms/.../Participants/..."
  }
}
```

---

### 3. Remove/Kick Participant

**POST** `/api/appointments/video-participant/<appointment_id>/<participant_identity_or_sid>/remove/`

Remove a participant from the video room by setting their status to `disconnected`.

**Parameters:**
- `appointment_id`: Appointment ID
- `participant_identity_or_sid`: Participant identity or SID

**Permissions:**
- Appointment psychologist (can remove any participant)
- Admin
- Practice Manager

**Note:** Patients cannot remove participants.

**Example Request:**
```bash
POST /api/appointments/video-participant/48/2-jane.doe@example.com/remove/
Authorization: Bearer <token>
```

**Example Response:**
```json
{
  "message": "Participant removed successfully",
  "appointment_id": 48,
  "room_name": "apt-48-1763195593-abc123",
  "room_sid": "RMxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "participant": {
    "sid": "PAxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "identity": "2-jane.doe@example.com",
    "status": "disconnected",
    "duration": 120,
    "connected_at": "2025-11-16T10:00:00Z",
    "disconnected_at": "2025-11-16T10:02:00Z",
    "removed_at": "2025-11-16T10:02:00Z"
  }
}
```

---

## Video Service Methods

### `get_room_participants(room_sid, status=None)`

List participants in a room with optional status filter.

**Parameters:**
- `room_sid`: Room SID or room name
- `status` (optional): Filter by status ('connected', 'disconnected', 'reconnecting')

**Returns:** List of participant dictionaries

### `get_participant(room_sid, participant_identity_or_sid)`

Get a specific participant by identity or SID.

**Parameters:**
- `room_sid`: Room SID or room name
- `participant_identity_or_sid`: Participant identity or SID

**Returns:** Participant dictionary

### `remove_participant(room_sid, participant_identity_or_sid)`

Remove/kick a participant from a room.

**Parameters:**
- `room_sid`: Room SID or room name
- `participant_identity_or_sid`: Participant identity or SID

**Returns:** Updated participant dictionary with `status: 'disconnected'`

---

## Use Cases

### 1. Monitor Who's in the Room

```python
# Frontend can poll this endpoint to see who's connected
GET /api/appointments/video-participants/48/?status=connected
```

### 2. Check if Patient Joined

```python
# Check if patient has joined
GET /api/appointments/video-participant/48/2-jane.doe@example.com/
```

### 3. End Session Early (Psychologist)

```python
# Psychologist can end session by removing patient
POST /api/appointments/video-participant/48/2-jane.doe@example.com/remove/
```

### 4. Handle Disruptive Participants

```python
# Admin can remove any participant
POST /api/appointments/video-participant/48/PAxxxxxxxxxxxxxxxxxxxxxxxxxx/remove/
```

---

## Participant Identity Format

Participants are identified by their `identity` field, which is set when generating the access token:

- **Format**: `{user_id}-{email}`
- **Example**: `2-jane.doe@example.com`
- **Example**: `19-sarah.johnson@example.com`

This matches the format used in `GetVideoAccessTokenView`:
```python
user_identity = f"{user.id}-{user.email}"
```

---

## Status Values

- **`connected`**: Participant is currently in the room
- **`disconnected`**: Participant has left the room
- **`reconnecting`**: Participant is reconnecting (network issues)

---

## Error Responses

### 404 Not Found
```json
{
  "error": "Appointment not found"
}
```

```json
{
  "error": "No video room found for this appointment"
}
```

```json
{
  "error": "Participant not found"
}
```

### 403 Forbidden
```json
{
  "error": "Permission denied"
}
```

```json
{
  "error": "Only psychologists or admins can remove participants"
}
```

### 500 Internal Server Error
```json
{
  "error": "Failed to get participants: <error message>"
}
```

---

## Integration with Status Callbacks

When a participant is removed via the API, Twilio will send a `participant-disconnected` event to your status callback webhook (if configured).

The webhook will receive:
- `StatusCallbackEvent`: `participant-disconnected`
- `ParticipantSid`: Participant SID
- `ParticipantIdentity`: Participant identity
- `ParticipantDuration`: Total duration in room (seconds)

---

## Security Notes

1. **Permission Checks**: Only authorized users can view/remove participants
2. **Audit Logging**: Participant removal is logged via audit system
3. **Identity Validation**: Participants are identified by the identity set in their access token
4. **Room Access**: Users can only access participants in their own appointment rooms (unless admin)

---

## Frontend Integration Example

```typescript
// List connected participants
const getParticipants = async (appointmentId: number) => {
  const response = await fetch(
    `/api/appointments/video-participants/${appointmentId}/?status=connected`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  const data = await response.json();
  return data.participants;
};

// Remove a participant (psychologist only)
const removeParticipant = async (
  appointmentId: number,
  participantIdentity: string
) => {
  const response = await fetch(
    `/api/appointments/video-participant/${appointmentId}/${participantIdentity}/remove/`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return await response.json();
};
```

---

## Summary

✅ **List participants** - See who's in the room
✅ **Get participant details** - Check specific participant status
✅ **Remove participants** - Kick users from room (psychologist/admin only)
✅ **Status filtering** - Filter by connected/disconnected
✅ **Permission-based access** - Role-based access control
✅ **Audit logging** - All removals are logged

All participant management features are now available via the API!

