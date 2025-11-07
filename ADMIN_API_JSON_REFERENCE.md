# 📋 Admin API - Complete JSON Response Reference

**For Frontend Development Team**

This document contains all admin API endpoints with complete JSON response examples.

---

## 🔐 **Authentication**

All endpoints require JWT Bearer token authentication:

```http
Authorization: Bearer <your_jwt_token>
```

**Base URL:** `http://localhost:8000/api`

---

## 1. 📊 **Admin Dashboard**

### **Endpoint:** `GET /api/auth/dashboard/admin/`

**Response Example:**
```json
{
  "stats": {
    "total_users": 500,
    "total_patients": 400,
    "total_psychologists": 15,
    "total_practice_managers": 3,
    "total_admins": 2,
    "new_users_this_month": 25,
    "new_patients_this_month": 20,
    "new_psychologists_this_month": 2,
    "verified_users": 450,
    "unverified_users": 50,
    "total_appointments": 2500,
    "completed_appointments": 2000,
    "scheduled_appointments": 400,
    "cancelled_appointments": 100,
    "total_progress_notes": 1800,
    "total_invoices": 2000,
    "total_revenue": 300000.00,
    "total_medicare_claims": 1500
  },
  "system_health": {
    "status": "good",
    "total_users": 500,
    "total_appointments": 2500,
    "active_patients": 120,
    "verified_users_percentage": 90.0
  },
  "recent_users": [
    {
      "id": 501,
      "name": "John Smith",
      "email": "john.smith@email.com",
      "role": "patient",
      "is_verified": true,
      "created_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 500,
      "name": "Dr. Sarah Johnson",
      "email": "sarah@clinic.com",
      "role": "psychologist",
      "is_verified": true,
      "created_at": "2024-01-14T14:20:00Z"
    }
  ]
}
```

---

## 2. 👥 **User Management**

### **2.1 List All Users**
**Endpoint:** `GET /api/users/`

**Query Parameters:**
- `role`: Filter by role (`patient`, `psychologist`, `practice_manager`, `admin`)
- `search`: Search by name or email
- `page`: Page number (pagination)
- `page_size`: Items per page

**Response Example:**
```json
{
  "count": 500,
  "next": "http://localhost:8000/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "john.smith",
      "email": "john.smith@email.com",
      "first_name": "John",
      "last_name": "Smith",
      "phone_number": "+61400123456",
      "role": "patient",
      "is_verified": true,
      "is_active": true,
      "date_of_birth": "1990-05-15",
      "created_at": "2024-01-01T10:00:00Z",
      "last_login": "2024-01-15T09:30:00Z"
    },
    {
      "id": 2,
      "username": "dr.sarah",
      "email": "sarah@clinic.com",
      "first_name": "Sarah",
      "last_name": "Johnson",
      "phone_number": "+61400123457",
      "role": "psychologist",
      "is_verified": true,
      "is_active": true,
      "date_of_birth": null,
      "created_at": "2023-12-01T08:00:00Z",
      "last_login": "2024-01-15T14:20:00Z"
    }
  ]
}
```

### **2.2 Get Single User**
**Endpoint:** `GET /api/users/{id}/`

**Response Example:**
```json
{
  "id": 1,
  "username": "john.smith",
  "email": "john.smith@email.com",
  "first_name": "John",
  "last_name": "Smith",
  "phone_number": "+61400123456",
  "role": "patient",
  "is_verified": true,
  "is_active": true,
  "date_of_birth": "1990-05-15",
  "address_line_1": "123 Collins Street",
  "suburb": "Melbourne",
  "state": "VIC",
  "postcode": "3000",
  "medicare_number": "1234567890",
  "created_at": "2024-01-01T10:00:00Z",
  "last_login": "2024-01-15T09:30:00Z"
}
```

### **2.3 Create User**
**Endpoint:** `POST /api/users/`

**Request Body:**
```json
{
  "username": "new.user",
  "email": "new.user@email.com",
  "password": "securepassword123",
  "first_name": "New",
  "last_name": "User",
  "phone_number": "+61400123458",
  "role": "patient",
  "date_of_birth": "1995-01-01"
}
```

**Response:** Same as Get Single User (201 Created)

### **2.4 Update User**
**Endpoint:** `PUT /api/users/{id}/` or `PATCH /api/users/{id}/`

**Request Body:**
```json
{
  "first_name": "Updated",
  "last_name": "Name",
  "email": "updated@email.com",
  "role": "patient",
  "is_verified": true
}
```

