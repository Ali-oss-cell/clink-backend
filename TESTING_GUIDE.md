# Testing Guide - Preferences & Consent Features

**Date:** 2025-01-19  
**Test File:** `users/tests_preferences.py`

---

## 🧪 **Test Coverage**

### **1. Notification Preferences Tests**

#### **Test: Email Notifications Disabled**
- **File:** `users/tests_preferences.py::NotificationPreferencesTestCase::test_email_notifications_disabled`
- **What it tests:** Emails are not sent when `email_notifications_enabled = False`
- **Expected:** Returns `{'skipped': True, 'reason': 'Email notifications disabled by patient'}`

#### **Test: Email Notifications Enabled**
- **File:** `users/tests_preferences.py::NotificationPreferencesTestCase::test_email_notifications_enabled`
- **What it tests:** Emails are sent when `email_notifications_enabled = True`
- **Expected:** Email function is called

#### **Test: SMS Notifications Disabled**
- **File:** `users/tests_preferences.py::NotificationPreferencesTestCase::test_sms_notifications_disabled`
- **What it tests:** SMS are not sent when `sms_notifications_enabled = False`
- **Expected:** Returns `{'skipped': True, 'reason': 'SMS notifications disabled by patient'}`

#### **Test: Appointment Reminders Disabled**
- **File:** `users/tests_preferences.py::NotificationPreferencesTestCase::test_appointment_reminders_disabled`
- **What it tests:** Reminders are not sent when `appointment_reminders_enabled = False`
- **Expected:** Returns `{'skipped': True}`

#### **Test: WhatsApp Respects SMS Preference**
- **File:** `users/tests_preferences.py::NotificationPreferencesTestCase::test_whatsapp_respects_sms_preference`
- **What it tests:** WhatsApp respects SMS notification preference
- **Expected:** Patient doesn't receive WhatsApp if SMS disabled

---

### **2. Recording Consent Tests**

#### **Test: Recording Without Consent Returns Error**
- **File:** `users/tests_preferences.py::RecordingConsentTestCase::test_recording_without_consent_returns_error`
- **What it tests:** Enabling recording without consent returns 403 error
- **Expected:** HTTP 403 with error message about consent

#### **Test: Recording With Consent Succeeds**
- **File:** `users/tests_preferences.py::RecordingConsentTestCase::test_recording_with_consent_succeeds`
- **What it tests:** Enabling recording with consent succeeds
- **Expected:** Room created with `enable_recording=True`

#### **Test: Automatic Room Creation Respects Consent**
- **File:** `users/tests_preferences.py::RecordingConsentTestCase::test_automatic_room_creation_respects_consent`
- **What it tests:** Automatic room creation only enables recording if consent given
- **Expected:** 
  - Without consent → `enable_recording=False`
  - With consent → `enable_recording=True`

---

### **3. Progress Sharing Tests**

#### **Test: Progress Sharing With Consent Sends SMS**
- **File:** `users/tests_preferences.py::ProgressSharingTestCase::test_progress_sharing_with_consent_sends_sms`
- **What it tests:** Progress is shared when consent is given
- **Expected:** SMS sent with non-sensitive summary

#### **Test: Progress Sharing Without Consent Skips**
- **File:** `users/tests_preferences.py::ProgressSharingTestCase::test_progress_sharing_without_consent_skips`
- **What it tests:** Progress is not shared when consent is not given
- **Expected:** Returns `{'shared': False, 'reason': 'Patient has not consented...'}`

#### **Test: Progress Summary Is Non-Sensitive**
- **File:** `users/tests_preferences.py::ProgressSharingTestCase::test_progress_summary_is_non_sensitive`
- **What it tests:** Summary only contains non-sensitive information
- **Expected:** 
  - Contains: Patient name, progress rating, general update
  - Does NOT contain: Diagnosis, clinical impressions, treatment details

---

### **4. Preferences API Tests**

#### **Test: Get Preferences**
- **File:** `users/tests_preferences.py::PreferencesAPITestCase::test_get_preferences`
- **What it tests:** GET `/api/auth/preferences/` returns current preferences
- **Expected:** Returns all preference fields

#### **Test: Update Preferences**
- **File:** `users/tests_preferences.py::PreferencesAPITestCase::test_update_preferences`
- **What it tests:** PATCH `/api/auth/preferences/` updates preferences
- **Expected:** Preferences updated in database

#### **Test: Enable Recording Consent Tracks Date**
- **File:** `users/tests_preferences.py::PreferencesAPITestCase::test_enable_recording_consent_tracks_date`
- **What it tests:** Enabling recording consent tracks date and version
- **Expected:** `telehealth_recording_consent_date` and `version` are set

#### **Test: Disable Recording Consent Clears Date**
- **File:** `users/tests_preferences.py::PreferencesAPITestCase::test_disable_recording_consent_clears_date`
- **What it tests:** Disabling recording consent clears date and version
- **Expected:** `telehealth_recording_consent_date` and `version` are cleared

