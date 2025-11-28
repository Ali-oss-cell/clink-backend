# 📅 Available Time Slots Endpoint - Complete Guide

## 🎯 **Endpoint**

**URL:** `GET /api/appointments/available-slots/`

**Full URL:** `https://api.tailoredpsychology.com.au/api/appointments/available-slots/`

**Authentication:** Not required (public endpoint)

---

## ⚠️ **IMPORTANT: Required Parameters**

The endpoint requires **TWO mandatory parameters**:

1. **`psychologist_id`** (required) - ID of the psychologist
2. **`start_date`** (required) - Start date in YYYY-MM-DD format

---

## 📋 **Query Parameters**

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `psychologist_id` | integer | **YES** | ID of the psychologist | `1` |
| `start_date` | string | **YES** | Start date (YYYY-MM-DD) | `2025-12-28` |
| `end_date` | string | No | End date (defaults to 30 days from start) | `2026-01-28` |
| `service_id` | integer | No | Filter by service type | `2` |
| `session_type` | string | No | Filter: `telehealth` or `in_person` | `telehealth` |

---

## ✅ **Correct Request Examples**

### **Example 1: Basic Request**
```http
GET /api/appointments/available-slots/?psychologist_id=1&start_date=2025-12-28
```

### **Example 2: With Service and Session Type**
```http
GET /api/appointments/available-slots/?psychologist_id=1&start_date=2025-12-28&service_id=2&session_type=telehealth
```

### **Example 3: With End Date**
```http
GET /api/appointments/available-slots/?psychologist_id=1&start_date=2025-12-28&end_date=2026-01-28&session_type=in_person
```

---

## ✅ **Success Response (200 OK)**

```json
{
  "psychologist_id": 1,
  "psychologist_name": "Dr. Sarah Johnson",
  "psychologist_title": "Clinical Psychologist",
  "is_accepting_new_patients": true,
  "telehealth_available": true,
  "in_person_available": true,
  "consultation_fee": "150.00",
  "medicare_rebate_amount": "93.35",
  "patient_cost_after_rebate": "56.65",
  "date_range": {
    "start_date": "2025-12-28",
    "end_date": "2026-01-27"
  },
  "available_dates": [
    {
      "date": "2025-12-28",
      "day_name": "Sunday",
      "slots": [
        {
          "id": 123,
          "start_time": "2025-12-28T10:00:00+11:00",
          "end_time": "2025-12-28T10:50:00+11:00",
          "start_time_formatted": "10:00 AM",
          "end_time_formatted": "10:50 AM",
          "is_available": true
        },
        {
          "id": 124,
          "start_time": "2025-12-28T11:00:00+11:00",
          "end_time": "2025-12-28T11:50:00+11:00",
          "start_time_formatted": "11:00 AM",
          "end_time_formatted": "11:50 AM",
          "is_available": true
        }
      ]
    },
    {
      "date": "2025-12-29",
      "day_name": "Monday",
      "slots": [
        {
          "id": 125,
          "start_time": "2025-12-29T09:00:00+11:00",
          "end_time": "2025-12-29T09:50:00+11:00",
          "start_time_formatted": "09:00 AM",
          "end_time_formatted": "09:50 AM",
          "is_available": true
        }
      ]
    }
  ]
}
```

---

## ❌ **Error Responses**

### **400 Bad Request - Missing psychologist_id**
```json
{
  "error": "psychologist_id parameter is required"
}
```

### **400 Bad Request - Missing start_date**
```json
{
  "error": "start_date parameter is required (format: YYYY-MM-DD)"
}
```

### **400 Bad Request - Invalid date format**
```json
{
  "error": "Invalid start_date format. Use YYYY-MM-DD"
}
```

### **404 Not Found - Psychologist not found**
```json
{
  "error": "Psychologist not found"
}
```

**Causes:**
- `psychologist_id` doesn't exist
- User with that ID is not a psychologist
- Psychologist doesn't have a profile

### **400 Bad Request - Session type not available**
```json
{
  "error": "This psychologist does not offer telehealth sessions"
}
```
or
```json
{
  "error": "This psychologist does not offer in-person sessions"
}
```

### **200 OK - Not accepting new patients**
```json
{
  "psychologist_id": 1,
  "psychologist_name": "Dr. Sarah Johnson",
  "is_accepting_new_patients": false,
  "available_dates": [],
  "message": "This psychologist is not currently accepting new patients"
}
```

