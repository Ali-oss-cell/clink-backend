# 🏥 Dashboard System API Documentation

## 🎯 **Overview**
Role-based dashboard system for the Psychology Clinic backend. Each user role has a customized dashboard with relevant data and functionality.

---

## 🔧 **API Endpoints**

### **Base URL:**
```
http://127.0.0.1:8000/api
```

### **Authentication:**
All dashboard endpoints require JWT token in Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

---

## 👤 **Patient Dashboard**

### **Endpoint:**
```typescript
GET /api/auth/dashboard/patient/
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

### **Response (200):**
```json
{
    "next_appointment": {},
    "total_sessions": 5,
    "intake_completed": true,
    "outstanding_invoices": 0,
    "recent_progress": []
}
```

### **Response (403 - Wrong Role):**
```json
{
    "error": "Only patients can access this dashboard"
}
```

### **Patient Dashboard Features:**
- **Next Appointment** - Upcoming appointment details
- **Total Sessions** - Number of completed therapy sessions
- **Intake Completion** - Whether intake form is completed
- **Outstanding Invoices** - Number of unpaid invoices
- **Recent Progress** - Latest progress updates

---

## 🧠 **Psychologist Dashboard**

### **Endpoint:**
```typescript
GET /api/auth/dashboard/psychologist/
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

### **Response (200):**
```json
{
    "today_appointments": 3,
    "total_patients": 15,
    "pending_notes": 2,
    "upcoming_sessions": [],
    "recent_notes": [
        {
            "id": 1,
            "patient": 1,
            "psychologist": 2,
            "appointment": 1,
            "subjective": "Patient reports feeling more anxious...",
            "objective": "Patient appeared tense during session...",
            "assessment": "Patient is experiencing increased anxiety...",
            "plan": "1. Review and practice advanced breathing techniques...",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### **Response (403 - Wrong Role):**
```json
{
    "error": "Only psychologists can access this dashboard"
}
```

### **Psychologist Dashboard Features:**
- **Today's Appointments** - Number of appointments today
- **Total Patients** - Number of patients under care
- **Pending Notes** - Number of notes awaiting completion
- **Upcoming Sessions** - List of upcoming appointments
- **Recent Notes** - Latest SOAP notes written

---

## 📊 **Practice Manager Dashboard**

### **Endpoint:**
```typescript
GET /api/auth/dashboard/practice-manager/
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

### **Response (200):**
```json
{
    "user": {
        "id": 3,
        "email": "manager@clinic.com",
        "first_name": "Practice",
        "last_name": "Manager",
        "role": "practice_manager"
    },
    "staff": [],
    "patients": [],
    "appointments": [],
    "billing": {},
    "analytics": {}
}
```

### **Practice Manager Dashboard Features:**
- **Staff Management** - List of all staff members
- **Patient Overview** - Patient statistics and information
- **Appointment Management** - All clinic appointments
- **Billing Overview** - Financial summaries and reports
- **Analytics** - Practice performance metrics

---

## ⚙️ **Admin Dashboard**

### **Endpoint:**
```typescript
GET /api/auth/dashboard/admin/
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

### **Response (200):**
```json
{
    "user": {
        "id": 4,
        "email": "admin@clinic.com",
        "first_name": "System",
        "last_name": "Admin",
        "role": "admin"
    },
    "users": [],
    "system_stats": {},
    "analytics": {},
    "settings": {}
}
```

### **Admin Dashboard Features:**
- **User Management** - All system users
- **System Statistics** - Overall system metrics
- **Analytics** - Comprehensive system analytics
- **Settings** - System configuration options

---

## 🔧 **React Integration**

### **TypeScript Interfaces:**
```typescript
interface PatientDashboard {
    next_appointment: Appointment | null;
    total_sessions: number;
    intake_completed: boolean;
    outstanding_invoices: number;
    recent_progress: ProgressUpdate[];
}

interface PsychologistDashboard {
    today_appointments: number;
    total_patients: number;
    pending_notes: number;
    upcoming_sessions: Appointment[];
    recent_notes: ProgressNote[];
}

interface PracticeManagerDashboard {
    user: User;
    staff: StaffMember[];
    patients: Patient[];
    appointments: Appointment[];
    billing: BillingSummary;
    analytics: AnalyticsData;
}

interface AdminDashboard {
    user: User;
    users: User[];
    system_stats: SystemStats;
    analytics: AnalyticsData;
    settings: SystemSettings;
}
```

### **Dashboard Service:**
```typescript
class DashboardService {
    private baseURL = 'http://127.0.0.1:8000/api';
    
    async getPatientDashboard(): Promise<PatientDashboard> {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${this.baseURL}/auth/dashboard/patient/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load patient dashboard');
        }
        
