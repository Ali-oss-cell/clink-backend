# 📋 Psychology Clinic Intake Form System Documentation

## 🎯 **Overview**
The Psychology Clinic backend supports a comprehensive digital intake form system that collects all necessary patient information for Australian healthcare compliance. The system intelligently pre-fills data from user registration and guides patients through a structured intake process.

---

## 🏗️ **System Architecture**

### **Data Flow:**
```
User Registration → Pre-fill Intake Form → Complete Missing Fields → Save to Database
```

### **Key Components:**
- **User Model** - Basic patient information (pre-filled)
- **PatientProfile Model** - Extended intake form data
- **IntakeFormSerializer** - Handles form submission and validation
- **IntakeFormView** - API endpoint for form management

---

## 📊 **Complete Field Mapping**

### **Step 1: Personal Details** 👤
| Frontend Field | Backend Field | Model | Required | Pre-filled |
|----------------|---------------|-------|----------|------------|
| `fullName` | `first_name` + `last_name` | User | ✅ | ✅ |
| `preferredName` | `preferred_name` | PatientProfile | ❌ | ❌ |
| `dateOfBirth` | `date_of_birth` | User | ✅ | ✅ |
| `genderIdentity` | `gender_identity` | PatientProfile | ❌ | ❌ |
| `pronouns` | `pronouns` | PatientProfile | ❌ | ❌ |
| `streetAddress` | `address_line_1` | User | ✅ | ❌ |
| `suburb` | `suburb` | User | ✅ | ❌ |
| `postcode` | `postcode` | User | ✅ | ❌ |
| `homePhone` | `home_phone` | PatientProfile | ❌ | ❌ |
| `mobilePhone` | `phone_number` | User | ✅ | ✅ |
| `emailAddress` | `email` | User | ✅ | ✅ |

### **Step 2: Emergency Contact** 🚨
| Frontend Field | Backend Field | Model | Required | Pre-filled |
|----------------|---------------|-------|----------|------------|
| `emergencyName` | `emergency_contact_name` | PatientProfile | ✅ | ❌ |
| `emergencyRelationship` | `emergency_contact_relationship` | PatientProfile | ✅ | ❌ |
| `emergencyPhone` | `emergency_contact_phone` | PatientProfile | ✅ | ❌ |

### **Step 3: Referral Information** 🏥
| Frontend Field | Backend Field | Model | Required | Pre-filled |
|----------------|---------------|-------|----------|------------|
| `referralSource` | `referral_source` | PatientProfile | ✅ | ❌ |
| `referredByGP` | `has_gp_referral` | PatientProfile | ❌ | ❌ |
| `gpName` | `gp_name` | PatientProfile | ❌ | ❌ |
| `gpPractice` | `gp_practice_name` | PatientProfile | ❌ | ❌ |
| `gpProviderNumber` | `gp_provider_number` | PatientProfile | ❌ | ❌ |
| `gpAddress` | `gp_address` | PatientProfile | ❌ | ❌ |

### **Step 4: Medical & Mental Health History** 🩺
| Frontend Field | Backend Field | Model | Required | Pre-filled |
|----------------|---------------|-------|----------|------------|
| `previousTherapy` | `previous_therapy` | PatientProfile | ❌ | ❌ |
| `previousTherapyDetails` | `previous_therapy_details` | PatientProfile | ❌ | ❌ |
| `currentMedications` | `current_medications` | PatientProfile | ❌ | ❌ |
| `medicationList` | `medication_list` | PatientProfile | ❌ | ❌ |
| `otherHealthProfessionals` | `other_health_professionals` | PatientProfile | ❌ | ❌ |
| `otherHealthDetails` | `other_health_details` | PatientProfile | ❌ | ❌ |
| `medicalConditions` | `medical_conditions` | PatientProfile | ❌ | ❌ |
| `medicalConditionsDetails` | `medical_conditions_details` | PatientProfile | ❌ | ❌ |

### **Step 5: Presenting Concerns** 🎯
| Frontend Field | Backend Field | Model | Required | Pre-filled |
|----------------|---------------|-------|----------|------------|
| `presentingConcerns` | `presenting_concerns` | PatientProfile | ✅ | ❌ |
| `therapyGoals` | `therapy_goals` | PatientProfile | ✅ | ❌ |

