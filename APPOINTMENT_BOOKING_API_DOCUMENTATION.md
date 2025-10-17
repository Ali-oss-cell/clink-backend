# Appointment Booking API - Complete Documentation

## Overview
This document provides comprehensive information about the appointment booking system API, including time slot retrieval, calendar views, session type selection, and booking endpoints.

---

## 🔄 Complete Booking Flow

### Step 1: Select Psychologist
**Endpoint:** `GET /api/services/psychologists/`
See `PSYCHOLOGIST_SELECTION_ENDPOINT_DOCUMENTATION.md` for details.

### Step 2: View Available Time Slots
**Endpoint:** `GET /api/appointments/available-slots/`

### Step 3: Select Date & Time
Use the calendar view or slot list to select a specific time.

### Step 4: Choose Session Type
Select either telehealth or in-person session.

### Step 5: Book Appointment
**Endpoint:** `POST /api/appointments/book-enhanced/`

### Step 6: View Booking Summary
**Endpoint:** `GET /api/appointments/booking-summary/`

### Step 7: Proceed to Payment
Navigate to payment page with booking details.

---

## 📅 API Endpoints

### 1. Get Available Time Slots

**Endpoint:** `GET /api/appointments/available-slots/`

**Description:** Fetches all available time slots for a specific psychologist within a date range.

**Authentication:** Not required (public endpoint)

**Query Parameters:**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `psychologist_id` | integer | Yes | ID of the psychologist | `1` |
| `start_date` | string | Yes | Start date (YYYY-MM-DD) | `2025-10-08` |
| `end_date` | string | No | End date (defaults to 30 days from start) | `2025-11-08` |
| `service_id` | integer | No | Filter by service type | `1` |
| `session_type` | string | No | Filter by telehealth or in_person | `telehealth` |

**Response:**

```json
{
  "psychologist_id": 1,
  "psychologist_name": "Dr. Sarah Johnson",
  "psychologist_title": "Dr",
  "is_accepting_new_patients": true,
  "telehealth_available": true,
  "in_person_available": true,
  "consultation_fee": "180.00",
  "medicare_rebate_amount": "87.45",
  "patient_cost_after_rebate": 92.55,
  "date_range": {
    "start_date": "2025-10-08",
    "end_date": "2025-11-08"
  },
  "available_dates": [
    {
      "date": "2025-10-08",
      "day_name": "Wednesday",
      "slots": [
        {
          "id": 123,
          "start_time": "2025-10-08T09:00:00+11:00",
          "end_time": "2025-10-08T09:50:00+11:00",
          "start_time_formatted": "09:00 AM",
          "end_time_formatted": "09:50 AM",
          "is_available": true
        },
        {
          "id": 124,
          "start_time": "2025-10-08T10:00:00+11:00",
          "end_time": "2025-10-08T10:50:00+11:00",
          "start_time_formatted": "10:00 AM",
          "end_time_formatted": "10:50 AM",
          "is_available": true
        }
      ]
    },
    {
      "date": "2025-10-09",
      "day_name": "Thursday",
      "slots": [
        {
          "id": 125,
          "start_time": "2025-10-09T09:00:00+11:00",
          "end_time": "2025-10-09T09:50:00+11:00",
          "start_time_formatted": "09:00 AM",
          "end_time_formatted": "09:50 AM",
          "is_available": true
        }
      ]
    }
  ],
  "total_available_slots": 15
}
```

**Example cURL:**

```bash
curl -X GET "http://localhost:8000/api/appointments/available-slots/?psychologist_id=1&start_date=2025-10-08"
```

---

### 2. Get Calendar View

**Endpoint:** `GET /api/appointments/calendar-view/`

**Description:** Returns a simplified view of available dates for calendar display (month view).

**Authentication:** Not required (public endpoint)

**Query Parameters:**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `psychologist_id` | integer | Yes | ID of the psychologist | `1` |
| `month` | integer | No | Month (1-12, defaults to current month) | `10` |
| `year` | integer | No | Year (defaults to current year) | `2025` |

**Response:**

```json
{
  "psychologist_id": 1,
  "psychologist_name": "Dr. Sarah Johnson",
  "month": 10,
  "year": 2025,
  "available_dates": [
    "2025-10-08",
    "2025-10-09",
    "2025-10-10",
    "2025-10-13",
    "2025-10-14",
    "2025-10-15",
    "2025-10-16",
    "2025-10-17"
  ],
  "total_available_days": 8
}
```

