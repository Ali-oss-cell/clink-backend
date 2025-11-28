# 📅 Patient Appointments - Complete Frontend Guide

## 🎯 **Endpoint**

**URL:** `GET /api/appointments/patient/appointments/`

**Full URL:** `https://api.tailoredpsychology.com.au/api/appointments/patient/appointments/`

**Authentication:** Required (JWT Token)

---

## 📋 **Query Parameters**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `status` | string | No | `all` | Filter: `all`, `upcoming`, `completed`, `cancelled`, `past` |
| `page` | integer | No | `1` | Page number |
| `page_size` | integer | No | `10` | Results per page (max: 50) |

---

## ✅ **Response Structure**

```json
{
  "count": 15,
  "next": "https://api.tailoredpsychology.com.au/api/appointments/patient/appointments/?page=2&page_size=10&status=upcoming",
  "previous": null,
  "results": [
    {
      "id": "apt-001",
      "appointment_date": "2025-12-15T10:00:00+11:00",
      "formatted_date": "2025-12-15",
      "formatted_time": "10:00 AM",
      "duration_minutes": 50,
      "session_type": "telehealth",
      "status": "upcoming",
      "psychologist": {
        "name": "Dr. Sarah Johnson",
        "title": "Clinical Psychologist",
        "profile_image_url": "https://api.tailoredpsychology.com.au/media/psychologist_profiles/dr_sarah.jpg"
      },
      "location": null,
      "meeting_link": "https://video.twilio.com/v1/Rooms/RM123",
      "notes": "Follow-up session",
      "can_reschedule": true,
      "can_cancel": true,
      "reschedule_deadline": "2025-12-13T10:00:00+11:00",
      "cancellation_deadline": "2025-12-14T10:00:00+11:00"
    }
  ]
}
```

---

## 🔄 **Frontend Implementation (React/TypeScript)**

### **⚠️ IMPORTANT: Preventing Loop Errors**

Common causes of infinite loops:
1. **Missing dependency array in useEffect**
2. **Fetching on every render**
3. **Circular state updates**
4. **Incorrect pagination handling**

### **✅ Correct Implementation**

```typescript
// services/api/appointments.ts
import { authAPI } from './auth';

export interface PatientAppointment {
  id: string;
  appointment_date: string;
  formatted_date: string;
  formatted_time: string;
  duration_minutes: number;
  session_type: 'telehealth' | 'in_person';
  status: 'upcoming' | 'completed' | 'cancelled' | 'past' | 'no_show';
  psychologist: {
    name: string;
    title: string;
    profile_image_url: string | null;
  };
  location: string | null;
  meeting_link: string | null;
  notes: string | null;
  can_reschedule: boolean;
  can_cancel: boolean;
  reschedule_deadline: string;
  cancellation_deadline: string;
}

export interface AppointmentsResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: PatientAppointment[];
}

export const appointmentsService = {
  /**
   * Get patient appointments with pagination
   * 
   * @param status - Filter by status (all, upcoming, completed, cancelled, past)
   * @param page - Page number (default: 1)
   * @param pageSize - Results per page (default: 10)
   * @returns Promise with appointments data
   */
  getAppointments: async (
    status: string = 'all',
    page: number = 1,
    pageSize: number = 10
  ): Promise<AppointmentsResponse> => {
    const params = new URLSearchParams({
      status,
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    const response = await authAPI.get<AppointmentsResponse>(
      `/appointments/patient/appointments/?${params.toString()}`
    );
    
    return response.data;
  },

  /**
   * Get upcoming appointments only
   */
  getUpcomingAppointments: async (): Promise<AppointmentsResponse> => {
    return appointmentsService.getAppointments('upcoming', 1, 10);
  },

  /**
   * Get completed appointments
   */
  getCompletedAppointments: async (page: number = 1): Promise<AppointmentsResponse> => {
    return appointmentsService.getAppointments('completed', page, 10);
  },
};
```

### **✅ React Hook Implementation (No Loops!)**

