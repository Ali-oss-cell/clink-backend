# 💻 Telehealth Consent & Emergency Plan Endpoint

## ✅ **Endpoint Exists!**

**URL:** `/api/auth/telehealth-consent/`

---

## 📋 **API Endpoints**

### **1. GET /api/auth/telehealth-consent/**

Get current telehealth consent status, emergency plan, and recording consent.

**Authentication:** Required (JWT Token)

**Response (200 OK):**
```json
{
  "consent_to_telehealth": true,
  "telehealth_consent_date": "2025-11-28T10:00:00Z",
  "telehealth_consent_version": "1.0",
  "latest_version": "1.0",
  "needs_update": false,
  "telehealth_requirements_url": "https://yourclinic.com.au/telehealth-requirements",
  "telehealth_emergency_protocol_acknowledged": true,
  "telehealth_emergency_acknowledged_date": "2025-11-28T10:00:00Z",
  "telehealth_emergency_contact": "John Doe (+61 412 345 678)",
  "telehealth_emergency_plan": "Call emergency contact then dial 000 if needed",
  "telehealth_tech_requirements_acknowledged": true,
  "telehealth_tech_acknowledged_date": "2025-11-28T10:00:00Z",
  "telehealth_recording_consent": true,
  "telehealth_recording_consent_date": "2025-11-28T10:00:00Z",
  "telehealth_recording_consent_version": "1.0"
}
```

**Response Fields:**
- `consent_to_telehealth` (boolean) - Whether patient consented to telehealth
- `telehealth_consent_date` (string, ISO format) - When consent was given
- `telehealth_consent_version` (string) - Version of consent form accepted
- `latest_version` (string) - Current version available
- `needs_update` (boolean) - True if consent version is outdated
- `telehealth_requirements_url` (string) - Link to requirements page
- `telehealth_emergency_protocol_acknowledged` (boolean) - Emergency procedures acknowledged
- `telehealth_emergency_acknowledged_date` (string, ISO format) - When acknowledged
- `telehealth_emergency_contact` (string) - Emergency contact details
- `telehealth_emergency_plan` (string) - Emergency plan text
- `telehealth_tech_requirements_acknowledged` (boolean) - Tech requirements acknowledged
- `telehealth_tech_acknowledged_date` (string, ISO format) - When acknowledged
- `telehealth_recording_consent` (boolean) - Consent to record sessions
- `telehealth_recording_consent_date` (string, ISO format) - When recording consent given
- `telehealth_recording_consent_version` (string) - Version of recording consent

**Status Codes:**
- `200 OK` - Success
- `401 Unauthorized` - Missing/invalid token

---

### **2. POST /api/auth/telehealth-consent/**

Submit/update telehealth consent with emergency plan and recording consent.

**Authentication:** Required (JWT Token, Patient only)

**Request Body:**
```json
{
  "consent_to_telehealth": true,
  "telehealth_emergency_protocol_acknowledged": true,
  "telehealth_emergency_contact": "John Doe (+61 412 345 678)",
  "telehealth_emergency_plan": "Call emergency contact then dial 000 if needed",
  "telehealth_tech_requirements_acknowledged": true,
  "telehealth_recording_consent": false
}
```

**Required Fields:**
- `consent_to_telehealth` (boolean) - Must be `true`
- `telehealth_emergency_protocol_acknowledged` (boolean) - Must acknowledge emergency procedures
- `telehealth_emergency_contact` (string) - Emergency contact information
- `telehealth_emergency_plan` (string) - Emergency plan description
- `telehealth_tech_requirements_acknowledged` (boolean) - Must acknowledge tech requirements

**Optional Fields:**
- `telehealth_recording_consent` (boolean) - Consent to record sessions (default: `false`)

**Response (200 OK):**
```json
{
  "message": "Telehealth consent updated successfully",
  "consent_to_telehealth": true,
  "telehealth_consent_version": "1.0",
  "telehealth_consent_date": "2025-11-28T10:00:00Z",
  "telehealth_emergency_protocol_acknowledged": true,
  "telehealth_emergency_acknowledged_date": "2025-11-28T10:00:00Z",
  "telehealth_emergency_contact": "John Doe (+61 412 345 678)",
  "telehealth_emergency_plan": "Call emergency contact then dial 000 if needed",
  "telehealth_tech_requirements_acknowledged": true,
  "telehealth_tech_acknowledged_date": "2025-11-28T10:00:00Z",
  "telehealth_recording_consent": false,
  "telehealth_recording_consent_date": null,
  "telehealth_recording_consent_version": "1.0",
  "updated_at": "2025-11-28T10:00:00Z"
}
```

