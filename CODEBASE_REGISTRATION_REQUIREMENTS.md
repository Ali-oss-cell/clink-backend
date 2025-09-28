# 📋 Patient Registration - Based on Current Codebase

## 🎯 **Exact Information Requirements from Django Models & Serializers**

Based on our current Django codebase, here's exactly what information we need to collect during patient registration:

---

## 📝 **Step 1: Basic Registration (PatientRegistrationSerializer)**

### **🔐 Required Fields for Account Creation:**
```python
# From PatientRegistrationSerializer fields:
'email'                    # ✅ Required - Unique identifier
'password'                 # ✅ Required - Min 8 characters  
'password_confirm'        # ✅ Required - Must match password
'first_name'              # ✅ Required - User identity
'last_name'               # ✅ Required - User identity
'phone_number'            # ✅ Required - Australian format validation
'date_of_birth'           # ✅ Required - Age verification
'address_line_1'          # ✅ Required - Street address
'suburb'                  # ✅ Required - Suburb name
'state'                   # ✅ Required - Australian state
'postcode'                # ✅ Required - 4-digit postcode
'medicare_number'         # ✅ Required - Healthcare rebates
```

### **📱 Phone Number Validation:**
```python
# From User model phone_regex:
regex=r'^\+?61[0-9]{9}$|^0[0-9]{9}$'
# Accepts: +61XXXXXXXXX or 0XXXXXXXXX
```

### **🏛️ Australian States:**
```python
# From User model state choices:
('NSW', 'New South Wales')
('VIC', 'Victoria') 
('QLD', 'Queensland')
('WA', 'Western Australia')
('SA', 'South Australia')
('TAS', 'Tasmania')
('ACT', 'Australian Capital Territory')
('NT', 'Northern Territory')
```

---

## 📋 **Step 2: Extended Patient Profile (IntakeFormSerializer)**

### **👤 Personal Details:**
```python
'preferred_name'           # Optional - If different from first name
'gender_identity'          # Optional - Gender identity
'pronouns'                 # Optional - Preferred pronouns
```

### **🚨 Emergency Contact:**
```python
'emergency_contact_name'           # Optional - Emergency contact name
'emergency_contact_relationship'   # Optional - Relationship to patient
'emergency_contact_phone'          # Optional - Emergency contact phone
```

### **👨‍⚕️ Referral Information:**
```python
'referral_source'         # Optional - How they found us
'has_gp_referral'         # Optional - Boolean for GP referral
'gp_name'                 # Optional - GP name
'gp_practice_name'        # Optional - GP practice name
```

### **🏥 Medical History:**
```python
'previous_therapy'         # Optional - Boolean for previous therapy
'previous_therapy_details' # Optional - Details about previous therapy
'current_medications'      # Optional - Current medications list
'medical_conditions'       # Optional - Medical conditions
```

### **🎯 Therapy Information:**
```python
'presenting_concerns'      # Optional - What brings them to therapy
'therapy_goals'           # Optional - What they want to achieve
```

### **✅ Consent Fields:**
```python
'consent_to_treatment'    # Optional - Boolean for treatment consent
'consent_to_telehealth'   # Optional - Boolean for telehealth consent
'intake_completed'        # Optional - Boolean for intake completion
```

---

## 🔄 **Registration Flow Based on Codebase**

### **Option 1: Quick Registration (PatientRegistrationSerializer)**
```python
# API Endpoint: POST /api/auth/register/patient/
# Required fields only:
{
    "email": "john.smith@email.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123", 
    "first_name": "John",
    "last_name": "Smith",
    "phone_number": "+61412345678",
    "date_of_birth": "1990-01-15",
    "address_line_1": "123 Collins Street",
    "suburb": "Melbourne",
    "state": "VIC",
    "postcode": "3000",
    "medicare_number": "1234567890"
}
```