---

## 💻 **Frontend Implementation**

### **TypeScript Interface**

```typescript
// types/appointments.ts
export interface TimeSlot {
  id: number;
  start_time: string; // ISO 8601
  end_time: string; // ISO 8601
  start_time_formatted: string; // "10:00 AM"
  end_time_formatted: string; // "10:50 AM"
  is_available: boolean;
}

export interface AvailableDate {
  date: string; // YYYY-MM-DD
  day_name: string; // "Monday", "Tuesday", etc.
  slots: TimeSlot[];
}

export interface AvailableSlotsResponse {
  psychologist_id: number;
  psychologist_name: string;
  psychologist_title: string;
  is_accepting_new_patients: boolean;
  telehealth_available: boolean;
  in_person_available: boolean;
  consultation_fee: string;
  medicare_rebate_amount: string;
  patient_cost_after_rebate: string;
  date_range: {
    start_date: string;
    end_date: string;
  };
  available_dates: AvailableDate[];
  message?: string; // Present if not accepting new patients
}
```

### **API Service**

```typescript
// services/api/appointments.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.tailoredpsychology.com.au';

export interface GetAvailableSlotsParams {
  psychologist_id: number;
  start_date: string; // YYYY-MM-DD
  end_date?: string; // YYYY-MM-DD (optional)
  service_id?: number;
  session_type?: 'telehealth' | 'in_person';
}

export const appointmentsAPI = {
  /**
   * Get available time slots for a psychologist
   * 
   * @param params - Query parameters
   * @returns Promise with available slots data
   * @throws Error if psychologist not found or invalid parameters
   */
  getAvailableSlots: async (params: GetAvailableSlotsParams): Promise<AvailableSlotsResponse> => {
    // ✅ Validate required parameters
    if (!params.psychologist_id) {
      throw new Error('psychologist_id is required');
    }
    
    if (!params.start_date) {
      throw new Error('start_date is required (format: YYYY-MM-DD)');
    }

    // ✅ Build query string
    const queryParams = new URLSearchParams({
      psychologist_id: params.psychologist_id.toString(),
      start_date: params.start_date,
    });

    if (params.end_date) {
      queryParams.append('end_date', params.end_date);
    }
    
    if (params.service_id) {
      queryParams.append('service_id', params.service_id.toString());
    }
    
    if (params.session_type) {
      queryParams.append('session_type', params.session_type);
    }

    try {
      // ✅ CORRECT ENDPOINT: /api/appointments/available-slots/
      const response = await axios.get<AvailableSlotsResponse>(
        `${API_BASE_URL}/api/appointments/available-slots/?${queryParams.toString()}`
      );
      
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error(`Psychologist with ID ${params.psychologist_id} not found`);
      }
      if (error.response?.status === 400) {
        throw new Error(error.response.data.error || 'Invalid request parameters');
      }
      throw error;
    }
  },
};
```

### **React Hook**

```typescript
// hooks/useAvailableSlots.ts
import { useState, useEffect, useCallback } from 'react';
import { appointmentsAPI, GetAvailableSlotsParams, AvailableSlotsResponse } from '../services/api/appointments';

export const useAvailableSlots = (params: GetAvailableSlotsParams | null) => {
  const [data, setData] = useState<AvailableSlotsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchSlots = useCallback(async (fetchParams: GetAvailableSlotsParams) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await appointmentsAPI.getAvailableSlots(fetchParams);
      setData(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err : new Error('Failed to load available slots');
      setError(errorMessage);
      setData(null);
      console.error('[useAvailableSlots] Error:', errorMessage);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    // ✅ Only fetch if params are valid
    if (params && params.psychologist_id && params.start_date) {
      fetchSlots(params);
    } else {
      // Clear data if params are invalid
      setData(null);
      setError(null);
    }
  }, [params, fetchSlots]);

  return {
    slots: data,
    loading,
    error,
    refetch: () => params && fetchSlots(params),
  };
};
```

### **DateTimeSelectionPage Component (Fixed)**

