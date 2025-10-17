# Patient Appointments Endpoint - Flow Diagram

## 🔄 Request Flow

```
┌─────────────────┐
│  Frontend App   │
│  (React/Vue/JS) │
└────────┬────────┘
         │
         │ GET /api/appointments/patient/appointments/
         │ ?status=upcoming&page=1&page_size=10
         │ Authorization: Bearer <JWT_TOKEN>
         │
         ▼
┌─────────────────────────────────────────────────┐
│         Django REST Framework                   │
│  ┌───────────────────────────────────────────┐ │
│  │  1. Authentication Check                  │ │
│  │     - Verify JWT Token                    │ │
│  │     - Identify Patient User               │ │
│  └───────────────┬───────────────────────────┘ │
│                  │                              │
│  ┌───────────────▼───────────────────────────┐ │
│  │  2. PatientAppointmentsListView          │ │
│  │     - Parse query parameters             │ │
│  │     - status, page, page_size            │ │
│  └───────────────┬───────────────────────────┘ │
│                  │                              │
│  ┌───────────────▼───────────────────────────┐ │
│  │  3. Database Query (PostgreSQL/SQLite)   │ │
│  │     - Filter: patient = current_user     │ │
│  │     - Filter: status (if specified)      │ │
│  │     - select_related: psychologist       │ │
│  │     - select_related: profile            │ │
│  │     - Order by: appointment_date DESC    │ │
│  └───────────────┬───────────────────────────┘ │
│                  │                              │
│  ┌───────────────▼───────────────────────────┐ │
│  │  4. Apply Pagination                     │ │
│  │     - Calculate start_index              │ │
│  │     - Calculate end_index                │ │
│  │     - Slice queryset                     │ │
│  └───────────────┬───────────────────────────┘ │
│                  │                              │
│  ┌───────────────▼───────────────────────────┐ │
│  │  5. Serialize Data                       │ │
│  │     - PatientAppointmentDetailSerializer │ │
│  │     - Format dates and times             │ │
│  │     - Get psychologist details           │ │
│  │     - Calculate can_reschedule           │ │
│  │     - Calculate can_cancel               │ │
│  │     - Generate meeting links             │ │
│  └───────────────┬───────────────────────────┘ │
│                  │                              │
│  ┌───────────────▼───────────────────────────┐ │
│  │  6. Build Response                       │ │
│  │     - count: total_count                 │ │
│  │     - next: next_page_url                │ │
│  │     - previous: previous_page_url        │ │
│  │     - results: serialized_appointments   │ │
│  └───────────────┬───────────────────────────┘ │
└──────────────────┼───────────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  JSON Response  │
         │  Status: 200 OK │
         └─────────────────┘
```

---

## 🗄️ Database Query Flow

```
┌──────────────────────────────────────────────────────┐
│  Query Building Process                              │
├──────────────────────────────────────────────────────┤
│                                                      │
│  1. Base Query:                                      │
│     Appointment.objects.filter(patient=current_user) │
│                                                      │
│  2. Optimization:                                    │
│     .select_related('psychologist')                  │
│     .select_related('psychologist__psychologist_     │
│                      profile')                       │
│     .select_related('service')                       │
│                                                      │
│  3. Status Filter (if provided):                     │
│     ┌─ upcoming → appointment_date >= now            │
│     │            status IN ['scheduled','confirmed'] │
│     │                                                │
│     ├─ completed → status = 'completed'              │
│     │                                                │
│     ├─ cancelled → status = 'cancelled'              │
│     │                                                │
│     ├─ past → appointment_date < now OR              │
│     │         status IN ['completed','cancelled',    │
│     │                    'no_show']                  │
│     │                                                │
│     └─ all → no additional filter                    │
│                                                      │
│  4. Ordering:                                        │
│     .order_by('-appointment_date')                   │
│                                                      │
│  5. Pagination:                                      │
│     [start_index:end_index]                          │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 📊 Data Transformation Flow

```
┌────────────────────┐
│  Database Record   │
│  (Appointment)     │
└─────────┬──────────┘
          │
          ▼
┌─────────────────────────────────────────────┐
│  PatientAppointmentDetailSerializer         │
├─────────────────────────────────────────────┤
│                                             │
│  Raw Data → Transformed Data                │
│                                             │
│  appointment_date (datetime)                │
│    ├─→ appointment_date (ISO 8601)          │
│    ├─→ formatted_date (YYYY-MM-DD)          │
│    └─→ formatted_time (HH:MM AM/PM)         │
│                                             │
│  psychologist (User object)                 │
│    └─→ psychologist: {                      │
│         name: "Dr. Sarah Johnson"           │
│         title: "Clinical Psychologist"      │
│         profile_image_url: "https://..."    │
│       }                                     │
│                                             │
│  status (database field)                    │
│    └─→ status (computed):                   │
│         - scheduled/confirmed + future      │
│           → "upcoming"                      │
│         - scheduled/confirmed + past        │
│           → "past"                          │
│         - completed → "completed"           │
│         - cancelled → "cancelled"           │
│         - no_show → "no_show"               │
│                                             │
│  session_type + video_room_id               │
│    ├─→ location (if in_person)              │
│    └─→ meeting_link (if telehealth)         │
│                                             │
│  appointment_date + current_time            │
│    ├─→ can_reschedule (48-hour rule)        │
│    ├─→ can_cancel (24-hour rule)            │
│    ├─→ reschedule_deadline                  │
│    └─→ cancellation_deadline                │
│                                             │
└─────────────────────────────────────────────┘
          │
          ▼
