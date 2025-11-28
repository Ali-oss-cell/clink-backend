# 👨‍⚕️ Psychologist Profile - Editable Fields

## What Psychologists Can Update

Psychologists can update their profile using the **`PsychologistProfileUpdateSerializer`** which includes the following editable fields:

---

## 📋 Editable Fields by Category

### 1. Professional Information
- ✅ **`title`** - Title (Dr, Mr, Ms, Mrs)
- ✅ **`qualifications`** - Professional qualifications and certifications (text)
- ✅ **`years_experience`** - Years of professional experience (integer)
- ✅ **`bio`** - Professional biography for patient portal (text)

### 2. Practice Details
- ✅ **`practice_name`** - Name of the practice or clinic
- ✅ **`practice_address`** - Practice address
- ✅ **`practice_phone`** - Practice phone number
- ✅ **`practice_email`** - Practice email address
- ✅ **`personal_website`** - Personal or practice website URL

### 3. Communication & Languages
- ✅ **`languages_spoken`** - Languages spoken (comma-separated string)
- ✅ **`session_types`** - Types of sessions offered (comma-separated string)

### 4. Insurance & Billing
- ✅ **`insurance_providers`** - Insurance providers accepted (many-to-many)
- ✅ **`medicare_rebate_amount`** - Medicare rebate amount (decimal)
- ❌ **`billing_methods`** - Removed (not needed for psychologists to edit)

### 5. Availability & Scheduling
- ✅ **`working_hours`** - Working hours (JSON or text)
- ✅ **`working_days`** - Days of week working (comma-separated)
- ✅ **`start_time`** - Start time (time field)
- ✅ **`end_time`** - End time (time field)
- ✅ **`session_duration_minutes`** - Session duration in minutes (integer)
- ✅ **`break_between_sessions_minutes`** - Break between sessions (integer)
- ✅ **`telehealth_available`** - Whether telehealth is available (boolean)
- ✅ **`in_person_available`** - Whether in-person sessions available (boolean)

### 6. Profile & Settings
- ✅ **`profile_image`** - Profile photo (image file)
- ✅ **`specializations`** - Areas of specialization (many-to-many)
- ✅ **`services_offered`** - Services provided (many-to-many)
- ✅ **`is_accepting_new_patients`** - Accepting new patients (boolean)
- ✅ **`max_patients_per_day`** - Maximum patients per day (integer)
- ✅ **`is_active_practitioner`** - Active practitioner status (boolean)

---

## ❌ Fields Psychologists CANNOT Update (Admin Only)

These fields are managed by admins/practice managers:

- ❌ **`ahpra_registration_number`** - AHPRA number (admin only)
- ❌ **`ahpra_expiry_date`** - AHPRA expiry date (admin only)
- ❌ **`consultation_fee`** - Consultation fee (admin only)
- ❌ **`medicare_provider_number`** - Medicare provider number (admin only)
- ❌ **`total_patients_seen`** - Statistics (system generated)
- ❌ **`currently_active_patients`** - Statistics (system generated)
- ❌ **`sessions_completed`** - Statistics (system generated)
- ❌ **`average_rating`** - Statistics (system generated)
- ❌ **`total_reviews`** - Statistics (system generated)

---

## 🔗 API Endpoints

### Update Profile
```
PUT /api/services/psychologists/{id}/
PATCH /api/services/psychologists/{id}/
```

**Uses:** `PsychologistProfileUpdateSerializer`

### Get My Profile
```
GET /api/services/psychologists/my_profile/
```

**Returns:** Full profile with all fields (read-only)

### Update Profile Image
```
POST /api/services/psychologists/{id}/upload_image/
```

**Uses:** `PsychologistProfileImageSerializer`

### Update Availability
```
POST /api/services/psychologists/{id}/update_availability/
```

**Allows updating:**
- `is_accepting_new_patients`
- `max_patients_per_day`
- `is_active_practitioner`

---

## 📝 Example Update Request

```json
PUT /api/services/psychologists/1/

{
  "title": "Dr",
  "qualifications": "PhD in Clinical Psychology, AHPRA Registered",
  "years_experience": 10,
  "bio": "Experienced clinical psychologist specializing in anxiety and depression...",
  "practice_name": "Tailored Psychology Clinic",
  "practice_address": "123 Main St, Sydney NSW 2000",
  "practice_phone": "+61234567890",
  "practice_email": "info@tailoredpsychology.com.au",
  "personal_website": "https://www.drpsychologist.com.au",
  "languages_spoken": "English, Spanish",
  "session_types": "Individual, Couples, Group",
  "medicare_rebate_amount": 75.00,
  "working_days": "Monday,Tuesday,Wednesday,Thursday,Friday",
  "start_time": "09:00:00",
  "end_time": "17:00:00",
  "session_duration_minutes": 60,
  "break_between_sessions_minutes": 15,
  "telehealth_available": true,
  "in_person_available": true,
  "is_accepting_new_patients": true,
  "max_patients_per_day": 8,
  "is_active_practitioner": true
}
```

---

## 🔐 Permissions

- ✅ **Psychologists** can update their own profile
- ✅ **Admins** can update any profile
- ✅ **Practice Managers** can update any profile
- ❌ **Patients** cannot update psychologist profiles

---

## 📊 Summary

**Total Editable Fields:** 23 fields

**Categories:**
- Professional Info: 4 fields
- Practice Details: 5 fields
- Communication: 2 fields
- Insurance & Billing: 3 fields
- Availability: 7 fields
- Profile & Settings: 6 fields

**Restricted Fields:** 9 fields (admin only)

---

**Psychologists have full control over their professional presentation and availability settings!** ✅


