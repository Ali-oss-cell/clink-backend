# Fix: 400 Bad Request on Patient Registration

## Problem
Getting 400 Bad Request when trying to register a patient at `/api/auth/register/patient/`

## Solution

The error is likely due to missing required fields or validation failures. The backend now returns detailed error messages.

### Check What Fields Are Required

The `PatientRegistrationSerializer` requires these fields:

```typescript
{
  email: string (required)
  password: string (required, min 8 characters)
  password_confirm: string (required, must match password)
  first_name: string (required)
  last_name: string (required)
  phone_number: string (required, Australian format)
  date_of_birth: string (required, YYYY-MM-DD format)
  address_line_1: string (required)
  suburb: string (required)
  state: string (required, one of: NSW, VIC, QLD, WA, SA, TAS, ACT, NT)
  postcode: string (required, 4 digits)
  medicare_number: string (optional)
}
```

### Frontend Registration Form Example

Make sure your frontend is sending all required fields:

```typescript
const registerData = {
  email: 'patient@example.com',
  password: 'password123',
  password_confirm: 'password123',  // Must match password
  first_name: 'John',
  last_name: 'Doe',
  phone_number: '+61412345678',  // Australian format
  date_of_birth: '1990-01-01',  // YYYY-MM-DD format
  address_line_1: '123 Main St',
  suburb: 'Melbourne',
  state: 'VIC',  // Must be valid Australian state
  postcode: '3000',  // 4 digits
  medicare_number: '1234567890'  // Optional
};

// Send to backend
const response = await axios.post('/api/auth/register/patient/', registerData);
```

### Check the Error Response

The backend now returns detailed error messages. Check your browser's Network tab:

1. Open DevTools (F12)
2. Go to Network tab
3. Try to register
4. Click on the failed request
5. Look at the Response tab

You should see something like:
```json
{
  "error": "Registration validation failed",
  "details": {
    "email": ["This field is required."],
    "password": ["This field is required."],
    // ... other field errors
  }
}
```

### Common Issues

1. **Missing required fields** - Make sure all required fields are sent
2. **Password mismatch** - `password` and `password_confirm` must match
3. **Invalid phone format** - Must be Australian format: `+61XXXXXXXXX` or `0XXXXXXXXX`
4. **Invalid state** - Must be one of: NSW, VIC, QLD, WA, SA, TAS, ACT, NT
5. **Invalid postcode** - Must be 4 digits
6. **Invalid date format** - Must be YYYY-MM-DD

### Test with curl

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/patient/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+61412345678",
    "date_of_birth": "1990-01-01",
    "address_line_1": "123 Main St",
    "suburb": "Melbourne",
    "state": "VIC",
    "postcode": "3000"
  }' | python3 -m json.tool
```

This will show you the exact validation errors.

