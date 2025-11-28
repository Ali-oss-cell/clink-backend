# 📋 Frontend Intake Form Implementation Guide

## 🎯 **Correct API Endpoint**

### **Endpoint URL:**
```
POST /api/users/intake-form/
```
**OR** (preferred, documented):
```
PUT /api/auth/intake-form/
```

### **Headers:**
```javascript
{
  "Authorization": "Bearer YOUR_JWT_TOKEN",
  "Content-Type": "application/json"
}
```

### **HTTP Method:**
- ✅ **POST** - Supported (creates/updates)
- ✅ **PUT** - Supported (updates, preferred)
- ✅ **GET** - Get existing form data

---

## 📝 **Complete Field Reference**

### **🔴 REQUIRED FIELDS** (Must be provided)

| Field Name | Type | Format | Example | Notes |
|------------|------|--------|---------|-------|
| `first_name` | string | Text | `"John"` | From user registration |
| `last_name` | string | Text | `"Smith"` | From user registration |
| `phone_number` | string | Australian format | `"+61412345678"` or `"0412345678"` | Must match: `+61XXXXXXXXX` or `0XXXXXXXXX` |
| `date_of_birth` | string | ISO Date | `"1990-05-15"` | Format: `YYYY-MM-DD` |
| `address_line_1` | string | Text | `"123 Main Street"` | Street address |
| `suburb` | string | Text | `"Melbourne"` | City/suburb name |
| `state` | string | Select | `"VIC"` | See state options below |
| `postcode` | string | 4 digits | `"3000"` | Australian postcode |

---

### **🟡 OPTIONAL FIELDS** (Can be empty/omitted)

#### **Personal Details**
| Field Name | Type | Format | Example | Notes |
|------------|------|--------|---------|-------|
| `preferred_name` | string | Text | `"Johnny"` | What patient prefers to be called |
| `gender_identity` | string | Text | `"Male"`, `"Female"`, `"Non-Binary"`, `"Other"` | Free text |
| `pronouns` | string | Text | `"He/Him"`, `"She/Her"`, `"They/Them"` | Free text |
| `home_phone` | string | Australian format | `"+61412345678"` | Optional home phone |
| `medicare_number` | string | 10 digits | `"1234567890"` | Medicare card number |

#### **Emergency Contact**
| Field Name | Type | Format | Example | Notes |
|------------|------|--------|---------|-------|
| `emergency_contact_name` | string | Text | `"Jane Smith"` | Full name |
| `emergency_contact_relationship` | string | Text | `"Spouse"`, `"Parent"`, `"Friend"` | Relationship to patient |
| `emergency_contact_phone` | string | Australian format | `"+61412345678"` | Contact phone number |

#### **Referral Information**
| Field Name | Type | Format | Example | Notes |
|------------|------|--------|---------|-------|
| `referral_source` | string | Text | `"GP Referral"`, `"Friend"`, `"Google"` | How they heard about clinic |
| `has_gp_referral` | boolean | true/false | `true` | Do they have GP referral? |
| `gp_name` | string | Text | `"Dr. Sarah Johnson"` | Required if `has_gp_referral` is `true` |
| `gp_practice_name` | string | Text | `"Melbourne Medical Centre"` | GP practice name |
| `gp_provider_number` | string | Text | `"1234567A"` | GP provider number |
| `gp_address` | string | Text | `"123 Medical St, Melbourne VIC 3000"` | GP practice address |

#### **Medical History**
| Field Name | Type | Format | Example | Notes |
|------------|------|--------|---------|-------|
| `previous_therapy` | boolean | true/false | `true` | Have they had therapy before? |
| `previous_therapy_details` | string | Text (long) | `"Saw psychologist for anxiety in 2020"` | Required if `previous_therapy` is `true` |
| `current_medications` | boolean | true/false | `true` | Taking medications? |
| `medication_list` | string | Text (long) | `"Prozac 20mg daily"` | Required if `current_medications` is `true` |
| `other_health_professionals` | boolean | true/false | `true` | Seeing other health professionals? |
| `other_health_details` | string | Text (long) | `"Seeing psychiatrist monthly"` | Required if `other_health_professionals` is `true` |
| `medical_conditions` | boolean | true/false | `true` | Has medical conditions? |
| `medical_conditions_details` | string | Text (long) | `"Type 2 Diabetes, managed"` | Required if `medical_conditions` is `true` |

