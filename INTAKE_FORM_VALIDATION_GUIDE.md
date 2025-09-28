# 📋 Intake Form Validation Guide

## 🎯 **Overview**
Complete validation rules for the Psychology Clinic intake form system. This guide covers all field requirements, data types, and validation logic.

---

## ✅ **VALID Fields (Required for Submission)**

### **1. Emergency Contact (3 Required Fields)**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `emergency_contact_name` | string | ✅ **YES** | Max 255 characters, cannot be empty |
| `emergency_contact_relationship` | string | ✅ **YES** | Max 100 characters, cannot be empty |
| `emergency_contact_phone` | string | ✅ **YES** | Max 15 characters, cannot be empty |

### **2. Referral Information (1 Required Field)**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `referral_source` | string | ✅ **YES** | Max 200 characters, cannot be empty |

### **3. Presenting Concerns (2 Required Fields)**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `presenting_concerns` | string | ✅ **YES** | Cannot be empty, detailed description required |
| `therapy_goals` | string | ✅ **YES** | Cannot be empty, goals description required |

### **4. Consent & Legal (3 Required Fields)**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `consent_to_treatment` | boolean | ✅ **YES** | Must be `true` |
| `client_signature` | string | ✅ **YES** | Max 255 characters, cannot be empty |
| `consent_date` | string | ✅ **YES** | Valid date format (YYYY-MM-DD) |

---

## ❌ **INVALID Fields (Optional - Can Be Empty)**

### **1. Personal Details (4 Optional Fields)**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `preferred_name` | string | ❌ **NO** | Max 100 characters, can be empty |
| `gender_identity` | string | ❌ **NO** | Max 50 characters, can be empty |
| `pronouns` | string | ❌ **NO** | Max 20 characters, can be empty |
| `home_phone` | string | ❌ **NO** | Max 15 characters, can be empty |

### **2. GP Referral Information (5 Optional Fields)**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `has_gp_referral` | boolean | ❌ **NO** | Default: `false` |
| `gp_name` | string | ❌ **NO** | Max 255 characters, can be empty |
| `gp_practice_name` | string | ❌ **NO** | Max 255 characters, can be empty |
| `gp_provider_number` | string | ❌ **NO** | Max 20 characters, can be empty |
| `gp_address` | string | ❌ **NO** | Text field, can be empty |

### **3. Medical History (8 Optional Fields)**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `previous_therapy` | boolean | ❌ **NO** | Default: `false` |
| `previous_therapy_details` | string | ❌ **NO** | Text field, can be empty |
| `current_medications` | boolean | ❌ **NO** | Default: `false` |
| `medication_list` | string | ❌ **NO** | Text field, can be empty |
| `other_health_professionals` | boolean | ❌ **NO** | Default: `false` |
| `other_health_details` | string | ❌ **NO** | Text field, can be empty |
| `medical_conditions` | boolean | ❌ **NO** | Default: `false` |
| `medical_conditions_details` | string | ❌ **NO** | Text field, can be empty |

### **4. Telehealth Consent (1 Optional Field)**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `consent_to_telehealth` | boolean | ❌ **NO** | Default: `false` |

---

## 🔄 **CONDITIONAL Validation Rules**

### **1. If `has_gp_referral` is `true`:**
- `gp_name` becomes **recommended** (but not required)
- `gp_practice_name` becomes **recommended** (but not required)

### **2. If `previous_therapy` is `true`:**
- `previous_therapy_details` becomes **recommended** (but not required)

### **3. If `current_medications` is `true`:**
- `medication_list` becomes **recommended** (but not required)

### **4. If `other_health_professionals` is `true`:**
- `other_health_details` becomes **recommended** (but not required)

### **5. If `medical_conditions` is `true`:**
- `medical_conditions_details` becomes **recommended** (but not required)

---

## 📊 **Validation Summary**

### **Total Fields: 30**
- **Required Fields: 9** (30%)
- **Optional Fields: 21** (70%)

