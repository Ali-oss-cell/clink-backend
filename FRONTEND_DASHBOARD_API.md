# 📱 Frontend Integration Guide - Practice Manager & Admin Dashboards

## 🎯 **Quick Start**

This document provides everything your frontend team needs to integrate the Practice Manager and Admin dashboard endpoints.

---

## 🔐 **Authentication**

All endpoints require JWT authentication. Include the token in the Authorization header:

```typescript
headers: {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
}
```

---

## 📊 **Practice Manager Dashboard**

### **Endpoint**
```
GET /api/auth/dashboard/practice-manager/
```

**Alternative route:**
```
GET /api/auth/practice-manager/dashboard/
```

### **TypeScript Interface**
```typescript
interface PracticeManagerDashboard {
  stats: {
    today_appointments: number;
    this_week_appointments: number;
    this_month_appointments: number;
    completed_sessions_today: number;
    cancelled_appointments_today: number;
    total_patients: number;
    active_patients: number;
    new_patients_this_month: number;
    total_psychologists: number;
    total_practice_managers: number;
    today_revenue: number;
    this_week_revenue: number;
    this_month_revenue: number;
    total_revenue: number;
    pending_invoices: number;
  };
  recent_appointments: AppointmentSummary[];
  upcoming_appointments: AppointmentSummary[];
  top_psychologists: PsychologistSummary[];
  recent_invoices: InvoiceSummary[];
}

interface AppointmentSummary {
  id: number;
  patient_name: string;
  psychologist_name: string;
  service_name: string;
  appointment_date: string; // ISO format
  status: string;
  session_type: string;
}

interface PsychologistSummary {
  id: number;
  name: string;
  email: string;
  appointment_count: number;
}

interface InvoiceSummary {
  id: number;
  invoice_number: string;
  patient_name: string;
  total_amount: number;
  status: string;
  service_date: string | null; // ISO format
}
```

### **Example Response**
```json
{
  "stats": {
    "today_appointments": 15,
    "this_week_appointments": 48,
    "this_month_appointments": 180,
    "completed_sessions_today": 8,
    "cancelled_appointments_today": 2,
    "total_patients": 245,
    "active_patients": 120,
    "new_patients_this_month": 15,
    "total_psychologists": 8,
    "total_practice_managers": 2,
    "today_revenue": 2250.00,
    "this_week_revenue": 7200.00,
    "this_month_revenue": 27000.00,
    "total_revenue": 150000.00,
    "pending_invoices": 12
  },
  "recent_appointments": [
    {
      "id": 1,
      "patient_name": "John Doe",
      "psychologist_name": "Dr. Sarah Smith",
      "service_name": "Individual Therapy",
      "appointment_date": "2024-01-15T10:00:00Z",
      "status": "completed",
      "session_type": "telehealth"
    }
  ],
  "upcoming_appointments": [
    {
      "id": 2,
      "patient_name": "Jane Smith",
      "psychologist_name": "Dr. Sarah Smith",
      "service_name": "Individual Therapy",
      "appointment_date": "2024-01-16T14:00:00Z",
      "status": "scheduled",
      "session_type": "in-person"
    }
  ],
  "top_psychologists": [
    {
      "id": 5,
      "name": "Dr. Sarah Smith",
      "email": "sarah@clinic.com",
      "appointment_count": 45
    }
  ],
  "recent_invoices": [
    {
      "id": 1,
      "invoice_number": "INV-ABC12345",
      "patient_name": "John Doe",
      "total_amount": 150.00,
      "status": "paid",
      "service_date": "2024-01-15"
    }
  ]
}
```

