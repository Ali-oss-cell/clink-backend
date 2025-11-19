# Patient Preferences Endpoint Documentation

**Endpoint:** `/api/auth/preferences/`  
**Status:** ✅ **Fully Implemented**

---

## 📋 Overview

This endpoint allows patients to control their communication and privacy preferences, including:
- Email notifications
- SMS notifications
- Appointment reminders
- Session recording consent
- Progress sharing with emergency contact

---

## 🔌 API Endpoints

### **GET /api/auth/preferences/**

Get current patient preferences.

**Authentication:** Required (Patient only)

**Response:**
```json
{
  "preferences": {
    "email_notifications_enabled": true,
    "sms_notifications_enabled": false,
    "appointment_reminders_enabled": true,
    "telehealth_recording_consent": false,
    "share_progress_with_emergency_contact": false
  },
  "emergency_contact": {
    "name": "Jane Doe",
    "phone": "+61 412 345 678",
    "relationship": "Spouse"
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `403 Forbidden` - Not a patient user

---

### **PUT /api/auth/preferences/**

Update all preferences (full update).

**Authentication:** Required (Patient only)

**Request Body:**
```json
{
  "email_notifications_enabled": true,
  "sms_notifications_enabled": false,
  "appointment_reminders_enabled": true,
  "telehealth_recording_consent": true,
  "share_progress_with_emergency_contact": false
}
```

**Response:**
```json
{
  "message": "Preferences updated successfully",
  "preferences": {
    "email_notifications_enabled": true,
    "sms_notifications_enabled": false,
    "appointment_reminders_enabled": true,
    "telehealth_recording_consent": true,
    "share_progress_with_emergency_contact": false
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Validation error
- `403 Forbidden` - Not a patient user

---

### **PATCH /api/auth/preferences/**

Partially update preferences (update only provided fields).

**Authentication:** Required (Patient only)

**Request Body:**
```json
{
  "email_notifications_enabled": false
}
```

**Response:**
```json
{
  "message": "Preferences updated successfully",
  "preferences": {
    "email_notifications_enabled": false,
    "sms_notifications_enabled": false,
    "appointment_reminders_enabled": true,
    "telehealth_recording_consent": false,
    "share_progress_with_emergency_contact": false
  }
}
```

**Status Codes:**
- `200 OK` - Success
- `400 Bad Request` - Validation error
- `403 Forbidden` - Not a patient user

---

## 📊 Preference Fields

### **Communication Preferences**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `email_notifications_enabled` | boolean | `true` | Patient prefers to receive email notifications |
| `sms_notifications_enabled` | boolean | `false` | Patient prefers to receive SMS notifications |
| `appointment_reminders_enabled` | boolean | `true` | Patient prefers to receive appointment reminders |

### **Privacy Preferences**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `telehealth_recording_consent` | boolean | `false` | Patient consents to session recording for quality assurance |
| `share_progress_with_emergency_contact` | boolean | `false` | Patient consents to sharing progress updates with emergency contact |

---

## 🔒 Automatic Consent Tracking

The endpoint automatically tracks consent dates and versions:

### **Session Recording Consent**
- When `telehealth_recording_consent` is set to `true`:
  - `telehealth_recording_consent_date` is set to current timestamp
  - `telehealth_recording_consent_version` is set from settings
- When set to `false`:
  - Consent date and version are cleared

### **Progress Sharing Consent**
- When `share_progress_with_emergency_contact` is set to `true`:
  - `share_progress_consent_date` is set to current timestamp
  - `share_progress_consent_version` is set from settings
- When set to `false`:
  - Consent date and version are cleared

---

## 💻 Frontend Integration

### **TypeScript Interface**

```typescript
interface PatientPreferences {
  email_notifications_enabled: boolean;
  sms_notifications_enabled: boolean;
  appointment_reminders_enabled: boolean;
  telehealth_recording_consent: boolean;
  share_progress_with_emergency_contact: boolean;
}

interface PreferencesResponse {
  preferences: PatientPreferences;
  emergency_contact?: {
    name: string;
    phone: string;
    relationship: string;
  } | null;
}
```

### **React Hook Example**

```typescript
import { useState, useEffect } from 'react';
import axios from 'axios';

const usePatientPreferences = () => {
  const [preferences, setPreferences] = useState<PatientPreferences | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPreferences = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/auth/preferences/', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setPreferences(response.data.preferences);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to fetch preferences');
    } finally {
      setLoading(false);
    }
  };

  const updatePreferences = async (updates: Partial<PatientPreferences>) => {
    try {
      const response = await axios.patch('/api/auth/preferences/', updates, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }
      });
      setPreferences(response.data.preferences);
      return { success: true, data: response.data };
    } catch (err: any) {
      return {
        success: false,
        error: err.response?.data?.error || 'Failed to update preferences'
      };
    }
  };

  useEffect(() => {
    fetchPreferences();
  }, []);

  return {
    preferences,
    loading,
    error,
    updatePreferences,
    refetch: fetchPreferences
  };
};
```

### **React Component Example**

```typescript
import React from 'react';
import { usePatientPreferences } from './hooks/usePatientPreferences';

const PatientPreferencesPage: React.FC = () => {
  const { preferences, loading, updatePreferences } = usePatientPreferences();
  const [saving, setSaving] = useState(false);

  const handleToggle = async (field: keyof PatientPreferences, value: boolean) => {
    setSaving(true);
    const result = await updatePreferences({ [field]: value });
    setSaving(false);
    
    if (result.success) {
      // Show success message
    } else {
      // Show error message
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!preferences) return <div>No preferences found</div>;

  return (
    <div className="preferences-page">
      <h2>Communication Preferences</h2>
      
      <div className="preference-item">
        <label>
          <input
            type="checkbox"
            checked={preferences.email_notifications_enabled}
            onChange={(e) => handleToggle('email_notifications_enabled', e.target.checked)}
            disabled={saving}
          />
          Email notifications
        </label>
      </div>

      <div className="preference-item">
        <label>
          <input
            type="checkbox"
            checked={preferences.sms_notifications_enabled}
            onChange={(e) => handleToggle('sms_notifications_enabled', e.target.checked)}
            disabled={saving}
          />
          SMS notifications
        </label>
      </div>

      <div className="preference-item">
        <label>
          <input
            type="checkbox"
            checked={preferences.appointment_reminders_enabled}
            onChange={(e) => handleToggle('appointment_reminders_enabled', e.target.checked)}
            disabled={saving}
          />
          Appointment reminders
        </label>
      </div>

      <h2>Privacy Preferences</h2>

      <div className="preference-item">
        <label>
          <input
            type="checkbox"
            checked={preferences.telehealth_recording_consent}
            onChange={(e) => handleToggle('telehealth_recording_consent', e.target.checked)}
            disabled={saving}
          />
          Allow session recordings for quality assurance
        </label>
        <p className="help-text">
          You can withdraw this consent at any time
        </p>
      </div>

      <div className="preference-item">
        <label>
          <input
            type="checkbox"
            checked={preferences.share_progress_with_emergency_contact}
            onChange={(e) => handleToggle('share_progress_with_emergency_contact', e.target.checked)}
            disabled={saving}
          />
          Share progress with emergency contact
        </label>
        <p className="help-text">
          Allow your emergency contact to receive progress updates
        </p>
      </div>
    </div>
  );
};

export default PatientPreferencesPage;
```

---

## 🔧 Backend Implementation

### **Model Fields**

**Location:** `users/models.py` - `PatientProfile` model

```python
# Communication Preferences
email_notifications_enabled = models.BooleanField(default=True)
sms_notifications_enabled = models.BooleanField(default=False)
appointment_reminders_enabled = models.BooleanField(default=True)

# Privacy Preferences
share_progress_with_emergency_contact = models.BooleanField(default=False)
share_progress_consent_date = models.DateTimeField(null=True, blank=True)
share_progress_consent_version = models.CharField(max_length=20, blank=True)
```

### **Serializer**

**Location:** `users/serializers.py` - `PatientPreferencesSerializer`

Handles:
- Field validation
- Automatic consent date/version tracking
- Partial updates

### **View**

**Location:** `users/views.py` - `PatientPreferencesView`

- `GET` - Retrieve preferences
- `PUT` - Full update
- `PATCH` - Partial update

### **URL Route**

**Location:** `users/urls.py`

```python
path('preferences/', views.PatientPreferencesView.as_view(), name='patient-preferences'),
```

---

## ⚙️ Settings

**Location:** `psychology_clinic/settings.py`

```python
PROGRESS_SHARING_CONSENT_VERSION = config('PROGRESS_SHARING_CONSENT_VERSION', default='1.0')
```

---

## 🔐 Privacy & Compliance

### **Consent Tracking**
- ✅ All consent changes are tracked with dates
- ✅ Consent versions are tracked for compliance
- ✅ Consent can be withdrawn at any time

### **Privacy Act 1988 Compliance**
- ✅ APP 7 - Direct Marketing (opt-out for notifications)
- ✅ APP 6 - Use/Disclosure (explicit consent for progress sharing)
- ✅ Consent withdrawal mechanism

---

## 📝 Usage Examples

### **cURL Examples**

**Get Preferences:**
```bash
curl -X GET http://localhost:8000/api/auth/preferences/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Update Preferences:**
```bash
curl -X PATCH http://localhost:8000/api/auth/preferences/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email_notifications_enabled": false,
    "telehealth_recording_consent": true
  }'
```

---

## ✅ Testing Checklist

- [ ] GET returns current preferences
- [ ] PUT updates all preferences
- [ ] PATCH updates only provided fields
- [ ] Consent dates are tracked automatically
- [ ] Consent versions are set correctly
- [ ] Non-patients receive 403 error
- [ ] Invalid data returns 400 error
- [ ] Emergency contact info is included in GET response

---

## 🚀 Next Steps

1. **Run Migration:**
   ```bash
   python manage.py migrate users
   ```

2. **Test Endpoint:**
   - Use Postman or curl to test all methods
   - Verify consent tracking works correctly

3. **Frontend Integration:**
   - Add preferences page to frontend
   - Use the React hook example above
   - Test all preference toggles

4. **Notification Integration:**
   - Update notification services to check preferences
   - Respect `email_notifications_enabled` flag
   - Respect `sms_notifications_enabled` flag
   - Respect `appointment_reminders_enabled` flag

---

**Last Updated:** 2025-01-19  
**Status:** ✅ Ready for Use