#### **Presenting Concerns**
| Field Name | Type | Format | Example | Notes |
|------------|------|--------|---------|-------|
| `presenting_concerns` | string | Text (long) | `"Anxiety and stress from work"` | What brings them to therapy |
| `therapy_goals` | string | Text (long) | `"Learn coping strategies for anxiety"` | What they hope to achieve |

#### **Consent Fields** (Privacy Act 1988 Compliance)
| Field Name | Type | Format | Example | Notes |
|------------|------|--------|---------|-------|
| `consent_to_treatment` | boolean | true/false | `true` | **REQUIRED for treatment** |
| `consent_to_telehealth` | boolean | true/false | `true` | Required if using telehealth |
| `telehealth_emergency_protocol_acknowledged` | boolean | true/false | `true` | Required if `consent_to_telehealth` is `true` |
| `telehealth_tech_requirements_acknowledged` | boolean | true/false | `true` | Required if `consent_to_telehealth` is `true` |
| `telehealth_recording_consent` | boolean | true/false | `false` | Optional - consent to record sessions |
| `privacy_policy_accepted` | boolean | true/false | `true` | **REQUIRED** - Privacy Act compliance |
| `consent_to_data_sharing` | boolean | true/false | `true` | Required for third-party services (Twilio, Stripe) |
| `consent_to_marketing` | boolean | true/false | `false` | Optional - marketing emails |

#### **Communication Preferences**
| Field Name | Type | Format | Example | Notes |
|------------|------|--------|---------|-------|
| `email_notifications_enabled` | boolean | true/false | `true` | Default: `true` |
| `sms_notifications_enabled` | boolean | true/false | `false` | Default: `false` |
| `appointment_reminders_enabled` | boolean | true/false | `true` | Default: `true` |

#### **Privacy Preferences**
| Field Name | Type | Format | Example | Notes |
|------------|------|--------|---------|-------|
| `share_progress_with_emergency_contact` | boolean | true/false | `false` | Share progress updates with emergency contact |

#### **Parental Consent** (For minors under 18)
| Field Name | Type | Format | Example | Notes |
|------------|------|--------|---------|-------|
| `parental_consent` | boolean | true/false | `true` | Required if patient is under 18 |
| `parental_consent_name` | string | Text | `"Jane Smith"` | Parent/guardian name |
| `parental_consent_signature` | string | Text | `"Jane Smith"` | Signature (text or digital) |

#### **Completion Flag**
| Field Name | Type | Format | Example | Notes |
|------------|------|--------|---------|-------|
| `intake_completed` | boolean | true/false | `true` | Set to `true` when form is fully submitted |

---

## 📋 **Field Type Reference**

### **State Options** (Australian States/Territories)
```javascript
const STATES = [
  { value: "NSW", label: "New South Wales" },
  { value: "VIC", label: "Victoria" },
  { value: "QLD", label: "Queensland" },
  { value: "WA", label: "Western Australia" },
  { value: "SA", label: "South Australia" },
  { value: "TAS", label: "Tasmania" },
  { value: "ACT", label: "Australian Capital Territory" },
  { value: "NT", label: "Northern Territory" }
];
```

### **Phone Number Format**
- ✅ Valid: `"+61412345678"` (with country code)
- ✅ Valid: `"0412345678"` (without country code)
- ❌ Invalid: `"1234567890"` (missing +61 or 0)
- ❌ Invalid: `"041234567"` (too short)

### **Date Format**
- Format: `YYYY-MM-DD`
- Example: `"1990-05-15"` (May 15, 1990)

### **Boolean Fields**
- Use `true` or `false` (not `"true"` or `"false"` as strings)
- Don't send if field is optional and value is `false`

---

## 💻 **Frontend Implementation Example**