### **React Example**
```typescript
import { useState, useEffect } from 'react';
import axios from 'axios';

const PracticeManagerDashboard = () => {
  const [dashboardData, setDashboardData] = useState<PracticeManagerDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get(
          'http://localhost:8000/api/auth/dashboard/practice-manager/',
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
        setDashboardData(response.data);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to load dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!dashboardData) return null;

  return (
    <div>
      <h1>Practice Manager Dashboard</h1>
      
      {/* Stats Cards */}
      <div className="stats-grid">
        <StatCard title="Today's Appointments" value={dashboardData.stats.today_appointments} />
        <StatCard title="This Week" value={dashboardData.stats.this_week_appointments} />
        <StatCard title="Total Patients" value={dashboardData.stats.total_patients} />
        <StatCard title="Today's Revenue" value={`$${dashboardData.stats.today_revenue.toFixed(2)}`} />
        <StatCard title="This Month Revenue" value={`$${dashboardData.stats.this_month_revenue.toFixed(2)}`} />
        <StatCard title="Pending Invoices" value={dashboardData.stats.pending_invoices} />
      </div>

      {/* Recent Appointments */}
      <div>
        <h2>Recent Appointments</h2>
        {dashboardData.recent_appointments.map(apt => (
          <div key={apt.id}>
            <p>{apt.patient_name} - {apt.psychologist_name}</p>
            <p>{new Date(apt.appointment_date).toLocaleString()}</p>
          </div>
        ))}
      </div>

      {/* Upcoming Appointments */}
      <div>
        <h2>Upcoming Appointments</h2>
        {dashboardData.upcoming_appointments.map(apt => (
          <div key={apt.id}>
            <p>{apt.patient_name} - {apt.psychologist_name}</p>
            <p>{new Date(apt.appointment_date).toLocaleString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## ⚙️ **Admin Dashboard**

### **Endpoint**
```
GET /api/auth/dashboard/admin/
```

**Alternative route:**
```
GET /api/auth/admin/dashboard/
```

### **TypeScript Interface**
```typescript
interface AdminDashboard {
  stats: {
    total_users: number;
    total_patients: number;
    total_psychologists: number;
    total_practice_managers: number;
    total_admins: number;
    new_users_this_month: number;
    new_patients_this_month: number;
    new_psychologists_this_month: number;
    verified_users: number;
    unverified_users: number;
    total_appointments: number;
    completed_appointments: number;
    scheduled_appointments: number;
    cancelled_appointments: number;
    total_progress_notes: number;
    total_invoices: number;
    total_revenue: number;
    total_medicare_claims: number;
  };
  system_health: {
    status: string;
    total_users: number;
    total_appointments: number;
    active_patients: number;
    verified_users_percentage: number;
  };
  recent_users: UserSummary[];
}

interface UserSummary {
  id: number;
  name: string;
  email: string;
  role: string;
  is_verified: boolean;
  created_at: string; // ISO format
}
```

### **Example Response**
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
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "role": "patient",
      "is_verified": true,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### **React Example**
```typescript
import { useState, useEffect } from 'react';
import axios from 'axios';

