# Session Recording - User Access Guide

## 👥 Who Can Use Session Recordings?

The session recording functionality is available to **4 user roles** with different access levels:

---

## 1. 👤 **PATIENTS** 

### ✅ What They Can Do:
- **View recordings** of their own appointments only
- **Download recordings** of their own appointments
- **List all their recordings** (filtered to only their appointments)

### ❌ What They Cannot Do:
- Cannot see recordings of other patients
- Cannot see recordings of appointments they didn't attend
- Cannot access recordings before they're completed

### 📍 Where They See Recordings:
- In their appointment detail page
- In a "My Recordings" section/page
- When viewing past completed appointments

### 🔒 Access Control:
```python
# Patients can only access recordings where:
appointment.patient == current_user
```

---

## 2. 🧠 **PSYCHOLOGISTS**

### ✅ What They Can Do:
- **View recordings** of sessions they conducted
- **Download recordings** of their own sessions
- **List all recordings** of sessions they conducted

### ❌ What They Cannot Do:
- Cannot see recordings of other psychologists' sessions
- Cannot see recordings of patients they didn't treat
- Cannot access recordings before they're completed

### 📍 Where They See Recordings:
- In their appointment schedule/detail pages
- In a "My Session Recordings" section
- When reviewing past sessions

### 🔒 Access Control:
```python
# Psychologists can only access recordings where:
appointment.psychologist == current_user
```

---

## 3. 👔 **PRACTICE MANAGERS**

### ✅ What They Can Do:
- **View ALL recordings** in the system
- **Download ANY recording**
- **List all recordings** (no filtering)
- **Access recordings for quality assurance**

### ❌ What They Cannot Do:
- Cannot modify or delete recordings (read-only access)
- Cannot create recordings (only Twilio webhooks create them)

### 📍 Where They See Recordings:
- In a "All Recordings" admin page
- Can search/filter by patient, psychologist, date
- Can access recordings from any appointment

### 🔒 Access Control:
```python
# Practice managers can access ALL recordings:
# No filtering applied - full access
```

---

## 4. 🔑 **ADMINS**

### ✅ What They Can Do:
- **View ALL recordings** in the system
- **Download ANY recording**
- **List all recordings** (no filtering)
- **Full system access** (same as practice managers)

### ❌ What They Cannot Do:
- Cannot modify or delete recordings (read-only access)
- Cannot create recordings (only Twilio webhooks create them)

### 📍 Where They See Recordings:
- In admin dashboard
- In Django admin interface (via admin.py)
- Can access recordings from any appointment

### 🔒 Access Control:
```python
# Admins can access ALL recordings:
# No filtering applied - full access
```

---

## 📊 Access Summary Table

| User Role | View Own | View Others | View All | Download Own | Download Others | List All |
|-----------|----------|-------------|----------|--------------|-----------------|----------|
| **Patient** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ (only own) |
| **Psychologist** | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ (only own sessions) |
| **Practice Manager** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 🔐 Permission Checks

### For Individual Recording Access:
```python
# User can access recording if:
- User is the patient of the appointment, OR
- User is the psychologist of the appointment, OR
- User is a practice manager, OR
- User is an admin
```

### For Recording List:
```python
# Patients see:
- Only recordings where appointment.patient == user

# Psychologists see:
- Only recordings where appointment.psychologist == user

# Practice Managers/Admins see:
- ALL recordings (no filter)
```

---

## 📝 API Endpoints Access

### `GET /api/appointments/{appointment_id}/recording/`
- ✅ **Patient**: If it's their appointment
- ✅ **Psychologist**: If it's their session
- ✅ **Practice Manager**: Always
- ✅ **Admin**: Always

### `GET /api/appointments/recordings/`
- ✅ **Patient**: Lists only their recordings
- ✅ **Psychologist**: Lists only their session recordings
- ✅ **Practice Manager**: Lists all recordings
- ✅ **Admin**: Lists all recordings

### `GET /api/appointments/recordings/{recording_id}/download/`
- ✅ **Patient**: If it's their appointment
- ✅ **Psychologist**: If it's their session
- ✅ **Practice Manager**: Always
- ✅ **Admin**: Always

---

## 🛡️ Security Features

1. **Authentication Required**: All endpoints require login (`IsAuthenticated`)
2. **Role-Based Filtering**: Backend automatically filters based on user role
3. **Audit Logging**: All access is logged (who, when, what)
4. **Status Check**: Only `completed` recordings are accessible
5. **Permission Validation**: Double-checked at both list and detail levels

---

## 🎯 Use Cases

### Patient Use Case:
> "I want to review my therapy session from last week"
- Patient logs in
- Goes to "My Appointments"
- Clicks on completed appointment
- Sees "Recording Available" button
- Can view/download their recording

### Psychologist Use Case:
> "I need to review my session notes and the recording"
- Psychologist logs in
- Goes to "My Schedule" or "Past Sessions"
- Clicks on completed appointment
- Sees recording link
- Can view/download to review session

### Practice Manager Use Case:
> "I need to do quality assurance review of sessions"
- Practice Manager logs in
- Goes to "All Recordings" page
- Can search/filter by psychologist, patient, date
- Can access any recording for QA review

### Admin Use Case:
> "I need to check a recording for a support request"
- Admin logs in
- Goes to admin dashboard or recordings page
- Can access any recording
- Can also access via Django admin interface

---

## ⚠️ Important Notes

1. **Recording Status**: Only `completed` recordings are shown. `started` or `failed` recordings are not accessible.

2. **Recording Consent**: Recordings are only created if the patient has given consent (`telehealth_recording_consent = True`).

3. **No Direct Creation**: Users cannot manually create recordings. They are automatically created by Twilio webhooks when a session is recorded.

4. **Audit Trail**: Every access is logged for compliance and security.

5. **Privacy Compliance**: Access control ensures compliance with Australian Privacy Act 1988 (APP 12).

---

## 🧪 Testing Access

To test different user roles:

1. **Create test users** with different roles
2. **Create test appointments** with recordings
3. **Login as each role** and verify:
   - Patients only see their recordings
   - Psychologists only see their session recordings
   - Practice Managers/Admins see all recordings

---

**Last Updated**: January 19, 2025