**Example cURL:**

```bash
curl -X GET "http://localhost:8000/api/appointments/calendar-view/?psychologist_id=1&month=10&year=2025"
```

---

### 3. Book Appointment (Enhanced)

**Endpoint:** `POST /api/appointments/book-enhanced/`

**Description:** Creates a new appointment with full validation and session type selection.

**Authentication:** Required (patient must be logged in)

**Request Body:**

```json
{
  "psychologist_id": 1,
  "service_id": 1,
  "time_slot_id": 123,
  "session_type": "telehealth",
  "notes": "First session - anxiety management"
}
```

**Fields:**

| Field | Type | Required | Description | Values |
|-------|------|----------|-------------|--------|
| `psychologist_id` | integer | Yes | ID of the psychologist | Any valid psychologist ID |
| `service_id` | integer | Yes | ID of the service | Any valid service ID |
| `time_slot_id` | integer | Yes | ID of the time slot to book | Any available time slot ID |
| `session_type` | string | Yes | Type of session | `telehealth` or `in_person` |
| `notes` | string | No | Additional notes for the appointment | Any text |

**Response (Success - 201 Created):**

```json
{
  "message": "Appointment booked successfully",
  "appointment": {
    "id": 45,
    "patient": 10,
    "patient_name": "John Smith",
    "psychologist": 1,
    "psychologist_name": "Dr. Sarah Johnson",
    "service": 1,
    "service_name": "Individual Therapy Session",
    "appointment_date": "2025-10-08T09:00:00+11:00",
    "formatted_date": "08/10/2025 09:00 AM",
    "duration_minutes": 50,
    "duration_hours": 0.8,
    "status": "scheduled",
    "status_display": "Scheduled",
    "session_type": "telehealth",
    "notes": "First session - anxiety management",
    "video_room_id": "",
    "created_at": "2025-10-07T14:30:00+11:00",
    "updated_at": "2025-10-07T14:30:00+11:00"
  },
  "booking_details": {
    "psychologist_name": "Dr. Sarah Johnson",
    "service_name": "Individual Therapy Session",
    "session_type": "telehealth",
    "appointment_date": "2025-10-08T09:00:00+11:00",
    "duration_minutes": 50,
    "consultation_fee": "180.00",
    "medicare_rebate": "87.45",
    "out_of_pocket_cost": "92.55"
  }
}
```

**Error Responses:**

```json
// 400 Bad Request - Missing fields
{
  "error": "psychologist_id, service_id, and time_slot_id are required"
}

// 400 Bad Request - Invalid session type
{
  "error": "session_type must be either \"telehealth\" or \"in_person\""
}

// 400 Bad Request - Session type not available
{
  "error": "This psychologist does not offer telehealth sessions"
}

// 404 Not Found - Time slot unavailable
{
  "error": "Time slot not found or no longer available"
}

// 400 Bad Request - Past appointment
{
  "error": "Cannot book appointments in the past"
}
```

**Example cURL:**

```bash
curl -X POST "http://localhost:8000/api/appointments/book-enhanced/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "psychologist_id": 1,
    "service_id": 1,
    "time_slot_id": 123,
    "session_type": "telehealth",
    "notes": "First session - anxiety management"
  }'
```

---

### 4. Get Booking Summary

**Endpoint:** `GET /api/appointments/booking-summary/`

**Description:** Retrieves complete booking details for the payment page.

**Authentication:** Required (patient must own the appointment)

**Query Parameters:**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `appointment_id` | integer | Yes | ID of the booked appointment | `45` |

**Response:**

