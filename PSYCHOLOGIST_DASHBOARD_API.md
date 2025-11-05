# 🧠 Psychologist Dashboard API

## 📡 **Endpoint**

```
GET /api/auth/psychologist/dashboard/
```

**Alternative URL** (also works):
```
GET /api/auth/dashboard/psychologist/
```

## 🔐 **Authentication**

Requires JWT Bearer token:
```
Authorization: Bearer <your_jwt_token>
```

## 📋 **Response Format**

```json
{
  "today_appointments_count": 5,
  "upcoming_appointments_this_week": 12,
  "recent_notes": [
    {
      "id": 1,
      "patient_name": "John Smith",
      "session_number": 3,
      "session_date": "2024-07-20T10:00:00Z",
      "progress_rating": 7,
      "created_at": "2024-07-20T10:45:00Z"
    }
  ],
  "active_patients_count": 25,
  "total_patients_count": 150,
  "pending_notes_count": 3,
  "completed_sessions_today": 2,
  "stats": {
    "total_appointments_this_month": 45,
    "average_rating": 4.8,
    "sessions_completed_this_week": 18
  }
}
```

## 📊 **Field Descriptions**

| Field | Type | Description |
|-------|------|-------------|
| `today_appointments_count` | integer | Number of appointments scheduled for today |
| `upcoming_appointments_this_week` | integer | Count of scheduled/confirmed appointments this week (Monday-Sunday) |
| `recent_notes` | array | Last 5 progress notes, ordered by creation date (newest first) |
| `active_patients_count` | integer | Patients with appointments in last 90 days or upcoming |
| `total_patients_count` | integer | Total unique patients seen by psychologist |
| `pending_notes_count` | integer | Completed sessions in last 7 days without progress notes |
| `completed_sessions_today` | integer | Number of appointments completed today |
| `stats.total_appointments_this_month` | integer | All appointments (any status) in current month |
| `stats.average_rating` | float | Average progress rating from all notes (1-10 scale) |
| `stats.sessions_completed_this_week` | integer | Completed sessions this week (Monday-Sunday) |

## 🎯 **Recent Notes Structure**

Each note in `recent_notes` contains:
- `id`: Note ID
- `patient_name`: Full name of patient
- `session_number`: Session number for this patient
- `session_date`: ISO format date/time of session
- `progress_rating`: Rating (1-10) or null
- `created_at`: ISO format timestamp when note was created

## ✅ **Status Codes**

- **200 OK**: Dashboard data returned successfully
- **401 Unauthorized**: Missing or invalid JWT token
- **403 Forbidden**: User is not a psychologist

## 📝 **Example Usage**

### cURL
```bash
curl -X GET "http://localhost:8000/api/auth/psychologist/dashboard/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### JavaScript/TypeScript
```typescript
const response = await fetch('/api/auth/psychologist/dashboard/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const dashboardData = await response.json();
```

## 🔄 **Data Calculations**

- **Week**: Monday to Sunday (current week)
- **Month**: First day to last day of current month
- **Active Patients**: Patients with appointments in last 90 days OR with upcoming scheduled/confirmed appointments
- **Pending Notes**: Completed appointments in last 7 days that don't have a corresponding progress note

## 🚀 **Performance Notes**

- Single database query per statistic
- Optimized with `select_related` for patient data
- Returns only last 5 recent notes (not paginated)
- All counts are calculated in real-time

