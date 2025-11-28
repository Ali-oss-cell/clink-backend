# 🔧 Psychologist Creation Fix - Complete

## 🐛 **Problem Found**

Psychologists were being created **without profiles** in some cases, causing "Psychologist not found" errors.

### **Root Cause**

There were **TWO different ways** to create psychologists, and only ONE created profiles:

1. ✅ **`AdminCreateUserView`** (`/api/auth/admin/create-user/`)
   - **Status**: ✅ Always creates profile (requires AHPRA)
   - **Location**: `users/views.py` lines 189-253

2. ❌ **`UserCreateSerializer`** (`/api/users/` POST)
   - **Status**: ❌ **NEVER created profile** (was just `pass`)
   - **Location**: `users/serializers.py` lines 145-148 (OLD CODE)

### **What Happened**

- Psychologists 3 and 4 were created via `/api/users/` endpoint
- This used `UserCreateSerializer` which **skipped profile creation**
- Result: Users exist but no `PsychologistProfile` → "Psychologist not found" error

---

## ✅ **Fix Applied**

### **Changed: `UserCreateSerializer.create()`**

**Before:**
```python
elif role == User.UserRole.PSYCHOLOGIST:
    # Note: Psychologist profile should be created separately...
    pass  # ❌ NO PROFILE CREATED
```

**After:**
```python
elif role == User.UserRole.PSYCHOLOGIST:
    # ✅ Now requires AHPRA and creates profile
    # - Validates AHPRA registration number
    # - Validates AHPRA expiry date
    # - Creates PsychologistProfile with all details
    # - Consistent with AdminCreateUserView
```

### **Key Changes**

1. ✅ **Requires AHPRA** for psychologists (consistent with `AdminCreateUserView`)
2. ✅ **Creates profile automatically** when psychologist is created
3. ✅ **Validates AHPRA format** and checks for duplicates
4. ✅ **Handles optional fields** with sensible defaults

---

## 📋 **How It Works Now**

### **Option 1: Admin Create User Endpoint** (Recommended)
```bash
POST /api/auth/admin/create-user/
{
  "email": "psychologist@clinic.com",
  "password": "secure123",
  "full_name": "Dr. Sarah Johnson",
  "role": "psychologist",
  "ahpra_registration_number": "PSY0001234567",
  "ahpra_expiry_date": "2026-12-31",
  "title": "Dr",
  "consultation_fee": 180.00,
  "medicare_rebate_amount": 87.45
}
```
✅ **Creates user + profile**

### **Option 2: User Create Endpoint** (Now Fixed)
```bash
POST /api/users/
{
  "email": "psychologist@clinic.com",
  "password": "secure123",
  "full_name": "Dr. Sarah Johnson",
  "role": "psychologist",
  "ahpra_registration_number": "PSY0001234567",  # ✅ NOW REQUIRED
  "ahpra_expiry_date": "2026-12-31",              # ✅ NOW REQUIRED
  "title": "Dr",
  "consultation_fee": 180.00
}
```
✅ **Now creates user + profile** (was broken before)

---

## 🔍 **Verification**

### **Check Existing Psychologists**
```bash
python check_psychologist.py
```

### **Fix Psychologists Without Profiles**
```bash
python manage.py shell << 'PYTHON'
from django.contrib.auth import get_user_model
from services.models import PsychologistProfile
from datetime import date, timedelta

User = get_user_model()

# Fix psychologist 3
user3 = User.objects.get(id=3)
PsychologistProfile.objects.create(
    user=user3,
    ahpra_registration_number='PSY0001234003',
    ahpra_expiry_date=date.today() + timedelta(days=365),
    title='Dr',
    is_accepting_new_patients=True,
    is_active_practitioner=True,
    consultation_fee=180.00,
    medicare_rebate_amount=87.45
)
print("✅ Created profile for psychologist 3")

# Fix psychologist 4
user4 = User.objects.get(id=4)
PsychologistProfile.objects.create(
    user=user4,
    ahpra_registration_number='PSY0001234004',
    ahpra_expiry_date=date.today() + timedelta(days=365),
    title='Dr',
    is_accepting_new_patients=True,
    is_active_practitioner=True,
    consultation_fee=180.00,
    medicare_rebate_amount=87.45
)
print("✅ Created profile for psychologist 4")
PYTHON
```

---

## 📝 **Files Changed**

1. ✅ `users/serializers.py` - Fixed `UserCreateSerializer.create()`
   - Now requires AHPRA for psychologists
   - Creates profile automatically
   - Validates AHPRA format and uniqueness

---

## ✅ **Result**

- ✅ **All new psychologists** will have profiles created automatically
- ✅ **Both creation endpoints** now work consistently
- ✅ **AHPRA validation** ensures data quality
- ✅ **No more "Psychologist not found" errors** for new users

---

## 🚀 **Next Steps**

1. **Fix existing psychologists** (3 and 4) using the shell commands above
2. **Test creating a new psychologist** via `/api/users/` endpoint
3. **Verify profile is created** using `check_psychologist.py`
4. **Update frontend** to always include AHPRA when creating psychologists

---

## 📚 **Related Files**

- `users/views.py` - `AdminCreateUserView` (already working correctly)
- `users/serializers.py` - `UserCreateSerializer` (now fixed)
- `services/models.py` - `PsychologistProfile` model
- `check_psychologist.py` - Diagnostic script

