# Patient Appointments API Documentation

## Overview
This document describes the Patient Appointments List API endpoint that provides detailed appointment information for patients in the psychology clinic system.

## Endpoint Details

### Get Patient Appointments
**Endpoint:** `GET /api/appointments/patient/appointments/`

**Authentication:** Required (JWT Token)

**Description:** Returns a paginated list of all appointments for the authenticated patient with comprehensive details including psychologist information, appointment status, and action capabilities.

---

## Request

### Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | `all` | Filter appointments by status: `upcoming`, `completed`, `cancelled`, `past`, `all` |
| `page` | integer | No | `1` | Page number for pagination |
| `page_size` | integer | No | `10` | Number of results per page |

### Example Requests

#### Get all appointments (default)
```bash
GET /api/appointments/patient/appointments/
```

#### Get only upcoming appointments
```bash
GET /api/appointments/patient/appointments/?status=upcoming
```

#### Get completed appointments with pagination
```bash
GET /api/appointments/patient/appointments/?status=completed&page=1&page_size=20
```

---

## Response

### Success Response (200 OK)

#### Response Structure
```json
{
  "count": 15,
  "next": "http://localhost:8000/api/appointments/patient/appointments/?page=2&page_size=10",
  "previous": null,
  "results": [
    {
      "id": "apt-001",
      "appointment_date": "2024-01-20T10:00:00+11:00",
      "formatted_date": "2024-01-20",
      "formatted_time": "10:00 AM",
      "duration_minutes": 50,
      "session_type": "in_person",
      "status": "upcoming",
      "psychologist": {
        "name": "Dr. Sarah Johnson",
        "title": "Clinical Psychologist",
        "profile_image_url": "https://example.com/media/psychologist_profiles/dr_sarah_profile.jpg"
      },
      "location": "MindWell Clinic",
      "meeting_link": null,
      "notes": "Initial consultation",
      "can_reschedule": true,
      "can_cancel": true,
      "reschedule_deadline": "2024-01-18T10:00:00+11:00",
      "cancellation_deadline": "2024-01-19T10:00:00+11:00"
    }
  ]
}
```

### Response Fields

#### Root Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `count` | integer | Total number of appointments matching the filter |
| `next` | string/null | URL to the next page of results (null if no next page) |
| `previous` | string/null | URL to the previous page of results (null if no previous page) |
| `results` | array | Array of appointment objects |

#### Appointment Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique appointment identifier |
| `appointment_date` | string (ISO 8601) | Full datetime in ISO format with timezone |
| `formatted_date` | string | Date formatted as YYYY-MM-DD |
| `formatted_time` | string | Time formatted as HH:MM AM/PM |
| `duration_minutes` | integer | Duration of the appointment in minutes |
| `session_type` | string | Type of session: `telehealth` or `in_person` |
| `status` | string | Current status: `upcoming`, `completed`, `cancelled`, `no_show`, `past` |
| `psychologist` | object | Psychologist details object |
| `location` | string/null | Physical location for in-person appointments, null for telehealth |
| `meeting_link` | string/null | Video meeting link for telehealth appointments, null for in-person |
| `notes` | string/null | Additional notes about the appointment |
| `can_reschedule` | boolean | Whether the appointment can be rescheduled (48 hours before) |
| `can_cancel` | boolean | Whether the appointment can be cancelled (24 hours before) |
| `reschedule_deadline` | string (ISO 8601) | Last datetime when rescheduling is allowed |
| `cancellation_deadline` | string (ISO 8601) | Last datetime when cancellation is allowed |

#### Psychologist Object Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Full name with title (e.g., "Dr. Sarah Johnson") |
| `title` | string | Professional title (e.g., "Clinical Psychologist") |
| `profile_image_url` | string/null | Full URL to psychologist's profile image, null if not available |

---

## Status Filtering

### Available Status Filters

| Status Value | Description | What It Returns |
|--------------|-------------|-----------------|
| `all` | All appointments | Every appointment regardless of status |
| `upcoming` | Upcoming appointments | Appointments in the future with status `scheduled` or `confirmed` |
| `completed` | Completed appointments | Appointments marked as `completed` |
| `cancelled` | Cancelled appointments | Appointments marked as `cancelled` |
| `past` | Past appointments | Appointments in the past or with terminal status (`completed`, `cancelled`, `no_show`) |

---

## Status Values

The `status` field in the response can have the following values:

| Status | Description |
|--------|-------------|
| `upcoming` | Appointment is scheduled for the future |
| `past` | Appointment date has passed but not marked as completed |
| `completed` | Appointment was successfully completed |
| `cancelled` | Appointment was cancelled |
| `no_show` | Patient did not show up for the appointment |

---

## Session Types

| Type | Description |
|------|-------------|
| `telehealth` | Virtual appointment via video call |
| `in_person` | Physical appointment at clinic location |

---

## Business Rules

### Rescheduling Rules
- Appointments can be rescheduled up to **48 hours** before the scheduled time
- Completed, cancelled, or no-show appointments cannot be rescheduled
- The `can_reschedule` field indicates whether rescheduling is allowed
- The `reschedule_deadline` field shows the exact cutoff datetime

### Cancellation Rules
- Appointments can be cancelled up to **24 hours** before the scheduled time
- Completed, cancelled, or no-show appointments cannot be cancelled
- The `can_cancel` field indicates whether cancellation is allowed
- The `cancellation_deadline` field shows the exact cutoff datetime

### Location & Meeting Link Logic
- **In-person appointments**: `location` contains clinic name/address, `meeting_link` is null
- **Telehealth appointments**: `meeting_link` contains video call URL, `location` is null