**Response:** Same as Get Single User (200 OK)

### **2.5 Delete User**
**Endpoint:** `DELETE /api/users/{id}/`

**Response:** `204 No Content`

---

## 3. 👤 **Patient Management**

### **3.1 List All Patients**
**Endpoint:** `GET /api/auth/patients/`

**Query Parameters:**
- `search`: Search by name, email, or phone
- `status`: Filter by status (`active`, `inactive`, `completed`)
- `sort`: Sort by (`created_at`, `last_appointment`)
- `page`: Page number
- `page_size`: Items per page

**Response Example:**
```json
{
  "count": 400,
  "total_count": 400,
  "results": [
    {
      "id": 1,
      "name": "John Smith",
      "fullName": "John Smith",
      "firstName": "John",
      "first_name": "John",
      "lastName": "Smith",
      "last_name": "Smith",
      "email": "john.smith@email.com",
      "emailAddress": "john.smith@email.com",
      "phone": "+61400123456",
      "phone_number": "+61400123456",
      "date_of_birth": "1990-05-15",
      "dateOfBirth": "1990-05-15",
      "age": 33,
      "gender": "Male",
      "gender_identity": "Male",
      "intake_completed": true,
      "total_sessions": 12,
      "totalSessions": 12,
      "completed_sessions": 10,
      "completedSessions": 10,
      "upcoming_sessions": 2,
      "upcomingSessions": 2,
      "progress_notes_count": 10,
      "last_progress_rating": 7.5,
      "lastProgressRating": 7.5,
      "average_progress_rating": 7.2,
      "averageProgressRating": 7.2,
      "last_appointment": "2024-01-10T14:00:00Z",
      "lastAppointment": "2024-01-10T14:00:00Z",
      "last_session_date": "2024-01-10T14:00:00Z",
      "lastSessionDate": "2024-01-10T14:00:00Z",
      "next_appointment": "2024-01-20T10:00:00Z",
      "nextAppointment": "2024-01-20T10:00:00Z",
      "therapy_goals": "Manage anxiety, improve sleep quality",
      "therapyFocus": "Manage anxiety, improve sleep quality",
      "presenting_concerns": "Anxiety, panic attacks",
      "status": "active",
      "registered_date": "2023-12-01",
      "registeredDate": "2023-12-01",
      "created_at": "2023-12-01T10:00:00Z",
      "is_verified": true
    }
  ],
  "filters_applied": {
    "search": "",
    "status": "",
    "sort": "created_at"
  }
}
```

### **3.2 Get Patient Detail**
**Endpoint:** `GET /api/auth/patients/{patient_id}/`

**Response Example:**
```json
{
  "patient": {
    "id": 1,
    "name": "John Smith",
    "email": "john.smith@email.com",
    "phone_number": "+61400123456",
    "date_of_birth": "1990-05-15",
    "age": 33,
    "address": {
      "line_1": "123 Collins Street",
      "suburb": "Melbourne",
      "state": "VIC",
      "postcode": "3000"
    },
    "medicare_number": "1234567890",
    "is_verified": true,
    "created_at": "2023-12-01T10:00:00Z"
  },
  "profile": {
    "preferred_name": "John",
    "gender_identity": "Male",
    "pronouns": "he/him",
    "emergency_contact": {
      "name": "Jane Smith",
      "relationship": "Spouse",
      "phone": "+61400123459"
    },
    "referral_info": {
      "source": "GP Referral",
      "has_gp_referral": true,
      "gp_name": "Dr. Brown"
    },
    "intake_completed": true,
    "presenting_concerns": "Anxiety, panic attacks",
    "therapy_goals": "Manage anxiety, improve sleep quality"
  },
  "statistics": {
    "total_appointments": 12,
    "completed_appointments": 10,
    "cancelled_appointments": 1,
    "progress_notes_count": 10,
    "last_appointment_date": "2024-01-10T14:00:00Z"
  },
  "next_appointment": {
    "id": 25,
    "appointment_date": "2024-01-20T10:00:00Z",
    "psychologist_name": "Dr. Sarah Johnson",
    "service_name": "Individual Therapy Session",
    "status": "scheduled",
    "duration_minutes": 50
  },
  "appointment_history": [
    {
      "id": 24,
      "appointment_date": "2024-01-10T14:00:00Z",
      "psychologist_name": "Dr. Sarah Johnson",
      "service_name": "Individual Therapy Session",
      "status": "completed",
      "duration_minutes": 50
    }
  ],
  "recent_progress": [
    {
      "id": 10,
      "session_number": 10,
      "session_date": "2024-01-10",
      "progress_rating": 7.5,
      "psychologist_name": "Dr. Sarah Johnson"
    }
  ]
}
```

