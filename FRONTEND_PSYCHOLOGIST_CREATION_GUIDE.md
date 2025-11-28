# 📋 Frontend Guide: Creating Psychologists

## 🎯 **What the Frontend Must Send**

When creating a psychologist through the admin panel, the frontend **MUST** include AHPRA fields, otherwise the profile won't be created.

---

## 📡 **API Endpoints**

You can use **either** endpoint:

1. **`POST /api/users/`** - General user creation (now fixed ✅)
2. **`POST /api/auth/admin/create-user/`** - Admin-specific endpoint (already working ✅)

Both now work the same way for psychologists.

---

## ✅ **Required Fields for Psychologist**

### **Basic User Fields (Always Required)**
```typescript
{
  email: string;              // ✅ Required
  password: string;           // ✅ Required (min 8 characters)
  full_name: string;          // ✅ Required (or use first_name + last_name)
  role: "psychologist";       // ✅ Required
}
```

### **AHPRA Fields (Required for Psychologists)**
```typescript
{
  ahpra_registration_number: string;  // ✅ REQUIRED for psychologists
  ahpra_expiry_date: string;          // ✅ REQUIRED for psychologists (YYYY-MM-DD)
}
```

**AHPRA Format:**
- Format: `PSY` + 10 digits (e.g., `PSY0001234567`)
- Will be normalized automatically (spaces/dashes removed)
- Must start with `PSY` for psychologists
- Must be unique (not already in database)

---

## 📝 **Complete Request Example**

### **Minimal Request (Only Required Fields)**
```typescript
const createPsychologist = async (data: {
  email: string;
  password: string;
  full_name: string;
  ahpra_registration_number: string;
  ahpra_expiry_date: string; // YYYY-MM-DD
}) => {
  const response = await fetch('/api/users/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: data.email,
      password: data.password,
      full_name: data.full_name,
      role: 'psychologist',
      ahpra_registration_number: data.ahpra_registration_number,
      ahpra_expiry_date: data.ahpra_expiry_date
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.ahpra_registration_number?.[0] || error.error || 'Failed to create psychologist');
  }
  
  return await response.json();
};
```

### **Full Request (With Optional Fields)**
```typescript
const createPsychologist = async (data: {
  email: string;
  password: string;
  full_name: string;
  phone_number?: string;
  ahpra_registration_number: string;
  ahpra_expiry_date: string;
  title?: string;
  qualifications?: string;
  years_experience?: number;
  consultation_fee?: number;
  medicare_rebate_amount?: number;
  medicare_provider_number?: string;
  bio?: string;
  is_accepting_new_patients?: boolean;
}) => {
  const response = await fetch('/api/users/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      // Required
      email: data.email,
      password: data.password,
      full_name: data.full_name,
      role: 'psychologist',
      ahpra_registration_number: data.ahpra_registration_number,
      ahpra_expiry_date: data.ahpra_expiry_date,
      
      // Optional
      phone_number: data.phone_number,
      title: data.title || 'Dr',
      qualifications: data.qualifications || '',
      years_experience: data.years_experience || 0,
      consultation_fee: data.consultation_fee || 180.00,
      medicare_rebate_amount: data.medicare_rebate_amount || 87.45,
      medicare_provider_number: data.medicare_provider_number || '',
      bio: data.bio || '',
      is_accepting_new_patients: data.is_accepting_new_patients !== false
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.ahpra_registration_number?.[0] || error.ahpra_expiry_date?.[0] || error.error || 'Failed to create psychologist');
  }
  
  return await response.json();
};
```

---

## 🎨 **React Form Component Example**

