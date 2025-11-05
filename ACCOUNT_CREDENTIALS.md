# 🔐 Account Credentials - Admin & Practice Manager

## ✅ **Accounts Created Successfully!**

---

## 👤 **ADMIN ACCOUNT**

**Email:** `admin@clinic.com`  
**Password:** `admin123`  
**Role:** `Admin`  
**Status:** ✅ Verified

**Access:**
- ✅ Full system access
- ✅ Admin Dashboard: `GET /api/auth/dashboard/admin/`
- ✅ All user management endpoints
- ✅ System configuration
- ✅ All data and operations

---

## 👤 **PRACTICE MANAGER ACCOUNT**

**Email:** `manager@clinic.com`  
**Password:** `manager123`  
**Role:** `Practice Manager`  
**Status:** ✅ Verified

**Access:**
- ✅ Practice Manager Dashboard: `GET /api/auth/dashboard/practice-manager/`
- ✅ All clinic appointments
- ✅ All patients and staff
- ✅ Billing and financial data
- ✅ Reports and analytics

---

## 🔑 **Login**

### **API Endpoint:**
```
POST /api/auth/login/
```

### **Request Body:**
```json
{
  "email": "admin@clinic.com",
  "password": "admin123"
}
```

### **Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "admin@clinic.com",
    "first_name": "System",
    "last_name": "Administrator",
    "role": "admin"
  }
}
```

---

## 🧪 **Test Login with cURL**

### **Admin Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@clinic.com",
    "password": "admin123"
  }'
```

### **Practice Manager Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager@clinic.com",
    "password": "manager123"
  }'
```

---

## 📝 **Test Dashboard Access**

### **Admin Dashboard:**
```bash
curl -X GET http://localhost:8000/api/auth/dashboard/admin/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### **Practice Manager Dashboard:**
```bash
curl -X GET http://localhost:8000/api/auth/dashboard/practice-manager/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔄 **Recreate Accounts**

If you need to recreate or update these accounts, run:

```bash
python create_admin_manager_accounts.py
```

This script will:
- Create accounts if they don't exist
- Update existing accounts with correct roles and passwords
- Set passwords to default values

---

## ⚠️ **Security Note**

**These are default credentials for development/testing!**

For production:
- ✅ Change passwords immediately
- ✅ Use strong, unique passwords
- ✅ Enable two-factor authentication
- ✅ Rotate passwords regularly
- ✅ Monitor account activity

---

## 📋 **Quick Reference**

| Account | Email | Password | Role | Dashboard Endpoint |
|---------|-------|----------|------|-------------------|
| Admin | `admin@clinic.com` | `admin123` | `admin` | `/api/auth/dashboard/admin/` |
| Practice Manager | `manager@clinic.com` | `manager123` | `practice_manager` | `/api/auth/dashboard/practice-manager/` |

---

**✅ Ready to use!** You can now login with these accounts and test the dashboards.

