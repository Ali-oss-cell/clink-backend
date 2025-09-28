# 🌐 Psychology Clinic Website - Complete User Journey Flow

## 🏠 **Landing Page (First Visit)**
```
URL: https://yourpsychologyclinic.com.au
```

### **What Users See:**
- **Hero Section**: "Professional Psychology Services in Australia"
- **Services Overview**: Individual Therapy, Couples Therapy, etc.
- **Meet Our Psychologists**: AHPRA registered professionals
- **Online Booking**: "Book Your First Appointment"
- **Telehealth Available**: Video consultations
- **Medicare Rebates**: Bulk billing information

### **Call-to-Action Buttons:**
- 🔵 **"Book Appointment"** → Registration Flow
- 🔵 **"Patient Login"** → Existing patients
- 🔵 **"Psychologist Login"** → Staff access
- 📞 **"Call Us"** → Phone booking

---

## 👤 **NEW PATIENT JOURNEY**

### **Step 1: Registration Page**
```
URL: /register
React Component: <PatientRegistration />
API: POST /api/auth/register/patient/
```

**Form Fields:**
```javascript
{
  "email": "john.smith@email.com",
  "password": "securepass123",
  "password_confirm": "securepass123", 
  "first_name": "John",
  "last_name": "Smith",
  "phone_number": "+61412345678",
  "date_of_birth": "1990-05-15"
}
```

**Success Response:**
- JWT tokens stored
- Automatic login
- Redirect to → **Intake Form**

### **Step 2: Digital Intake Form**
```
URL: /patient/intake-form
React Component: <IntakeForm />
API: PUT /api/auth/intake-form/
```

**Multi-Step Form:**

#### **Page 1: Personal Details**
- Full Name, Preferred Name
- Date of Birth, Gender Identity, Pronouns
- Address (Australian format)
- Contact Details

#### **Page 2: Emergency Contact**
- Contact Name, Relationship
- Phone Number

#### **Page 3: Referral Information**
- How did you hear about us?
- GP Referral (Yes/No)
- GP Details & Provider Number
- Mental Health Care Plan

#### **Page 4: Medical History**
- Previous Therapy (Yes/No + Details)
- Current Medications
- Medical Conditions
- Other Health Professionals

#### **Page 5: Presenting Concerns**
- What brings you to therapy?
- Your therapy goals
- Preferred appointment times

#### **Page 6: Consent & Agreement**
- Consent to Treatment ✅
- Consent to Telehealth ✅
- Privacy Policy Agreement ✅
- Service Agreement Terms ✅

**Completion:** Redirect to → **Patient Dashboard**

### **Step 3: Patient Dashboard**
```
URL: /patient/dashboard
React Component: <PatientDashboard />
API: GET /api/auth/dashboard/patient/
```

**Dashboard Sections:**

#### **🎯 Quick Actions**
- 📅 **Book Appointment**
- 💳 **Pay Invoice** 
- 🎥 **Join Video Session**
- 📋 **Update Profile**

#### **📊 My Overview**
- ✅ Intake Form: Completed
- 📈 Total Sessions: 0
- 📅 Next Appointment: Not scheduled
- 💰 Outstanding Balance: $0

#### **🔄 Recent Activity**
- "Welcome! Please book your first appointment"
- "Intake form completed successfully"

---

## 📅 **APPOINTMENT BOOKING FLOW**

### **Step 4: Book Appointment**
```
URL: /patient/book-appointment
React Component: <AppointmentBooking />
API: GET /api/services/psychologists/
```

#### **Page 1: Choose Service**
- Individual Therapy (50min) - $180
- Couples Therapy (60min) - $220
- Assessment (90min) - $280
- Medicare Rebate: $87.45

#### **Page 2: Choose Psychologist**
```javascript
// Display available psychologists
{
  "psychologists": [
    {
      "id": 1,
      "name": "Dr. Sarah Johnson",
      "title": "Clinical Psychologist",
      "specializations": ["Anxiety", "Depression"],
      "ahpra_number": "PSY0001234567",
      "bio": "Specializes in CBT and mindfulness...",
      "is_accepting_patients": true
    }
  ]
}
```

#### **Page 3: Choose Date & Time**
- Calendar widget
- Available time slots
- Telehealth or In-Person option

#### **Page 4: Confirm Booking**
- Appointment summary
- Payment required: $92.55 (after Medicare)
- Confirmation → **Payment Page**

---

## 💳 **PAYMENT FLOW**

### **Step 5: Payment Processing**
```
URL: /patient/payment
React Component: <PaymentForm />
API: POST /api/billing/create-payment-intent/
```

**Stripe Integration:**
- Card details form
- Australian payment processing
- GST calculation (10%)
- Medicare rebate applied

**Success:** Redirect to → **Appointment Confirmed**

---

## 📧 **CONFIRMATION & NOTIFICATIONS**

### **Step 6: Appointment Confirmed**
```
URL: /patient/appointment-confirmed
```

**Confirmation Page:**
- ✅ Appointment booked successfully
- 📧 Email confirmation sent
- 📱 WhatsApp reminder scheduled
- 🎥 Video session link (if telehealth)