```typescript
import React, { useState } from 'react';

interface PsychologistFormData {
  email: string;
  password: string;
  full_name: string;
  phone_number: string;
  ahpra_registration_number: string;
  ahpra_expiry_date: string;
  title: string;
  qualifications: string;
  consultation_fee: number;
  medicare_rebate_amount: number;
}

function CreatePsychologistForm() {
  const [formData, setFormData] = useState<PsychologistFormData>({
    email: '',
    password: '',
    full_name: '',
    phone_number: '',
    ahpra_registration_number: '',
    ahpra_expiry_date: '',
    title: 'Dr',
    qualifications: '',
    consultation_fee: 180.00,
    medicare_rebate_amount: 87.45
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const validateAHPRA = (ahpra: string): boolean => {
    // Client-side validation
    const cleaned = ahpra.replace(/[\s\-_]/g, '').toUpperCase();
    const pattern = /^PSY[0-9]{10}$/;
    return pattern.test(cleaned);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setLoading(true);

    // Validate AHPRA format
    if (!validateAHPRA(formData.ahpra_registration_number)) {
      setErrors({
        ahpra_registration_number: 'Invalid AHPRA format. Must be PSY followed by 10 digits (e.g., PSY0001234567)'
      });
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/users/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          role: 'psychologist'
        })
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle validation errors
        if (data.ahpra_registration_number) {
          setErrors({ ahpra_registration_number: data.ahpra_registration_number[0] });
        } else if (data.ahpra_expiry_date) {
          setErrors({ ahpra_expiry_date: data.ahpra_expiry_date[0] });
        } else {
          setErrors({ general: data.error || 'Failed to create psychologist' });
        }
        return;
      }

      // Success!
      alert('Psychologist created successfully!');
      // Reset form or redirect
      setFormData({
        email: '',
        password: '',
        full_name: '',
        phone_number: '',
        ahpra_registration_number: '',
        ahpra_expiry_date: '',
        title: 'Dr',
        qualifications: '',
        consultation_fee: 180.00,
        medicare_rebate_amount: 87.45
      });
    } catch (error) {
      setErrors({ general: 'Network error. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Required Fields */}
      <div>
        <label>Email *</label>
        <input
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          required
        />
      </div>

      <div>
        <label>Password * (min 8 characters)</label>
        <input
          type="password"
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          minLength={8}
          required
        />
      </div>

      <div>
        <label>Full Name *</label>
        <input
          type="text"
          value={formData.full_name}
          onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
          required
        />
      </div>

      {/* AHPRA Fields - REQUIRED */}
      <div>
        <label>AHPRA Registration Number *</label>
        <input
          type="text"
          value={formData.ahpra_registration_number}
          onChange={(e) => setFormData({ ...formData, ahpra_registration_number: e.target.value })}
          placeholder="PSY0001234567"
          required
        />
        {errors.ahpra_registration_number && (
          <span className="error">{errors.ahpra_registration_number}</span>
        )}
        <small>Format: PSY followed by 10 digits (e.g., PSY0001234567)</small>
      </div>

      <div>
        <label>AHPRA Expiry Date *</label>
        <input
          type="date"
          value={formData.ahpra_expiry_date}
          onChange={(e) => setFormData({ ...formData, ahpra_expiry_date: e.target.value })}
          required
        />
        {errors.ahpra_expiry_date && (
          <span className="error">{errors.ahpra_expiry_date}</span>
        )}
      </div>

      {/* Optional Fields */}
      <div>
        <label>Phone Number</label>
        <input
          type="tel"
          value={formData.phone_number}
          onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
          placeholder="+61400123456"
        />
      </div>

      <div>
        <label>Title</label>
        <select
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
        >
          <option value="Dr">Dr</option>
          <option value="Mr">Mr</option>
          <option value="Ms">Ms</option>
          <option value="Mrs">Mrs</option>
        </select>
      </div>

      <div>
        <label>Consultation Fee (AUD)</label>
        <input
          type="number"
          step="0.01"
          value={formData.consultation_fee}
          onChange={(e) => setFormData({ ...formData, consultation_fee: parseFloat(e.target.value) })}
        />
      </div>

      {errors.general && <div className="error">{errors.general}</div>}

      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create Psychologist'}
      </button>
    </form>
  );
}

export default CreatePsychologistForm;
```

---

## ⚠️ **Important Notes**

### **1. AHPRA is Now Required**
- ❌ **Before**: Could create psychologist without AHPRA → No profile created
- ✅ **Now**: AHPRA is required → Profile always created

### **2. Error Handling**
The backend will return specific errors:

```typescript
// Missing AHPRA
{
  "ahpra_registration_number": ["AHPRA registration number is required for psychologists"]
}

// Invalid AHPRA format
{
  "ahpra_registration_number": ["Invalid AHPRA registration number format. Expected format: 3 letters (e.g., PSY) followed by 10 digits"]
}

// AHPRA already exists
{
  "ahpra_registration_number": ["AHPRA registration number already exists"]
}

// Invalid date format
{
  "ahpra_expiry_date": ["Invalid AHPRA expiry date format. Use YYYY-MM-DD"]
}
```

### **3. Default Values**
If optional fields are not provided, defaults are used:
- `title`: `"Dr"`
- `consultation_fee`: `180.00`
- `medicare_rebate_amount`: `87.45`
- `years_experience`: `0`
- `is_accepting_new_patients`: `true`

---

## ✅ **Success Response**

```json
{
  "id": 7,
  "email": "psychologist@clinic.com",
  "username": "psychologist",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "full_name": "Sarah Johnson",
  "role": "psychologist",
  "phone_number": "+61400123457",
  "is_verified": true,
  "is_active": true,
  "created_at": "2025-11-29T10:00:00Z",
  "psychologist_profile": {
    "id": 7,
    "ahpra_registration_number": "PSY0001234567",
    "ahpra_expiry_date": "2026-12-31",
    "title": "Dr",
    "is_accepting_new_patients": true,
    "is_active_practitioner": true
  }
}
```

---

## 🔍 **Testing**

### **Test with cURL**
```bash
curl -X POST https://api.tailoredpsychology.com.au/api/users/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test.psychologist@clinic.com",
    "password": "secure123",
    "full_name": "Dr. Test Psychologist",
    "role": "psychologist",
    "ahpra_registration_number": "PSY0001234567",
    "ahpra_expiry_date": "2026-12-31",
    "title": "Dr",
    "consultation_fee": 180.00
  }'
```

---

## 📚 **Summary**

**What Frontend MUST Send:**
1. ✅ `email`, `password`, `full_name`, `role: "psychologist"`
2. ✅ `ahpra_registration_number` (format: PSY + 10 digits)
3. ✅ `ahpra_expiry_date` (format: YYYY-MM-DD)

**What Frontend CAN Send (Optional):**
- `phone_number`, `title`, `qualifications`, `years_experience`
- `consultation_fee`, `medicare_rebate_amount`, `medicare_provider_number`
- `bio`, `is_accepting_new_patients`

**Result:**
- ✅ User account created
- ✅ PsychologistProfile created automatically
- ✅ No more "Psychologist not found" errors!

