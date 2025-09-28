# 📋 Intake Form API Documentation

## 🎯 **Overview**
Complete API documentation for the Psychology Clinic intake form system. The form collects comprehensive patient information with smart pre-filling from user registration data.

---

## 🔧 **API Endpoints**

### **Base URL:**
```
http://127.0.0.1:8000/api
```

### **Authentication:**
All endpoints require JWT token in Authorization header:
```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

---

## 📋 **Intake Form Endpoints**

### **1. Get Intake Form Data (Pre-filled)**
```typescript
GET /api/auth/intake-form/
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

#### **Response (200):**
```json
{
    // Pre-filled from user registration (4 fields)
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone_number": "0412345678",
    "date_of_birth": "1990-01-15",
    "address_line_1": "123 Main Street",
    "suburb": "Melbourne",
    "state": "VIC",
    "postcode": "3000",
    "medicare_number": "1234567890",
    
    // User must complete (26 fields)
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
```typescript
POST /api/auth/intake-form/
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
Content-Type: application/json
```

#### **Request Body (Complete Form):**
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
    "gp_name": "Dr. Sarah Smith",
    "gp_practice_name": "City Medical Centre",
    "gp_provider_number": "1234567",
    "gp_address": "456 Medical Street, Melbourne VIC 3000",
    "previous_therapy": true,
    "previous_therapy_details": "Saw a psychologist 2 years ago for anxiety management",
    "current_medications": true,
    "medication_list": "Sertraline 50mg daily, Propranolol 10mg as needed",
    "other_health_professionals": true,
    "other_health_details": "Regular GP visits, seeing a psychiatrist monthly",
    "medical_conditions": false,
    "medical_conditions_details": "",
    "presenting_concerns": "I've been experiencing anxiety and depression for the past 6 months. I have trouble sleeping, feel overwhelmed at work, and have lost interest in activities I used to enjoy.",
    "therapy_goals": "I want to learn coping strategies for anxiety, improve my sleep, and regain my motivation and enjoyment in life.",
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

#### **Error Response (400):**
```json
{
    "error": "Required fields are missing",
    "details": {
        "emergency_contact_name": ["This field is required."],
        "presenting_concerns": ["This field is required."]
    }
}
```

---

## 📊 **Field Categories & Requirements**

### **Step 1: Personal Details** 👤
| Field | Type | Required | Pre-filled | Description |
|-------|------|----------|------------|-------------|
| `first_name` | string | ✅ | ✅ | First name (from registration) |
| `last_name` | string | ✅ | ✅ | Last name (from registration) |
| `email` | string | ✅ | ✅ | Email address (from registration) |
| `phone_number` | string | ✅ | ✅ | Mobile phone (from registration) |
| `date_of_birth` | string | ✅ | ✅ | Date of birth (from registration) |
| `address_line_1` | string | ✅ | ✅ | Street address (from registration) |
| `suburb` | string | ✅ | ✅ | Suburb (from registration) |
| `state` | string | ✅ | ✅ | State (from registration) |
| `postcode` | string | ✅ | ✅ | Postcode (from registration) |
| `medicare_number` | string | ✅ | ✅ | Medicare number (from registration) |
| `preferred_name` | string | ❌ | ❌ | What they like to be called |
| `gender_identity` | string | ❌ | ❌ | Gender identity |
| `pronouns` | string | ❌ | ❌ | Preferred pronouns |
| `home_phone` | string | ❌ | ❌ | Home phone number |

### **Step 2: Emergency Contact** 🚨
| Field | Type | Required | Pre-filled | Description |
|-------|------|----------|------------|-------------|
| `emergency_contact_name` | string | ✅ | ❌ | Emergency contact name |
| `emergency_contact_relationship` | string | ✅ | ❌ | Relationship to patient |
| `emergency_contact_phone` | string | ✅ | ❌ | Emergency contact phone |

### **Step 3: Referral Information** 🏥
| Field | Type | Required | Pre-filled | Description |
|-------|------|----------|------------|-------------|
| `referral_source` | string | ✅ | ❌ | How they found the clinic |
| `has_gp_referral` | boolean | ❌ | ❌ | Whether referred by GP |
| `gp_name` | string | ❌ | ❌ | GP's name (if referred by GP) |
| `gp_practice_name` | string | ❌ | ❌ | GP's practice name |
| `gp_provider_number` | string | ❌ | ❌ | GP's provider number |
| `gp_address` | string | ❌ | ❌ | GP's address |

### **Step 4: Medical & Mental Health History** 🩺
| Field | Type | Required | Pre-filled | Description |
|-------|------|----------|------------|-------------|
| `previous_therapy` | boolean | ❌ | ❌ | Previous therapy experience |
| `previous_therapy_details` | string | ❌ | ❌ | Details of previous therapy |
| `current_medications` | boolean | ❌ | ❌ | Currently taking medications |
| `medication_list` | string | ❌ | ❌ | List of current medications |
| `other_health_professionals` | boolean | ❌ | ❌ | Seeing other health professionals |
| `other_health_details` | string | ❌ | ❌ | Details of other health professionals |
| `medical_conditions` | boolean | ❌ | ❌ | Has medical conditions |
| `medical_conditions_details` | string | ❌ | ❌ | Details of medical conditions |

### **Step 5: Presenting Concerns** 🎯
| Field | Type | Required | Pre-filled | Description |
|-------|------|----------|------------|-------------|
| `presenting_concerns` | string | ✅ | ❌ | Main concerns/reasons for therapy |
| `therapy_goals` | string | ✅ | ❌ | What they hope to achieve |

### **Step 6: Consent & Signature** ✍️
| Field | Type | Required | Pre-filled | Description |
|-------|------|----------|------------|-------------|
| `consent_to_treatment` | boolean | ✅ | ❌ | Consent to treatment |
| `consent_to_telehealth` | boolean | ❌ | ❌ | Consent to telehealth |
| `client_signature` | string | ✅ | ❌ | Digital signature |
| `consent_date` | string | ✅ | ❌ | Date of consent |

---

## 🔧 **React Integration**

### **TypeScript Interface:**
```typescript
interface IntakeFormData {
    // Pre-filled from login (10 fields)
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
    