```json
{
  "appointment_id": 45,
  "status": "scheduled",
  "patient": {
    "name": "John Smith",
    "email": "john.smith@example.com",
    "phone": "+61412345678"
  },
  "psychologist": {
    "id": 1,
    "name": "Dr. Sarah Johnson",
    "title": "Dr",
    "qualifications": "PhD Clinical Psychology, M.Psych (Clinical), B.Psych (Hons)",
    "ahpra_number": "PSY0001234567",
    "profile_image_url": "http://localhost:8000/media/psychologist_profiles/dr_sarah.jpg"
  },
  "service": {
    "id": 1,
    "name": "Individual Therapy Session",
    "description": "One-on-one therapy session for personal growth and mental health",
    "duration_minutes": 50
  },
  "session": {
    "type": "telehealth",
    "appointment_date": "2025-10-08T09:00:00+11:00",
    "formatted_date": "Wednesday, 08 October 2025",
    "formatted_time": "09:00 AM",
    "video_room_id": null
  },
  "pricing": {
    "consultation_fee": "180.00",
    "medicare_rebate": "87.45",
    "out_of_pocket_cost": "92.55",
    "medicare_item_number": "80110"
  },
  "notes": "First session - anxiety management",
  "created_at": "2025-10-07T14:30:00+11:00"
}
```

**Example cURL:**

```bash
curl -X GET "http://localhost:8000/api/appointments/booking-summary/?appointment_id=45" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🎨 Frontend Implementation Guide

### React Components Structure

```
BookingFlow/
├── PsychologistSelectionPage.tsx
├── DateTimeSelectorPage.tsx
│   ├── CalendarView.tsx
│   ├── TimeSlotList.tsx
│   └── SessionTypeSelector.tsx
├── BookingConfirmationPage.tsx
└── PaymentPage.tsx
```

### Step-by-Step Implementation

#### 1. Date & Time Selector Component

```typescript
// DateTimeSelectorPage.tsx
import { useState, useEffect } from 'react';
import { appointmentService } from '../api/appointment.service';

interface TimeSlot {
  id: number;
  start_time: string;
  end_time: string;
  start_time_formatted: string;
  end_time_formatted: string;
  is_available: boolean;
}

interface AvailableDate {
  date: string;
  day_name: string;
  slots: TimeSlot[];
}

interface BookingData {
  psychologistId: number;
  serviceId: number;
  sessionType: 'telehealth' | 'in_person';
}