### **3.3 Get Patient Progress**
**Endpoint:** `GET /api/auth/patients/{patient_id}/progress/`

**Response Example:**
```json
{
  "patient_name": "John Smith",
  "total_sessions": 10,
  "average_progress_rating": 7.2,
  "latest_rating": 7.5,
  "progress_over_time": [
    {
      "session_number": 1,
      "session_date": "2023-12-01",
      "progress_rating": 5.0,
      "psychologist_name": "Dr. Sarah Johnson",
      "duration": 50
    },
    {
      "session_number": 10,
      "session_date": "2024-01-10",
      "progress_rating": 7.5,
      "psychologist_name": "Dr. Sarah Johnson",
      "duration": 50
    }
  ],
  "recent_sessions": [
    {
      "id": 10,
      "session_number": 10,
      "session_date": "2024-01-10",
      "progress_rating": 7.5,
      "psychologist_name": "Dr. Sarah Johnson",
      "subjective": "Patient reported feeling more confident...",
      "objective": "Patient appeared calm and engaged...",
      "assessment": "Patient shows significant improvement...",
      "plan": "Continue with current treatment plan..."
    }
  ],
  "progress_summary": {
    "first_session": "2023-12-01",
    "last_session": "2024-01-10",
    "total_duration_hours": 8.33,
    "sessions_with_ratings": 10
  }
}
```

---

## 4. 📅 **Appointment Management**

### **4.1 List All Appointments**
**Endpoint:** `GET /api/appointments/`

**Query Parameters:**
- `status`: Filter by status (`scheduled`, `confirmed`, `completed`, `cancelled`, `no_show`)
- `psychologist`: Filter by psychologist ID
- `patient`: Filter by patient ID
- `date_from`: Filter from date (YYYY-MM-DD)
- `date_to`: Filter to date (YYYY-MM-DD)
- `page`: Page number
- `page_size`: Items per page

