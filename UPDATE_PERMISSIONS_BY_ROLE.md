# Update Permissions by Role

## 📋 Practice Manager - What They Can Update

### Endpoint: `PUT/PATCH /api/users/{id}/`

Practice managers can update **all users EXCEPT admins**.

### ✅ Can Update:

#### Basic User Fields (for any user):
- ✅ `email` - User email address
- ✅ `first_name` - First name
- ✅ `last_name` - Last name
- ✅ `full_name` - Full name (will be split into first_name/last_name)
- ✅ `phone_number` - Phone number
- ✅ `date_of_birth` - Date of birth
- ✅ `is_verified` - Email verification status
- ✅ `is_active` - Account active status

#### Psychologist Profile Fields (when updating a psychologist):
- ✅ `ahpra_registration_number` - AHPRA registration number
- ✅ `ahpra_expiry_date` - AHPRA expiry date
- ✅ `title` - Title (Dr, Mr, Ms, Mrs)
- ✅ `qualifications` - Professional qualifications
- ✅ `years_experience` - Years of experience
- ✅ `consultation_fee` - Consultation fee
- ✅ `medicare_provider_number` - Medicare provider number
- ✅ `bio` - Professional biography
- ✅ `is_accepting_new_patients` - Accepting new patients status
- ✅ `specializations` - Array of specialization IDs
- ✅ `services_offered` - Array of service IDs

### ❌ Cannot Update:
- ❌ `role` - Cannot change user roles (admin only)
- ❌ Admin users - Cannot update administrators at all
- ❌ Cannot delete users (admin only)

### Example Request:
```json
PATCH /api/users/5/
{
  "full_name": "Dr. Sarah Johnson",
  "phone_number": "+61400123456",
  "is_verified": true,
  "qualifications": "PhD Psychology, Master of Clinical Psychology",
  "years_experience": 15,
  "consultation_fee": "200.00",
  "is_accepting_new_patients": true,
  "specializations": [1, 2, 3]
}
```

---

## 👨‍⚕️ Psychologist (Doctor) - What They Can Update

### Endpoint: `PUT/PATCH /api/auth/profile/`

Psychologists can **only update their own profile**.

### ✅ Can Update (Their Own Profile):

#### Basic User Fields:
- ✅ `email` - Their email address
- ✅ `first_name` - First name
- ✅ `last_name` - Last name
- ✅ `phone_number` - Phone number
- ✅ `date_of_birth` - Date of birth

#### Psychologist Profile Fields (via separate endpoint):
Psychologists should update their professional profile via:
- `PUT/PATCH /api/services/psychologists/my_profile/`

This includes:
- ✅ `ahpra_registration_number` - AHPRA registration number
- ✅ `ahpra_expiry_date` - AHPRA expiry date
- ✅ `title` - Title (Dr, Mr, Ms, Mrs)
- ✅ `qualifications` - Professional qualifications
- ✅ `years_experience` - Years of experience
- ✅ `consultation_fee` - Consultation fee
- ✅ `medicare_provider_number` - Medicare provider number
- ✅ `bio` - Professional biography
- ✅ `is_accepting_new_patients` - Accepting new patients status
- ✅ `specializations` - Array of specialization IDs
- ✅ `services_offered` - Array of service IDs
- ✅ `profile_image` - Profile image upload
- ✅ `working_hours` - Working hours
- ✅ `telehealth_available` - Telehealth availability
- ✅ And other profile-specific fields

### ❌ Cannot Update:
- ❌ Other users - Cannot update any other user's profile
- ❌ `role` - Cannot change their own role
- ❌ `is_verified` - Cannot change verification status
- ❌ `is_active` - Cannot change active status
- ❌ Cannot delete users

### Example Request (Basic Profile):
```json
PATCH /api/auth/profile/
{
  "first_name": "Sarah",
  "last_name": "Johnson",
  "phone_number": "+61400123456"
}
```