### **Step 6: Consent & Signature** ✍️
| Frontend Field | Backend Field | Model | Required | Pre-filled |
|----------------|---------------|-------|----------|------------|
| `consentToTreatment` | `consent_to_treatment` | PatientProfile | ✅ | ❌ |
| `clientSignature` | `client_signature` | PatientProfile | ✅ | ❌ |
| `consentDate` | `consent_date` | PatientProfile | ✅ | ❌ |

---

## 🔧 **Backend Implementation**

### **1. PatientProfile Model (`users/models.py`)**
```python
class PatientProfile(models.Model):
    """Extended patient profile matching Australian psychology clinic intake forms"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    
    # Personal Details
    preferred_name = models.CharField(max_length=100, blank=True)
    gender_identity = models.CharField(max_length=50, blank=True)
    pronouns = models.CharField(max_length=20, blank=True)
    home_phone = models.CharField(max_length=15, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    
    # Referral Information
    referral_source = models.CharField(max_length=200, blank=True)
    has_gp_referral = models.BooleanField(default=False)
    gp_name = models.CharField(max_length=255, blank=True)
    gp_practice_name = models.CharField(max_length=255, blank=True)
    gp_provider_number = models.CharField(max_length=20, blank=True)
    gp_address = models.TextField(blank=True)
    
    # Medical History
    previous_therapy = models.BooleanField(default=False)
    previous_therapy_details = models.TextField(blank=True)
    current_medications = models.BooleanField(default=False)
    medication_list = models.TextField(blank=True)
    other_health_professionals = models.BooleanField(default=False)
    other_health_details = models.TextField(blank=True)
    medical_conditions = models.BooleanField(default=False)
    medical_conditions_details = models.TextField(blank=True)
    
    # Presenting Concerns
    presenting_concerns = models.TextField(blank=True)
    therapy_goals = models.TextField(blank=True)
    
    # Consent & Legal
    consent_to_treatment = models.BooleanField(default=False)
    consent_to_telehealth = models.BooleanField(default=False)
    client_signature = models.CharField(max_length=255, blank=True)
    consent_date = models.DateField(null=True, blank=True)
    intake_completed = models.BooleanField(default=False)
```

### **2. IntakeFormSerializer (`users/serializers.py`)**
```python
class IntakeFormSerializer(serializers.ModelSerializer):
    """Complete intake form serializer for React frontend"""
    
    # User fields (pre-filled from login)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number')
    date_of_birth = serializers.DateField(source='user.date_of_birth')
    address_line_1 = serializers.CharField(source='user.address_line_1')
    suburb = serializers.CharField(source='user.suburb')
    state = serializers.CharField(source='user.state')
    postcode = serializers.CharField(source='user.postcode')
    medicare_number = serializers.CharField(source='user.medicare_number')
    
    class Meta:
        model = PatientProfile
        fields = [
            # User fields (pre-filled from login)
            'first_name', 'last_name', 'email', 'phone_number', 'date_of_birth',
            'address_line_1', 'suburb', 'state', 'postcode', 'medicare_number',
            
            # Patient profile fields (user must complete)
            'preferred_name', 'gender_identity', 'pronouns', 'home_phone',
            'emergency_contact_name', 'emergency_contact_relationship', 
            'emergency_contact_phone', 'referral_source', 'has_gp_referral',
            'gp_name', 'gp_practice_name', 'gp_provider_number', 'gp_address',
            'previous_therapy', 'previous_therapy_details', 'current_medications',
            'medication_list', 'other_health_professionals', 'other_health_details',
            'medical_conditions', 'medical_conditions_details', 'presenting_concerns', 
            'therapy_goals', 'consent_to_treatment', 'consent_to_telehealth',
            'client_signature', 'consent_date', 'intake_completed'
        ]
```

---

## 🌐 **API Endpoints**

### **1. Get Intake Form Data**
- **URL:** `GET /api/auth/intake-form/`
- **Authentication:** Required (JWT token)
- **Response:** Complete intake form data with pre-filled user information