**Response Example:**
```json
{
  "count": 2500,
  "next": "http://localhost:8000/api/appointments/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "patient": 1,
      "patient_name": "John Smith",
      "psychologist": 2,
      "psychologist_name": "Dr. Sarah Johnson",
      "service": 1,
      "service_name": "Individual Therapy Session",
      "appointment_date": "2024-01-20T10:00:00Z",
      "duration_minutes": 50,
      "session_type": "telehealth",
      "status": "scheduled",
      "location": null,
      "meeting_link": "https://zoom.us/j/123456789",
      "notes": "Follow-up session",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

---

## 5. 👨‍⚕️ **Staff Management**

### **5.1 List Psychologists**
**Endpoint:** `GET /api/users/?role=psychologist`

**Query Parameters:**
- `search`: Search by name or email
- `page`: Page number
- `page_size`: Items per page

**Response Example:**
```json
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "username": "dr.sarah",
      "email": "sarah@clinic.com",
      "first_name": "Sarah",
      "last_name": "Johnson",
      "phone_number": "+61400123457",
      "role": "psychologist",
      "is_verified": true,
      "is_active": true,
      "created_at": "2023-12-01T08:00:00Z",
      "last_login": "2024-01-15T14:20:00Z"
    }
  ]
}
```

### **5.2 List Practice Managers**
**Endpoint:** `GET /api/users/?role=practice_manager`

**Response:** Same format as List Psychologists

---

## 6. 💰 **Billing & Financials**

### **6.1 List All Invoices**
**Endpoint:** `GET /api/billing/invoices/`

**Query Parameters:**
- `status`: Filter by status (`draft`, `sent`, `paid`, `overdue`, `cancelled`)
- `patient`: Filter by patient ID
- `page`: Page number
- `page_size`: Items per page

**Response Example:**
```json
{
  "count": 2000,
  "next": "http://localhost:8000/api/billing/invoices/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "invoice_number": "INV-2024-0001",
      "patient": 1,
      "patient_name": "John Smith",
      "patient_email": "john.smith@email.com",
      "patient_medicare_number": "1234567890",
      "appointment": 24,
      "appointment_date": "2024-01-10T14:00:00Z",
      "psychologist_name": "Dr. Sarah Johnson",
      "service_description": "Individual Therapy Session",
      "service_date": "2024-01-10",
      "subtotal_amount": "200.00",
      "gst_amount": "20.00",
      "gst_percentage": 10.0,
      "total_amount": "220.00",
      "medicare_item_number": 1,
      "medicare_item_description": "Individual Psychological Therapy",
      "medicare_rebate": "89.65",
      "medicare_coverage_percentage": 40.75,
      "out_of_pocket": "130.35",
      "status": "paid",
      "due_date": "2024-02-10",
      "paid_date": "2024-01-12",
      "is_overdue": false,
      "abn": "12345678901",
      "created_at": "2024-01-10T15:00:00Z",
      "updated_at": "2024-01-12T10:30:00Z"
    }
  ]
}
```

### **6.2 List All Payments**
**Endpoint:** `GET /api/billing/payments/`

**Query Parameters:**
- `status`: Filter by status (`pending`, `completed`, `failed`, `refunded`)
- `payment_method`: Filter by method (`card`, `bank_transfer`, `medicare`, `cash`)
- `page`: Page number
- `page_size`: Items per page

**Response Example:**
```json
{
  "count": 1800,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "payment_id": "PAY-2024-0001",
      "invoice": 1,
      "invoice_number": "INV-2024-0001",
      "patient": 1,
      "patient_name": "John Smith",
      "amount": "130.35",
      "payment_method": "card",
      "payment_method_display": "Credit/Debit Card",
      "status": "completed",
      "status_display": "Completed",
      "is_completed": true,
      "is_failed": false,
      "is_refunded": false,
      "stripe_payment_intent_id": "pi_1234567890",
      "stripe_charge_id": "ch_1234567890",
      "bank_reference": null,
      "medicare_claim": null,
      "processed_at": "2024-01-12T10:30:00Z",
      "failure_reason": null,
      "gst_amount": "11.85",
      "created_at": "2024-01-12T10:25:00Z",
      "updated_at": "2024-01-12T10:30:00Z"
    }
  ]
}
```

### **6.3 List All Medicare Claims**
**Endpoint:** `GET /api/billing/medicare-claims/`

**Query Parameters:**
- `status`: Filter by status (`pending`, `approved`, `rejected`, `processed`)
- `page`: Page number
- `page_size`: Items per page

**Response Example:**
```json
{
  "count": 1500,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "claim_number": "MC-2024-0001",
      "invoice": 1,
      "invoice_number": "INV-2024-0001",
      "patient": 1,
      "patient_name": "John Smith",
      "patient_medicare_number": "1234567890",
      "medicare_number": "1234567890",
      "medicare_item_number": 1,
      "item_description": "Individual Psychological Therapy",
      "service_fee": "220.00",
      "medicare_rebate": "89.65",
      "patient_payment": "130.35",
      "status": "approved",
      "status_display": "Approved",
      "is_approved": true,
      "is_rejected": false,
      "claim_date": "2024-01-10",
      "processed_date": "2024-01-11",
      "medicare_reference": "REF123456",
      "rejection_reason": null,
      "bulk_billing": false,
      "safety_net_applied": false,
      "created_at": "2024-01-10T15:00:00Z",
      "updated_at": "2024-01-11T09:00:00Z"
    }
  ]
}
```

---

## 7. ⚙️ **System Settings**

### **7.1 Get System Settings**
**Endpoint:** `GET /api/auth/admin/settings/`

**Response Example:**
```json
{
  "clinic": {
    "name": "Psychology Clinic",
    "address": "123 Collins Street, Melbourne VIC 3000",
    "phone": "+61 3 1234 5678",
    "email": "info@clinic.com",
    "website": "https://clinic.com",
    "abn": "12345678901"
  },
  "system": {
    "timezone": "Australia/Sydney",
    "language": "en-au",
    "gst_rate": 0.10,
    "medicare_provider_number": "1234567A",
    "ahpra_registration_number": "PSY0001234567"
  },
  "notifications": {
    "email_enabled": true,
    "sms_enabled": false,
    "whatsapp_enabled": false
  },
  "billing": {
    "default_payment_method": "card",
    "invoice_terms_days": 30,
    "auto_generate_invoices": true
  }
}
```

### **7.2 Update System Settings**
**Endpoint:** `PUT /api/auth/admin/settings/`

**Request Body:**
```json
{
  "clinic": {
    "name": "Updated Clinic Name",
    "address": "456 New Street",
    "phone": "+61 3 9876 5432"
  },
  "notifications": {
    "email_enabled": true,
    "sms_enabled": true
  }
}
```

**Response:**
```json
{
  "message": "Settings update via API is not fully implemented. Please update settings via environment variables or Django settings file.",
  "note": "For production, consider implementing a Settings model to store these values in the database."
}
```

**Note:** Currently returns a message. Full implementation requires a Settings model.

---

## 8. 📊 **System Analytics**

### **8.1 Get System Analytics**
**Endpoint:** `GET /api/auth/admin/analytics/`

**Query Parameters:**
- `period`: Predefined period (`today`, `week`, `month`, `year`, `all`) - default: `month`
- `start_date`: Start date (YYYY-MM-DD) - optional
- `end_date`: End date (YYYY-MM-DD) - optional

**Example Requests:**
```bash
# Monthly analytics (default)
GET /api/auth/admin/analytics/