**Automatic Actions:**
- WhatsApp message: "Appointment confirmed for [date/time]"
- Email with calendar invite
- Reminder scheduled 24 hours before

---

## 🎥 **SESSION DAY FLOW**

### **Step 7: Pre-Session**
**24 Hours Before:**
- 📱 WhatsApp reminder: "Your appointment is tomorrow at 2:00 PM"
- 📧 Email with session preparation tips

**1 Hour Before:**
- 📱 WhatsApp: "Your session starts in 1 hour. Click here for video link"

### **Step 8: Video Session**
```
URL: /patient/video-session/[appointment_id]
React Component: <TwilioVideoCall />
API: POST /api/appointments/[id]/video-room/
```

**Twilio Video Integration:**
- Secure video room created
- Screen sharing available
- Session recording (with consent)
- Chat functionality

---

## 🔄 **RETURNING PATIENT JOURNEY**

### **Login Flow**
```
URL: /login
React Component: <Login />
API: POST /api/auth/login/
```

**Role-Based Redirect:**
```javascript
const user = response.data.user;
switch(user.role) {
  case 'patient':
    navigate('/patient/dashboard');
    break;
  case 'psychologist':
    navigate('/psychologist/dashboard');
    break;
  case 'practice_manager':
    navigate('/manager/dashboard');
    break;
}
```

---

## 🧠 **PSYCHOLOGIST JOURNEY**

### **Psychologist Dashboard**
```
URL: /psychologist/dashboard
React Component: <PsychologistDashboard />
```

**Dashboard Sections:**

#### **📅 Today's Schedule**
- Upcoming appointments
- Patient names and times
- Session type (in-person/telehealth)

#### **📝 Quick Actions**
- Create Progress Note
- View Patient Files
- Update Availability
- Start Video Session

#### **📊 My Statistics**
- Today's Appointments: 6
- Total Patients: 42
- Pending Notes: 2
- This Week's Revenue: $1,800

### **Progress Notes (SOAP)**
```
URL: /psychologist/progress-notes/create
React Component: <SOAPNoteForm />
API: POST /api/auth/progress-notes/
```

**SOAP Note Form:**
- **S**ubjective: Patient's reported experience
- **O**bjective: Observable behaviors
- **A**ssessment: Clinical impression
- **P**lan: Next steps and interventions

---

## 📋 **PRACTICE MANAGER JOURNEY**

### **Manager Dashboard**
```
URL: /manager/dashboard
React Component: <ManagerDashboard />
```

**Management Sections:**
- 👥 **User Management**: All patients and psychologists
- 📅 **Appointment Overview**: All bookings
- 💰 **Financial Dashboard**: Revenue, Medicare claims
- 📊 **Reports**: Session statistics, patient progress

---

## 🔄 **COMPLETE CYCLE SUMMARY**

### **Patient Lifecycle:**
1. **Discovery** → Landing page visit
2. **Registration** → Account creation
3. **Intake** → Digital form completion
4. **Booking** → First appointment scheduled
5. **Payment** → Session fee processed
6. **Session** → Video/in-person therapy
7. **Follow-up** → Progress tracking
8. **Ongoing** → Regular appointments

### **Psychologist Workflow:**
1. **Login** → Role-based dashboard
2. **Schedule Review** → Today's appointments
3. **Session Delivery** → Video/in-person
4. **Documentation** → SOAP notes
5. **Patient Management** → Progress tracking

### **System Integration:**
- 🔐 **JWT Authentication** throughout
- 📱 **WhatsApp Notifications** at key points
- 💳 **Stripe Payments** with Australian compliance
- 🎥 **Twilio Video** for telehealth
- 🇦🇺 **Medicare Integration** for rebates

---

## 🎯 **Key Pages Your React App Needs:**

### **Public Pages:**
- `/` - Landing page
- `/services` - Services overview
- `/psychologists` - Team profiles
- `/about` - Clinic information
- `/contact` - Contact details

### **Authentication:**
- `/login` - User login
- `/register` - Patient registration
- `/forgot-password` - Password reset

### **Patient Portal:**
- `/patient/dashboard` - Main dashboard
- `/patient/intake-form` - Digital intake
- `/patient/book-appointment` - Appointment booking
- `/patient/appointments` - Appointment history
- `/patient/invoices` - Billing history
- `/patient/profile` - Profile management
- `/patient/video-session/[id]` - Video calls

### **Psychologist Portal:**
- `/psychologist/dashboard` - Main dashboard
- `/psychologist/schedule` - Daily schedule
- `/psychologist/patients` - Patient list
- `/psychologist/progress-notes` - SOAP notes
- `/psychologist/video-session/[id]` - Video calls

### **Manager Portal:**
- `/manager/dashboard` - Overview dashboard
- `/manager/users` - User management
- `/manager/appointments` - All appointments
- `/manager/billing` - Financial overview
- `/manager/reports` - Analytics

**Your backend APIs are ready to support this entire journey!** 🚀