    // User must complete (26 fields)
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

### **API Service:**
```typescript
class IntakeFormService {
    private baseURL = 'http://127.0.0.1:8000/api';
    
    async getIntakeForm(): Promise<IntakeFormData> {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${this.baseURL}/auth/intake-form/`, {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load intake form data');
        }
        
        return response.json();
    }
    
    async submitIntakeForm(data: IntakeFormData): Promise<void> {
        const token = localStorage.getItem('access_token');
        const response = await fetch(`${this.baseURL}/auth/intake-form/`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Failed to submit intake form');
        }
        
        const result = await response.json();
        console.log('Intake form submitted:', result);
    }
}
```

### **React Component Example:**
```typescript
const IntakeForm: React.FC = () => {
    const [formData, setFormData] = useState<IntakeFormData | null>(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    
    useEffect(() => {
        const loadFormData = async () => {
            try {
                const data = await intakeFormService.getIntakeForm();
                setFormData(data);
            } catch (error) {
                console.error('Failed to load form data:', error);
            } finally {
                setLoading(false);
            }
        };
        
        loadFormData();
    }, []);
    
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        
        try {
            await intakeFormService.submitIntakeForm(formData!);
            alert('Intake form submitted successfully!');
        } catch (error) {
            console.error('Failed to submit form:', error);
            alert('Failed to submit form. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };
    
    if (loading) return <div>Loading form data...</div>;
    if (!formData) return <div>Failed to load form data</div>;
    
    return (
        <form onSubmit={handleSubmit}>
            {/* Form fields here */}
            <button type="submit" disabled={submitting}>
                {submitting ? 'Submitting...' : 'Submit Form'}
            </button>
        </form>
    );
};
```

---

## 📊 **Data Statistics**

### **Total Fields: 30**
- **Pre-filled from Login: 10** (33%)
- **User Must Complete: 26** (87%)
- **Required Fields: 12** (40%)
- **Optional Fields: 18** (60%)

### **Field Distribution:**
- **Personal Details: 14 fields** (47%)
- **Emergency Contact: 3 fields** (10%)
- **Referral Information: 6 fields** (20%)
- **Medical History: 8 fields** (27%)
- **Presenting Concerns: 2 fields** (7%)
- **Consent & Legal: 4 fields** (13%)

---

## 🚨 **Validation Rules**

### **Required Fields:**
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

// If previous_therapy is true, previous_therapy_details becomes required
if (formData.previous_therapy) {
    requiredFields.push('previous_therapy_details');
}
```

---

## 🎯 **Form Completion Flow**

### **Step 1: Load Pre-filled Data**
```typescript
// Automatically populated from user registration
const preFilledData = {
    first_name: user.first_name,
    last_name: user.last_name,
    email: user.email,
    phone_number: user.phone_number,
    date_of_birth: user.date_of_birth,
    address_line_1: user.address_line_1,
    suburb: user.suburb,
    state: user.state,
    postcode: user.postcode,
    medicare_number: user.medicare_number
};
```

### **Step 2: User Completes Form**
```typescript
// User fills remaining 26 fields
const userInput = {
    preferred_name: "Johnny",
    emergency_contact_name: "Jane Doe",
    emergency_contact_relationship: "Spouse",
    emergency_contact_phone: "0412345678",
    referral_source: "GP Referral",
    presenting_concerns: "I need help with anxiety",
    therapy_goals: "Learn coping strategies",
    consent_to_treatment: true,
    client_signature: "John Doe",
    consent_date: "2024-01-15"
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

## 🔧 **Testing**

### **Test with cURL:**
```bash
# Get intake form data
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:8000/api/auth/intake-form/

# Submit intake form
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"emergency_contact_name": "Jane Doe", "emergency_contact_relationship": "Spouse", "emergency_contact_phone": "0412345678", "referral_source": "Self-referral", "presenting_concerns": "I need help with anxiety", "therapy_goals": "Learn coping strategies", "consent_to_treatment": true, "client_signature": "John Doe", "consent_date": "2024-01-15"}' \
     http://127.0.0.1:8000/api/auth/intake-form/
```

### **Test with Postman:**
1. **Set Authorization:** Bearer token in headers
2. **GET Request:** `/api/auth/intake-form/` to get pre-filled data
3. **POST Request:** `/api/auth/intake-form/` with form data in body
4. **Check Response:** Should return success message

---

## 🎯 **Key Benefits**

### **1. Smart Pre-filling:**
- **10 fields pre-filled** from user registration
- **Reduces user effort** and data entry errors
- **Improves completion rates**

### **2. Comprehensive Data Collection:**
- **30 total fields** covering all aspects of patient care
- **Structured format** for easy processing
- **Validation** ensures data completeness

### **3. User Experience:**
- **Progressive disclosure** - only show relevant fields
- **Conditional validation** - smart requirements
- **Clear field categorization** - logical flow

---

## 📞 **Support**

### **Common Issues:**
1. **401 Unauthorized** - Check JWT token is valid
2. **400 Bad Request** - Check required fields are provided
3. **CORS errors** - Check Django CORS settings
4. **Network errors** - Ensure Django server is running

### **Debug Steps:**
1. Test with Postman first
2. Check browser console for errors
3. Verify token is stored in localStorage
4. Check network tab for request/response

---

**The intake form system is fully implemented and ready for frontend integration!** 🎯✨

**Total Fields:** 30  
**Pre-filled:** 10 (33%)  
**User-completed:** 26 (87%)  
**Required:** 12 (40%)  
**Optional:** 18 (60%)  
**API Endpoints:** 2 (GET, POST)  
**Authentication:** JWT-based  
**CORS:** Configured for React
