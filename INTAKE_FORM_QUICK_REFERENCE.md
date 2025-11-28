# 📋 Intake Form - Quick Reference for Frontend

## 🎯 **API Endpoint**
```
POST /api/users/intake-form/
PUT /api/auth/intake-form/  (preferred)
```

**Headers:**
```javascript
{
  "Authorization": "Bearer JWT_TOKEN",
  "Content-Type": "application/json"
}
```

---

## ✅ **REQUIRED FIELDS** (Must Send)

| Field | Type | Example |
|-------|------|---------|
| `first_name` | string | `"John"` |
| `last_name` | string | `"Smith"` |
| `phone_number` | string | `"+61412345678"` or `"0412345678"` |
| `date_of_birth` | string | `"1990-05-15"` (YYYY-MM-DD) |
| `address_line_1` | string | `"123 Main Street"` |
| `suburb` | string | `"Melbourne"` |
| `state` | string | `"VIC"` (see states below) |
| `postcode` | string | `"3000"` (4 digits) |
| `consent_to_treatment` | boolean | `true` |
| `privacy_policy_accepted` | boolean | `true` |

---

## 📋 **OPTIONAL FIELDS** (Can Omit)

### Personal
- `preferred_name` (string)
- `gender_identity` (string)
- `pronouns` (string)
- `home_phone` (string)
- `medicare_number` (string, 10 digits)

### Emergency Contact
- `emergency_contact_name` (string)
- `emergency_contact_relationship` (string)
- `emergency_contact_phone` (string)

### Referral
- `referral_source` (string)
- `has_gp_referral` (boolean)
- `gp_name` (string) - **if** `has_gp_referral` is `true`
- `gp_practice_name` (string)
- `gp_provider_number` (string)
- `gp_address` (string)

### Medical History
- `previous_therapy` (boolean)
- `previous_therapy_details` (string) - **if** `previous_therapy` is `true`
- `current_medications` (boolean)
- `medication_list` (string) - **if** `current_medications` is `true`
- `other_health_professionals` (boolean)
- `other_health_details` (string) - **if** `other_health_professionals` is `true`
- `medical_conditions` (boolean)
- `medical_conditions_details` (string) - **if** `medical_conditions` is `true`

### Presenting Concerns
- `presenting_concerns` (string, long text)
- `therapy_goals` (string, long text)

### Consent (Optional but Recommended)
- `consent_to_telehealth` (boolean)
- `telehealth_emergency_protocol_acknowledged` (boolean) - **if** `consent_to_telehealth` is `true`
- `telehealth_tech_requirements_acknowledged` (boolean) - **if** `consent_to_telehealth` is `true`
- `telehealth_recording_consent` (boolean)
- `consent_to_data_sharing` (boolean)
- `consent_to_marketing` (boolean)

### Communication Preferences
- `email_notifications_enabled` (boolean, default: `true`)
- `sms_notifications_enabled` (boolean, default: `false`)
- `appointment_reminders_enabled` (boolean, default: `true`)

### Privacy
- `share_progress_with_emergency_contact` (boolean)

### Parental Consent (If Under 18)
- `parental_consent` (boolean)
- `parental_consent_name` (string)
- `parental_consent_signature` (string)

### Completion
- `intake_completed` (boolean) - Set to `true` when submitting

---

## 📍 **State Options**
```javascript
["NSW", "VIC", "QLD", "WA", "SA", "TAS", "ACT", "NT"]
```

---

## 📞 **Phone Number Format**
- ✅ `"+61412345678"` (with country code)
- ✅ `"0412345678"` (without country code)
- ❌ `"1234567890"` (invalid - missing +61 or 0)

---

## 📅 **Date Format**
- Format: `YYYY-MM-DD`
- Example: `"1990-05-15"`

---

## 💻 **Minimal Example Payload**
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

---

## 🔄 **Conditional Fields Logic**

Show these fields **only if** parent field is `true`:

| Parent Field | Show These Fields |
|--------------|-------------------|
| `has_gp_referral: true` | `gp_name`, `gp_practice_name`, `gp_provider_number`, `gp_address` |
| `previous_therapy: true` | `previous_therapy_details` |
| `current_medications: true` | `medication_list` |
| `other_health_professionals: true` | `other_health_details` |
| `medical_conditions: true` | `medical_conditions_details` |
| `consent_to_telehealth: true` | `telehealth_emergency_protocol_acknowledged`, `telehealth_tech_requirements_acknowledged` |
| Patient age < 18 | `parental_consent`, `parental_consent_name`, `parental_consent_signature` |

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

## ❌ **Error Response (400)**
```json
{
  "phone_number": ["Phone number must be in Australian format"],
  "state": ["This field is required"],
  "consent_to_treatment": ["This field is required"]
}
```

---

## 🚀 **Quick Checklist**
- [ ] Use `POST /api/users/intake-form/` or `PUT /api/auth/intake-form/`
- [ ] Include `Authorization: Bearer TOKEN` header
- [ ] Send all **required fields**
- [ ] Validate phone: `+61XXXXXXXXX` or `0XXXXXXXXX`
- [ ] Validate date: `YYYY-MM-DD`
- [ ] Validate state: One of 8 Australian states/territories
- [ ] Validate postcode: 4 digits
- [ ] Set `consent_to_treatment: true`
- [ ] Set `privacy_policy_accepted: true`
- [ ] Set `intake_completed: true` on final submit
- [ ] Handle conditional fields (show/hide based on booleans)

---

**Full Documentation:** See `FRONTEND_INTAKE_FORM_GUIDE.md` for complete details.

