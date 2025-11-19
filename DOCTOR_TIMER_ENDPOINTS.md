# Doctor/Psychologist Timer Endpoints

## ✅ Yes! Doctors Get the Same Timer Data

All timer fields are now available for doctors/psychologists through multiple endpoints. This document explains which endpoints doctors can use to get session timer information.

---

## 🎯 Endpoints for Doctors/Psychologists

### 1. **Main Appointments List** (Recommended)
**Endpoint:** `GET /api/appointments/`

**Description:** Returns all appointments for the logged-in psychologist with timer fields included.

**Response Format:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 48,
      "patient": 2,
      "patient_name": "Jane Doe",
      "psychologist": 19,
      "psychologist_name": "Sarah Johnson",
      "service": 7,
      "service_name": "Couples Therapy",
      "appointment_date": "2025-11-16",
      "appointment_time": "08:33:13",
      "duration_minutes": 60,
      "status": "confirmed",
      "status_display": "Confirmed",
      "session_type": "telehealth",
      "session_start_time": "2025-11-16T08:33:13.400627+00:00",
      "session_end_time": "2025-11-16T09:33:13.400627+00:00",
      "time_until_start_seconds": 84363,
      "time_remaining_seconds": null,
      "session_status": "upcoming",
      "can_join_session": false,
      "notes": "",
      "created_at": "2025-11-15T19:33:13.415408+11:00",
      "updated_at": "2025-11-15T19:33:13.415423+11:00"
    }
  ]
}
```

**Query Parameters:**
- `status` - Filter by status (scheduled, confirmed, completed, cancelled, no_show)
- `date_from` - Filter from date (YYYY-MM-DD)
- `date_to` - Filter to date (YYYY-MM-DD)
- `page` - Page number
- `page_size` - Results per page (default: 100)

**Usage:**
```typescript
// Get all appointments with timer data
const response = await fetch('/api/appointments/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const data = await response.json();
// data.results contains appointments with timer fields
```

---

### 2. **Appointment Detail**
**Endpoint:** `GET /api/appointments/{id}/`

**Description:** Returns detailed information about a specific appointment with timer fields.

**Response Format:**
```json
{
  "id": 48,
  "patient": 2,
  "patient_name": "Jane Doe",
  "psychologist": 19,
  "psychologist_name": "Sarah Johnson",
  "service": 7,
  "service_name": "Couples Therapy",
  "appointment_date": "2025-11-16T08:33:13.400627Z",
  "formatted_date": "16/11/2025 08:33 AM",
  "duration_minutes": 60,
  "duration_hours": 1.0,
  "status": "confirmed",
  "status_display": "Confirmed",
  "session_type": "telehealth",
  "session_start_time": "2025-11-16T08:33:13.400627+00:00",
  "session_end_time": "2025-11-16T09:33:13.400627+00:00",
  "time_until_start_seconds": 84363,
  "time_remaining_seconds": null,
  "session_status": "upcoming",
  "can_join_session": false,
  "notes": "",
  "video_room_id": "test-session-1763195593-3400",
  "created_at": "2025-11-15T19:33:13.415408+11:00",
  "updated_at": "2025-11-15T19:33:13.415423+11:00"
}
```

**Usage:**
```typescript
// Get specific appointment with timer data
const response = await fetch(`/api/appointments/${appointmentId}/`, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const appointment = await response.json();
// appointment contains all timer fields
```

---

### 3. **Psychologist Schedule** (Specialized for Doctors)
**Endpoint:** `GET /api/appointments/psychologist/schedule/`

**Description:** Specialized endpoint for psychologist schedule view with formatted dates and timer fields.

**Response Format:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 48,
      "patient_id": 2,
      "patient_name": "Jane Doe",
      "service_name": "Couples Therapy",
      "appointment_date": "2025-11-16T08:33:13.400627Z",
      "formatted_date": "16 Nov 2025",
      "formatted_time": "8:33 AM",
      "duration_minutes": 60,
      "session_type": "telehealth",
      "status": "confirmed",
      "session_start_time": "2025-11-16T08:33:13.400627+00:00",
      "session_end_time": "2025-11-16T09:33:13.400627+00:00",
      "time_until_start_seconds": 84363,
      "time_remaining_seconds": null,
      "session_status": "upcoming",
      "can_join_session": false,
      "notes": "",
      "location": null,
      "meeting_link": "https://meet.psychologyclinic.com.au/test-session-1763195593-3400"
    }
  ]
}
```

**Query Parameters:**
- `start_date` - Filter from date (YYYY-MM-DD)
- `end_date` - Filter to date (YYYY-MM-DD)
- `month` - Filter by month (YYYY-MM)
- `year` - Filter by year (YYYY)
- `status` - Filter by status (scheduled, confirmed, completed, cancelled, no_show, all)
- `page` - Page number (default: 1)
- `page_size` - Results per page (default: 50)

**Usage:**
```typescript
// Get psychologist schedule with timer data
const response = await fetch('/api/appointments/psychologist/schedule/?status=confirmed', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const data = await response.json();
// data.results contains appointments with timer fields
```

---

### 4. **Upcoming Appointments**
**Endpoint:** `GET /api/appointments/upcoming/`

**Description:** Returns only upcoming appointments (future appointments with status 'scheduled' or 'confirmed').

**Response Format:** Same as main appointments list, but filtered to upcoming only.

**Usage:**
```typescript
// Get only upcoming appointments
const response = await fetch('/api/appointments/upcoming/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const appointments = await response.json();
// appointments contains upcoming appointments with timer fields
```

---

### 5. **Today's Appointments**
**Endpoint:** `GET /api/appointments/today/`

**Description:** Returns all appointments scheduled for today.

**Response Format:** Same as main appointments list, but filtered to today only.

**Usage:**
```typescript
// Get today's appointments
const response = await fetch('/api/appointments/today/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const appointments = await response.json();
// appointments contains today's appointments with timer fields
```

---

## 📊 Timer Fields Available in All Endpoints

All endpoints return these timer fields:

| Field | Type | Description |
|-------|------|-------------|
| `session_start_time` | string (ISO) | Exact start time of session |
| `session_end_time` | string (ISO) | Exact end time of session |
| `time_until_start_seconds` | number or null | Seconds until session starts |
| `time_remaining_seconds` | number or null | Seconds remaining in session |
| `session_status` | string | Status: `upcoming`, `starting_soon`, `in_progress`, `ended` |
| `can_join_session` | boolean | Whether user can join video session |

---

## 🎯 Recommended Endpoint for Doctors

**For Schedule/Calendar View:**
- Use: `/api/appointments/psychologist/schedule/`
- Why: Includes formatted dates, meeting links, and all timer fields

**For List View:**
- Use: `/api/appointments/`
- Why: Standard format, includes all timer fields, supports filtering

**For Detail View:**
- Use: `/api/appointments/{id}/`
- Why: Complete appointment details with timer fields

---

## 💻 Frontend Implementation Example

```typescript
// Example: Fetch appointments with timer data for doctor
const fetchDoctorAppointments = async () => {
  try {
    const response = await fetch('/api/appointments/psychologist/schedule/', {
      headers: {
        'Authorization': `Bearer ${authToken}`,
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response.json();
    
    // Each appointment in data.results has timer fields
    data.results.forEach(appointment => {
      console.log('Appointment:', appointment.patient_name);
      console.log('Time until start:', appointment.time_until_start_seconds);
      console.log('Session status:', appointment.session_status);
      console.log('Can join:', appointment.can_join_session);
    });
    
    return data.results;
  } catch (error) {
    console.error('Error fetching appointments:', error);
  }
};
```

---

## ✅ Summary

**Yes, doctors get the same timer data!** All endpoints that return appointment data for psychologists now include:

1. ✅ Session start/end times
2. ✅ Countdown timer (time until start)
3. ✅ Remaining time (during session)
4. ✅ Session status
5. ✅ Can join session flag

**Use any of these endpoints:**
- `/api/appointments/` - Main list
- `/api/appointments/{id}/` - Detail view
- `/api/appointments/psychologist/schedule/` - Schedule view (recommended for doctors)
- `/api/appointments/upcoming/` - Upcoming only
- `/api/appointments/today/` - Today only

All endpoints automatically filter to show only the psychologist's own appointments based on authentication.

