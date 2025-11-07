# 👥 User Creation Guide - Admin/Practice Manager

## 🔧 **Fixed Issues**

### **405 Error Fixed:**
- ✅ Added `UserCreateSerializer` for user creation
- ✅ Updated `UserViewSet` to use the correct serializer for POST requests
- ✅ Added permission check (only admin/practice manager can create users)
- ✅ Added support for `full_name` field (splits into first_name/last_name)

---

## 📋 **User Creation Endpoint**

**Endpoint:** `POST /api/users/`  
**Authentication:** Required (Admin or Practice Manager)  
**Content-Type:** `application/json`

---

## 👤 **Creating Different User Types**

### **1. Creating a Patient** ✅

**Required Fields:**
```json
{
  "email": "patient@example.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Smith",
  "role": "patient"
}
```

**OR using full_name:**
```json
{
  "email": "patient@example.com",
  "password": "securepassword123",
  "full_name": "John Smith",
  "role": "patient"
}
```

**Optional Fields:**
- `phone_number`: Australian format (+61XXXXXXXXX or 0XXXXXXXXX)
- `date_of_birth`: YYYY-MM-DD format
- `username`: Auto-generated from email if not provided
- `is_verified`: Boolean (default: false)
- `is_active`: Boolean (default: true)

**What Happens:**
- ✅ User account is created
- ✅ PatientProfile is automatically created
- ✅ User can complete intake form later

**Example Request:**
```bash
POST /api/users/
{
  "email": "john.smith@email.com",
  "password": "patient123",
  "full_name": "John Smith",
  "phone_number": "+61400123456",
  "date_of_birth": "1990-05-15",
  "role": "patient"
}
```

---

### **2. Creating a Psychologist** ⚠️ **Requires Additional Steps**

**Step 1: Create User Account**

**Required Fields:**
```json
{
  "email": "psychologist@clinic.com",
  "password": "securepassword123",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "role": "psychologist"
}
```

**What Happens:**
- ✅ User account is created
- ⚠️ **PsychologistProfile is NOT created automatically** (requires AHPRA details)

**Step 2: Create Psychologist Profile** (REQUIRED)

**Endpoint:** `POST /api/services/psychologists/` or via psychologist profile endpoint

**Required Fields for Psychologist Profile:**
```json
{
  "ahpra_registration_number": "PSY0001234567",
  "ahpra_expiry_date": "2025-12-31",
  "title": "Dr",
  "qualifications": "PhD Psychology, Master of Clinical Psychology",
  "years_experience": 15,
  "consultation_fee": "200.00",
  "medicare_provider_number": "1234567A",
  "is_accepting_new_patients": true,
  "max_patients_per_day": 10,
  "bio": "Dr. Sarah Johnson is a senior clinical psychologist..."
}
```

**Optional Fields:**
- `profile_image`: Image file
- `practice_name`: "MindWell Psychology Clinic"
- `practice_address`: "123 Collins Street, Melbourne VIC 3000"
- `practice_phone`: "+61 3 1234 5678"
- `practice_email`: "info@clinic.com"
- `personal_website`: "https://dr-sarah-johnson.com.au"
- `specializations`: Array of specialization IDs
- `services_offered`: Array of service IDs

**Complete Example - Creating Psychologist:**

```bash
# Step 1: Create user
POST /api/users/
{
  "email": "sarah@clinic.com",
  "password": "psychologist123",
  "full_name": "Sarah Johnson",
  "phone_number": "+61400123457",
  "role": "psychologist"
}

# Step 2: Create psychologist profile
POST /api/services/psychologists/
{
  "ahpra_registration_number": "PSY0001234567",
  "ahpra_expiry_date": "2025-12-31",
  "title": "Dr",
  "qualifications": "PhD Psychology, Master of Clinical Psychology",
  "years_experience": 15,
  "consultation_fee": "200.00",
  "medicare_provider_number": "1234567A",
  "is_accepting_new_patients": true,
  "max_patients_per_day": 10,
  "bio": "Dr. Sarah Johnson is a senior clinical psychologist with 15 years of experience..."
}
```

---

### **3. Creating a Practice Manager**

**Required Fields:**
```json
{
  "email": "manager@clinic.com",
  "password": "securepassword123",
  "first_name": "Practice",
  "last_name": "Manager",
  "role": "practice_manager"
}
```

**What Happens:**
- ✅ User account is created
- ✅ No additional profile needed

**Example Request:**
```bash
POST /api/users/
{
  "email": "manager@clinic.com",
  "password": "manager123",
  "full_name": "Practice Manager",
  "phone_number": "+61400123458",
  "role": "practice_manager"
}
```

---

### **4. Creating an Admin**