#### **Success Response (200):**
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "0412345678",
    "date_of_birth": "1990-01-01",
    "address_line_1": "123 Main St",
    "suburb": "Melbourne",
    "state": "VIC",
    "postcode": "3000",
    "medicare_number": "1234567890",
    "preferred_name": "",
    "gender_identity": "",
    "pronouns": "",
    "home_phone": "",
    "emergency_contact_name": "",
    "emergency_contact_relationship": "",
    "emergency_contact_phone": "",
    "referral_source": "",
    "has_gp_referral": false,
    "gp_name": "",
    "gp_practice_name": "",
    "gp_provider_number": "",
    "gp_address": "",
    "previous_therapy": false,
    "previous_therapy_details": "",
    "current_medications": false,
    "medication_list": "",
    "other_health_professionals": false,
    "other_health_details": "",
    "medical_conditions": false,
    "medical_conditions_details": "",
    "presenting_concerns": "",
    "therapy_goals": "",
    "consent_to_treatment": false,
    "consent_to_telehealth": false,
    "client_signature": "",
    "consent_date": null,
    "intake_completed": false
}
```

### **2. Submit Intake Form**
- **URL:** `POST /api/auth/intake-form/`
- **Authentication:** Required (JWT token)
- **Content-Type:** `application/json`

#### **Request Body:**
```json
{
    "preferred_name": "Johnny",
    "gender_identity": "Male",
    "pronouns": "he/him",
    "home_phone": "0398765432",
    "emergency_contact_name": "Jane Doe",
    "emergency_contact_relationship": "Spouse",
    "emergency_contact_phone": "0412345678",
    "referral_source": "GP Referral",
    "has_gp_referral": true,
    "gp_name": "Dr. Smith",
    "gp_practice_name": "City Medical Centre",
    "gp_provider_number": "1234567",
    "gp_address": "456 Medical St, Melbourne VIC 3000",
    "previous_therapy": true,
    "previous_therapy_details": "Saw a psychologist 2 years ago",
    "current_medications": true,
    "medication_list": "Antidepressant - Sertraline 50mg daily",
    "other_health_professionals": true,
    "other_health_details": "Regular GP visits",
    "medical_conditions": false,
    "medical_conditions_details": "",
    "presenting_concerns": "Anxiety and depression",
    "therapy_goals": "Learn coping strategies for anxiety",
    "consent_to_treatment": true,
    "consent_to_telehealth": true,
    "client_signature": "John Doe",
    "consent_date": "2024-01-15"
}
```

#### **Success Response (200):**
```json
{
    "message": "Intake form submitted successfully",
    "intake_completed": true,
    "profile": {
        "id": 1,
        "preferred_name": "Johnny",
        "intake_completed": true,
        "created_at": "2024-01-15T10:30:00Z"
    }
}
```

---

## 🎯 **Frontend Integration**

### **1. Get Pre-filled Data:**
```typescript
const getIntakeFormData = async (): Promise<IntakeFormData> => {
    const response = await fetch('http://127.0.0.1:8000/api/auth/intake-form/', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to load intake form data');
    }
    
    return response.json();
};
```

### **2. Submit Intake Form:**
```typescript
const submitIntakeForm = async (formData: IntakeFormData): Promise<void> => {
    const response = await fetch('http://127.0.0.1:8000/api/auth/intake-form/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to submit intake form');
    }
    
    const result = await response.json();
    console.log('Intake form submitted:', result);
};
```

### **3. TypeScript Interface:**
```typescript
interface IntakeFormData {
    // Pre-filled from login (read-only)
    first_name: string;
    last_name: string;
    email: string;
    phone_number: string;
    date_of_birth: string;
    address_line_1: string;
    suburb: string;
    state: string;
    postcode: string;
    medicare_number: string;
    