**Response:**
```python
{
    "message": "Patient registered successfully",
    "user": {
        "id": 1,
        "email": "john.smith@email.com",
        "first_name": "John",
        "last_name": "Smith",
        "role": "patient",
        "is_verified": false,
        "created_at": "2025-01-15T10:30:00Z"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### **Option 2: Complete Intake Form (IntakeFormSerializer)**
```python
# API Endpoint: PUT /api/auth/intake-form/
# Complete patient profile:
{
    # User fields (from PatientRegistrationSerializer)
    "first_name": "John",
    "last_name": "Smith", 
    "phone_number": "+61412345678",
    "date_of_birth": "1990-01-15",
    "address_line_1": "123 Collins Street",
    "suburb": "Melbourne",
    "state": "VIC", 
    "postcode": "3000",
    "medicare_number": "1234567890",
    
    # Patient profile fields
    "preferred_name": "Johnny",
    "gender_identity": "Male",
    "pronouns": "He/Him",
    "emergency_contact_name": "Jane Smith",
    "emergency_contact_relationship": "Mother",
    "emergency_contact_phone": "+61412345679",
    "referral_source": "GP",
    "has_gp_referral": true,
    "gp_name": "Dr. Sarah Wilson",
    "gp_practice_name": "Collins Street Medical Centre",
    "previous_therapy": true,
    "previous_therapy_details": "Saw psychologist for 6 months in 2020",
    "current_medications": "Sertraline 50mg daily",
    "medical_conditions": "Anxiety disorder, diagnosed 2020",
    "presenting_concerns": "Experiencing anxiety about work and social situations",
    "therapy_goals": "Reduce anxiety, improve sleep, build confidence",
    "consent_to_treatment": true,
    "consent_to_telehealth": true,
    "intake_completed": true
}
```

---

## 🎯 **API Endpoints Available**

### **🔐 Authentication Endpoints:**
```python
POST /api/auth/register/patient/     # Patient registration
POST /api/auth/login/                # JWT login
POST /api/auth/refresh/              # Token refresh
POST /api/auth/verify/               # Token verification
```

### **👤 Profile Management:**
```python
GET /api/auth/profile/              # Get user profile
PUT /api/auth/profile/              # Update user profile
POST /api/auth/change-password/     # Change password
```

### **📋 Intake Form:**
```python
GET /api/auth/intake-form/          # Get intake form data
PUT /api/auth/intake-form/          # Update intake form data
```

### **📊 Dashboards:**
```python
GET /api/auth/dashboard/patient/    # Patient dashboard
GET /api/auth/dashboard/psychologist/ # Psychologist dashboard
```

---

## 🔒 **Security & Validation Features**

### **✅ Built-in Validations:**
```python
# Email uniqueness validation
email = models.EmailField(unique=True)

# Australian phone number validation  
phone_regex = RegexValidator(
    regex=r'^\+?61[0-9]{9}$|^0[0-9]{9}$',
    message="Phone number must be in Australian format"
)

# Password confirmation
def validate(self, attrs):
    if attrs['password'] != attrs['password_confirm']:
        raise serializers.ValidationError("Passwords don't match")
    return attrs
```

### **🔐 Role-Based Access:**
```python
# User roles defined in User model:
class UserRole(models.TextChoices):
    PATIENT = 'patient', 'Patient'
    PSYCHOLOGIST = 'psychologist', 'Psychologist' 
    PRACTICE_MANAGER = 'practice_manager', 'Practice Manager'
    ADMIN = 'admin', 'Admin'
```

### **🛡️ Permission Classes:**
```python
# Authentication required for most endpoints
permission_classes = [IsAuthenticated]

# Public registration endpoint
permission_classes = [AllowAny]  # PatientRegistrationView

# Role-based filtering in views
def get_queryset(self):
    if user.is_psychologist():
        return User.objects.filter(role=User.UserRole.PATIENT)
```

---

## 📱 **Frontend Integration Requirements**

### **React Form Fields Needed:**
```typescript
// Basic Registration Form
interface PatientRegistration {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  date_of_birth: string;
  address_line_1: string;
  suburb: string;
  state: 'NSW' | 'VIC' | 'QLD' | 'WA' | 'SA' | 'TAS' | 'ACT' | 'NT';
  postcode: string;
  medicare_number: string;
}

// Complete Intake Form
interface IntakeForm extends PatientRegistration {
  preferred_name?: string;
  gender_identity?: string;
  pronouns?: string;
  emergency_contact_name?: string;
  emergency_contact_relationship?: string;
  emergency_contact_phone?: string;
  referral_source?: string;
  has_gp_referral?: boolean;
  gp_name?: string;
  gp_practice_name?: string;
  previous_therapy?: boolean;
  previous_therapy_details?: string;
  current_medications?: string;
  medical_conditions?: string;
  presenting_concerns?: string;
  therapy_goals?: string;
  consent_to_treatment?: boolean;
  consent_to_telehealth?: boolean;
  intake_completed?: boolean;
}
```

---

## 🎯 **Summary: What We Need to Collect**

### **✅ Minimum Required (Quick Registration):**
1. **Email & Password** - Account access
2. **Name & DOB** - Identity verification
3. **Phone & Address** - Contact and location  
4. **Medicare Number** - Healthcare rebates
5. **Password Confirmation** - Security

### **📋 Extended Information (Complete Registration):**
1. **Emergency Contact** - Safety requirement
2. **GP Information** - Healthcare coordination
3. **Medical History** - Treatment planning
4. **Presenting Concerns** - Therapy focus
5. **Consent Agreements** - Legal compliance

### **🔄 Registration Options:**
- **Quick Registration** → Complete intake form later
- **Complete Registration** → Ready to book immediately
- **Progressive Registration** → Multi-step form

**Our codebase is perfectly set up to handle all Australian psychology clinic registration requirements with proper validation, security, and role-based access!** 🎯✨