# Weekly analytics
GET /api/auth/admin/analytics/?period=week

# Custom date range
GET /api/auth/admin/analytics/?start_date=2024-01-01&end_date=2024-01-31

# All-time analytics
GET /api/auth/admin/analytics/?period=all
```

**Response Example:**
```json
{
  "period": {
    "type": "month",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "users": {
    "total": 25,
    "by_role": [
      {
        "role": "patient",
        "count": 20
      },
      {
        "role": "psychologist",
        "count": 2
      },
      {
        "role": "practice_manager",
        "count": 2
      },
      {
        "role": "admin",
        "count": 1
      }
    ],
    "growth": [
      {
        "date": "2024-01-01",
        "count": 5
      },
      {
        "date": "2024-01-02",
        "count": 3
      },
      {
        "date": "2024-01-03",
        "count": 2
      }
    ],
    "verified_count": 450,
    "verification_rate": 90.0
  },
  "appointments": {
    "total": 180,
    "by_status": [
      {
        "status": "completed",
        "count": 150
      },
      {
        "status": "scheduled",
        "count": 25
      },
      {
        "status": "cancelled",
        "count": 5
      }
    ],
    "by_type": [
      {
        "session_type": "individual",
        "count": 160
      },
      {
        "session_type": "telehealth",
        "count": 20
      }
    ],
    "trends": [
      {
        "date": "2024-01-01",
        "count": 8
      },
      {
        "date": "2024-01-02",
        "count": 6
      },
      {
        "date": "2024-01-03",
        "count": 7
      }
    ]
  },
  "financial": {
    "total_revenue": 33000.00,
    "total_invoices": 150,
    "paid_invoices": 140,
    "pending_invoices": 10,
    "total_medicare_claims": 120
  },
  "progress_notes": {
    "total": 150,
    "average_rating": 7.5
  },
  "performance": {
    "active_patients": 120,
    "total_users": 500,
    "verification_rate": 90.0
  }
}
```

---

## ❌ **Error Responses**

All endpoints may return these error responses:

### **401 Unauthorized**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### **403 Forbidden**
```json
{
  "error": "Only administrators can access this dashboard"
}
```

### **404 Not Found**
```json
{
  "error": "Patient not found"
}
```

### **400 Bad Request**
```json
{
  "error": "Invalid date format. Use YYYY-MM-DD"
}
```

Or validation errors:
```json
{
  "email": ["This field is required."],
  "password": ["This field must be at least 8 characters."]
}
```

---

## 📝 **Notes for Frontend**

1. **Pagination:** Most list endpoints support pagination with `page` and `page_size` parameters
2. **Date Formats:** All dates are in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)
3. **Currency:** All monetary values are strings with 2 decimal places (e.g., "220.00")
4. **Field Names:** Patient endpoints return both snake_case and camelCase for compatibility
5. **Authentication:** Always include JWT token in Authorization header
6. **Base URL:** Use `http://localhost:8000/api` for development

---

## 🚀 **Quick Reference**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/dashboard/admin/` | GET | Admin dashboard stats |
| `/api/users/` | GET/POST | List/Create users |
| `/api/users/{id}/` | GET/PUT/DELETE | Get/Update/Delete user |
| `/api/auth/patients/` | GET | List all patients |
| `/api/auth/patients/{id}/` | GET | Get patient details |
| `/api/auth/patients/{id}/progress/` | GET | Get patient progress |
| `/api/appointments/` | GET | List all appointments |
| `/api/billing/invoices/` | GET | List all invoices |
| `/api/billing/payments/` | GET | List all payments |
| `/api/billing/medicare-claims/` | GET | List all Medicare claims |
| `/api/auth/admin/settings/` | GET/PUT | Get/Update settings |
| `/api/auth/admin/analytics/` | GET | Get analytics |

---

**Last Updated:** 2024-01-15
**Version:** 1.0

