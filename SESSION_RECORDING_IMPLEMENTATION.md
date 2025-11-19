# Session Recording Storage & Access Implementation

## Overview

This document describes the complete implementation of session recording storage and access functionality for the psychology clinic backend. Recordings are stored in Twilio's cloud storage, and metadata is stored in the database for access control and audit logging.

## Features Implemented

### 1. Database Model (`SessionRecording`)

- **Location**: `appointments/models.py`
- **Purpose**: Stores recording metadata and links to Twilio storage
- **Fields**:
  - `appointment`: Foreign key to Appointment
  - `recording_sid`: Unique Twilio recording identifier
  - `media_uri`: Twilio URL to access recording
  - `media_external_location`: External storage location (optional)
  - `duration`: Recording duration in seconds
  - `size`: File size in bytes
  - `status`: started, completed, or failed
  - `participant_identity`: Participant who was recorded
  - `created_at`: When metadata was created
  - `completed_at`: When recording was completed

### 2. Webhook Handler Updates

- **Location**: `appointments/views.py` - `TwilioStatusCallbackView`
- **Events Handled**:
  - `recording-started`: Creates initial recording record
  - `recording-completed`: Updates recording with media URI and metadata
  - `recording-failed`: Updates recording status to failed

### 3. Access Endpoints

#### GET `/api/appointments/{appointment_id}/recording/`
- **Purpose**: Get recording for a specific appointment
- **Access Control**:
  - Patient: Can access their own recordings
  - Psychologist: Can access recordings of their sessions
  - Practice Manager: Can access all recordings
  - Admin: Can access all recordings
- **Response**: Full recording metadata with patient/psychologist names

#### GET `/api/appointments/recordings/`
- **Purpose**: List all recordings accessible to current user
- **Access Control**: Role-based filtering
  - Patients: Only their own recordings
  - Psychologists: Only their session recordings
  - Practice Managers/Admins: All recordings
- **Response**: Paginated list of recordings

#### GET `/api/appointments/recordings/{recording_id}/download/`
- **Purpose**: Get download URL for a recording
- **Access Control**: Same as appointment recording endpoint
- **Response**: Download URL and recording metadata

### 4. Audit Logging

All recording access is logged:
- `view_recording`: When a recording is viewed
- `list_recordings`: When recordings list is accessed
- `download_recording`: When download URL is requested

### 5. Admin Interface

- **Location**: `appointments/admin.py`
- **Features**:
  - List view with key fields
  - Search by recording SID, patient email, psychologist email
  - Filter by status and creation date
  - Read-only fields for metadata

## Database Migration

Migration file: `appointments/migrations/0002_add_session_recording.py`

To apply:
```bash
python manage.py migrate appointments
```

## API Usage Examples

### Get Recording for Appointment

```bash
GET /api/appointments/123/recording/
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "appointment_id": 123,
  "recording_sid": "RT1234567890abcdef",
  "media_uri": "https://video.twilio.com/v1/Recordings/RT1234567890abcdef",
  "duration": 3600,
  "duration_formatted": "60m 0s",
  "size": 52428800,
  "size_formatted": "50.00 MB",
  "status": "completed",
  "status_display": "Completed",
  "created_at": "2025-01-19T10:00:00Z",
  "completed_at": "2025-01-19T11:00:00Z",
  "patient_name": "John Doe",
  "psychologist_name": "Dr. Jane Smith"
}
```

### List Recordings

```bash
GET /api/appointments/recordings/?page=1&page_size=20
Authorization: Bearer <token>

Response:
{
  "count": 45,
  "next": "http://api.example.com/api/appointments/recordings/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "recording_sid": "RT1234567890abcdef",
      "appointment_date": "2025-01-19T10:00:00Z",
      "patient_name": "John Doe",
      "psychologist_name": "Dr. Jane Smith",
      "duration": 3600,
      "duration_formatted": "60m 0s",
      "size": 52428800,
      "size_formatted": "50.00 MB",
      "status": "completed",
      "created_at": "2025-01-19T10:00:00Z",
      "completed_at": "2025-01-19T11:00:00Z"
    }
  ]
}
```

### Get Download URL

```bash
GET /api/appointments/recordings/1/download/
Authorization: Bearer <token>

Response:
{
  "recording_id": 1,
  "appointment_id": 123,
  "download_url": "https://video.twilio.com/v1/Recordings/RT1234567890abcdef",
  "external_location": null,
  "duration": 3600,
  "size": 52428800,
  "size_formatted": "50.00 MB",
  "duration_formatted": "60m 0s",
  "created_at": "2025-01-19T10:00:00Z",
  "completed_at": "2025-01-19T11:00:00Z",
  "note": "Use the download_url to access the recording. This URL is provided by Twilio and may require authentication."
}
```

## Access Control Rules

1. **Patients**: Can only access recordings of their own appointments
2. **Psychologists**: Can access recordings of sessions they conducted
3. **Practice Managers**: Can access all recordings (for quality assurance)
4. **Admins**: Can access all recordings (full system access)

## Compliance & Security

### Privacy Act 1988 (APP 12)
- ✅ Patients have right to access their health records (including recordings)
- ✅ Access is logged for audit purposes
- ✅ Only authorized personnel can access recordings

### Audit Trail
- All recording access is logged with:
  - User who accessed
  - Timestamp
  - Recording ID
  - Action type (view/list/download)

### Data Retention
- Recordings are stored in Twilio cloud storage
- Metadata is stored in database
- Retention policy: 7 years (Australian healthcare requirement)
- Deletion should be handled through Twilio API when retention period expires

## Why We Need This

1. **Legal Compliance**: Australian Privacy Act requires patient access to health records
2. **Clinical Value**: Psychologists can review sessions for continuity of care
3. **Quality Assurance**: Practice managers can review for standards compliance
4. **Legal Protection**: Recordings serve as evidence if needed
5. **Transparency**: Builds trust with patients

## Next Steps

1. **Frontend Integration**: Create UI components for:
   - Recording list view
   - Recording playback/download
   - Recording access controls

2. **Retention Management**: Implement automated cleanup:
   - Celery task to check retention periods
   - Delete recordings after 7 years
   - Archive metadata before deletion

3. **Download Proxy**: Consider implementing a proxy endpoint:
   - Stream recordings through backend
   - Add additional access controls
   - Track download statistics

4. **Recording Consent**: Ensure recording consent is checked:
   - Before creating video room
   - Before enabling recording
   - Display consent status in UI

## Testing

To test the implementation:

1. **Create a test recording**:
   - Book an appointment
   - Enable recording consent
   - Start video session with recording enabled
   - Complete session
   - Check webhook receives recording-completed event

2. **Test access endpoints**:
   - As patient: Access own recording
   - As psychologist: Access session recording
   - As practice manager: Access all recordings
   - Verify access denied for unauthorized users

3. **Test audit logging**:
   - Access recordings
   - Check audit logs for access events
   - Verify metadata is logged correctly

## Files Modified

- `appointments/models.py`: Added `SessionRecording` model
- `appointments/serializers.py`: Added recording serializers
- `appointments/views.py`: Added recording endpoints and webhook updates
- `appointments/urls.py`: Added recording URL routes
- `appointments/admin.py`: Added admin interface
- `appointments/migrations/0002_add_session_recording.py`: Database migration

---

**Last Updated**: January 19, 2025
**Status**: ✅ Complete and Ready for Testing

