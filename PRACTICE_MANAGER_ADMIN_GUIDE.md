# 📋 Practice Manager & Admin Roles - Complete Guide

## 🎯 **What They Do**

---

## 📊 **PRACTICE MANAGER** Role

### **Job Responsibilities:**
Practice Managers oversee the **day-to-day operations** of the psychology clinic. They manage staff, handle billing, monitor appointments, and generate reports.

### **What They Need to Do:**

#### 1. **👥 Staff Management**
- View all psychologists and their profiles
- View all practice managers
- See staff availability and schedules
- Monitor staff performance metrics
- Manage staff assignments

#### 2. **👤 Patient Management**
- View all clinic patients
- See patient statistics and demographics
- Monitor patient intake forms completion
- Track patient appointments and progress
- View patient billing history

#### 3. **📅 Appointment Management**
- View **ALL appointments** across the clinic
- See appointment statistics (today, this week, this month)
- Monitor cancellations and reschedules
- Track appointment completion rates
- View appointment revenue

#### 4. **💰 Financial Management**
- View all invoices and payments
- Monitor revenue (daily, weekly, monthly)
- Track Medicare claims and rebates
- Generate financial reports
- View outstanding payments
- Track billing by psychologist

#### 5. **📊 Analytics & Reports**
- Clinic performance metrics
- Appointment statistics
- Revenue reports
- Patient statistics
- Staff productivity reports
- Medicare claim tracking

---

## ⚙️ **ADMIN** Role

### **Job Responsibilities:**
Admins have **full system access** and manage system configuration, user roles, and overall system health.

### **What They Need to Do:**

#### 1. **👥 User Management**
- View **ALL users** (patients, psychologists, practice managers, admins)
- Create/edit/delete users
- Change user roles
- Manage user permissions
- View user activity logs

#### 2. **⚙️ System Configuration**
- Manage system settings
- Configure clinic information
- Manage service types and specializations
- Configure billing settings
- Manage Medicare item numbers

#### 3. **📊 System Analytics**
- Overall system statistics
- User growth metrics
- System health monitoring
- Error logs and debugging
- Performance metrics

#### 4. **🔐 Security & Compliance**
- Monitor security events
- Manage authentication settings
- Compliance tracking (AHPRA, Medicare)
- Audit logs
- Data export capabilities

---

## 🎨 **Pages/Features to Build**

---

### 📊 **PRACTICE MANAGER PAGES**

#### **1. Dashboard** (`/manager/dashboard`)
**Endpoint:** `GET /api/auth/dashboard/practice-manager/`

**What to Show:**
```json
{
  "stats": {
    "today_appointments": 15,
    "this_week_appointments": 48,
    "this_month_appointments": 180,
    "total_patients": 245,
    "total_psychologists": 8,
    "today_revenue": 2250.00,
    "this_week_revenue": 7200.00,
    "this_month_revenue": 27000.00,
    "pending_invoices": 12,
    "completed_sessions_today": 8,
    "cancelled_appointments_today": 2
  },
  "recent_appointments": [...],
  "upcoming_appointments": [...],
  "recent_invoices": [...],
  "top_psychologists": [...],
  "revenue_chart_data": {...}
}
```

**Features:**
- Quick stats cards (appointments, revenue, patients)
- Today's appointments list
- Revenue charts (daily/weekly/monthly)
- Recent activity feed
- Quick action buttons

---

#### **2. Staff Management** (`/manager/staff`)
**Endpoint:** `GET /api/users/?role=psychologist`

**What to Show:**
- List of all psychologists
- Each psychologist's:
  - Profile information
  - Availability schedule
  - Patient count
  - Appointment statistics
  - Revenue generated
  - Ratings

**Features:**
- Search/filter psychologists
- View psychologist details
- See psychologist schedules
- View psychologist performance metrics

---

#### **3. Patients Management** (`/manager/patients`)
**Endpoint:** `GET /api/auth/patients/` (already exists!)

**What to Show:**
- All clinic patients
- Patient statistics:
  - Total patients
  - Active patients
  - New patients this month
  - Patients by psychologist

**Features:**
- Search/filter patients
- View patient details
- See patient appointment history
- View patient billing history
- Export patient list

---

#### **4. Appointments Overview** (`/manager/appointments`)
**Endpoint:** `GET /api/appointments/` (filters all appointments)

**What to Show:**
- All clinic appointments
- Filter by:
  - Date range
  - Psychologist
  - Status (scheduled, completed, cancelled)
  - Session type

**Features:**
- Calendar view
- List view
- Appointment statistics
- Export appointments

---

#### **5. Financial Dashboard** (`/manager/billing`)
**Endpoints:**
- `GET /api/billing/invoices/` (all invoices)
- `GET /api/billing/payments/` (all payments)
- `GET /api/billing/medicare-claims/` (all claims)

