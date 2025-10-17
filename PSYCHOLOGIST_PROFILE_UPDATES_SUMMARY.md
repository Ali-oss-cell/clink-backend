# Psychologist Profile Updates - Summary

## 🎯 What We Accomplished

We have successfully enhanced the psychologist profile system to support the frontend's psychologist selection page requirements. All necessary backend infrastructure is now in place.

---

## 🆕 New Fields Added

### **User Model (`users/models.py`)**
Added the following field to support gender-based filtering:

```python
gender = models.CharField(
    max_length=20,
    choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('non_binary', 'Non-Binary'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ],
    blank=True,
    help_text="Gender identification"
)
```

### **PsychologistProfile Model (`services/models.py`)**
Added the following fields to support availability display:

```python
working_days = models.CharField(
    max_length=200,
    blank=True,
    help_text="Working days (comma-separated: Monday,Tuesday,Wednesday)"
)

start_time = models.TimeField(
    null=True,
    blank=True,
    help_text="Standard start time for work day"
)

end_time = models.TimeField(
    null=True,
    blank=True,
    help_text="Standard end time for work day"
)
```

### **New Model Properties**
Added the following computed properties to `PsychologistProfile`:

```python
@property
def working_days_list(self):
    """Return working days as a list"""
    if self.working_days:
        return [day.strip() for day in self.working_days.split(',')]
    return []

def get_next_available_slot(self, service_id=None):
    """
    Get the next available appointment slot for this psychologist
    
    Returns:
        datetime or None: Next available slot datetime
    """
    from appointments.models import TimeSlot
    from django.utils import timezone
    
    now = timezone.now()
    available_slots = TimeSlot.objects.filter(
        availability_slot__psychologist=self.user,
        is_available=True,
        start_time__gte=now
    ).order_by('start_time')
    
    if available_slots.exists():
        return available_slots.first().start_time
    return None
```

---

## 🔄 Updated Serializers

### **PsychologistListSerializer** (Used for `/api/services/psychologists/`)
Enhanced to include all fields needed for the selection page:

**New Fields Added:**
- `user_gender` - Gender for filtering
- `services_list` - Full service details
- `is_ahpra_current` - AHPRA verification status
- `experience_level` - Computed experience level
- `working_days_list` - Days as array
- `session_types_list` - Session types as array
- `patient_cost_after_rebate` - Out-of-pocket cost
- `working_days`, `start_time`, `end_time` - Working hours
- `next_available_slot` - Next available appointment

### **PsychologistPublicSerializer** (Used for public profile view)
Enhanced to include:
- All the same fields as PsychologistListSerializer
- `ahpra_registration_number` - For verification display
- Complete practice details
- All professional statistics

### **PsychologistProfileSerializer** (Main serializer)
Updated to include:
- `working_days`, `start_time`, `end_time`

### **PsychologistProfileUpdateSerializer** (For edits)
Updated to allow editing:
- `working_days`, `start_time`, `end_time`

---

## 📊 Complete Data Structure for Frontend

### **Endpoint:** `GET /api/services/psychologists/`

Returns an array of psychologist profiles with the following structure:

```typescript
interface PsychologistProfile {
  // Basic Information
  id: number;
  user_name: string;
  user_gender: 'male' | 'female' | 'non_binary' | 'prefer_not_to_say' | '';
  display_name: string;
  title: string;
  
  // Profile Image
  profile_image: string;
  profile_image_url: string;
  has_profile_image: boolean;
  
  // Professional Credentials
  ahpra_registration_number: string;
  is_ahpra_current: boolean;
  qualifications: string;
  years_experience: number;
  experience_level: 'Junior' | 'Mid-level' | 'Experienced' | 'Senior';
  
  // Pricing
  consultation_fee: string;
  medicare_rebate_amount: string;
  patient_cost_after_rebate: string;
  
  // Availability
  is_accepting_new_patients: boolean;
  telehealth_available: boolean;
  in_person_available: boolean;
  working_days: string;
  working_days_list: string[];
  start_time: string;
  end_time: string;
  session_types: string;
  session_types_list: string[];
  next_available_slot: string | null;
  
  // Profile & Bio
  bio: string;
  average_rating: string;
  total_reviews: number;
  
  // Relationships
  specializations_list: Array<{
    id: number;
    name: string;
    description: string;
    is_active: boolean;
  }>;
  services_list: Array<{
    id: number;
    name: string;
    description: string;
    standard_fee: string;
    medicare_rebate: string;
    out_of_pocket_cost: string;
    duration_minutes: number;
    is_active: boolean;
  }>;
  
  // Status
  is_active_practitioner: boolean;
}
```

---

## 🗄️ Database Migrations

### **Created Migrations:**
1. **`services/migrations/0004_psychologistprofile_end_time_and_more.py`**
   - Added `end_time` field
   - Added `start_time` field
   - Added `working_days` field