---

## Example Usage

### cURL Example

```bash
# Get upcoming appointments
curl -X GET \
  'http://localhost:8000/api/appointments/patient/appointments/?status=upcoming' \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...' \
  -H 'Content-Type: application/json'
```

### JavaScript (Fetch API) Example

```javascript
// Get all appointments with pagination
const getAppointments = async (page = 1, status = 'all') => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch(
      `http://localhost:8000/api/appointments/patient/appointments/?status=${status}&page=${page}&page_size=10`,
      {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (!response.ok) {
      throw new Error('Failed to fetch appointments');
    }
    
    const data = await response.json();
    console.log(`Total appointments: ${data.count}`);
    console.log('Appointments:', data.results);
    
    return data;
  } catch (error) {
    console.error('Error:', error);
  }
};

// Usage
getAppointments(1, 'upcoming');
```

### Python (Requests) Example

```python
import requests

def get_patient_appointments(token, status='all', page=1, page_size=10):
    """
    Get patient appointments from the API
    
    Args:
        token: JWT access token
        status: Filter by status (all, upcoming, completed, cancelled, past)
        page: Page number
        page_size: Number of results per page
    
    Returns:
        dict: API response with appointments data
    """
    url = 'http://localhost:8000/api/appointments/patient/appointments/'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    params = {
        'status': status,
        'page': page,
        'page_size': page_size
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    return response.json()

# Usage
data = get_patient_appointments(
    token='your_jwt_token_here',
    status='upcoming',
    page=1,
    page_size=20
)

print(f"Total appointments: {data['count']}")
for appointment in data['results']:
    print(f"Appointment with {appointment['psychologist']['name']} on {appointment['formatted_date']}")
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Cause:** Missing or invalid JWT token

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Cause:** User is not authenticated or doesn't have patient role

### 400 Bad Request
```json
{
  "error": "Invalid page number"
}
```

**Cause:** Invalid query parameter values

---

## Frontend Integration Tips

### 1. Display Upcoming Appointments Dashboard
```javascript
const loadUpcomingAppointments = async () => {
  const data = await getAppointments(1, 'upcoming');
  
  data.results.forEach(appointment => {
    // Display appointment card
    console.log(`
      Date: ${appointment.formatted_date}
      Time: ${appointment.formatted_time}
      Psychologist: ${appointment.psychologist.name}
      Type: ${appointment.session_type}
      Can Cancel: ${appointment.can_cancel}
    `);
  });
};
```

### 2. Enable/Disable Action Buttons
```javascript
const renderActionButtons = (appointment) => {
  return `
    <button 
      ${appointment.can_reschedule ? '' : 'disabled'} 
      onclick="reschedule('${appointment.id}')">
      Reschedule
    </button>
    <button 
      ${appointment.can_cancel ? '' : 'disabled'} 
      onclick="cancel('${appointment.id}')">
      Cancel
    </button>
  `;
};
```

### 3. Show Meeting Link for Telehealth
```javascript
const renderAppointmentDetails = (appointment) => {
  if (appointment.session_type === 'telehealth' && appointment.meeting_link) {
    return `
      <a href="${appointment.meeting_link}" target="_blank">
        Join Video Session
      </a>
    `;
  } else if (appointment.session_type === 'in_person') {
    return `
      <p>Location: ${appointment.location}</p>
    `;
  }
};
```

### 4. Implement Pagination
```javascript
const handlePagination = (data) => {
  const paginationInfo = {
    currentPage: Math.floor((data.results.length - 1) / pageSize) + 1,
    totalPages: Math.ceil(data.count / pageSize),
    hasNext: !!data.next,
    hasPrevious: !!data.previous
  };
  
  // Render pagination controls
  return paginationInfo;
};
```

---

## Testing

### Test Checklist

- [ ] Get all appointments without filters
- [ ] Get only upcoming appointments
- [ ] Get completed appointments
- [ ] Get cancelled appointments
- [ ] Get past appointments
- [ ] Test pagination (next page)
- [ ] Test pagination (previous page)
- [ ] Verify appointment details are correct
- [ ] Verify psychologist information is populated
- [ ] Verify profile images load correctly
- [ ] Test can_reschedule logic (48 hours before)
- [ ] Test can_cancel logic (24 hours before)
- [ ] Verify meeting link for telehealth appointments
- [ ] Verify location for in-person appointments
- [ ] Test authentication (401 without token)
- [ ] Test with different page sizes

---

## Related Endpoints

This endpoint works in conjunction with other appointment management endpoints:

- **Cancel Appointment:** `POST /api/appointments/cancel/<appointment_id>/`
- **Reschedule Appointment:** `POST /api/appointments/reschedule/<appointment_id>/`
- **Book Appointment:** `POST /api/appointments/book/`
- **Get Appointment Summary:** `GET /api/appointments/summary/`

---

## Notes

1. **Timezone Handling:** All datetime values are returned in ISO 8601 format with timezone information. The server uses the timezone configured in Django settings.

2. **Profile Images:** Profile image URLs are absolute URLs. If no profile image is set, the field will be `null`.

3. **Performance:** The endpoint uses `select_related()` to optimize database queries by reducing the number of queries needed to fetch psychologist and service information.

4. **Default Ordering:** Appointments are ordered by `appointment_date` in descending order (most recent first).

5. **Patient-Only Access:** This endpoint is specifically designed for patients. Psychologists should use the psychologist-specific appointment endpoints.

---

## Support

For issues or questions about this endpoint, please contact the development team or refer to the main project documentation.