┌────────────────────┐
│  JSON Response     │
│  (Frontend Ready)  │
└────────────────────┘
```

---

## 🔐 Authentication & Authorization Flow

```
┌──────────────────┐
│  Client Request  │
└────────┬─────────┘
         │
         ▼
┌────────────────────────────┐
│  JWT Token Present?        │
├────────┬───────────────────┤
│  NO    │  YES              │
│   │    │   │               │
│   │    │   ▼               │
│   │    │ ┌─────────────────────┐
│   │    │ │  Verify Token       │
│   │    │ │  - Signature valid? │
│   │    │ │  - Not expired?     │
│   │    │ └──────┬──────────────┘
│   │    │        │              │
│   │    │    Valid  Invalid     │
│   │    │      │      │         │
│   ▼    ▼      │      ▼         │
│  ┌────────────┘   ┌──────────┐ │
│  │              │ │  401     │ │
│  │              │ │  Error   │ │
│  │              │ └──────────┘ │
│  │              │              │
│  │              ▼              │
│  │  ┌──────────────────────┐  │
│  │  │  Extract User from   │  │
│  │  │  Token               │  │
│  │  └──────┬───────────────┘  │
│  │         │                  │
│  │         ▼                  │
│  │  ┌──────────────────────┐  │
│  │  │  User is Patient?    │  │
│  │  ├─────────┬────────────┤  │
│  │  │  YES    │  NO        │  │
│  │  │   │     │   │        │  │
│  │  │   │     │   ▼        │  │
│  │  │   │     │ ┌──────────┤  │
│  │  │   │     │ │  403     │  │
│  │  │   │     │ │  Error   │  │
│  │  │   │     │ └──────────┘  │
│  │  │   │     │              │
│  │  │   ▼     │              │
│  │  │ ┌──────────────────┐  │
│  │  │ │  Process Request │  │
│  │  │ │  Return Data     │  │
│  │  │ └──────────────────┘  │
└──┴──┴─────────────────────────┘
```

---

## 🎯 Status Filtering Logic

```
Input: status query parameter

┌─────────────────────────────────────────────────┐
│  Status Filter Decision Tree                    │
├─────────────────────────────────────────────────┤
│                                                 │
│  status = ?                                     │
│     │                                           │
│     ├─ "upcoming"                               │
│     │    └─ Filter:                             │
│     │        - appointment_date >= now          │
│     │        - status IN ['scheduled',          │
│     │                     'confirmed']          │
│     │                                           │
│     ├─ "completed"                              │
│     │    └─ Filter:                             │
│     │        - status = 'completed'             │
│     │                                           │
│     ├─ "cancelled"                              │
│     │    └─ Filter:                             │
│     │        - status = 'cancelled'             │
│     │                                           │
│     ├─ "past"                                   │
│     │    └─ Filter:                             │
│     │        - appointment_date < now OR        │
│     │        - status IN ['completed',          │
│     │                     'cancelled',          │
│     │                     'no_show']            │
│     │                                           │
│     └─ "all" (default)                          │
│          └─ No additional filter                │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## 📄 Pagination Logic

```
Input: 
- page = 2
- page_size = 10
- total_count = 25

┌─────────────────────────────────────────────────┐
│  Pagination Calculation                         │
├─────────────────────────────────────────────────┤
│                                                 │
│  1. Calculate Indices:                          │
│     start_index = (page - 1) × page_size        │
│                 = (2 - 1) × 10                  │
│                 = 10                            │
│                                                 │
│     end_index = start_index + page_size         │
│               = 10 + 10                         │
│               = 20                              │
│                                                 │
│  2. Slice Queryset:                             │
│     queryset[10:20]                             │
│     Returns: records 10-19 (10 records)         │
│                                                 │
│  3. Check for Next Page:                        │
│     if end_index < total_count:                 │
│        20 < 25 → YES                            │
│        next = page 3                            │
│                                                 │
│  4. Check for Previous Page:                    │
│     if page > 1:                                │
│        2 > 1 → YES                              │
│        previous = page 1                        │
│                                                 │
│  5. Build URLs:                                 │
│     next = "...?page=3&page_size=10"            │
│     previous = "...?page=1&page_size=10"        │
│                                                 │
└─────────────────────────────────────────────────┘

Result:
{
  "count": 25,
  "next": "http://...?page=3&page_size=10",
  "previous": "http://...?page=1&page_size=10",
  "results": [10 appointments]
}
```

