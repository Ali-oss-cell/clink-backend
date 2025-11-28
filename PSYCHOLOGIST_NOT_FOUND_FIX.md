# 🔧 Fix: "Psychologist not found" Error

## 🚨 **Error Message**

```
Error: Psychologist with ID 1 not found. Please select a different psychologist.
```

**Status Code:** 404 Not Found

---

## 🔍 **Root Cause**

The endpoint `/api/appointments/available-slots/` requires:
1. ✅ User with `id=1` exists
2. ✅ User has `role='psychologist'`
3. ✅ User has a `PsychologistProfile` record

**The error occurs when ANY of these conditions fail.**

---

## ✅ **How to Check & Fix**

### **Method 1: Check via API (Recommended)**

#### **Check if Psychologist Exists**

```bash
# Get all psychologists
curl -X GET "https://api.tailoredpsychology.com.au/api/services/psychologists/" \
  -H "Content-Type: application/json"
```

**Look for:**
- Does psychologist ID 1 exist in the list?
- Does it have a profile?

#### **Check Specific Psychologist**

```bash
# Get psychologist by ID
curl -X GET "https://api.tailoredpsychology.com.au/api/services/psychologists/1/" \
  -H "Content-Type: application/json"
```

**If 404:** Psychologist doesn't exist or doesn't have a profile

---

### **Method 2: Check via Database (PostgreSQL)**

```sql
-- Check if user exists and is a psychologist
SELECT id, email, first_name, last_name, role 
FROM users_user 
WHERE id = 1;

-- Check if psychologist profile exists
SELECT pp.id, pp.user_id, pp.ahpra_registration_number, pp.title
FROM services_psychologist_profile pp
WHERE pp.user_id = 1;
```

**Expected Results:**
- First query should return a user with `role='psychologist'`
- Second query should return a profile record

**If missing:** Create the profile (see below)

---

### **Method 3: Check via Django Admin**

1. Go to: `https://api.tailoredpsychology.com.au/admin/`
2. Navigate to: **Users** → Find user ID 1
3. Check:
   - Role is set to "Psychologist"
   - Has a related "Psychologist Profile"

---

## 🔧 **How to Fix**

### **Fix 1: User Doesn't Exist**

Create a psychologist user:

```bash
# Via Django admin or API
POST /api/auth/admin/create-user/
```

**Request Body:**
```json
{
  "email": "psychologist@example.com",
  "password": "SecurePassword123!",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "role": "psychologist",
  "phone_number": "+61412345678"
}
```

### **Fix 2: User Exists but Wrong Role**

Update user role:

```sql
-- Via PostgreSQL
UPDATE users_user 
SET role = 'psychologist' 
WHERE id = 1;
```

Or via Django admin:
1. Go to Users → User ID 1
2. Change "Role" to "Psychologist"
3. Save

### **Fix 3: User is Psychologist but No Profile**

Create psychologist profile via API:

```bash
POST /api/services/psychologists/
Authorization: Bearer <psychologist_jwt_token>
```

**Request Body:**
```json
{
  "ahpra_registration_number": "PSY0001234567",
  "ahpra_expiry_date": "2026-12-31",
  "title": "Clinical Psychologist",
  "qualifications": "PhD in Psychology",
  "years_experience": 10,
  "consultation_fee": "150.00",
  "medicare_provider_number": "1234567A",
  "is_accepting_new_patients": true,
  "telehealth_available": true,
  "in_person_available": true,
  "is_active_practitioner": true
}
```

**Or via Django Admin:**
1. Go to: **Services** → **Psychologist Profiles** → **Add Psychologist Profile**
2. Select User: User ID 1
3. Fill in required fields:
   - AHPRA Registration Number (e.g., `PSY0001234567`)
   - AHPRA Expiry Date
   - Title
   - Other details
4. Save

---

## 📋 **Quick Diagnostic Checklist**

Run these checks:

```bash
# 1. Check if user exists
curl "https://api.tailoredpsychology.com.au/api/services/psychologists/1/"

# 2. List all psychologists
curl "https://api.tailoredpsychology.com.au/api/services/psychologists/"

# 3. Test available slots endpoint
curl "https://api.tailoredpsychology.com.au/api/appointments/available-slots/?psychologist_id=1&start_date=2025-12-28"
```

---

## 🎯 **Frontend Fix: Handle Missing Psychologist**

Update your frontend to handle this gracefully:

```typescript
// components/DateTimeSelectionPage.tsx
const { slots, loading, error } = useAvailableSlots(slotsParams);

useEffect(() => {
  if (error && error.message.includes('not found')) {
    console.error('[DateTimeSelectionPage] Psychologist not found:', error);
    
    // Option 1: Redirect to psychologist selection
    navigate('/psychologists', {
      state: { 
        error: 'The selected psychologist is no longer available. Please select another psychologist.' 
      }
    });
    
    // Option 2: Show error message and allow retry
    // setShowError(true);
  }
}, [error, navigate]);
```

---

## 🔍 **Common Scenarios**

### **Scenario 1: Psychologist ID 1 is a Patient**

**Problem:** User ID 1 exists but `role='patient'`

**Fix:**
```sql
UPDATE users_user SET role = 'psychologist' WHERE id = 1;
-- Then create profile
```

### **Scenario 2: Psychologist Profile Was Deleted**

**Problem:** User is psychologist but profile was deleted

**Fix:** Recreate profile (see Fix 3 above)

### **Scenario 3: Wrong Psychologist ID**

**Problem:** Frontend is using hardcoded ID 1, but actual psychologist has different ID

**Fix:** 
1. Get correct psychologist ID from `/api/services/psychologists/`
2. Update frontend to use correct ID
3. Pass psychologist ID through URL params or state

---

## ✅ **Verification Steps**

After fixing, verify:

1. **Check User:**
   ```bash
   GET /api/services/psychologists/1/
   ```
   Should return psychologist data (not 404)

2. **Check Available Slots:**
   ```bash
   GET /api/appointments/available-slots/?psychologist_id=1&start_date=2025-12-28
   ```
   Should return available slots (not 404)

3. **Test in Frontend:**
   - Navigate to booking flow
   - Select psychologist
   - Should load available slots without error

---

## 📝 **Prevention: Always Validate Psychologist ID**

```typescript
// Before calling available slots endpoint
const validatePsychologist = async (psychologistId: number) => {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/api/services/psychologists/${psychologistId}/`
    );
    return response.data; // Psychologist exists
  } catch (error) {
    if (error.response?.status === 404) {
      throw new Error(`Psychologist ${psychologistId} not found`);
    }
    throw error;
  }
};

// Use before fetching slots
const psychologist = await validatePsychologist(psychologistId);
if (!psychologist) {
  navigate('/psychologists');
  return;
}
```

---

## 🔗 **Related Endpoints**

- **List Psychologists:** `GET /api/services/psychologists/`
- **Get Psychologist:** `GET /api/services/psychologists/{id}/`
- **Available Slots:** `GET /api/appointments/available-slots/?psychologist_id={id}&start_date={date}`

---

## 💡 **Quick Fix Commands**

### **Via PostgreSQL (if you have access)**

```sql
-- 1. Check user
SELECT id, email, role FROM users_user WHERE id = 1;

-- 2. Update role if needed
UPDATE users_user SET role = 'psychologist' WHERE id = 1;

-- 3. Check profile
SELECT * FROM services_psychologist_profile WHERE user_id = 1;

-- 4. Create profile if missing (adjust values as needed)
INSERT INTO services_psychologist_profile (
  user_id, ahpra_registration_number, ahpra_expiry_date, 
  title, is_active_practitioner, is_accepting_new_patients,
  telehealth_available, in_person_available, created_at, updated_at
) VALUES (
  1, 'PSY0001234567', '2026-12-31',
  'Clinical Psychologist', true, true,
  true, true, NOW(), NOW()
);
```

---

**After fixing, the "Psychologist not found" error should be resolved!** ✅