        return response.json();
    }
    
    async getPsychologistDashboard(): Promise<PsychologistDashboard> {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${this.baseURL}/auth/dashboard/psychologist/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load psychologist dashboard');
        }
        
        return response.json();
    }
    
    async getPracticeManagerDashboard(): Promise<PracticeManagerDashboard> {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${this.baseURL}/auth/dashboard/practice-manager/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load practice manager dashboard');
        }
        
        return response.json();
    }
    
    async getAdminDashboard(): Promise<AdminDashboard> {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${this.baseURL}/auth/dashboard/admin/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load admin dashboard');
        }
        
        return response.json();
    }
}
```

### **Role-based Dashboard Component:**
```typescript
const Dashboard: React.FC = () => {
    const [dashboardData, setDashboardData] = useState<any>(null);
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState<User | null>(null);
    
    useEffect(() => {
        const loadDashboard = async () => {
            try {
                const userData = JSON.parse(localStorage.getItem('user') || '{}');
                setUser(userData);
                
                let data;
                switch (userData.role) {
                    case 'patient':
                        data = await dashboardService.getPatientDashboard();
                        break;
                    case 'psychologist':
                        data = await dashboardService.getPsychologistDashboard();
                        break;
                    case 'practice_manager':
                        data = await dashboardService.getPracticeManagerDashboard();
                        break;
                    case 'admin':
                        data = await dashboardService.getAdminDashboard();
                        break;
                    default:
                        throw new Error('Invalid user role');
                }
                
                setDashboardData(data);
            } catch (error) {
                console.error('Failed to load dashboard:', error);
            } finally {
                setLoading(false);
            }
        };
        
        loadDashboard();
    }, []);
    
    if (loading) return <div>Loading dashboard...</div>;
    if (!dashboardData) return <div>Failed to load dashboard</div>;
    
    return (
        <div className="dashboard">
            {user?.role === 'patient' && <PatientDashboardView data={dashboardData} />}
            {user?.role === 'psychologist' && <PsychologistDashboardView data={dashboardData} />}
            {user?.role === 'practice_manager' && <PracticeManagerDashboardView data={dashboardData} />}
            {user?.role === 'admin' && <AdminDashboardView data={dashboardData} />}
        </div>
    );
};
```

### **Patient Dashboard Component:**
```typescript
const PatientDashboardView: React.FC<{ data: PatientDashboard }> = ({ data }) => {
    return (
        <div className="patient-dashboard">
            <h1>Patient Dashboard</h1>
            
            <div className="dashboard-cards">
                <div className="card">
                    <h3>Next Appointment</h3>
                    <p>{data.next_appointment ? 'Scheduled' : 'No upcoming appointments'}</p>
                </div>
                
                <div className="card">
                    <h3>Total Sessions</h3>
                    <p>{data.total_sessions}</p>
                </div>
                
                <div className="card">
                    <h3>Intake Form</h3>
                    <p>{data.intake_completed ? 'Completed' : 'Pending'}</p>
                </div>
                
                <div className="card">
                    <h3>Outstanding Invoices</h3>
                    <p>{data.outstanding_invoices}</p>
                </div>
            </div>
            
            <div className="recent-progress">
                <h3>Recent Progress</h3>
                {data.recent_progress.length > 0 ? (
                    <ul>
                        {data.recent_progress.map((progress, index) => (
                            <li key={index}>{progress}</li>
                        ))}
                    </ul>
                ) : (
                    <p>No recent progress updates</p>
                )}
            </div>
        </div>
    );
};
```

### **Psychologist Dashboard Component:**
```typescript
const PsychologistDashboardView: React.FC<{ data: PsychologistDashboard }> = ({ data }) => {
    return (
        <div className="psychologist-dashboard">
            <h1>Psychologist Dashboard</h1>
            
            <div className="dashboard-cards">
                <div className="card">
                    <h3>Today's Appointments</h3>
                    <p>{data.today_appointments}</p>
                </div>
                
                <div className="card">
                    <h3>Total Patients</h3>
                    <p>{data.total_patients}</p>
                </div>
                
                <div className="card">
                    <h3>Pending Notes</h3>
                    <p>{data.pending_notes}</p>
                </div>
            </div>
            
            <div className="recent-notes">
                <h3>Recent Notes</h3>
                {data.recent_notes.length > 0 ? (
                    <ul>
                        {data.recent_notes.map((note) => (
                            <li key={note.id}>
                                <strong>Patient {note.patient}</strong> - {note.created_at}
                                <p>{note.subjective.substring(0, 100)}...</p>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>No recent notes</p>
                )}
            </div>
        </div>
    );
};
```

---

## 🎯 **Role-based Access Control**

### **User Roles:**
```typescript
type UserRole = 'patient' | 'psychologist' | 'practice_manager' | 'admin';
```

### **Dashboard Access Matrix:**
| Role | Patient Dashboard | Psychologist Dashboard | Practice Manager Dashboard | Admin Dashboard |
|------|------------------|----------------------|---------------------------|-----------------|
| **Patient** | ✅ | ❌ | ❌ | ❌ |
| **Psychologist** | ❌ | ✅ | ❌ | ❌ |
| **Practice Manager** | ❌ | ❌ | ✅ | ❌ |
| **Admin** | ❌ | ❌ | ❌ | ✅ |

### **Permission Checks:**
```typescript
const checkDashboardAccess = (userRole: string, dashboardType: string): boolean => {
    const accessMatrix = {
        'patient': ['patient'],
        'psychologist': ['psychologist'],
        'practice_manager': ['practice_manager'],
        'admin': ['admin']
    };
    
    return accessMatrix[userRole]?.includes(dashboardType) || false;
};
```

---

## 🚨 **Error Handling**

### **Common Error Responses:**

#### **401 Unauthorized:**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

#### **403 Forbidden (Wrong Role):**
```json
{
    "error": "Only patients can access this dashboard"
}
```

#### **403 Forbidden (Insufficient Permissions):**
```json
{
    "error": "Permission denied"
}
```

### **Error Handling in React:**
```typescript
const handleDashboardError = (error: any) => {
    if (error.status === 401) {
        // Redirect to login
        window.location.href = '/login';
    } else if (error.status === 403) {
        // Show unauthorized message
        alert('You do not have permission to access this dashboard');
    } else {
        // Show generic error
        alert('Failed to load dashboard. Please try again.');
    }
};
```

---

## 🔧 **Testing**

### **Test with cURL:**
```bash
# Test Patient Dashboard
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:8000/api/auth/dashboard/patient/

# Test Psychologist Dashboard
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:8000/api/auth/dashboard/psychologist/

# Test Practice Manager Dashboard
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:8000/api/auth/dashboard/practice-manager/

# Test Admin Dashboard
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:8000/api/auth/dashboard/admin/
```

### **Test with Postman:**
1. **Set Authorization:** Bearer token in headers
2. **GET Request:** `/api/auth/dashboard/{role}/`
3. **Check Response:** Should return role-specific dashboard data
4. **Test Wrong Role:** Try accessing dashboard with wrong user role

---

## 📊 **Dashboard Data Sources**

### **Patient Dashboard Data:**
- **Next Appointment** - From appointments model (future implementation)
- **Total Sessions** - Count of progress notes for patient
- **Intake Completed** - From patient profile
- **Outstanding Invoices** - From billing model (future implementation)
- **Recent Progress** - From progress tracking (future implementation)

### **Psychologist Dashboard Data:**
- **Today's Appointments** - Count of today's appointments (future implementation)
- **Total Patients** - Count of unique patients with progress notes
- **Pending Notes** - Count of incomplete notes (future implementation)
- **Upcoming Sessions** - List of upcoming appointments (future implementation)
- **Recent Notes** - Latest 5 progress notes written by psychologist

### **Practice Manager Dashboard Data:**
- **Staff** - All staff members (future implementation)
- **Patients** - All clinic patients (future implementation)
- **Appointments** - All clinic appointments (future implementation)
- **Billing** - Financial summaries (future implementation)
- **Analytics** - Practice metrics (future implementation)

### **Admin Dashboard Data:**
- **Users** - All system users (future implementation)
- **System Stats** - Overall system metrics (future implementation)
- **Analytics** - Comprehensive analytics (future implementation)
- **Settings** - System configuration (future implementation)

---

## 🎯 **Key Features**

### **✅ Implemented:**
- **Role-based access control** - Each role has specific dashboard
- **Authentication required** - JWT token validation
- **Permission checks** - Role verification for dashboard access
- **Patient dashboard** - Basic patient information and progress
- **Psychologist dashboard** - Patient management and notes

### **🔄 Future Implementation:**
- **Appointment integration** - Real appointment data
- **Billing integration** - Financial information
- **Analytics** - Comprehensive reporting
- **Staff management** - Practice manager features
- **System administration** - Admin panel features

---

## 📞 **Support**

### **Common Issues:**
1. **403 Forbidden** - Check user role matches dashboard type
2. **401 Unauthorized** - Check JWT token is valid
3. **Empty data** - Some features require future model implementations
4. **CORS errors** - Check Django CORS settings

### **Debug Steps:**
1. Verify user role in localStorage
2. Check JWT token is not expired
3. Test with Postman first
4. Check browser console for errors

---

**The dashboard system is implemented and ready for frontend integration!** 🎯✨

**Total Endpoints:** 4 (one per role)  
**Authentication:** JWT-based  
**Role-based Access:** ✅ Implemented  
**Permission Checks:** ✅ Implemented  
**Future Features:** Appointment, billing, analytics integration