```typescript
// hooks/usePatientAppointments.ts
import { useState, useEffect, useCallback } from 'react';
import { appointmentsService, AppointmentsResponse } from '../services/api/appointments';

interface UseAppointmentsOptions {
  status?: string;
  pageSize?: number;
  autoFetch?: boolean; // Prevent auto-fetch on mount if false
}

export const usePatientAppointments = (options: UseAppointmentsOptions = {}) => {
  const { status = 'all', pageSize = 10, autoFetch = true } = options;

  const [data, setData] = useState<AppointmentsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [currentPage, setCurrentPage] = useState(1);

  // ✅ Use useCallback to prevent function recreation on every render
  const fetchAppointments = useCallback(async (page: number = 1) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await appointmentsService.getAppointments(status, page, pageSize);
      setData(response);
      setCurrentPage(page);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch appointments'));
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [status, pageSize]); // ✅ Dependencies: only status and pageSize

  // ✅ useEffect with proper dependencies - only runs when needed
  useEffect(() => {
    if (autoFetch) {
      fetchAppointments(1);
    }
  }, [fetchAppointments, autoFetch]); // ✅ Include fetchAppointments in deps

  // ✅ Manual fetch function (for refresh button, etc.)
  const refetch = useCallback(() => {
    fetchAppointments(currentPage);
  }, [fetchAppointments, currentPage]);

  // ✅ Pagination functions
  const nextPage = useCallback(() => {
    if (data?.next) {
      const nextPageNum = currentPage + 1;
      fetchAppointments(nextPageNum);
    }
  }, [data?.next, currentPage, fetchAppointments]);

  const previousPage = useCallback(() => {
    if (data?.previous) {
      const prevPageNum = currentPage - 1;
      fetchAppointments(prevPageNum);
    }
  }, [data?.previous, currentPage, fetchAppointments]);

  return {
    appointments: data?.results || [],
    count: data?.count || 0,
    loading,
    error,
    currentPage,
    hasNext: !!data?.next,
    hasPrevious: !!data?.previous,
    refetch,
    nextPage,
    previousPage,
    fetchAppointments, // Expose for manual control
  };
};
```

### **✅ React Component Example**

```typescript
// components/PatientAppointments.tsx
import React, { useState } from 'react';
import { usePatientAppointments } from '../hooks/usePatientAppointments';

export const PatientAppointments: React.FC = () => {
  const [statusFilter, setStatusFilter] = useState<string>('all');
  
  // ✅ Use the hook - it handles all the logic
  const {
    appointments,
    loading,
    error,
    count,
    hasNext,
    hasPrevious,
    nextPage,
    previousPage,
    refetch,
  } = usePatientAppointments({
    status: statusFilter,
    pageSize: 10,
    autoFetch: true, // ✅ Auto-fetch on mount
  });

  // ✅ Handle status filter change
  const handleStatusChange = (newStatus: string) => {
    setStatusFilter(newStatus);
    // Hook will automatically refetch when status changes
  };

  if (loading) {
    return <div>Loading appointments...</div>;
  }

  if (error) {
    return (
      <div>
        <p>Error: {error.message}</p>
        <button onClick={refetch}>Retry</button>
      </div>
    );
  }

  return (
    <div>
      <h2>My Appointments ({count})</h2>

      {/* Status Filter */}
      <div>
        <button onClick={() => handleStatusChange('all')}>All</button>
        <button onClick={() => handleStatusChange('upcoming')}>Upcoming</button>
        <button onClick={() => handleStatusChange('completed')}>Completed</button>
        <button onClick={() => handleStatusChange('cancelled')}>Cancelled</button>
        <button onClick={() => handleStatusChange('past')}>Past</button>
      </div>

      {/* Appointments List */}
      <div>
        {appointments.length === 0 ? (
          <p>No appointments found.</p>
        ) : (
          appointments.map((appointment) => (
            <div key={appointment.id} className="appointment-card">
              <h3>{appointment.psychologist.name}</h3>
              <p>Date: {appointment.formatted_date}</p>
              <p>Time: {appointment.formatted_time}</p>
              <p>Type: {appointment.session_type}</p>
              <p>Status: {appointment.status}</p>
              
              {appointment.session_type === 'telehealth' && appointment.meeting_link && (
                <a href={appointment.meeting_link} target="_blank" rel="noopener noreferrer">
                  Join Video Session
                </a>
              )}
              
              {appointment.session_type === 'in_person' && appointment.location && (
                <p>Location: {appointment.location}</p>
              )}

              <div>
                {appointment.can_reschedule && (
                  <button onClick={() => handleReschedule(appointment.id)}>
                    Reschedule
                  </button>
                )}
                {appointment.can_cancel && (
                  <button onClick={() => handleCancel(appointment.id)}>
                    Cancel
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      <div>
        <button onClick={previousPage} disabled={!hasPrevious}>
          Previous
        </button>
        <span>Page {currentPage}</span>
        <button onClick={nextPage} disabled={!hasNext}>
          Next
        </button>
      </div>
    </div>
  );
};
```

---

## 🚫 **Common Loop Errors & Fixes**

### **❌ Error 1: Missing Dependencies**