const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState<AdminDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await axios.get(
          'http://localhost:8000/api/auth/dashboard/admin/',
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          }
        );
        setDashboardData(response.data);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to load dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!dashboardData) return null;

  return (
    <div>
      <h1>Admin Dashboard</h1>
      
      {/* System Health */}
      <div className="system-health">
        <div className={`status-badge ${dashboardData.system_health.status}`}>
          System Status: {dashboardData.system_health.status.toUpperCase()}
        </div>
        <p>Verified Users: {dashboardData.system_health.verified_users_percentage}%</p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <StatCard title="Total Users" value={dashboardData.stats.total_users} />
        <StatCard title="Total Patients" value={dashboardData.stats.total_patients} />
        <StatCard title="Total Psychologists" value={dashboardData.stats.total_psychologists} />
        <StatCard title="New Users This Month" value={dashboardData.stats.new_users_this_month} />
        <StatCard title="Total Revenue" value={`$${dashboardData.stats.total_revenue.toFixed(2)}`} />
        <StatCard title="Total Appointments" value={dashboardData.stats.total_appointments} />
      </div>

      {/* Recent Users */}
      <div>
        <h2>Recent Users</h2>
        {dashboardData.recent_users.map(user => (
          <div key={user.id}>
            <p>{user.name} ({user.email}) - {user.role}</p>
            <p>Verified: {user.is_verified ? 'Yes' : 'No'}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
```

---

## ⚠️ **Error Handling**

### **403 Forbidden (Wrong Role)**
```json
{
  "error": "Only practice managers and admins can access this dashboard"
}
```

**For Admin Dashboard:**
```json
{
  "error": "Only administrators can access this dashboard"
}
```

### **401 Unauthorized (No Token)**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### **401 Unauthorized (Invalid Token)**
```json
{
  "detail": "Given token not valid for any token type"
}
```

### **Error Handling Example**
```typescript
try {
  const response = await axios.get(endpoint, { headers });
  // Handle success
} catch (error: any) {
  if (error.response?.status === 403) {
    // User doesn't have permission - redirect or show message
    console.error('Access denied:', error.response.data.error);
  } else if (error.response?.status === 401) {
    // Token expired or invalid - redirect to login
    localStorage.removeItem('access_token');
    window.location.href = '/login';
  } else {
    // Other error
    console.error('Error:', error.response?.data || error.message);
  }
}
```

---

## 📋 **Quick Reference**

### **Practice Manager Dashboard**
- **URL:** `/api/auth/dashboard/practice-manager/`
- **Method:** `GET`
- **Auth:** Required (JWT)
- **Role:** `practice_manager` or `admin`
- **Response:** `PracticeManagerDashboard`

### **Admin Dashboard**
- **URL:** `/api/auth/dashboard/admin/`
- **Method:** `GET`
- **Auth:** Required (JWT)
- **Role:** `admin` only
- **Response:** `AdminDashboard`

---

## 🎨 **UI Suggestions**

### **Practice Manager Dashboard UI Components:**

1. **Stats Cards** (Grid Layout)
   - Today's Appointments
   - This Week's Appointments
   - Total Patients
   - Active Patients
   - Today's Revenue
   - This Month's Revenue
   - Pending Invoices

2. **Recent Activity Section**
   - Recent Appointments (table/list)
   - Upcoming Appointments (table/list)
   - Recent Invoices (table/list)

3. **Top Psychologists Section**
   - List or cards showing top performers
   - Appointment count badges

4. **Charts/Graphs** (Optional)
   - Revenue trend chart
   - Appointment trends
   - Patient growth chart

### **Admin Dashboard UI Components:**

1. **System Health Banner**
   - Status indicator (green/yellow/red)
   - Key metrics at a glance

2. **User Statistics Cards**
   - Total users by role
   - New users this month
   - Verification status

3. **System Metrics**
   - Total appointments
   - Revenue statistics
   - Progress notes count

4. **Recent Users Table**
   - User list with verification status
   - Role badges
   - Registration dates

---

## 🔗 **Related Endpoints**

For additional data, you can use these existing endpoints:

- **All Appointments:** `GET /api/appointments/`
- **All Users:** `GET /api/users/`
- **All Patients:** `GET /api/auth/patients/`
- **All Invoices:** `GET /api/billing/invoices/`
- **All Progress Notes:** `GET /api/auth/progress-notes/`

---

## 📝 **Notes**

1. **Date Format:** All dates are in ISO 8601 format (e.g., `"2024-01-15T10:00:00Z"`)
2. **Revenue:** All revenue values are numbers (floats), not strings
3. **Financial Data:** If billing app is not installed, revenue values will be `0.00`
4. **Lists:** Recent/upcoming lists are limited to 10 items
5. **Status Values:** 
   - Appointments: `scheduled`, `confirmed`, `completed`, `cancelled`
   - Invoices: `draft`, `sent`, `paid`, `overdue`, `cancelled`, `refunded`

---

## ✅ **Ready to Integrate!**

All endpoints are tested and ready for frontend integration. The data structures are consistent and follow REST API best practices.

**Need help?** Check the backend logs or test with Postman first before integrating into React.