**Required Fields:**
```json
{
  "email": "admin@clinic.com",
  "password": "securepassword123",
  "first_name": "Admin",
  "last_name": "User",
  "role": "admin"
}
```

**What Happens:**
- ✅ User account is created
- ✅ No additional profile needed

**Example Request:**
```bash
POST /api/users/
{
  "email": "admin@clinic.com",
  "password": "admin123",
  "full_name": "Admin User",
  "phone_number": "+61400123459",
  "role": "admin"
}
```

---

## 📝 **Field Details**

### **Common Fields (All User Types):**

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `email` | string | ✅ Yes | Unique email address | "user@example.com" |
| `password` | string | ✅ Yes | Min 8 characters | "securepass123" |
| `first_name` | string | ✅ Yes* | First name | "John" |
| `last_name` | string | ✅ Yes* | Last name | "Smith" |
| `full_name` | string | ✅ Yes* | Alternative to first_name/last_name | "John Smith" |
| `role` | string | ✅ Yes | User role | "patient", "psychologist", "practice_manager", "admin" |
| `phone_number` | string | ❌ No | Australian format | "+61400123456" |
| `date_of_birth` | date | ❌ No | YYYY-MM-DD | "1990-05-15" |
| `username` | string | ❌ No | Auto-generated from email | "user" |
| `is_verified` | boolean | ❌ No | Email verification status | true |
| `is_active` | boolean | ❌ No | Account active status | true |

*Either `first_name` + `last_name` OR `full_name` is required

---

## ⚠️ **Important Notes**

### **For Psychologists:**
1. ⚠️ **User account must be created first** via `/api/users/`
2. ⚠️ **PsychologistProfile must be created separately** via `/api/services/psychologists/`
3. ⚠️ **AHPRA registration number is REQUIRED** for psychologist profile
4. ⚠️ **Without psychologist profile, psychologist cannot:**
   - Accept appointments
   - Set availability
   - Be listed in psychologist search
   - Have consultation fees

### **For Patients:**
1. ✅ PatientProfile is **automatically created** when user is created
2. ✅ Patient can complete intake form later via `/api/auth/intake-form/`

### **Phone Number Format:**
- ✅ Australian format: `+61XXXXXXXXX` or `0XXXXXXXXX`
- ❌ Invalid: `123-456-7890`, `(02) 1234 5678`

### **Password Requirements:**
- ✅ Minimum 8 characters
- ✅ No maximum length
- ✅ No special character requirements (but recommended)

---

## 🔄 **Response Format**

### **Success Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "user",
  "first_name": "John",
  "last_name": "Smith",
  "full_name": "John Smith",
  "role": "patient",
  "phone_number": "+61400123456",
  "date_of_birth": "1990-05-15",
  "age": 33,
  "is_verified": false,
  "created_at": "2024-01-15T10:00:00Z"
}
```

### **Error Response (400 Bad Request):**
```json
{
  "email": ["This field is required."],
  "password": ["This field must be at least 8 characters."],
  "first_name": ["First name is required"]
}
```

### **Error Response (403 Forbidden):**
```json
{
  "error": "Only admins and practice managers can create users"
}
```

---

## 🧪 **Testing Examples**

### **Create Patient:**
```bash
curl -X POST http://127.0.0.1:8000/api/users/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "password": "patient123",
    "full_name": "John Smith",
    "phone_number": "+61400123456",
    "role": "patient"
  }'
```

### **Create Psychologist (Step 1):**
```bash
curl -X POST http://127.0.0.1:8000/api/users/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "psychologist@clinic.com",
    "password": "psychologist123",
    "full_name": "Sarah Johnson",
    "phone_number": "+61400123457",
    "role": "psychologist"
  }'
```

### **Create Psychologist Profile (Step 2):**
```bash
curl -X POST http://127.0.0.1:8000/api/services/psychologists/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ahpra_registration_number": "PSY0001234567",
    "ahpra_expiry_date": "2025-12-31",
    "title": "Dr",
    "qualifications": "PhD Psychology",
    "years_experience": 15,
    "consultation_fee": "200.00",
    "is_accepting_new_patients": true
  }'
```

---

## ✅ **Summary**

| User Type | User Creation | Profile Creation | Notes |
|-----------|---------------|------------------|-------|
| **Patient** | ✅ `/api/users/` | ✅ Automatic | PatientProfile auto-created |
| **Psychologist** | ✅ `/api/users/` | ⚠️ Manual | Must create PsychologistProfile separately |
| **Practice Manager** | ✅ `/api/users/` | ❌ None | No profile needed |
| **Admin** | ✅ `/api/users/` | ❌ None | No profile needed |

---

**Last Updated:** 2024-01-15  
**Status:** ✅ Fixed and Documented