### **Required Fields Breakdown:**
- **Emergency Contact: 3 fields** (33%)
- **Referral Information: 1 field** (11%)
- **Presenting Concerns: 2 fields** (22%)
- **Consent & Legal: 3 fields** (33%)

### **Optional Fields Breakdown:**
- **Personal Details: 4 fields** (19%)
- **GP Referral: 5 fields** (24%)
- **Medical History: 8 fields** (38%)
- **Telehealth: 1 field** (5%)
- **Other: 3 fields** (14%)

---

## 🚨 **Common Validation Errors**

### **1. Missing Required Fields:**
```json
{
    "error": "Required fields are missing",
    "details": {
        "emergency_contact_name": ["This field is required."],
        "emergency_contact_relationship": ["This field is required."],
        "emergency_contact_phone": ["This field is required."],
        "referral_source": ["This field is required."],
        "presenting_concerns": ["This field is required."],
        "therapy_goals": ["This field is required."],
        "consent_to_treatment": ["This field is required."],
        "client_signature": ["This field is required."],
        "consent_date": ["This field is required."]
    }
}
```

### **2. Invalid Data Types:**
```json
{
    "error": "Invalid data types",
    "details": {
        "consent_to_treatment": ["Must be a valid boolean."],
        "consent_date": ["Date has wrong format. Use one of these formats instead: YYYY-MM-DD."]
    }
}
```

### **3. Field Length Exceeded:**
```json
{
    "error": "Field length exceeded",
    "details": {
        "emergency_contact_name": ["Ensure this field has no more than 255 characters."],
        "client_signature": ["Ensure this field has no more than 255 characters."]
    }
}
```

---

## 🔧 **Frontend Validation Rules**

### **1. Required Field Validation:**
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

