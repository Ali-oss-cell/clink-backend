# 🚀 Next Steps - Patient Appointments Endpoint

## ✅ What's Done
The patient appointments endpoint is **fully implemented and running** at:
```
GET http://localhost:8000/api/appointments/patient/appointments/
```

---

## 🧪 Option 1: Quick Test with Python Script

I've created a test script for you. Run it:

```bash
cd /home/ali/Desktop/projects/clink-backend
source venv/bin/activate
python test_patient_appointments.py
```

This script will:
- Prompt for patient login credentials
- Get a JWT token
- Let you test different filters (all, upcoming, completed, etc.)
- Display results in a nice format
- Show the full JSON response

---

## 🔧 Option 2: Test with cURL

### Step 1: Get a JWT Token
```bash
# Login as a patient
curl -X POST http://localhost:8000/api/users/login/ \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "patient@example.com",
    "password": "your_password"
  }'

# Save the "access" token from the response
```

### Step 2: Test the Endpoint
```bash
# Replace YOUR_TOKEN with the access token from step 1

# Get all appointments
curl -X GET 'http://localhost:8000/api/appointments/patient/appointments/' \
  -H 'Authorization: Bearer YOUR_TOKEN'

# Get upcoming appointments
curl -X GET 'http://localhost:8000/api/appointments/patient/appointments/?status=upcoming' \
  -H 'Authorization: Bearer YOUR_TOKEN'

# Get with pagination
curl -X GET 'http://localhost:8000/api/appointments/patient/appointments/?page=1&page_size=5' \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

---

## 📮 Option 3: Test with Postman

1. **Import the collection:**
   - Open Postman
   - Click "Import"
   - Select `PATIENT_APPOINTMENTS_POSTMAN.json`

2. **Set variables:**
   - `base_url`: `http://localhost:8000`
   - `access_token`: Your JWT token

3. **Run requests:**
   - Try "Get All Appointments"
   - Try "Get Upcoming Appointments"
   - Try other pre-configured requests

---

## 🌐 Option 4: Test in Browser

### Using Browser Extension (like RESTClient)

1. **GET** `http://localhost:8000/api/appointments/patient/appointments/?status=upcoming`

2. **Headers:**
   ```
   Authorization: Bearer YOUR_JWT_TOKEN
   Content-Type: application/json
   ```

3. Click **Send**

---

## 📊 What to Check

When testing, verify these things work:

### ✅ Basic Functionality
- [ ] Endpoint returns 200 OK status
- [ ] Response has `count`, `next`, `previous`, `results` fields
- [ ] Results array contains appointment objects

### ✅ Pagination
- [ ] Default page size is 10
- [ ] `next` URL works for page 2
- [ ] `previous` URL works when going back
- [ ] Custom page_size works

### ✅ Status Filtering
- [ ] `status=all` returns all appointments
- [ ] `status=upcoming` returns only future appointments
- [ ] `status=completed` returns completed ones
- [ ] `status=cancelled` returns cancelled ones
- [ ] `status=past` returns past appointments

### ✅ Appointment Fields
- [ ] `formatted_date` is in YYYY-MM-DD format
- [ ] `formatted_time` is in HH:MM AM/PM format
- [ ] `psychologist.name` includes title (e.g., "Dr. Sarah Johnson")
- [ ] `psychologist.profile_image_url` is an absolute URL or null
- [ ] `can_reschedule` is boolean
- [ ] `can_cancel` is boolean
- [ ] `reschedule_deadline` is ISO 8601 datetime
- [ ] `cancellation_deadline` is ISO 8601 datetime

### ✅ Session Type Logic
- [ ] In-person appointments have `location` set
- [ ] In-person appointments have `meeting_link` as null
- [ ] Telehealth appointments have `meeting_link` set (if video_room_id exists)
- [ ] Telehealth appointments have `location` as null

---

## 🔐 Getting a Patient User Account

If you don't have a patient account, you can:

### Option A: Check existing users
```bash
cd /home/ali/Desktop/projects/clink-backend
source venv/bin/activate
python manage.py shell -c "from users.models import User; patients = User.objects.filter(role='patient'); print('Patients:', [(u.email, u.id) for u in patients[:5]])"
```

### Option B: Create a test patient
```bash
python manage.py shell
```

Then in the shell:
```python
from users.models import User

# Create patient
patient = User.objects.create_user(
    email='testpatient@example.com',
    password='testpass123',
    first_name='Test',
    last_name='Patient',
    role='patient'
)
print(f"Created patient: {patient.email}")
```

---

## 🎨 Frontend Integration (Next Phase)

Once testing is complete, integrate with your frontend:

### React Example
```jsx
const fetchAppointments = async (status = 'upcoming') => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(
    `http://localhost:8000/api/appointments/patient/appointments/?status=${status}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  const data = await response.json();
  return data;
};
```

### Display in UI
```jsx
{appointments.map(apt => (
  <div key={apt.id} className="appointment-card">
    <img src={apt.psychologist.profile_image_url} />
    <h3>{apt.psychologist.name}</h3>
    <p>{apt.formatted_date} at {apt.formatted_time}</p>
    
    {apt.session_type === 'telehealth' && apt.meeting_link && (
      <a href={apt.meeting_link}>Join Video Session</a>
    )}
    
    {apt.can_reschedule && <button>Reschedule</button>}
    {apt.can_cancel && <button>Cancel</button>}
  </div>
))}
```

---

## 📚 Documentation Reference

Refer to these files for detailed information:

1. **`PATIENT_APPOINTMENTS_API_DOCUMENTATION.md`**
   - Complete API reference
   - All request/response examples
   - Error handling

2. **`PATIENT_APPOINTMENTS_ENDPOINT_SUMMARY.md`**
   - Implementation details
   - Business logic
   - Performance info

3. **`PATIENT_APPOINTMENTS_FLOW.md`**
   - Visual flow diagrams
   - Database query flow
   - Authentication flow

4. **`PATIENT_APPOINTMENTS_IMPLEMENTATION_COMPLETE.md`**
   - Complete summary
   - Checklist of features
   - Technical details

---

## 🐛 Troubleshooting

### Issue: 401 Unauthorized
**Solution:** Make sure JWT token is valid and included in Authorization header

### Issue: Empty results array
**Solution:** 
1. Check if the logged-in user is a patient
2. Verify patient has appointments in the database
3. Try `status=all` to see all appointments

### Issue: 500 Internal Server Error
**Solution:** 
1. Check Django server logs for error details
2. Verify database is accessible
3. Check if psychologist profile exists for appointments

### Issue: Profile image URL returns 404
**Solution:** 
1. Verify media files are configured correctly in settings
2. Check if psychologist has uploaded a profile image
3. Image URL will be `null` if no image exists (this is normal)

---

## ✨ Quick Start Command

**Run this one command to test everything:**

```bash
cd /home/ali/Desktop/projects/clink-backend && \
source venv/bin/activate && \
python test_patient_appointments.py
```

---

## 🎯 Recommended Testing Order

1. ✅ **First**: Run the Python test script (easiest)
2. ✅ **Second**: Try with cURL to verify raw responses
3. ✅ **Third**: Use Postman for interactive testing
4. ✅ **Fourth**: Integrate with your frontend

---

## 📞 Need Help?

If you encounter any issues:
1. Check the server logs for errors
2. Review the documentation files
3. Verify authentication token is valid
4. Check that you're logged in as a patient user

---

## 🚀 You're Ready!

The endpoint is **live and ready to use**. Start with the Python test script to see it in action!

```bash
python test_patient_appointments.py
```

**Happy Testing! 🎉**