### **TypeScript Interface**
```typescript
interface IntakeFormData {
  // Required fields
  first_name: string;
  last_name: string;
  phone_number: string;
  date_of_birth: string; // YYYY-MM-DD
  address_line_1: string;
  suburb: string;
  state: "NSW" | "VIC" | "QLD" | "WA" | "SA" | "TAS" | "ACT" | "NT";
  postcode: string; // 4 digits
  
  // Optional personal details
  preferred_name?: string;
  gender_identity?: string;
  pronouns?: string;
  home_phone?: string;
  medicare_number?: string;
  
  // Emergency contact
  emergency_contact_name?: string;
  emergency_contact_relationship?: string;
  emergency_contact_phone?: string;
  
  // Referral
  referral_source?: string;
  has_gp_referral?: boolean;
  gp_name?: string;
  gp_practice_name?: string;
  gp_provider_number?: string;
  gp_address?: string;
  
  // Medical history
  previous_therapy?: boolean;
  previous_therapy_details?: string;
  current_medications?: boolean;
  medication_list?: string;
  other_health_professionals?: boolean;
  other_health_details?: string;
  medical_conditions?: boolean;
  medical_conditions_details?: string;
  
  // Presenting concerns
  presenting_concerns?: string;
  therapy_goals?: string;
  
  // Consent (REQUIRED for treatment)
  consent_to_treatment: boolean;
  consent_to_telehealth?: boolean;
  telehealth_emergency_protocol_acknowledged?: boolean;
  telehealth_tech_requirements_acknowledged?: boolean;
  telehealth_recording_consent?: boolean;
  privacy_policy_accepted: boolean;
  consent_to_data_sharing?: boolean;
  consent_to_marketing?: boolean;
  
  // Communication preferences
  email_notifications_enabled?: boolean;
  sms_notifications_enabled?: boolean;
  appointment_reminders_enabled?: boolean;
  
  // Privacy
  share_progress_with_emergency_contact?: boolean;
  
  // Parental consent (if under 18)
  parental_consent?: boolean;
  parental_consent_name?: string;
  parental_consent_signature?: string;
  
  // Completion
  intake_completed?: boolean;
}
```

### **API Service Function**
```typescript
// services/api/intake.ts
import { authAPI } from './auth'; // or usersAPI if using /api/users/

export const intakeService = {
  // Get existing form data (pre-filled from registration)
  getIntakeForm: async (): Promise<IntakeFormData> => {
    const response = await authAPI.get('/intake-form/');
    return response.data;
  },

  // Submit/Update intake form
  submitIntakeForm: async (data: IntakeFormData): Promise<{ message: string; intake_completed: boolean }> => {
    // Use POST or PUT - both work
    const response = await authAPI.post('/intake-form/', {
      ...data,
      intake_completed: true, // Mark as completed when submitting
    });
    return response.data;
  },

  // Save draft (partial update)
  saveDraft: async (data: Partial<IntakeFormData>): Promise<IntakeFormData> => {
    const response = await authAPI.put('/intake-form/', data);
    return response.data;
  },
};
```

### **Example Payload (Minimal Required)**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone_number": "+61412345678",
  "date_of_birth": "1990-05-15",
  "address_line_1": "123 Main Street",
  "suburb": "Melbourne",
  "state": "VIC",
  "postcode": "3000",
  "consent_to_treatment": true,
  "privacy_policy_accepted": true,
  "intake_completed": true
}
```

### **Example Payload (Complete)**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone_number": "+61412345678",
  "date_of_birth": "1990-05-15",
  "address_line_1": "123 Main Street",
  "suburb": "Melbourne",
  "state": "VIC",
  "postcode": "3000",
  "preferred_name": "Johnny",
  "gender_identity": "Male",
  "pronouns": "He/Him",
  "medicare_number": "1234567890",
  "emergency_contact_name": "Jane Smith",
  "emergency_contact_relationship": "Spouse",
  "emergency_contact_phone": "+61412345679",
  "referral_source": "GP Referral",
  "has_gp_referral": true,
  "gp_name": "Dr. Sarah Johnson",
  "gp_practice_name": "Melbourne Medical Centre",
  "gp_provider_number": "1234567A",
  "gp_address": "123 Medical St, Melbourne VIC 3000",
  "previous_therapy": true,
  "previous_therapy_details": "Saw psychologist for anxiety in 2020",
  "current_medications": true,
  "medication_list": "Prozac 20mg daily",
  "medical_conditions": false,
  "presenting_concerns": "Anxiety and stress from work",
  "therapy_goals": "Learn coping strategies for anxiety",
  "consent_to_treatment": true,
  "consent_to_telehealth": true,
  "telehealth_emergency_protocol_acknowledged": true,
  "telehealth_tech_requirements_acknowledged": true,
  "telehealth_recording_consent": false,
  "privacy_policy_accepted": true,
  "consent_to_data_sharing": true,
  "consent_to_marketing": false,
  "email_notifications_enabled": true,
  "sms_notifications_enabled": false,
  "appointment_reminders_enabled": true,
  "share_progress_with_emergency_contact": false,
  "intake_completed": true
}
```

---

## ✅ **Success Response**