```typescript
// components/DateTimeSelectionPage.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useService } from '../hooks/useServices';
import { useAvailableSlots } from '../hooks/useAvailableSlots';
import { GetAvailableSlotsParams } from '../services/api/appointments';

export const DateTimeSelectionPage: React.FC = () => {
  const { serviceId, psychologistId } = useParams<{ 
    serviceId: string; 
    psychologistId?: string;
  }>();
  const navigate = useNavigate();
  const location = useLocation();
  
  // ✅ Get service
  const serviceIdNum = serviceId ? parseInt(serviceId, 10) : null;
  const { service, loading: serviceLoading, error: serviceError } = useService(serviceIdNum);
  
  // ✅ Get psychologist ID from URL params or location state
  const psychologistIdFromState = location.state?.psychologistId;
  const finalPsychologistId = psychologistId || psychologistIdFromState;
  const psychologistIdNum = finalPsychologistId ? parseInt(finalPsychologistId, 10) : null;
  
  // ✅ Get session type from location state or default
  const sessionType = location.state?.sessionType || 'telehealth';
  
  // ✅ Default start date to today
  const [startDate, setStartDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  
  // ✅ Build params for available slots
  const slotsParams: GetAvailableSlotsParams | null = 
    psychologistIdNum && startDate
      ? {
          psychologist_id: psychologistIdNum,
          start_date: startDate,
          service_id: serviceIdNum || undefined,
          session_type: sessionType as 'telehealth' | 'in_person',
        }
      : null;
  
  const { slots, loading: slotsLoading, error: slotsError } = useAvailableSlots(slotsParams);
  
  // ✅ Handle missing psychologist ID
  useEffect(() => {
    if (!psychologistIdNum && !serviceLoading) {
      console.warn('[DateTimeSelectionPage] Psychologist ID missing, redirecting');
      navigate('/psychologists', { 
        replace: true,
        state: { error: 'Please select a psychologist first' }
      });
    }
  }, [psychologistIdNum, serviceLoading, navigate]);
  
  // ✅ Handle psychologist not found error
  useEffect(() => {
    if (slotsError && slotsError.message.includes('not found')) {
      console.error('[DateTimeSelectionPage] Psychologist not found:', slotsError);
      // Optionally redirect or show error message
    }
  }, [slotsError]);

  if (serviceLoading) {
    return <div>Loading service details...</div>;
  }

  if (serviceError || !service) {
    return (
      <div>
        <p>Service not found.</p>
        <button onClick={() => navigate('/services')}>Go Back</button>
      </div>
    );
  }

  if (!psychologistIdNum) {
    return (
      <div>
        <p>Please select a psychologist first.</p>
        <button onClick={() => navigate('/psychologists')}>Select Psychologist</button>
      </div>
    );
  }

  return (
    <div>
      <h2>Select Date & Time</h2>
      
      <div className="service-info">
        <h3>{service.name}</h3>
        <p>Duration: {service.duration_minutes} minutes</p>
      </div>

      {slotsLoading && <div>Loading available slots...</div>}
      
      {slotsError && (
        <div className="error">
          <p>Error: {slotsError.message}</p>
          <button onClick={() => navigate('/psychologists')}>
            Select Different Psychologist
          </button>
        </div>
      )}

      {slots && (
        <div>
          {slots.is_accepting_new_patients ? (
            <>
              <h3>Available Times for {slots.psychologist_name}</h3>
              
              {/* Date selector */}
              <div>
                <label>Start Date:</label>
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  min={new Date().toISOString().split('T')[0]}
                />
              </div>

              {/* Available dates and slots */}
              {slots.available_dates.length === 0 ? (
                <p>No available slots in the selected date range.</p>
              ) : (
                slots.available_dates.map((dateInfo) => (
                  <div key={dateInfo.date} className="date-section">
                    <h4>{dateInfo.day_name}, {dateInfo.date}</h4>
                    <div className="slots-grid">
                      {dateInfo.slots.map((slot) => (
                        <button
                          key={slot.id}
                          onClick={() => handleSlotSelect(slot)}
                          disabled={!slot.is_available}
                        >
                          {slot.start_time_formatted}
                        </button>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </>
          ) : (
            <div className="warning">
              <p>{slots.message || 'This psychologist is not currently accepting new patients.'}</p>
              <button onClick={() => navigate('/psychologists')}>
                Select Different Psychologist
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
```

---

## 🚨 **Fixing "Psychologist not found" Error**

### **Common Causes:**

1. **Missing `psychologist_id` parameter**
   - ✅ Fix: Always include `psychologist_id` in query params

