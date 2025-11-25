# Video Call Test Script Usage Guide

## 🎯 What This Script Does

The `test_video_call.py` script automatically:
1. ✅ Creates test doctor and patient (first run only)
2. ✅ Reuses existing test users (subsequent runs)
3. ✅ Creates a new appointment (5 minutes from now by default)
4. ✅ Creates Twilio video room
5. ✅ Generates video tokens for both users
6. ✅ Provides full testing instructions

---

## 🚀 How to Run

### On Your Droplet:

```bash
# Navigate to project directory
cd /var/www/clink-backend

# Activate virtual environment
source venv/bin/activate

# Run the test script
python test_video_call.py
```

### On Your Local Machine:

```bash
# Navigate to project directory
cd /home/ali/Desktop/projects/clink-backend

# Activate virtual environment
source venv/bin/activate

# Run the test script
python test_video_call.py
```

---

## 📝 What You'll See

### First Run (Creates Test Users):

```
============================================================
     Step 1: Setting Up Test Users
============================================================

ℹ Creating new test users...
✓ Created doctor: Dr. Sarah Thompson (test.doctor@clinic.test)
✓ Created patient: John Smith (test.patient@clinic.test)
✓ Created test service: Telehealth Consultation

============================================================
        Step 2: Creating Test Appointment
============================================================

How many minutes from now should the appointment be?
Enter minutes (default: 5): 5

ℹ Scheduling appointment for: 2025-11-24 15:30:00
ℹ (In 5 minutes from now)
✓ Created appointment ID: 1
✓ Appointment date: 2025-11-24
✓ Appointment time: 15:30:00

============================================================
          Step 3: Creating Video Room
============================================================

ℹ Validating Twilio credentials...
✓ Twilio credentials valid
ℹ Creating video room...
✓ Video room created: apt-1-1732426800-a1b2c3d4
✓ Room SID: RMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

============================================================
     Step 4: Generating Video Access Tokens
============================================================

✓ Tokens generated successfully

============================================================
            ✅ Test Setup Complete!
============================================================

Test Users:
  Doctor:  test.doctor@clinic.test / password: test123
  Patient: test.patient@clinic.test / password: test123

Appointment Details:
  ID: 1
  Date: 2025-11-24
  Time: 15:30:00
  Room: apt-1-1732426800-a1b2c3d4

API Endpoints to Test:
  1. Get Doctor Token:
     GET https://api.tailoredpsychology.com.au/api/appointments/video-token/1/
     Authorization: Bearer <doctor_jwt_token>

  2. Get Patient Token:
     GET https://api.tailoredpsychology.com.au/api/appointments/video-token/1/
     Authorization: Bearer <patient_jwt_token>

Direct Tokens (for quick testing):
  Doctor Token:
    Identity: 2-test.doctor@clinic.test
    Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ...

  Patient Token:
    Identity: 1-test.patient@clinic.test
    Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ...

How to Test:
  1. Login as doctor in your frontend: test.doctor@clinic.test
  2. Login as patient in another browser: test.patient@clinic.test
  3. Both join the video call for appointment 1
  4. Tokens are valid for 2 hours

⚠ Note: Run this script again to create a new test appointment
⚠       The same test users will be reused
```

### Subsequent Runs (Reuses Test Users):

```
============================================================
     Step 1: Setting Up Test Users
============================================================

ℹ Found existing test users
✓ Doctor: Dr. Sarah Thompson (test.doctor@clinic.test)
✓ Patient: John Smith (test.patient@clinic.test)

... (continues with new appointment)
```

---

## 🎮 Testing Workflow

### 1. Run the Script

```bash
python test_video_call.py
```

### 2. Login as Doctor (Browser 1)

Go to your frontend: `https://tailoredpsychology.com.au/login`

- Email: `test.doctor@clinic.test`
- Password: `test123`

### 3. Login as Patient (Browser 2 or Incognito)

Go to your frontend: `https://tailoredpsychology.com.au/login`

- Email: `test.patient@clinic.test`
- Password: `test123`

### 4. Join Video Call

Both users navigate to the video call page for the appointment ID shown in the script output.

---

## 🔧 Customization

### Change Appointment Time

When prompted:
```
How many minutes from now should the appointment be?
Enter minutes (default: 5): 10  ← Enter your desired minutes
```

Or edit the script directly:
```python
# Line ~185
minutes = int(input(...) or "5")  # Change default here
```

### Change Test User Details

Edit the script at lines ~66-120 to customize:
- Email addresses
- Names
- Phone numbers
- Specialization
- Medicare details

---

## 🐛 Troubleshooting

### Error: "Twilio credentials invalid"

**Solution**: Check your `.env` file has all 4 Twilio variables:
```bash
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_API_KEY=your-twilio-api-key-sid
TWILIO_API_SECRET=your-twilio-api-secret
```

### Error: "API Key invalid"

**Solution**: Verify your `TWILIO_API_SECRET` matches your API Key:
```bash
python manage.py shell
```
```python
from appointments.video_service import get_video_service
video_service = get_video_service()
print(video_service.validate_credentials())
```

### Error: "Failed to create video room"

**Possible causes**:
1. Twilio credentials missing or invalid
2. Trial account restrictions (upgrade needed)
3. Network connectivity issues

**Solution**: Check Twilio Console for errors

### Test Users Already Exist

**This is normal!** The script reuses existing test users. If you want fresh users:
```bash
python manage.py shell
```
```python
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.filter(email__contains='clinic.test').delete()
```

---

## 📋 Quick Commands

### Get Test User JWT Tokens:

```bash
# Login as doctor
curl -X POST https://api.tailoredpsychology.com.au/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test.doctor@clinic.test", "password": "test123"}'

# Login as patient
curl -X POST https://api.tailoredpsychology.com.au/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test.patient@clinic.test", "password": "test123"}'
```

### Get Video Tokens via API:

```bash
# Doctor's token
curl -X GET https://api.tailoredpsychology.com.au/api/appointments/video-token/1/ \
  -H "Authorization: Bearer <doctor_jwt_token>"

# Patient's token
curl -X GET https://api.tailoredpsychology.com.au/api/appointments/video-token/1/ \
  -H "Authorization: Bearer <patient_jwt_token>"
```

### Delete Test Appointment:

```bash
python manage.py shell
```
```python
from appointments.models import Appointment
Appointment.objects.filter(patient__email='test.patient@clinic.test').delete()
```

---

## ✅ What to Test

1. **Token Generation**:
   - ✓ Both doctor and patient can get tokens
   - ✓ Tokens have different identities
   - ✓ Tokens work with Twilio Video SDK

2. **Video Room**:
   - ✓ Room is created successfully
   - ✓ Both users can join the same room
   - ✓ Users see each other's video/audio

3. **Security**:
   - ✓ Only authorized users can get tokens
   - ✓ Tokens expire after 2 hours
   - ✓ Users can only access their own appointments

4. **Edge Cases**:
   - ✓ Token refresh works
   - ✓ Multiple participants can't join (max 2)
   - ✓ Room closes after session ends

---

## 📚 Related Files

- `VIDEO_CALL_SETUP_GUIDE.md` - Full setup documentation
- `TWILIO_UPGRADE_GUIDE.md` - Upgrade from trial account
- `appointments/video_service.py` - Video service implementation
- `appointments/views.py` - Video token endpoints

---

## 🎉 Success Criteria

You know video calls are working when:
- ✅ Script runs without errors
- ✅ Both tokens are generated
- ✅ Doctor and patient can login
- ✅ Both can request video tokens via API
- ✅ Both can join the same video room
- ✅ Video and audio work for both users

Happy testing! 🚀