2. **`users/migrations/0004_user_gender_alter_user_address_line_1_and_more.py`**
   - Added `gender` field
   - Minor field alterations

3. **`appointments/migrations/0002_alter_appointment_appointment_date_and_more.py`**
   - Field alterations for consistency

### **Migration Status:** ✅ **APPLIED**

---

## ✅ What's Ready

### **Backend Features:**
✅ Gender field for filtering  
✅ Service relationships (ManyToMany)  
✅ Specialization relationships (ManyToMany)  
✅ Working days, start/end times  
✅ Next available slot calculation  
✅ Profile images with full URLs  
✅ Session types list  
✅ AHPRA verification  
✅ Medicare rebate calculations  
✅ Ratings and reviews  
✅ Experience level computation  

### **API Endpoints:**
✅ `GET /api/services/psychologists/` - List all psychologists  
✅ `GET /api/services/psychologists/{id}/` - Get single psychologist  
✅ `GET /api/services/psychologists/{id}/availability/` - Get availability  
✅ `GET /api/services/specializations/` - List specializations  
✅ `GET /api/services/services/` - List services  

### **Filtering Capabilities:**
✅ Filter by service ID  
✅ Filter by specialization ID  
✅ Filter by accepting new patients  
✅ Filter by telehealth availability  
✅ Filter by in-person availability  
✅ Client-side filter by gender  
✅ Client-side filter by session types  

---

## 📋 Frontend Integration Checklist

- [ ] Create psychologist API service with TypeScript interfaces
- [ ] Implement PsychologistSelectionPage component
- [ ] Add gender filter dropdown
- [ ] Add specialization filter dropdown
- [ ] Add session type filter
- [ ] Add telehealth/in-person toggle filters
- [ ] Display psychologist cards with profile images
- [ ] Show qualifications and experience level
- [ ] Display specializations as badges
- [ ] Show pricing with Medicare rebate
- [ ] Display "Next Available" slot
- [ ] Show ratings and reviews
- [ ] Implement psychologist selection and navigation to booking page

---

## 🧪 Testing Commands

### **Test the Endpoint:**
```bash
# Activate virtual environment
cd /home/ali/Desktop/projects/clink-backend
source venv/bin/activate

# Start the development server
python manage.py runserver

# In another terminal, test the endpoint
curl -X GET "http://localhost:8000/api/services/psychologists/" \
  -H "Accept: application/json" | jq
```

### **Create Test Data (if needed):**
```python
# Django shell
python manage.py shell

from django.contrib.auth import get_user_model
from services.models import PsychologistProfile, Specialization
from datetime import date, time

User = get_user_model()

# Update existing psychologist with new fields
psych = PsychologistProfile.objects.first()
psych.user.gender = 'female'
psych.user.save()

psych.working_days = 'Monday,Tuesday,Wednesday,Thursday,Friday'
psych.start_time = time(9, 0)
psych.end_time = time(17, 0)
psych.save()

print(f"Updated: {psych.display_name}")
print(f"Working days: {psych.working_days_list}")
print(f"Working hours: {psych.start_time} - {psych.end_time}")
```

---

## 📚 Documentation Files

1. **`PSYCHOLOGIST_SELECTION_ENDPOINT_DOCUMENTATION.md`**
   - Complete API documentation
   - Field reference
   - Frontend implementation examples
   - TypeScript interfaces
   - React component examples
   - cURL testing commands

2. **`PSYCHOLOGIST_PROFILE_UPDATES_SUMMARY.md`** (This file)
   - Summary of changes
   - New fields overview
   - Migration details
   - Integration checklist

---

## 🚀 Next Steps

### **Recommended Order:**
1. ✅ **Update existing psychologist profiles with new data** (working_days, start_time, end_time, gender)
2. Create time slots for psychologists (for next_available_slot to work)
3. Start frontend integration with the psychologist selection page
4. Implement filtering UI
5. Test end-to-end psychologist selection flow
6. Move to appointment booking page integration

### **Related TODOs:**
- Schedule Management Integration (for time slots and availability)
- Patient Management for Psychologists (for dashboard)
- Dashboard Enhancement (in progress)

---

## 💡 Notes

- The `next_available_slot` field requires time slots to be created in the `appointments` app
- Gender filter is implemented as client-side filtering (not server-side query parameter)
- All pricing calculations include Medicare rebate automatically
- Profile images have fallback handling for missing images
- AHPRA verification is automatically checked against expiry date
- Experience levels are automatically calculated from years_experience

---

## ✨ Summary

**Status:** ✅ **BACKEND READY FOR FRONTEND INTEGRATION**

All backend infrastructure is in place to support a comprehensive psychologist selection page. The frontend team can now:
1. Fetch psychologist data with all required fields
2. Implement filtering by gender, specialization, session type, and availability
3. Display rich psychologist profiles with images, credentials, and pricing
4. Show next available appointment slots
5. Enable psychologist selection for booking flow

The API is fully functional, documented, and tested.