2. **Wrong endpoint URL**
   - ❌ Wrong: `/api/auth/app...`
   - ✅ Correct: `/api/appointments/available-slots/`

3. **Invalid `psychologist_id` (not a number)**
   - ✅ Fix: Parse to integer: `parseInt(psychologistId, 10)`

4. **Psychologist doesn't exist**
   - ✅ Fix: Validate psychologist exists before calling endpoint

5. **Psychologist doesn't have a profile**
   - ✅ Fix: Ensure psychologist has a `PsychologistProfile`

### **Complete Error Handling**

```typescript
// services/api/appointments.ts (Enhanced)
export const appointmentsAPI = {
  getAvailableSlots: async (params: GetAvailableSlotsParams): Promise<AvailableSlotsResponse> => {
    // ✅ Validate required parameters
    if (!params.psychologist_id || isNaN(params.psychologist_id)) {
      throw new Error('Valid psychologist_id is required');
    }
    
    if (!params.start_date) {
      throw new Error('start_date is required (format: YYYY-MM-DD)');
    }

    // ✅ Validate date format
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(params.start_date)) {
      throw new Error('start_date must be in YYYY-MM-DD format');
    }

    const queryParams = new URLSearchParams({
      psychologist_id: params.psychologist_id.toString(),
      start_date: params.start_date,
    });

    if (params.end_date) {
      if (!dateRegex.test(params.end_date)) {
        throw new Error('end_date must be in YYYY-MM-DD format');
      }
      queryParams.append('end_date', params.end_date);
    }
    
    if (params.service_id) {
      queryParams.append('service_id', params.service_id.toString());
    }
    
    if (params.session_type) {
      queryParams.append('session_type', params.session_type);
    }

    try {
      // ✅ CORRECT ENDPOINT
      const response = await axios.get<AvailableSlotsResponse>(
        `${API_BASE_URL}/api/appointments/available-slots/?${queryParams.toString()}`
      );
      
      return response.data;
    } catch (error: any) {
      // ✅ Handle specific errors
      if (error.response?.status === 404) {
        throw new Error(
          `Psychologist with ID ${params.psychologist_id} not found. ` +
          `Please select a different psychologist.`
        );
      }
      if (error.response?.status === 400) {
        const errorMsg = error.response.data?.error || 'Invalid request parameters';
        throw new Error(errorMsg);
      }
      if (error.response?.status === 403) {
        throw new Error('Access denied');
      }
      
      // ✅ Network errors
      if (error.message === 'Network Error') {
        throw new Error('Network error. Please check your connection.');
      }
      
      throw new Error(error.message || 'Failed to load available slots');
    }
  },
};
```

---

## ✅ **Quick Fix Checklist**

- [ ] Use correct endpoint: `/api/appointments/available-slots/` (NOT `/api/auth/app...`)
- [ ] Include `psychologist_id` parameter (required)
- [ ] Include `start_date` parameter (required, format: YYYY-MM-DD)
- [ ] Parse `psychologist_id` to integer
- [ ] Validate `psychologist_id` exists before calling
- [ ] Handle 404 error (psychologist not found)
- [ ] Handle 400 error (missing/invalid parameters)
- [ ] Check if psychologist is accepting new patients
- [ ] Verify psychologist has a profile

---

## 📝 **Example: Complete Booking Flow**

```typescript
// 1. User selects psychologist
const handlePsychologistSelect = (psychologistId: number) => {
  navigate(`/book/${serviceId}/datetime`, {
    state: { 
      psychologistId,
      serviceId,
      sessionType: 'telehealth'
    }
  });
};

// 2. DateTimeSelectionPage loads
// - Gets serviceId from URL
// - Gets psychologistId from location.state
// - Fetches available slots with both IDs

// 3. User selects date/time
const handleSlotSelect = (slot: TimeSlot) => {
  navigate('/book/confirm', {
    state: {
      serviceId,
      psychologistId: psychologistIdNum,
      selectedSlot: slot,
      service,
    }
  });
};
```

---

## 🔗 **Related Endpoints**

- **Calendar View:** `GET /api/appointments/calendar-view/`
- **Book Appointment:** `POST /api/appointments/book-enhanced/`
- **Psychologists List:** `GET /api/services/psychologists/`

---

**This should fix your "Psychologist not found" and "Failed to load available slots" errors!** 🎯