export function DateTimeSelectorPage({ bookingData }: { bookingData: BookingData }) {
  const [availableDates, setAvailableDates] = useState<AvailableDate[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null);
  const [sessionType, setSessionType] = useState<'telehealth' | 'in_person'>('telehealth');
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadAvailableSlots();
  }, [bookingData.psychologistId]);
  
  const loadAvailableSlots = async () => {
    try {
      setLoading(true);
      const today = new Date().toISOString().split('T')[0];
      
      const response = await appointmentService.getAvailableSlots({
        psychologistId: bookingData.psychologistId,
        startDate: today,
        sessionType: sessionType
      });
      
      setAvailableDates(response.available_dates);
    } catch (error) {
      console.error('Failed to load slots:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleBooking = async () => {
    if (!selectedSlot) return;
    
    try {
      const response = await appointmentService.bookAppointment({
        psychologist_id: bookingData.psychologistId,
        service_id: bookingData.serviceId,
        time_slot_id: selectedSlot.id,
        session_type: sessionType,
        notes: ''
      });
      
      // Navigate to payment page
      window.location.href = `/booking/payment?appointment_id=${response.appointment.id}`;
    } catch (error) {
      console.error('Booking failed:', error);
    }
  };
  
  return (
    <div className="booking-page">
      <h1>Select Date & Time</h1>
      
      {/* Session Type Selector */}
      <div className="session-type-selector">
        <h2>Session Type</h2>
        <button
          className={sessionType === 'telehealth' ? 'active' : ''}
          onClick={() => setSessionType('telehealth')}
        >
          🎥 Telehealth
        </button>
        <button
          className={sessionType === 'in_person' ? 'active' : ''}
          onClick={() => setSessionType('in_person')}
        >
          🏥 In-Person
        </button>
      </div>
      
      {/* Calendar View */}
      <div className="calendar-container">
        <h2>Available Dates</h2>
        {loading ? (
          <div>Loading available dates...</div>
        ) : (
          <div className="dates-list">
            {availableDates.map((dateObj) => (
              <div
                key={dateObj.date}
                className={`date-card ${selectedDate === dateObj.date ? 'selected' : ''}`}
                onClick={() => setSelectedDate(dateObj.date)}
              >
                <div className="date">{new Date(dateObj.date).getDate()}</div>
                <div className="day">{dateObj.day_name}</div>
                <div className="slots-count">{dateObj.slots.length} slots</div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Time Slots for Selected Date */}
      {selectedDate && (
        <div className="time-slots-container">
          <h2>Available Times - {selectedDate}</h2>
          <div className="time-slots-list">
            {availableDates
              .find(d => d.date === selectedDate)
              ?.slots.map((slot) => (
                <button
                  key={slot.id}
                  className={`time-slot ${selectedSlot?.id === slot.id ? 'selected' : ''}`}
                  onClick={() => setSelectedSlot(slot)}
                >
                  {slot.start_time_formatted}
                </button>
              ))}
          </div>
        </div>
      )}
      
      {/* Booking Button */}
      <button
        className="book-button"
        disabled={!selectedSlot}
        onClick={handleBooking}
      >
        Continue to Payment
      </button>
    </div>
  );
}
```

#### 2. API Service

```typescript
// api/appointment.service.ts
export const appointmentService = {
  /**
   * Get available time slots for a psychologist
   */
  async getAvailableSlots(params: {
    psychologistId: number;
    startDate: string;
    endDate?: string;
    serviceId?: number;
    sessionType?: 'telehealth' | 'in_person';
  }) {
    const queryParams = new URLSearchParams({
      psychologist_id: params.psychologistId.toString(),
      start_date: params.startDate,
    });
    
    if (params.endDate) queryParams.append('end_date', params.endDate);
    if (params.serviceId) queryParams.append('service_id', params.serviceId.toString());
    if (params.sessionType) queryParams.append('session_type', params.sessionType);
    
    const response = await fetch(
      `/api/appointments/available-slots/?${queryParams.toString()}`
    );
    
    if (!response.ok) throw new Error('Failed to fetch available slots');
    return response.json();
  },
  
  /**
   * Get calendar view of available dates
   */
  async getCalendarView(params: {
    psychologistId: number;
    month?: number;
    year?: number;
  }) {
    const queryParams = new URLSearchParams({
      psychologist_id: params.psychologistId.toString(),
    });
    
    if (params.month) queryParams.append('month', params.month.toString());
    if (params.year) queryParams.append('year', params.year.toString());
    
    const response = await fetch(
      `/api/appointments/calendar-view/?${queryParams.toString()}`
    );
    
    if (!response.ok) throw new Error('Failed to fetch calendar');
    return response.json();
  },
  
  /**
   * Book an appointment
   */
  async bookAppointment(data: {
    psychologist_id: number;
    service_id: number;
    time_slot_id: number;
    session_type: 'telehealth' | 'in_person';
    notes?: string;
  }) {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch('/api/appointments/book-enhanced/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to book appointment');
    }
    
    return response.json();
  },
  
  /**
   * Get booking summary for payment page
   */
  async getBookingSummary(appointmentId: number) {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(
      `/api/appointments/booking-summary/?appointment_id=${appointmentId}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );
    
    if (!response.ok) throw new Error('Failed to fetch booking summary');
    return response.json();
  }
};
```

---

## 🔐 Authentication

Most booking endpoints require authentication:

```typescript
// Get JWT token from login
const loginResponse = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'patient@example.com',
    password: 'password123'
  })
});

const { access, refresh } = await loginResponse.json();

// Store tokens
localStorage.setItem('access_token', access);
localStorage.setItem('refresh_token', refresh);

// Use in subsequent requests
fetch('/api/appointments/book-enhanced/', {
  headers: {
    'Authorization': `Bearer ${access}`
  }
});
```

---

## ✅ Summary

### Backend Status: ✅ **READY**

All booking flow endpoints are implemented and ready:
- ✅ Time slot retrieval with date range
- ✅ Calendar view for month display
- ✅ Session type selection (telehealth/in-person)
- ✅ Enhanced booking with full validation
- ✅ Booking summary for payment page

### Frontend Tasks:
1. Implement DateTimeSelectorPage component
2. Create CalendarView component
3. Add TimeSlotList component
4. Implement SessionTypeSelector
5. Create BookingConfirmationPage
6. Integrate with payment system

### Next Steps:
1. Frontend integration
2. Payment processing implementation
3. Email notifications for bookings
4. SMS reminders (Twilio integration)
5. Video room creation for telehealth sessions