**Response Fields:**
- `message` (string) - Success message
- `consent_to_telehealth` (boolean) - Whether consent was granted
- `telehealth_consent_version` (string) - Version of consent form (e.g., "1.0" or "2025-01")
- `telehealth_consent_date` (string, ISO format) - When consent was saved/updated
- `telehealth_emergency_protocol_acknowledged` (boolean) - Emergency procedures acknowledged
- `telehealth_emergency_acknowledged_date` (string, ISO format) - When emergency procedures were acknowledged
- `telehealth_emergency_contact` (string) - Emergency contact information
- `telehealth_emergency_plan` (string) - Emergency plan description
- `telehealth_tech_requirements_acknowledged` (boolean) - Tech requirements acknowledged
- `telehealth_tech_acknowledged_date` (string, ISO format) - When tech requirements were acknowledged
- `telehealth_recording_consent` (boolean) - Recording consent status
- `telehealth_recording_consent_date` (string, ISO format or null) - When recording consent was given
- `telehealth_recording_consent_version` (string) - Version of recording consent form
- `updated_at` (string, ISO format) - Last update timestamp

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Missing required fields or validation error
- `403 Forbidden` - Not a patient user
- `401 Unauthorized` - Missing/invalid token

---

## 💻 **Frontend Integration Example**

### **TypeScript Interface**
```typescript
interface TelehealthConsent {
  consent_to_telehealth: boolean;
  telehealth_consent_date: string | null;
  telehealth_consent_version: string;
  latest_version: string;
  needs_update: boolean;
  telehealth_requirements_url: string;
  telehealth_emergency_protocol_acknowledged: boolean;
  telehealth_emergency_acknowledged_date: string | null;
  telehealth_emergency_contact: string;
  telehealth_emergency_plan: string;
  telehealth_tech_requirements_acknowledged: boolean;
  telehealth_tech_acknowledged_date: string | null;
  telehealth_recording_consent: boolean;
  telehealth_recording_consent_date: string | null;
  telehealth_recording_consent_version: string;
}

interface TelehealthConsentUpdate {
  consent_to_telehealth: boolean;
  telehealth_emergency_protocol_acknowledged: boolean;
  telehealth_emergency_contact: string;
  telehealth_emergency_plan: string;
  telehealth_tech_requirements_acknowledged: boolean;
  telehealth_recording_consent?: boolean;
}
```

### **API Service**
```typescript
// services/api/telehealth.ts
import { authAPI } from './auth';

export const telehealthService = {
  // Get current consent status
  getConsent: async (): Promise<TelehealthConsent> => {
    const response = await authAPI.get('/telehealth-consent/');
    return response.data;
  },

  // Update consent
  updateConsent: async (data: TelehealthConsentUpdate): Promise<{ message: string }> => {
    const response = await authAPI.post('/telehealth-consent/', data);
    return response.data;
  },
};
```

