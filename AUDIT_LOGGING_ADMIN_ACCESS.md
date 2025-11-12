# 🔐 Audit Logging - Admin Access Guide

## ✅ Yes! Admins Can Check Audit Logs

Admins have **full access** to view all audit logs through multiple methods:

---

## 📍 **Where Admins Can Check Audit Logs**

### **1. Django Admin Interface** ✅

**URL:** `http://localhost:8000/admin/audit/auditlog/`

**Access:**
- Login as admin user
- Navigate to **"Audit Logs"** in the sidebar
- View, search, and filter all logs

**Features:**
- ✅ View all actions (create, update, delete, login, etc.)
- ✅ Filter by action type, user role, date
- ✅ Search by user email, object name, IP address
- ✅ See what changed (before/after values)
- ✅ View IP addresses and browser info
- ✅ Date hierarchy navigation
- ✅ Export logs (via admin actions)

**Screenshot-like view:**
```
Admin Dashboard
├── Audit Logs
│   ├── List View (all logs)
│   │   ├── Timestamp | User Email | Action | Object | IP Address
│   │   ├── 2024-01-20 | admin@clinic.com | update | User #5 | 192.168.1.1
│   │   ├── 2024-01-20 | manager@clinic.com | create | Appointment #123 | 192.168.1.2
│   │   └── ...
│   │
│   └── Detail View (single log)
│       ├── Who: admin@clinic.com (Admin)
│       ├── What: Updated User #5
│       ├── When: 2024-01-20 14:30:00
│       ├── Changes:
│       │   ├── role: patient → psychologist
│       │   └── is_active: True → False
│       ├── IP: 192.168.1.1
│       └── Browser: Chrome 120.0
```

---

### **2. API Endpoint** ✅

**URL:** `GET /api/audit/logs/`

**Access:**
- Admin authentication required
- Use JWT token in Authorization header

**Example Request:**
```bash
curl -X GET \
  'http://localhost:8000/api/audit/logs/?action=update&start_date=2024-01-01' \
  -H 'Authorization: Bearer YOUR_ADMIN_TOKEN'
```

**Response:**
```json
{
  "count": 150,
  "results": [
    {
      "id": 1,
      "timestamp": "2024-01-20T14:30:00Z",
      "user_email": "admin@clinic.com",
      "user_role": "admin",
      "action": "update",
      "object_repr": "User #5 (john@example.com)",
      "changes": {
        "role": {
          "old": "patient",
          "new": "psychologist"
        },
        "is_active": {
          "old": true,
          "new": false
        }
      },
      "ip_address": "192.168.1.1",
      "request_path": "/api/users/5/",
      "request_method": "PUT"
    }
  ]
}
```

**Query Parameters:**
- `?user_id=1` - Filter by user
- `?action=update` - Filter by action (create, update, delete, login, etc.)
- `?start_date=2024-01-01` - Filter by date range
- `?end_date=2024-01-31`
- `?search=john@example.com` - Search by email, object name, IP
- `?user_role=admin` - Filter by user role
- `?ordering=-timestamp` - Sort by timestamp (newest first)

---

### **3. Frontend Admin Dashboard** ✅ (When Implemented)

**URL:** `http://localhost:5173/admin/audit-logs`

**Features:**
- ✅ View audit logs in admin dashboard
- ✅ Filter and search interface
- ✅ Export to CSV/PDF
- ✅ Statistics and charts
- ✅ Real-time updates

**Example Component:**
```tsx
// Admin Audit Logs Page
function AdminAuditLogs() {
  const [logs, setLogs] = useState([]);
  const [filters, setFilters] = useState({
    action: '',
    user_role: '',
    start_date: '',
    end_date: ''
  });

  useEffect(() => {
    // Fetch audit logs
    fetchAuditLogs(filters).then(setLogs);
  }, [filters]);

  return (
    <div>
      <h1>Audit Logs</h1>
      
      {/* Filters */}
      <FilterBar filters={filters} onChange={setFilters} />
      
      {/* Logs Table */}
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>User</th>
            <th>Action</th>
            <th>Object</th>
            <th>Changes</th>
            <th>IP Address</th>
          </tr>
        </thead>
        <tbody>
          {logs.map(log => (
            <tr key={log.id}>
              <td>{log.timestamp}</td>
              <td>{log.user_email}</td>
              <td>{log.action}</td>
              <td>{log.object_repr}</td>
              <td>
                {Object.entries(log.changes).map(([key, value]) => (
                  <div key={key}>
                    {key}: {value.old} → {value.new}
                  </div>
                ))}
              </td>
              <td>{log.ip_address}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

---

## 🔍 **What Admins Can See**

### **1. User Actions**
- ✅ Who created/updated/deleted users
- ✅ What fields changed (before/after values)
- ✅ When it happened
- ✅ IP address of the user

### **2. Appointment Actions**
- ✅ Who booked/cancelled appointments
- ✅ Appointment status changes
- ✅ Rescheduling history

### **3. Billing Actions**
- ✅ Invoice creation/updates
- ✅ Payment processing
- ✅ Medicare claim creation
- ✅ Financial changes

### **4. Security Events**
- ✅ Login/logout events
- ✅ Failed login attempts
- ✅ Unauthorized access attempts
- ✅ Permission denied errors

### **5. Patient Data Access**
- ✅ Who viewed patient profiles
- ✅ Who edited progress notes
- ✅ Intake form submissions

---

## 📊 **Admin Audit Log Statistics**

**Endpoint:** `GET /api/audit/logs/stats/`

**Response:**
```json
{
  "total_logs": 5000,
  "recent_logs_30_days": 1200,
  "actions_by_type": {
    "create": 450,
    "update": 600,
    "delete": 50,
    "login": 100
  },
  "actions_by_role": {
    "admin": 200,
    "practice_manager": 300,
    "psychologist": 400,
    "patient": 300
  }
}
```

---

## 🔐 **Permissions**

### **Who Can Access:**

| Role | Django Admin | API Endpoint | Frontend Dashboard |
|------|--------------|--------------|-------------------|
| **Admin** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Practice Manager** | ❌ No | ❌ No | ❌ No |
| **Psychologist** | ❌ No | ❌ No | ❌ No |
| **Patient** | ❌ No | ❌ No | ❌ No |

**Only Admins can view audit logs** - This is intentional for security and compliance.

---

## ✅ **Summary**

**Yes, admins can check audit logs through:**

1. ✅ **Django Admin** - Full interface with filters and search
2. ✅ **API Endpoint** - Programmatic access (`/api/audit/logs/`)
3. ✅ **Frontend Dashboard** - When implemented (admin-only page)

**What they can see:**
- ✅ All user actions (create, update, delete)
- ✅ Appointment changes
- ✅ Billing actions
- ✅ Security events (login, failed attempts)
- ✅ Patient data access
- ✅ IP addresses and timestamps
- ✅ Before/after values for changes

**This provides complete transparency and accountability for admins!** 🔒