```typescript
// ❌ WRONG - Causes infinite loop
useEffect(() => {
  fetchAppointments();
}, []); // Missing fetchAppointments dependency

// ✅ CORRECT
useEffect(() => {
  fetchAppointments();
}, [fetchAppointments]); // Include all dependencies
```

### **❌ Error 2: Fetching on Every Render**

```typescript
// ❌ WRONG - Fetches on every render
const Component = () => {
  const [data, setData] = useState(null);
  
  // This runs on EVERY render!
  fetch('/api/appointments').then(r => r.json()).then(setData);
  
  return <div>...</div>;
};

// ✅ CORRECT - Only fetch once on mount
const Component = () => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch('/api/appointments').then(r => r.json()).then(setData);
  }, []); // Empty array = only on mount
  
  return <div>...</div>;
};
```

### **❌ Error 3: State Update in Render**

```typescript
// ❌ WRONG - Updates state during render (infinite loop)
const Component = () => {
  const [page, setPage] = useState(1);
  
  // This causes infinite re-renders!
  if (someCondition) {
    setPage(2); // ❌ Never update state during render
  }
  
  return <div>...</div>;
};

// ✅ CORRECT - Update state in useEffect or event handler
const Component = () => {
  const [page, setPage] = useState(1);
  
  useEffect(() => {
    if (someCondition) {
      setPage(2); // ✅ Update in useEffect
    }
  }, [someCondition]);
  
  return <div>...</div>;
};
```

### **❌ Error 4: Circular Pagination**

```typescript
// ❌ WRONG - Automatically fetches next page causing loop
useEffect(() => {
  if (data?.next) {
    fetchAppointments(currentPage + 1); // ❌ Auto-fetches next page
  }
}, [data?.next]);

// ✅ CORRECT - Only fetch when user clicks "Next"
const handleNextPage = () => {
  if (data?.next) {
    fetchAppointments(currentPage + 1); // ✅ User-triggered
  }
};
```

---

## 📝 **Complete Example: Upcoming Appointments Only**

```typescript
// components/UpcomingAppointments.tsx
import React from 'react';
import { usePatientAppointments } from '../hooks/usePatientAppointments';

export const UpcomingAppointments: React.FC = () => {
  // ✅ Fetch only upcoming appointments
  const { appointments, loading, error, refetch } = usePatientAppointments({
    status: 'upcoming',
    pageSize: 5, // Show only 5 upcoming
    autoFetch: true,
  });

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <h2>Upcoming Appointments</h2>
      {appointments.length === 0 ? (
        <p>No upcoming appointments.</p>
      ) : (
        appointments.map((apt) => (
          <div key={apt.id}>
            <h3>{apt.psychologist.name}</h3>
            <p>{apt.formatted_date} at {apt.formatted_time}</p>
            {apt.meeting_link && (
              <a href={apt.meeting_link}>Join Session</a>
            )}
          </div>
        ))
      )}
      <button onClick={refetch}>Refresh</button>
    </div>
  );
};
```

---

## 🔍 **Debugging Tips**

### **1. Check Network Tab**
- Look for repeated requests to the same endpoint
- Check if requests are being made on every render

### **2. Add Console Logs**
```typescript
useEffect(() => {
  console.log('Fetching appointments...'); // Should only log once or when deps change
  fetchAppointments();
}, [fetchAppointments]);
```

### **3. Use React DevTools**
- Check component re-renders
- Verify state updates aren't causing loops

### **4. Verify Dependencies**
```typescript
// Add this to see what's changing
useEffect(() => {
  console.log('Dependencies changed:', { status, pageSize });
}, [status, pageSize]);
```

---

## ✅ **Best Practices Checklist**

- [ ] Use `useCallback` for fetch functions
- [ ] Include all dependencies in `useEffect`
- [ ] Never update state during render
- [ ] Use `autoFetch: false` if you want manual control
- [ ] Handle loading and error states
- [ ] Don't auto-fetch next page (only on user action)
- [ ] Use proper TypeScript types
- [ ] Memoize expensive computations
- [ ] Clean up subscriptions if needed

---

## 🔗 **Related Endpoints**

- **Cancel Appointment:** `POST /api/appointments/cancel/<id>/`
- **Reschedule Appointment:** `POST /api/appointments/reschedule/<id>/`
- **Book Appointment:** `POST /api/appointments/book-enhanced/`
- **Appointment Summary:** `GET /api/appointments/summary/`

---

## 📞 **Support**

If you're still experiencing loop errors:
1. Check browser console for errors
2. Verify JWT token is valid
3. Check network tab for request patterns
4. Ensure dependencies are correct in `useEffect`
5. Use the provided hook implementation above