---

## 🕐 Reschedule & Cancel Logic

```
┌──────────────────────────────────────────────────┐
│  Can Reschedule/Cancel Decision                  │
├──────────────────────────────────────────────────┤
│                                                  │
│  Appointment Status Check:                       │
│     │                                            │
│     ├─ Status = 'completed'    → NO             │
│     ├─ Status = 'cancelled'    → NO             │
│     ├─ Status = 'no_show'      → NO             │
│     └─ Status = 'scheduled' or 'confirmed'      │
│          │                                       │
│          ▼                                       │
│  Time Check:                                     │
│                                                  │
│  can_reschedule:                                 │
│     now = current_time                           │
│     deadline = appointment_date - 48 hours       │
│     if now < deadline → YES                      │
│     else → NO                                    │
│                                                  │
│  can_cancel:                                     │
│     now = current_time                           │
│     deadline = appointment_date - 24 hours       │
│     if now < deadline → YES                      │
│     else → NO                                    │
│                                                  │
└──────────────────────────────────────────────────┘

Example:
  Appointment: Jan 20, 2024 10:00 AM
  Current:     Jan 17, 2024 08:00 AM
  
  Reschedule Deadline: Jan 18, 2024 10:00 AM
  Current < Deadline → can_reschedule = true
  
  Cancellation Deadline: Jan 19, 2024 10:00 AM
  Current < Deadline → can_cancel = true
```

---

## 🏥 Location & Meeting Link Logic

```
┌────────────────────────────────────────────────┐
│  Session Type Handling                         │
├────────────────────────────────────────────────┤
│                                                │
│  session_type = ?                              │
│     │                                          │
│     ├─ "in_person"                             │
│     │    ├─ location:                          │
│     │    │    - Get psychologist.practice_name │
│     │    │    - Fallback: "MindWell Clinic"   │
│     │    │                                     │
│     │    └─ meeting_link: null                 │
│     │                                          │
│     └─ "telehealth"                            │
│          ├─ location: null                     │
│          │                                     │
│          └─ meeting_link:                      │
│               - if video_room_id exists:       │
│                  "/video-session/{room_id}"    │
│               - else: null                     │
│                                                │
└────────────────────────────────────────────────┘

Examples:

1. In-Person Appointment:
   {
     "session_type": "in_person",
     "location": "MindWell Clinic - Room 3",
     "meeting_link": null
   }

2. Telehealth Appointment:
   {
     "session_type": "telehealth",
     "location": null,
     "meeting_link": "http://.../video-session/room-123"
   }
```

---

## 🔄 Complete End-to-End Flow

```
1. Frontend sends request
   ↓
2. Django receives request
   ↓
3. Authentication middleware validates JWT
   ↓
4. View receives authenticated request
   ↓
5. Parse query parameters (status, page, page_size)
   ↓
6. Build database query
   ↓
7. Apply filters (patient, status)
   ↓
8. Optimize with select_related
   ↓
9. Count total results
   ↓
10. Apply pagination slice
    ↓
11. Execute query → Get appointments
    ↓
12. For each appointment:
    - Format dates/times
    - Get psychologist details
    - Calculate reschedule/cancel permissions
    - Determine location or meeting link
    - Compute status
    ↓
13. Build pagination URLs (next, previous)
    ↓
14. Construct response object
    ↓
15. Serialize to JSON
    ↓
16. Return HTTP 200 with JSON body
    ↓
17. Frontend receives and displays data
```

---

## 📊 Performance Considerations

```
Optimization Techniques Used:

1. select_related()
   - Reduces N+1 query problem
   - Fetches related objects in single query
   - Joins: psychologist, profile, service

2. Pagination
   - Limits results per request
   - Prevents loading entire dataset
   - Configurable page size

3. Index on appointment_date
   - Fast sorting and filtering
   - Efficient date range queries

4. Index on patient field
   - Fast patient filtering
   - Used in WHERE clause

Query Count per Request:
- Without optimization: 1 + N queries
  (1 for appointments, N for psychologists)
- With optimization: 1-2 queries total
  (1 main query with joins, 1 for count)
```

---

## 🎯 Key Takeaways

1. **Authentication**: JWT token required for all requests
2. **Filtering**: Five status options (all, upcoming, completed, cancelled, past)
3. **Pagination**: Configurable page size with next/previous URLs
4. **Optimization**: Uses select_related for efficient queries
5. **Computed Fields**: Smart calculation of permissions and statuses
6. **User-Friendly**: Formatted dates, times, and readable status values
7. **Flexible**: Supports various frontend frameworks
8. **Complete**: All requested fields included in response

---

## 📝 Notes

- All datetimes are in ISO 8601 format with timezone
- Profile images return absolute URLs
- Deadlines calculated dynamically based on current time
- Status computation considers both database status and datetime
- Location/meeting link mutually exclusive based on session type

