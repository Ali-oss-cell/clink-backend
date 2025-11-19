# Privacy Policy Endpoint Troubleshooting Guide

## Common Errors and Solutions

### Error: "PrivacyService] Error getting Privacy Policy status"

This error can occur for several reasons. Here's how to debug and fix it:

---

## 1. Check Authentication

**Problem:** User is not authenticated or token is invalid.

**Solution:**
```typescript
// In your frontend, make sure you're sending the token:
const token = localStorage.getItem('access_token');
if (!token) {
  // Redirect to login
  navigate('/login');
  return;
}

// Make sure axios instance includes the token
axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
```

**Test:**
```bash
# Test with curl
curl -X GET http://127.0.0.1:8000/api/auth/privacy-policy/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 2. Check User Role

**Problem:** User is not a patient (might be psychologist, admin, etc.)

**Solution:**
The endpoint only works for patients. If you're testing with a non-patient user, you'll get a 403 error.

**Check user role:**
```python
# In Django shell
python manage.py shell
>>> from users.models import User
>>> user = User.objects.get(email='test@example.com')
>>> print(user.role)  # Should be 'patient'
```

---

## 3. Check Database Migration

**Problem:** Migration hasn't been run, so the new fields don't exist.

**Solution:**
```bash
# Run migrations
python manage.py migrate

# Check if migration was applied
python manage.py showmigrations users
```

**Expected output:**
```
users
 [X] 0001_initial
 [X] 0002_...
 [X] 0005_add_privacy_consent_fields  <-- Should be checked
```

---

## 4. Check PatientProfile Exists

**Problem:** PatientProfile doesn't exist for the user.

**Solution:**
The endpoint now automatically creates a PatientProfile if it doesn't exist, but you can manually create one:

```python
# In Django shell
python manage.py shell
>>> from users.models import User, PatientProfile
>>> user = User.objects.get(email='test@example.com')
>>> profile, created = PatientProfile.objects.get_or_create(user=user)
>>> print(f"Profile created: {created}")
```

---

## 5. Check Settings Configuration

**Problem:** Settings are not configured correctly.

**Solution:**
Add to your `.env` file:
```env
PRIVACY_POLICY_VERSION=1.0
PRIVACY_POLICY_URL=https://yourclinic.com.au/privacy-policy
CONSENT_FORM_VERSION=1.0
TELEHEALTH_CONSENT_VERSION=1.0
```

Or check in Django shell:
```python
python manage.py shell
>>> from django.conf import settings
>>> print(getattr(settings, 'PRIVACY_POLICY_VERSION', 'Not set'))
>>> print(getattr(settings, 'PRIVACY_POLICY_URL', 'Not set'))
```

---

## 6. Check CORS Configuration

**Problem:** CORS is blocking the request from frontend.

**Solution:**
Make sure your frontend URL is in `CORS_ALLOWED_ORIGINS` in `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite
    "http://127.0.0.1:5173",
]
```

---

## 7. Check Server Logs

**Problem:** Server-side error that's not being shown in frontend.

**Solution:**
Check Django server logs for the actual error:
```bash
# Look for errors in terminal where Django is running
# Or check logs/django.log
tail -f logs/django.log
```

---

## 8. Test Endpoint Directly

**Test with curl:**
```bash
# 1. Get a token first
TOKEN=$(curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"patient@example.com","password":"password"}' \
  | jq -r '.access')

# 2. Test Privacy Policy endpoint
curl -X GET http://127.0.0.1:8000/api/auth/privacy-policy/ \
  -H "Authorization: Bearer $TOKEN" \
  | jq
```

**Expected response:**
```json
{
  "accepted": false,
  "accepted_date": null,
  "version": "",
  "latest_version": "1.0",
  "needs_update": true,
  "privacy_policy_url": "https://yourclinic.com.au/privacy-policy"
}
```

---

## 9. Frontend Error Handling

**Update your frontend API service to handle errors better:**

```typescript
// src/services/api/privacy.ts
export const getPrivacyPolicyStatus = async (): Promise<PrivacyPolicyStatus> => {
  try {
    const response = await axiosInstance.get<PrivacyPolicyStatus>('/api/auth/privacy-policy/');
    return response.data;
  } catch (error: any) {
    console.error('[PrivacyService] Error getting Privacy Policy status:', error);
    
    // Handle specific error cases
    if (error.response) {
      // Server responded with error status
      if (error.response.status === 401) {
        // Not authenticated - redirect to login
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        throw new Error('Authentication required');
      } else if (error.response.status === 403) {
        // Not a patient
        throw new Error('Only patients can view Privacy Policy status');
      } else if (error.response.status === 500) {
        // Server error
        throw new Error('Server error. Please try again later.');
      }
      
      // Return error message from server
      throw new Error(error.response.data?.error || 'Failed to get Privacy Policy status');
    } else if (error.request) {
      // Request made but no response
      throw new Error('No response from server. Please check your connection.');
    } else {
      // Something else happened
      throw new Error('An unexpected error occurred');
    }
  }
};
```

---

## 10. Debug Checklist

Run through this checklist:

- [ ] User is authenticated (has valid token)
- [ ] User role is 'patient'
- [ ] Migrations have been run (`python manage.py migrate`)
- [ ] Django server is running
- [ ] CORS is configured correctly
- [ ] Settings are configured (PRIVACY_POLICY_VERSION, etc.)
- [ ] Frontend is using correct API URL
- [ ] Frontend is sending Authorization header
- [ ] Check browser Network tab for actual error response
- [ ] Check Django server logs for errors

---

## Quick Fix Script

Run this to check everything:

```bash
# Check migrations
python manage.py showmigrations users | grep privacy

# Check if endpoint is registered
python manage.py show_urls | grep privacy

# Test with a patient user
python manage.py shell << EOF
from users.models import User, PatientProfile
from django.conf import settings

# Check if patient exists
patient = User.objects.filter(role='patient').first()
if patient:
    print(f"Patient found: {patient.email}")
    profile, created = PatientProfile.objects.get_or_create(user=patient)
    print(f"Profile exists: {not created}")
    print(f"Privacy Policy accepted: {profile.privacy_policy_accepted}")
    print(f"Version: {profile.privacy_policy_version}")
else:
    print("No patient users found")

# Check settings
print(f"PRIVACY_POLICY_VERSION: {getattr(settings, 'PRIVACY_POLICY_VERSION', 'Not set')}")
print(f"PRIVACY_POLICY_URL: {getattr(settings, 'PRIVACY_POLICY_URL', 'Not set')}")
EOF
```

---

## Still Having Issues?

1. **Check the actual error message** in browser console (Network tab)
2. **Check Django server logs** for server-side errors
3. **Test the endpoint directly** with curl or Postman
4. **Verify the user is a patient** in Django admin
5. **Check if PatientProfile exists** for the user

If you're still stuck, share:
- The exact error message from browser console
- The HTTP status code from Network tab
- Any errors from Django server logs

