# 👥 Admin Create User Endpoint - Simple & Clean

## 🎯 **Simple Endpoint for Admin**

**Endpoint:** `POST /api/auth/admin/create-user/`  
**Authentication:** Required (Admin only)  
**Content-Type:** `application/json`

---

## 📋 **Request Format**

### **For Practice Manager:**
```json
{
  "email": "manager@clinic.com",
  "password": "manager123",
  "full_name": "Practice Manager",
  "role": "practice_manager",
  "phone_number": "+61400123456"
}
```

### **For Psychologist (Required AHPRA fields):**
```json
{
  "email": "psychologist@clinic.com",
  "password": "psychologist123",
  "full_name": "Dr. Sarah Johnson",
  "role": "psychologist",
  "phone_number": "+61400123457",
  "ahpra_registration_number": "PSY0001234567",
  "ahpra_expiry_date": "2025-12-31",
  "title": "Dr",
  "qualifications": "PhD Psychology, Master of Clinical Psychology",
  "years_experience": 15,
  "consultation_fee": "200.00",
  "medicare_provider_number": "1234567A",
  "bio": "Dr. Sarah Johnson is a senior clinical psychologist...",
  "is_accepting_new_patients": true,
  "specializations": [1, 2],
  "services_offered": [1, 2]
}
```

### **For Psychologist (Minimal - Only Required Fields):**
```json
{
  "email": "psychologist@clinic.com",
  "password": "psychologist123",
  "full_name": "Dr. Sarah Johnson",
  "role": "psychologist",
  "ahpra_registration_number": "PSY0001234567",
  "ahpra_expiry_date": "2025-12-31"
}
```

### **For Admin:**
```json
{
  "email": "admin@clinic.com",
  "password": "admin123",
  "full_name": "Admin User",
  "role": "admin",
  "phone_number": "+61400123458"
}
```

---

## ✅ **Required Fields**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `email` | string | ✅ Yes | Unique email address |
| `password` | string | ✅ Yes | Min 8 characters |
| `full_name` | string | ✅ Yes | Full name (will be split into first_name/last_name) |
| `role` | string | ✅ Yes | Must be: `practice_manager`, `psychologist`, or `admin` |
| `phone_number` | string | ❌ No | Australian format (+61XXXXXXXXX or 0XXXXXXXXX) |

### **Additional Fields for Psychologists:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ahpra_registration_number` | string | ✅ Yes* | AHPRA registration number (required for psychologists) |
| `ahpra_expiry_date` | date | ✅ Yes* | AHPRA expiry date YYYY-MM-DD (required for psychologists) |
| `title` | string | ❌ No | Title (Dr, Mr, Ms, Mrs) - default: "Dr" |
| `qualifications` | string | ❌ No | Professional qualifications |
| `years_experience` | integer | ❌ No | Years of experience - default: 0 |
| `consultation_fee` | decimal | ❌ No | Consultation fee in AUD - default: 180.00 |
| `medicare_provider_number` | string | ❌ No | Medicare provider number |
| `bio` | string | ❌ No | Professional biography |
| `is_accepting_new_patients` | boolean | ❌ No | Accepting new patients - default: true |
| `specializations` | array | ❌ No | Array of specialization IDs |
| `services_offered` | array | ❌ No | Array of service IDs |

*Required only when `role` is `psychologist`

---

## 📤 **Response Format**

### **Success (201 Created):**
```json
{
  "message": "Psychologist created successfully",
  "user": {
    "id": 1,
    "email": "psychologist@clinic.com",
    "username": "psychologist",
    "first_name": "Sarah",
    "last_name": "Johnson",
    "full_name": "Sarah Johnson",
    "role": "psychologist",
    "phone_number": "+61400123457",
    "is_verified": true,
    "created_at": "2024-01-15T10:00:00Z"
  }
}
```

### **Error (400 Bad Request):**
```json
{
  "error": "Missing required fields: email, password, full_name, role"
}
```

### **Error (403 Forbidden):**
```json
{
  "error": "Only administrators can create users"
}
```

---

## 🔧 **What Happens**

### **For Practice Manager:**
- ✅ User account created
- ✅ Role set to `practice_manager`
- ✅ Account verified and activated
- ✅ No additional profile needed

### **For Psychologist:**
- ✅ User account created
- ✅ Role set to `psychologist`
- ✅ Account verified and activated
- ✅ **PsychologistProfile created with AHPRA details** (all provided in one request)
- ✅ Specializations and services linked if provided

### **For Admin:**
- ✅ User account created
- ✅ Role set to `admin`
- ✅ Account verified and activated
- ✅ No additional profile needed

---

## 🧪 **Example Requests**

### **Create Practice Manager:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/admin/create-user/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager@clinic.com",
    "password": "manager123",
    "full_name": "Practice Manager",
    "role": "practice_manager",
    "phone_number": "+61400123456"
  }'
```

### **Create Psychologist (Complete):**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/admin/create-user/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "psychologist@clinic.com",
    "password": "psychologist123",
    "full_name": "Dr. Sarah Johnson",
    "role": "psychologist",
    "phone_number": "+61400123457",
    "ahpra_registration_number": "PSY0001234567",
    "ahpra_expiry_date": "2025-12-31",
    "title": "Dr",
    "qualifications": "PhD Psychology, Master of Clinical Psychology",
    "years_experience": 15,
    "consultation_fee": "200.00",
    "medicare_provider_number": "1234567A",
    "bio": "Dr. Sarah Johnson is a senior clinical psychologist with 15 years of experience...",
    "is_accepting_new_patients": true
  }'
```

### **Create Psychologist (Minimal - Only Required):**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/admin/create-user/ \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "psychologist@clinic.com",
    "password": "psychologist123",
    "full_name": "Dr. Sarah Johnson",
    "role": "psychologist",
    "ahpra_registration_number": "PSY0001234567",
    "ahpra_expiry_date": "2025-12-31"
  }'
```

---

## ⚠️ **Important Notes**

1. **Admin Only:** Only users with `admin` role can use this endpoint
2. **Psychologist AHPRA Required:** For psychologists, `ahpra_registration_number` and `ahpra_expiry_date` are **required**. The profile is created with all provided details in one step.
3. **Email Uniqueness:** Email must be unique. If user exists, returns error.
4. **AHPRA Uniqueness:** AHPRA registration number must be unique. If exists, returns error.
5. **Password:** Minimum 8 characters required.
6. **Full Name:** Can be "First Last" or just "First" - will be split automatically.
7. **Date Format:** AHPRA expiry date must be in `YYYY-MM-DD` format.

---

## 🎯 **Frontend Integration**

```typescript
// Create user function
const createUser = async (userData: {
  email: string;
  password: string;
  full_name: string;
  role: 'practice_manager' | 'psychologist' | 'admin';
  phone_number?: string;
}) => {
  const response = await fetch('/api/auth/admin/create-user/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to create user');
  }
  
  return response.json();
};

// Usage
await createUser({
  email: 'psychologist@clinic.com',
  password: 'psychologist123',
  full_name: 'Dr. Sarah Johnson',
  role: 'psychologist',
  phone_number: '+61400123457'
});
```

---

**Last Updated:** 2024-01-15  
**Status:** ✅ Ready to Use