### **React Component Example**
```typescript
import React, { useState, useEffect } from 'react';
import { telehealthService } from '../services/api/telehealth';

function TelehealthConsentForm() {
  const [consent, setConsent] = useState<TelehealthConsent | null>(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    consent_to_telehealth: false,
    telehealth_emergency_protocol_acknowledged: false,
    telehealth_emergency_contact: '',
    telehealth_emergency_plan: '',
    telehealth_tech_requirements_acknowledged: false,
    telehealth_recording_consent: false,
  });

  useEffect(() => {
    loadConsent();
  }, []);

  const loadConsent = async () => {
    try {
      const data = await telehealthService.getConsent();
      setConsent(data);
      setFormData({
        consent_to_telehealth: data.consent_to_telehealth,
        telehealth_emergency_protocol_acknowledged: data.telehealth_emergency_protocol_acknowledged,
        telehealth_emergency_contact: data.telehealth_emergency_contact || '',
        telehealth_emergency_plan: data.telehealth_emergency_plan || '',
        telehealth_tech_requirements_acknowledged: data.telehealth_tech_requirements_acknowledged,
        telehealth_recording_consent: data.telehealth_recording_consent,
      });
    } catch (error) {
      console.error('Failed to load consent:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await telehealthService.updateConsent(formData);
      await loadConsent(); // Reload to get updated data
      alert('Telehealth consent updated successfully!');
    } catch (error) {
      console.error('Failed to update consent:', error);
      alert('Failed to update consent. Please try again.');
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h2>Telehealth Consent & Emergency Plan</h2>
      
      {/* Status Display */}
      {consent && (
        <div>
          <p><strong>Status:</strong> {consent.consent_to_telehealth ? 'Active' : 'Inactive'}</p>
          <p><strong>Consent Version:</strong> {consent.telehealth_consent_version}</p>
          <p><strong>Last Updated:</strong> {new Date(consent.telehealth_consent_date || '').toLocaleDateString()}</p>
          <p><strong>Recording Consent:</strong> {consent.telehealth_recording_consent ? 'Allowed' : 'Not Allowed'}</p>
          {consent.needs_update && (
            <p className="warning">⚠️ Your consent needs to be updated to the latest version.</p>
          )}
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit}>
        <label>
          <input
            type="checkbox"
            checked={formData.consent_to_telehealth}
            onChange={(e) => setFormData({ ...formData, consent_to_telehealth: e.target.checked })}
            required
          />
          I consent to telehealth sessions.
        </label>

        <label>
          <input
            type="checkbox"
            checked={formData.telehealth_emergency_protocol_acknowledged}
            onChange={(e) => setFormData({ ...formData, telehealth_emergency_protocol_acknowledged: e.target.checked })}
            required
          />
          I acknowledge the emergency procedures for telehealth sessions.
        </label>

        <label>
          Emergency Contact:
          <input
            type="text"
            value={formData.telehealth_emergency_contact}
            onChange={(e) => setFormData({ ...formData, telehealth_emergency_contact: e.target.value })}
            placeholder="Name and phone number"
            required
          />
        </label>

        <label>
          Emergency Plan:
          <textarea
            value={formData.telehealth_emergency_plan}
            onChange={(e) => setFormData({ ...formData, telehealth_emergency_plan: e.target.value })}
            placeholder="Describe your emergency plan"
            required
          />
        </label>

        <label>
          <input
            type="checkbox"
            checked={formData.telehealth_tech_requirements_acknowledged}
            onChange={(e) => setFormData({ ...formData, telehealth_tech_requirements_acknowledged: e.target.checked })}
            required
          />
          I acknowledge I meet the technical requirements for telehealth.
        </label>

        <label>
          <input
            type="checkbox"
            checked={formData.telehealth_recording_consent}
            onChange={(e) => setFormData({ ...formData, telehealth_recording_consent: e.target.checked })}
          />
          I consent to session recordings for quality assurance.
        </label>

        <button type="submit">Save Consent</button>
      </form>
    </div>
  );
}

export default TelehealthConsentForm;
```

---

## 📊 **Response Mapping to UI**

Based on your UI screenshot, here's how the API response maps:

| UI Field | API Response Field |
|----------|-------------------|
| **Status** | `consent_to_telehealth ? "Active" : "Inactive"` |
| **Consent Version** | `telehealth_consent_version` |
| **Last Updated** | `telehealth_consent_date` (format as date) |
| **Recording Consent** | `telehealth_recording_consent ? "Allowed" : "Not Allowed"` |
| **Emergency Contact** | `telehealth_emergency_contact` |
| **Emergency Plan** | `telehealth_emergency_plan` |

---

## 🔍 **Checking Consent Status**

The endpoint returns `needs_update: true` if:
- Consent version doesn't match `latest_version`
- Consent was never given (`telehealth_consent_version` is empty/null)

**Frontend Logic:**
```typescript
if (consent.needs_update) {
  // Show warning: "Your telehealth consent needs to be updated"
  // Prompt user to review and accept new version
}
```

---

## ✅ **Validation Rules**

1. **Required for POST:**
   - `consent_to_telehealth` must be `true`
   - `telehealth_emergency_protocol_acknowledged` must be `true`
   - `telehealth_emergency_contact` must be provided (non-empty string)
   - `telehealth_emergency_plan` must be provided (non-empty string)
   - `telehealth_tech_requirements_acknowledged` must be `true`

2. **Optional:**
   - `telehealth_recording_consent` (defaults to `false` if not provided)

---

## 🚨 **Error Handling**

### **400 Bad Request**
```json
{
  "error": "consent_to_telehealth is required"
}
```

### **403 Forbidden**
```json
{
  "error": "Only patients can update telehealth consent"
}
```

---

## 📝 **Notes**

- **Version Tracking:** The system automatically tracks consent versions for compliance
- **Automatic Dates:** When consent is given, dates are automatically set
- **Recording Consent:** Separate from main consent, can be updated independently
- **Emergency Plan:** Required for all telehealth sessions (AHPRA compliance)

---

## 🔗 **Related Endpoints**

- `/api/auth/preferences/` - General patient preferences (includes recording consent)
- `/api/auth/intake-form/` - Intake form (includes telehealth consent fields)

---

**Endpoint Status:** ✅ **Fully Implemented and Ready to Use**