**What to Show:**
- Revenue overview
- Invoice statistics
- Payment tracking
- Medicare claims status
- Outstanding payments
- Revenue by psychologist
- Revenue charts

**Features:**
- Revenue reports (daily/weekly/monthly)
- Invoice management
- Payment tracking
- Medicare claim monitoring
- Export financial reports

---

#### **6. Reports & Analytics** (`/manager/reports`)
**Endpoints:**
- Custom analytics endpoints (need to create)

**What to Show:**
- Appointment statistics
- Revenue reports
- Patient demographics
- Staff productivity
- Service utilization
- Medicare claim reports

**Features:**
- Generate custom reports
- Export reports (PDF/CSV)
- Date range filters
- Visual charts and graphs

---

### ⚙️ **ADMIN PAGES**

#### **1. Dashboard** (`/admin/dashboard`)
**Endpoint:** `GET /api/auth/dashboard/admin/`

**What to Show:**
```json
{
  "stats": {
    "total_users": 500,
    "total_patients": 400,
    "total_psychologists": 15,
    "total_practice_managers": 3,
    "total_admins": 2,
    "total_appointments": 2500,
    "system_health": "good",
    "recent_errors": 0
  },
  "user_growth": {...},
  "system_metrics": {...},
  "recent_activity": [...]
}
```

**Features:**
- System overview statistics
- User growth charts
- System health monitoring
- Recent activity log
- Quick actions

---

#### **2. User Management** (`/admin/users`)
**Endpoint:** `GET /api/users/` (all users)

**What to Show:**
- All system users
- Filter by role
- User details
- User activity

**Features:**
- Create new users
- Edit users
- Change user roles
- Delete users
- View user activity logs
- Export user list

---

#### **3. System Settings** (`/admin/settings`)
**Endpoints:**
- Custom settings endpoints (need to create)

**What to Show:**
- Clinic information
- System configuration
- Service types
- Specializations
- Medicare item numbers
- Billing settings

**Features:**
- Edit system settings
- Manage services
- Configure Medicare items
- Update clinic details

---

#### **4. System Analytics** (`/admin/analytics`)
**Endpoints:**
- Custom analytics endpoints (need to create)

**What to Show:**
- System-wide statistics
- User metrics
- Performance metrics
- Error logs
- Usage statistics

**Features:**
- Comprehensive analytics
- Export data
- System health monitoring
- Error tracking

---

## 🔨 **What Needs to Be Built**

### **✅ Already Available (Backend):**
1. ✅ User management endpoints (`GET /api/users/`)
2. ✅ Appointment endpoints (`GET /api/appointments/`)
3. ✅ Patient management (`GET /api/auth/patients/`)
4. ✅ Billing endpoints (`GET /api/billing/invoices/`)
5. ✅ Progress notes (`GET /api/auth/progress-notes/`)

### **❌ Missing (Need to Build):**

#### **Backend Endpoints:**
1. ❌ `GET /api/auth/dashboard/practice-manager/` - Dashboard data
2. ❌ `GET /api/auth/dashboard/admin/` - Admin dashboard data
3. ❌ `GET /api/manager/staff/` - Staff statistics
4. ❌ `GET /api/manager/analytics/` - Analytics data
5. ❌ `GET /api/admin/settings/` - System settings
6. ❌ `GET /api/admin/analytics/` - Admin analytics

#### **Frontend Pages:**
1. ❌ Practice Manager Dashboard
2. ❌ Staff Management Page
3. ❌ Financial Dashboard
4. ❌ Reports & Analytics Page
5. ❌ Admin Dashboard
6. ❌ User Management Page
7. ❌ System Settings Page

---

## 🚀 **Next Steps**

### **Priority 1: Practice Manager Dashboard**
1. Create `PracticeManagerDashboardView` in `users/views.py`
2. Add endpoint: `GET /api/auth/dashboard/practice-manager/`
3. Return comprehensive stats and data
4. Build React frontend page

### **Priority 2: Admin Dashboard**
1. Create `AdminDashboardView` in `users/views.py`
2. Add endpoint: `GET /api/auth/dashboard/admin/`
3. Return system-wide statistics
4. Build React frontend page

### **Priority 3: Financial Dashboard**
1. Enhance billing endpoints for practice managers
2. Add revenue analytics endpoints
3. Build financial dashboard page

### **Priority 4: Reports & Analytics**
1. Create analytics endpoints
2. Build reports generation
3. Add export functionality

---

## 📝 **Summary**

**Practice Managers:**
- Manage clinic operations
- Handle billing and finances
- Monitor appointments and staff
- Generate reports

**Admins:**
- Full system access
- User and role management
- System configuration
- System health monitoring

**What's Missing:**
- Dashboard endpoints for both roles
- Analytics and reporting endpoints
- Frontend pages for all features

**Start Here:**
1. Build Practice Manager Dashboard endpoint
2. Build Admin Dashboard endpoint
3. Create React pages for both dashboards
4. Add financial and analytics features