---

## 🚀 **Running Tests**

### **Run All Preference Tests:**
```bash
python manage.py test users.tests_preferences
```

### **Run Specific Test Class:**
```bash
python manage.py test users.tests_preferences.NotificationPreferencesTestCase
```

### **Run Specific Test:**
```bash
python manage.py test users.tests_preferences.NotificationPreferencesTestCase.test_email_notifications_disabled
```

### **Run with Verbose Output:**
```bash
python manage.py test users.tests_preferences --verbosity=2
```

---

## 📋 **Manual Testing Checklist**

### **Notification Preferences:**

1. **Disable Email Notifications:**
   ```bash
   PATCH /api/auth/preferences/
   {"email_notifications_enabled": false}
   ```
   - Create appointment → Verify no confirmation email sent
   - Wait for reminder → Verify no reminder email sent

2. **Disable SMS Notifications:**
   ```bash
   PATCH /api/auth/preferences/
   {"sms_notifications_enabled": false}
   ```
   - Create appointment → Verify no SMS/WhatsApp sent

3. **Disable Reminders:**
   ```bash
   PATCH /api/auth/preferences/
   {"appointment_reminders_enabled": false}
   ```
   - Wait for reminder time → Verify no reminders sent (email or SMS)

4. **Re-enable Preferences:**
   ```bash
   PATCH /api/auth/preferences/
   {
     "email_notifications_enabled": true,
     "sms_notifications_enabled": true,
     "appointment_reminders_enabled": true
   }
   ```
   - Verify notifications resume

---

### **Recording Consent:**

1. **Try to Enable Recording Without Consent:**
   ```bash
   POST /api/appointments/video-room/{appointment_id}/
   {"enable_recording": true}
   ```
   - Should get 403 error

2. **Give Consent:**
   ```bash
   PATCH /api/auth/preferences/
   {"telehealth_recording_consent": true}
   ```
   - Verify consent date is set

3. **Enable Recording With Consent:**
   ```bash
   POST /api/appointments/video-room/{appointment_id}/
   {"enable_recording": true}
   ```
   - Should succeed

4. **Withdraw Consent:**
   ```bash
   PATCH /api/auth/preferences/
   {"telehealth_recording_consent": false}
   ```
   - Verify consent date is cleared
   - Try to enable recording → Should get 403 error

5. **Automatic Room Creation:**
   - With consent → Room created with recording enabled
   - Without consent → Room created with recording disabled

---

### **Progress Sharing:**

1. **Enable Sharing:**
   ```bash
   PATCH /api/auth/preferences/
   {"share_progress_with_emergency_contact": true}
   ```

2. **Create Progress Note:**
   ```bash
   POST /api/auth/progress-notes/
   {
     "patient": 1,
     "session_date": "2025-01-19T10:00:00Z",
     "session_number": 1,
     "subjective": "Patient reports feeling better...",
     "objective": "Patient appeared calm...",
     "assessment": "Making good progress...",
     "plan": "Continue current approach..."
   }
   ```
   - Check emergency contact phone → Should receive SMS
   - Verify SMS content is non-sensitive

3. **Disable Sharing:**
   ```bash
   PATCH /api/auth/preferences/
   {"share_progress_with_emergency_contact": false}
   ```
   - Create progress note → Should NOT send SMS

---

## ✅ **Test Results Summary**

**Total Tests:** 15  
**Test Classes:** 4

### **NotificationPreferencesTestCase:** 5 tests
- ✅ Email notifications disabled
- ✅ Email notifications enabled
- ✅ SMS notifications disabled
- ✅ Appointment reminders disabled
- ✅ WhatsApp respects SMS preference

### **RecordingConsentTestCase:** 3 tests
- ✅ Recording without consent returns error
- ✅ Recording with consent succeeds
- ✅ Automatic room creation respects consent

### **ProgressSharingTestCase:** 4 tests
- ✅ Progress sharing with consent sends SMS
- ✅ Progress sharing without consent skips
- ✅ Progress summary is non-sensitive
- ✅ Progress sharing signal triggers

### **PreferencesAPITestCase:** 4 tests
- ✅ Get preferences
- ✅ Update preferences
- ✅ Enable recording consent tracks date
- ✅ Disable recording consent clears date

---

## 🔧 **Test Setup Requirements**

### **Dependencies:**
- Django TestCase
- DRF APIClient
- unittest.mock (for mocking external services)

### **Test Data:**
- Creates test patient with profile
- Creates test psychologist
- Creates test appointment
- Sets up emergency contact info

### **Mocking:**
- Email service (SendGrid)
- SMS service (Twilio)
- WhatsApp service (Twilio)
- Video service (Twilio)

---

## 📝 **Notes**

- Tests use mocking to avoid actual API calls
- Tests verify behavior, not implementation details
- All tests are isolated and can run independently
- Tests cover both success and failure scenarios

---

**Last Updated:** 2025-01-19  
**Status:** ✅ Test Suite Complete