### Example Request (Professional Profile):
```json
PATCH /api/services/psychologists/my_profile/
{
  "qualifications": "PhD Psychology, Master of Clinical Psychology",
  "years_experience": 16,
  "consultation_fee": "210.00",
  "bio": "Updated professional biography...",
  "is_accepting_new_patients": false,
  "specializations": [1, 2, 3]
}
```

---

## 🔐 Admin - What They Can Update

### Endpoint: `PUT/PATCH /api/users/{id}/`

Admins can update **all users** including other admins.

### ✅ Can Update:

#### Everything Practice Managers Can Update, PLUS:
- ✅ `role` - Can change user roles (except cannot make another user admin)
- ✅ Admin users - Can update other administrators
- ✅ Can delete users (with safety checks)

### ❌ Cannot Update:
- ❌ Cannot change another user to admin role (only themselves)

---

## 📊 Summary Table

| Field | Practice Manager | Psychologist (Own) | Admin |
|-------|-----------------|-------------------|-------|
| **Basic User Fields** |
| `email` | ✅ (non-admins) | ✅ (own) | ✅ (all) |
| `first_name` | ✅ (non-admins) | ✅ (own) | ✅ (all) |
| `last_name` | ✅ (non-admins) | ✅ (own) | ✅ (all) |
| `phone_number` | ✅ (non-admins) | ✅ (own) | ✅ (all) |
| `date_of_birth` | ✅ (non-admins) | ✅ (own) | ✅ (all) |
| `is_verified` | ✅ (non-admins) | ❌ | ✅ (all) |
| `is_active` | ✅ (non-admins) | ❌ | ✅ (all) |
| `role` | ❌ | ❌ | ✅ (all, except admin) |
| **Psychologist Profile** |
| `ahpra_registration_number` | ✅ (psychologists) | ✅ (own) | ✅ (all) |
| `ahpra_expiry_date` | ✅ (psychologists) | ✅ (own) | ✅ (all) |
| `title` | ✅ (psychologists) | ✅ (own) | ✅ (all) |
| `qualifications` | ✅ (psychologists) | ✅ (own) | ✅ (all) |
| `years_experience` | ✅ (psychologists) | ✅ (own) | ✅ (all) |
| `consultation_fee` | ✅ (psychologists) | ✅ (own) | ✅ (all) |
| `medicare_provider_number` | ✅ (psychologists) | ✅ (own) | ✅ (all) |
| `bio` | ✅ (psychologists) | ✅ (own) | ✅ (all) |
| `is_accepting_new_patients` | ✅ (psychologists) | ✅ (own) | ✅ (all) |
| `specializations` | ✅ (psychologists) | ✅ (own) | ✅ (all) |
| `services_offered` | ✅ (psychologists) | ✅ (own) | ✅ (all) |
| **Actions** |
| Update other users | ✅ (non-admins) | ❌ | ✅ (all) |
| Delete users | ❌ | ❌ | ✅ (with checks) |
| Update admins | ❌ | ❌ | ✅ |

---

## 🔍 Key Differences

### Practice Manager:
- **Can manage**: All users except admins
- **Cannot change**: User roles
- **Use case**: Day-to-day user management, updating psychologist profiles, managing patient information

### Psychologist:
- **Can manage**: Only their own profile
- **Use case**: Keeping their own information up to date, managing their professional profile

### Admin:
- **Can manage**: Everything
- **Use case**: Full system administration, user management, role changes

---

## 📝 Notes

1. **Practice Managers** have broad update permissions but cannot change roles or manage admins
2. **Psychologists** can only update their own profile via `/api/auth/profile/` and their professional profile via `/api/services/psychologists/my_profile/`
3. **Admins** have full control but cannot create other admin users (safety measure)
4. All updates support **partial updates** (PATCH) - you only need to send the fields you want to change
5. The `full_name` field is automatically split into `first_name` and `last_name` when provided

