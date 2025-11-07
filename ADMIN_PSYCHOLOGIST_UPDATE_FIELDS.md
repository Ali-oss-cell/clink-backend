# Admin - What Can Be Updated for Psychologists

## 🔐 Admin Update Permissions for Psychologists

### Endpoint: `PUT/PATCH /api/users/{id}/`

When updating a **psychologist user**, admins can update **ALL** of the following fields:

---

## ✅ Basic User Fields (All Users)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `email` | string | User email address | `"psychologist@clinic.com"` |
| `first_name` | string | First name | `"Sarah"` |
| `last_name` | string | Last name | `"Johnson"` |
| `full_name` | string | Full name (auto-split) | `"Dr. Sarah Johnson"` |
| `phone_number` | string | Phone number | `"+61400123456"` |
| `date_of_birth` | date | Date of birth | `"1985-05-15"` |
| `role` | string | User role | `"psychologist"` |
| `is_verified` | boolean | Email verification status | `true` |
| `is_active` | boolean | Account active status | `true` |

---

## ✅ Psychologist Profile Fields (Psychologist-Specific)

### Professional Credentials

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `ahpra_registration_number` | string | AHPRA registration number | `"PSY0001234567"` |
| `ahpra_expiry_date` | date | AHPRA registration expiry | `"2025-12-31"` |
| `title` | string | Professional title | `"Dr"`, `"Mr"`, `"Ms"`, `"Mrs"` |
| `qualifications` | string | Professional qualifications | `"PhD Psychology, Master of Clinical Psychology"` |
| `years_experience` | integer | Years of professional experience | `15` |

### Practice & Billing Information

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `consultation_fee` | decimal | Standard consultation fee (AUD) | `"200.00"` |
| `medicare_provider_number` | string | Medicare provider number | `"1234567A"` |
| `bio` | string | Professional biography | `"Experienced psychologist specializing in..."` |
| `is_accepting_new_patients` | boolean | Accepting new patients | `true` or `false` |

### Specializations & Services

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `specializations` | array | Array of specialization IDs | `[1, 2, 3]` |
| `services_offered` | array | Array of service IDs | `[1, 2, 5]` |

---

## 📝 Complete Example Request

### Update Psychologist with All Fields

```json
PATCH /api/users/5/
{
  // Basic User Fields
  "email": "sarah.johnson@clinic.com",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "full_name": "Dr. Sarah Johnson",  // Alternative to first_name/last_name
  "phone_number": "+61400123456",
  "date_of_birth": "1985-05-15",
  "is_verified": true,
  "is_active": true,
  
  // Psychologist Profile Fields
  "ahpra_registration_number": "PSY0001234567",
  "ahpra_expiry_date": "2025-12-31",
  "title": "Dr",
  "qualifications": "PhD Psychology, Master of Clinical Psychology, Bachelor of Psychology (Honours)",
  "years_experience": 15,
  "consultation_fee": "200.00",
  "medicare_provider_number": "1234567A",
  "bio": "Dr. Sarah Johnson is an experienced clinical psychologist with over 15 years of experience in treating anxiety, depression, and trauma-related disorders. She specializes in cognitive-behavioral therapy and mindfulness-based interventions.",
  "is_accepting_new_patients": true,
  "specializations": [1, 2, 3, 5],  // IDs of specializations
  "services_offered": [1, 2, 4]     // IDs of services
}
```

### Partial Update Example (Only Some Fields)

```json
PATCH /api/users/5/
{
  "consultation_fee": "210.00",
  "years_experience": 16,
  "is_accepting_new_patients": false,
  "bio": "Updated biography text..."
}
```

### Update Only Basic User Info

```json
PATCH /api/users/5/
{
  "email": "newemail@clinic.com",
  "phone_number": "+61400987654",
  "is_verified": true
}
```

### Update Only Professional Profile

```json
PATCH /api/users/5/
{
  "ahpra_registration_number": "PSY0001234567",
  "ahpra_expiry_date": "2026-12-31",
  "qualifications": "Updated qualifications",
  "specializations": [1, 2, 3]
}
```

---

## 🔄 Response Format

After updating, the response includes the complete user object with psychologist profile:

```json
{
  "id": 5,
  "email": "sarah.johnson@clinic.com",
  "full_name": "Dr. Sarah Johnson",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "role": "psychologist",
  "is_verified": true,
  "is_active": true,
  "created_at": "2024-01-15T10:00:00Z",
  "last_login": "2024-01-20T14:30:00Z",
  "phone_number": "+61400123456",
  "username": "sarah.johnson",
  "psychologist_profile": {
    "id": 3,
    "ahpra_registration_number": "PSY0001234567",
    "ahpra_expiry_date": "2025-12-31",
    "title": "Dr",
    "qualifications": "PhD Psychology, Master of Clinical Psychology",
    "years_experience": 15,
    "consultation_fee": "200.00",
    "medicare_provider_number": "1234567A",
    "bio": "Professional biography...",
    "is_accepting_new_patients": true,
    "specializations": [
      {"id": 1, "name": "Anxiety Disorders"},
      {"id": 2, "name": "Depression"},
      {"id": 3, "name": "Trauma"}
    ],
    "services_offered": [
      {"id": 1, "name": "Individual Therapy"},
      {"id": 2, "name": "Couples Therapy"}
    ],
    ...
  }
}
```

---

## ✅ Summary: What Admin Can Update for Psychologists

### ✅ **ALL Basic User Fields**
- Email, name, phone, date of birth
- Verification status, active status
- Role (can change to/from psychologist)

### ✅ **ALL Psychologist Profile Fields**
- AHPRA registration details
- Professional credentials (title, qualifications, experience)
- Practice information (fees, Medicare provider number)
- Bio and availability
- Specializations and services

### ✅ **Special Capabilities**
- Can change psychologist's role to another role
- Can activate/deactivate psychologist account
- Can verify/unverify email
- Can update all fields in a single request
- Can do partial updates (only send fields to change)

---

## 🚫 What Admin Cannot Do

- ❌ Cannot delete psychologist if they have active appointments
- ❌ Cannot delete psychologist if they have unpaid invoices
- ❌ Cannot change another user to admin role (safety measure)

---

## 💡 Important Notes

1. **Partial Updates**: You can send only the fields you want to update (PATCH)
2. **Full Updates**: Send all fields for complete replacement (PUT)
3. **Automatic Profile Creation**: If psychologist profile doesn't exist, it will be created when you update psychologist-specific fields
4. **Many-to-Many Fields**: `specializations` and `services_offered` replace the entire list, so send all IDs you want to keep
5. **Full Name**: If you send `full_name`, it will automatically split into `first_name` and `last_name`

---

## 📋 Quick Reference Checklist

When updating a psychologist, admin can update:

- [x] Email address
- [x] Name (first, last, or full)
- [x] Phone number
- [x] Date of birth
- [x] Verification status
- [x] Active status
- [x] Role
- [x] AHPRA registration number
- [x] AHPRA expiry date
- [x] Professional title
- [x] Qualifications
- [x] Years of experience
- [x] Consultation fee
- [x] Medicare provider number
- [x] Professional biography
- [x] Accepting new patients status
- [x] Specializations (list)
- [x] Services offered (list)

**Total: 18+ fields that can be updated!**