    // User must complete
    preferred_name?: string;
    gender_identity?: string;
    pronouns?: string;
    home_phone?: string;
    emergency_contact_name: string;
    emergency_contact_relationship: string;
    emergency_contact_phone: string;
    referral_source: string;
    has_gp_referral: boolean;
    gp_name?: string;
    gp_practice_name?: string;
    gp_provider_number?: string;
    gp_address?: string;
    previous_therapy: boolean;
    previous_therapy_details?: string;
    current_medications: boolean;
    medication_list?: string;
    other_health_professionals: boolean;
    other_health_details?: string;
    medical_conditions: boolean;
    medical_conditions_details?: string;
    presenting_concerns: string;
    therapy_goals: string;
    consent_to_treatment: boolean;
    consent_to_telehealth: boolean;
    client_signature: string;
    consent_date: string;
}
```

---

## 📊 **Data Statistics**

### **Total Fields: 30**
- **Pre-filled from Login: 4** (13%)
- **User Must Complete: 26** (87%)

### **Required Fields: 12** (40%)
- Personal: `address_line_1`, `suburb`, `state`, `postcode`
- Emergency: `emergency_contact_name`, `emergency_contact_relationship`, `emergency_contact_phone`
- Referral: `referral_source`
- Concerns: `presenting_concerns`, `therapy_goals`
- Consent: `consent_to_treatment`, `client_signature`, `consent_date`

### **Optional Fields: 18** (60%)
- All medical history fields
- GP referral details
- Personal preferences

---

## 🔄 **Form Completion Flow**

### **Step 1: Pre-fill from Login**
```typescript
// Automatically populated from user registration
const preFilledData = {
    first_name: user.first_name,
    last_name: user.last_name,
    email: user.email,
    phone_number: user.phone_number,
    date_of_birth: user.date_of_birth
};
```

### **Step 2: User Completes Form**
```typescript
// User fills remaining 26 fields
const userInput = {
    preferred_name: "Johnny",
    emergency_contact_name: "Jane Doe",
    // ... other fields
};
```

### **Step 3: Submit and Save**
```typescript
// Combine pre-filled and user input
const completeForm = { ...preFilledData, ...userInput };
await submitIntakeForm(completeForm);
```

---

## 🚨 **Validation Rules**

### **Required Field Validation:**
```typescript
const requiredFields = [
    'emergency_contact_name',
    'emergency_contact_relationship',
    'emergency_contact_phone',
    'referral_source',
    'presenting_concerns',
    'therapy_goals',
    'consent_to_treatment',
    'client_signature',
    'consent_date'
];
```

### **Conditional Validation:**
```typescript
// If has_gp_referral is true, GP fields become required
if (formData.has_gp_referral) {
    requiredFields.push('gp_name', 'gp_practice_name');
}

// If current_medications is true, medication_list becomes required
if (formData.current_medications) {
    requiredFields.push('medication_list');
}
```

---

## 🎯 **Benefits of This System**

### **1. User Experience:**
- **Pre-filled data** saves time and reduces errors
- **Progressive disclosure** - only show relevant fields
- **Smart validation** - conditional requirements

### **2. Data Quality:**
- **Comprehensive collection** - all necessary information
- **Structured format** - easy to process and analyze
- **Validation** - ensures data completeness

### **3. Compliance:**
- **Australian healthcare standards** - Medicare, AHPRA
- **Legal requirements** - consent and signatures
- **Privacy protection** - secure data handling

---

## 🛠️ **Development Setup**

### **1. Create Migration:**
```bash
python manage.py makemigrations users
python manage.py migrate
```

### **2. Test API Endpoints:**
```bash
# Get intake form data
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:8000/api/auth/intake-form/

# Submit intake form
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"preferred_name": "Johnny", ...}' \
     http://127.0.0.1:8000/api/auth/intake-form/
```

### **3. Frontend Integration:**
```typescript
// Load form data on component mount
useEffect(() => {
    const loadFormData = async () => {
        try {
            const data = await getIntakeFormData();
            setFormData(data);
        } catch (error) {
            console.error('Failed to load form data:', error);
        }
    };
    
    loadFormData();
}, []);
```

---

## 📞 **Support**

If you encounter issues:
1. Check Django server logs
2. Verify JWT token is valid
3. Ensure all required fields are provided
4. Check database for PatientProfile creation
5. Test with Postman first

**The intake form system is fully implemented and ready for frontend integration!** 🎯✨
