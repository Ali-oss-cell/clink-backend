# User Update & Delete Endpoints - Implementation Status

## ✅ COMPLETED

### 1. GET Single User Endpoint
- **Endpoint**: `GET /api/users/{id}/`
- **Status**: ✅ Implemented
- **Features**:
  - Returns user with all fields
  - Includes psychologist profile data if user is a psychologist
  - Uses `UserSerializer` which includes `psychologist_profile` field
  - Role-based access control (admins/practice managers can see all, others see only themselves)

### 2. Update User Endpoint
- **Endpoints**: 
  - `PUT /api/users/{id}/` (full update)
  - `PATCH /api/users/{id}/` (partial update)
- **Status**: ✅ Implemented
- **Features**:
  - ✅ Supports partial updates (PATCH)
  - ✅ Handles `full_name` field (splits into first_name/last_name)
  - ✅ Updates basic user fields (email, phone, role, is_verified, is_active, etc.)
  - ✅ Updates psychologist profile fields when role is psychologist
  - ✅ Handles specializations and services_offered (many-to-many)
  - ✅ Permission checks:
    - Admins can update all users (except cannot make another user admin)
    - Practice managers can update all users except admins
    - Practice managers cannot change roles
  - ✅ Returns updated user with full data including psychologist profile

### 3. Delete User Endpoint
- **Endpoint**: `DELETE /api/users/{id}/`
- **Status**: ✅ Implemented
- **Features**:
  - ✅ Admin-only access
  - ✅ Safety checks before deletion:
    - Checks for active appointments (scheduled/confirmed)
    - Checks for unpaid invoices
    - Prevents deletion of the only active admin
  - ✅ Returns 204 No Content on success
  - ✅ Returns 400 with error message if dependencies exist

### 4. Serializers
- **UserSerializer**: ✅ Updated to include `psychologist_profile` field
- **UserUpdateSerializer**: ✅ Created to handle user and psychologist profile updates

## 📋 Implementation Details

### UserUpdateSerializer
Handles:
- Basic user fields (email, first_name, last_name, full_name, phone_number, role, is_verified, is_active, date_of_birth)
- Psychologist profile fields:
  - `ahpra_registration_number`
  - `ahpra_expiry_date`
  - `title`
  - `qualifications`
  - `years_experience`
  - `consultation_fee`
  - `medicare_provider_number`
  - `bio`
  - `is_accepting_new_patients`
  - `specializations` (array of IDs)
  - `services_offered` (array of IDs)

### Permission Rules

#### Update Permissions:
1. **Admins**:
   - ✅ Can update all users
   - ✅ Can change roles (except cannot change another user to admin)
   - ✅ Can update all fields including psychologist profile

2. **Practice Managers**:
   - ✅ Can update all users (except admins)
   - ❌ Cannot change roles
   - ✅ Can update all fields including psychologist profile
   - ✅ Can update verification and active status

3. **Psychologists/Patients**:
   - ❌ Cannot update other users (only their own profile via different endpoint)

#### Delete Permissions:
1. **Admins**:
   - ✅ Can delete any user (with safety checks)

2. **Practice Managers/Others**:
   - ❌ Cannot delete users

### Safety Checks for Deletion
- ✅ User has active appointments (scheduled or confirmed)
- ✅ User has unpaid invoices
- ✅ User is the only admin in the system

## 📝 Example Usage

### Update Basic User Info
```bash
PATCH /api/users/1/
{
  "full_name": "John Smith",
  "phone_number": "+61400123456",
  "is_verified": true
}
```

### Update Psychologist Profile
```bash
PATCH /api/users/2/
{
  "qualifications": "PhD Psychology, Master of Clinical Psychology",
  "years_experience": 16,
  "consultation_fee": "210.00",
  "is_accepting_new_patients": false,
  "specializations": [1, 2, 3],
  "services_offered": [1, 2]
}
```

### Update Role and Status (Admin Only)
```bash
PATCH /api/users/3/
{
  "role": "practice_manager",
  "is_active": false
}
```

### Delete User (Admin Only)
```bash
DELETE /api/users/1/
```

### Get Single User
```bash
GET /api/users/1/
```

## 🔄 Response Formats

### Update Success (200 OK)
```json
{
  "id": 1,
  "email": "updated@example.com",
  "full_name": "Updated Name",
  "first_name": "Updated",
  "last_name": "Name",
  "role": "psychologist",
  "is_verified": true,
  "is_active": true,
  "created_at": "2024-01-15T10:00:00Z",
  "last_login": "2024-01-20T14:30:00Z",
  "phone_number": "+61400123456",
  "username": "updated",
  "psychologist_profile": {
    "id": 1,
    "ahpra_registration_number": "PSY0001234567",
    "qualifications": "PhD Psychology",
    ...
  }
}
```

### Delete Success (204 No Content)
No response body.

### Error Responses
- **403 Forbidden**: Permission denied
- **400 Bad Request**: Validation errors or safety check failures
- **404 Not Found**: User not found

## ✅ All Requirements Met

All requirements from the specification document have been implemented:
- ✅ Update endpoint with partial update support
- ✅ Delete endpoint with safety checks
- ✅ Get single user endpoint with psychologist profile
- ✅ Permission-based access control
- ✅ Psychologist profile update support
- ✅ Proper error handling and responses

## 🚀 Ready for Frontend Integration

The endpoints are fully functional and ready to be integrated with the frontend user management page.