```json
{
  "message": "Intake form submitted successfully",
  "intake_completed": true,
  "profile": {
    "id": 1,
    "preferred_name": "Johnny",
    "intake_completed": true,
    "created_at": "2025-11-28T10:00:00Z"
  }
}
```

---

## ❌ **Error Response**

### **400 Bad Request** (Validation Error)
```json
{
  "phone_number": ["Phone number must be in Australian format: +61XXXXXXXXX or 0XXXXXXXXX"],
  "state": ["This field is required"],
  "consent_to_treatment": ["This field is required"]
}
```

### **403 Forbidden** (Not a Patient)
```json
{
  "error": "Only patients can submit intake forms"
}
```

### **405 Method Not Allowed** (Wrong URL/Method)
- Check you're using: `POST /api/users/intake-form/` or `PUT /api/auth/intake-form/`
- Check headers include: `Authorization: Bearer TOKEN`

---

## 🔍 **Validation Rules**

### **Conditional Required Fields**

1. **If `has_gp_referral` is `true`:**
   - `gp_name` should be provided (recommended)

2. **If `previous_therapy` is `true`:**
   - `previous_therapy_details` should be provided (recommended)

3. **If `current_medications` is `true`:**
   - `medication_list` should be provided (recommended)

4. **If `other_health_professionals` is `true`:**
   - `other_health_details` should be provided (recommended)

5. **If `medical_conditions` is `true`:**
   - `medical_conditions_details` should be provided (recommended)

6. **If `consent_to_telehealth` is `true`:**
   - `telehealth_emergency_protocol_acknowledged` should be `true`
   - `telehealth_tech_requirements_acknowledged` should be `true`

7. **If patient is under 18:**
   - `parental_consent` should be `true`
   - `parental_consent_name` should be provided
   - `parental_consent_signature` should be provided

---

## 🎨 **UI/UX Recommendations**

### **Form Sections** (Multi-Step Form)
1. **Step 1: Personal Details** (Required fields)
2. **Step 2: Emergency Contact** (Optional)
3. **Step 3: Referral Information** (Optional)
4. **Step 4: Medical History** (Optional)
5. **Step 5: Presenting Concerns** (Optional)
6. **Step 6: Consent & Preferences** (Required: `consent_to_treatment`, `privacy_policy_accepted`)

### **Field Display Logic**
- Show `gp_name`, `gp_practice_name`, etc. only if `has_gp_referral` is `true`
- Show `previous_therapy_details` only if `previous_therapy` is `true`
- Show `medication_list` only if `current_medications` is `true`
- Show `other_health_details` only if `other_health_professionals` is `true`
- Show `medical_conditions_details` only if `medical_conditions` is `true`
- Show telehealth consent fields only if `consent_to_telehealth` is `true`
- Show parental consent fields only if patient age < 18

### **Pre-fill from Registration**
When user first opens form, these fields are pre-filled from registration:
- `first_name`
- `last_name`
- `email` (read-only)
- `phone_number`
- `date_of_birth`
- `address_line_1`
- `suburb`
- `state`
- `postcode`
- `medicare_number` (if provided during registration)

---

## 🚀 **Quick Start Checklist**

- [ ] Use endpoint: `POST /api/users/intake-form/` or `PUT /api/auth/intake-form/`
- [ ] Include `Authorization: Bearer TOKEN` header
- [ ] Send `Content-Type: application/json`
- [ ] Include all **required fields** (see table above)
- [ ] Validate phone number format (Australian format)
- [ ] Validate date format (`YYYY-MM-DD`)
- [ ] Validate state (must be one of: NSW, VIC, QLD, WA, SA, TAS, ACT, NT)
- [ ] Validate postcode (4 digits)
- [ ] Set `consent_to_treatment: true` (required)
- [ ] Set `privacy_policy_accepted: true` (required)
- [ ] Set `intake_completed: true` when fully submitted
- [ ] Handle conditional fields (show/hide based on boolean values)
- [ ] Display validation errors from API response
- [ ] Show success message on completion

---

## 📞 **Support**

If you encounter issues:
1. Check browser console for network errors
2. Verify JWT token is valid and not expired
3. Check API response for validation errors
4. Ensure all required fields are included
5. Verify phone number and date formats

**Backend Endpoints:**
- ✅ `POST /api/users/intake-form/` (works with routing fix)
- ✅ `PUT /api/auth/intake-form/` (documented, preferred)
- ✅ `GET /api/auth/intake-form/` (get existing data)