const validateRequiredFields = (formData: IntakeFormData): string[] => {
    const errors: string[] = [];
    
    requiredFields.forEach(field => {
        if (!formData[field] || formData[field] === '') {
            errors.push(`${field} is required`);
        }
    });
    
    return errors;
};
```

### **2. Conditional Validation:**
```typescript
const validateConditionalFields = (formData: IntakeFormData): string[] => {
    const errors: string[] = [];
    
    // If has_gp_referral is true, GP fields are recommended
    if (formData.has_gp_referral && !formData.gp_name) {
        errors.push('GP name is recommended when GP referral is selected');
    }
    
    // If previous_therapy is true, details are recommended
    if (formData.previous_therapy && !formData.previous_therapy_details) {
        errors.push('Previous therapy details are recommended');
    }
    
    // If current_medications is true, medication list is recommended
    if (formData.current_medications && !formData.medication_list) {
        errors.push('Medication list is recommended when taking medications');
    }
    
    return errors;
};
```

### **3. Data Type Validation:**
```typescript
const validateDataTypes = (formData: IntakeFormData): string[] => {
    const errors: string[] = [];
    
    // Boolean fields
    const booleanFields = [
        'has_gp_referral', 'previous_therapy', 'current_medications',
        'other_health_professionals', 'medical_conditions',
        'consent_to_treatment', 'consent_to_telehealth'
    ];
    
    booleanFields.forEach(field => {
        if (formData[field] !== undefined && typeof formData[field] !== 'boolean') {
            errors.push(`${field} must be a boolean value`);
        }
    });
    
    // Date validation
    if (formData.consent_date && !isValidDate(formData.consent_date)) {
        errors.push('consent_date must be a valid date (YYYY-MM-DD)');
    }
    
    return errors;
};
```

### **4. Field Length Validation:**
```typescript
const validateFieldLengths = (formData: IntakeFormData): string[] => {
    const errors: string[] = [];
    
    const fieldLimits = {
        'emergency_contact_name': 255,
        'emergency_contact_relationship': 100,
        'emergency_contact_phone': 15,
        'referral_source': 200,
        'gp_name': 255,
        'gp_practice_name': 255,
        'gp_provider_number': 20,
        'client_signature': 255,
        'preferred_name': 100,
        'gender_identity': 50,
        'pronouns': 20,
        'home_phone': 15
    };
    
    Object.entries(fieldLimits).forEach(([field, limit]) => {
        if (formData[field] && formData[field].length > limit) {
            errors.push(`${field} cannot exceed ${limit} characters`);
        }
    });
    
    return errors;
};
```

---

## 🎯 **Valid Submission Examples**

### **1. Minimal Valid Submission:**
```json
{
    "emergency_contact_name": "Jane Doe",
    "emergency_contact_relationship": "Spouse",
    "emergency_contact_phone": "0412345678",
    "referral_source": "Self-referral",
    "has_gp_referral": false,
    "previous_therapy": false,
    "current_medications": false,
    "other_health_professionals": false,
    "medical_conditions": false,
    "presenting_concerns": "I need help with anxiety and stress management",
    "therapy_goals": "Learn effective coping strategies for anxiety",
    "consent_to_treatment": true,
    "consent_to_telehealth": false,
    "client_signature": "John Doe",
    "consent_date": "2024-01-15"
}
```

### **2. Complete Valid Submission:**
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

---

## 🚨 **Invalid Submission Examples**

### **1. Missing Required Fields:**
```json
{
    "emergency_contact_name": "Jane Doe",
    "emergency_contact_relationship": "Spouse",
    // Missing: emergency_contact_phone, referral_source, presenting_concerns, etc.
    "consent_to_treatment": true
}
```
**Error:** `400 Bad Request` - Missing required fields

### **2. Invalid Data Types:**
```json
{
    "emergency_contact_name": "Jane Doe",
    "emergency_contact_relationship": "Spouse", 
    "emergency_contact_phone": "0412345678",
    "referral_source": "Self-referral",
    "consent_to_treatment": "yes", // Should be boolean true
    "consent_date": "15-01-2024" // Wrong date format
}
```
**Error:** `400 Bad Request` - Invalid data types

### **3. Field Length Exceeded:**
```json
{
    "emergency_contact_name": "Jane Doe with a very long name that exceeds the 255 character limit...",
    "client_signature": "John Doe with a very long signature that exceeds the 255 character limit..."
}
```
**Error:** `400 Bad Request` - Field length exceeded

---

## 🎯 **Key Validation Points**

### **✅ VALID:**
- **All 9 required fields** are provided
- **Data types** are correct (strings, booleans, dates)
- **Field lengths** are within limits
- **Boolean fields** are `true`/`false` (not strings)
- **Date format** is YYYY-MM-DD
- **Consent fields** are properly set

### **❌ INVALID:**
- **Missing required fields**
- **Wrong data types** (string instead of boolean)
- **Field length exceeded**
- **Invalid date format**
- **Empty required fields**
- **Null values** for required fields

---

## 📞 **Testing Validation**

### **Test with cURL:**
```bash
# Valid submission
curl -X POST http://127.0.0.1:8000/api/auth/intake-form/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"emergency_contact_name": "Jane Doe", "emergency_contact_relationship": "Spouse", "emergency_contact_phone": "0412345678", "referral_source": "Self-referral", "presenting_concerns": "I need help", "therapy_goals": "Learn strategies", "consent_to_treatment": true, "client_signature": "John Doe", "consent_date": "2024-01-15"}'

# Invalid submission (missing fields)
curl -X POST http://127.0.0.1:8000/api/auth/intake-form/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"emergency_contact_name": "Jane Doe"}'
```

---

**The intake form validation is comprehensive and ensures data quality while maintaining user flexibility!** 🎯✨

**Required Fields:** 9 (30%)  
**Optional Fields:** 21 (70%)  
**Validation Rules:** Field types, lengths, required fields  
**Error Handling:** Detailed error messages  
**Testing:** Ready for frontend integration
