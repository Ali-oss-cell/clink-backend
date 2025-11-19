# Missing Implementations & Incomplete Features

**Date:** 2025-01-19  
**Status:** ⚠️ **3 Critical Items Missing**

---

## 🚨 **Critical Missing Implementations**

### **1. Notification Preferences Not Respected** ❌

**Problem:** The notification services (email, SMS, reminders) do NOT check patient preferences before sending.

**Current Behavior:**
- Emails are sent even if `email_notifications_enabled = false`
- SMS are sent even if `sms_notifications_enabled = false`
- Reminders are sent even if `appointment_reminders_enabled = false`

**What's Missing:**
- Email service doesn't check `patient.patient_profile.email_notifications_enabled`
- SMS service doesn't check `patient.patient_profile.sms_notifications_enabled`
- Reminder tasks don't check `patient.patient_profile.appointment_reminders_enabled`

**Files That Need Updates:**
1. `core/email_service.py` - All email functions
2. `core/sms_service.py` - SMS functions
3. `core/whatsapp_service.py` - WhatsApp functions
4. `appointments/tasks.py` - Reminder tasks

**Impact:** ⚠️ **HIGH** - Patients can't actually control their notifications

---

### **2. Session Recording Consent Not Enforced** ❌

**Problem:** The `telehealth_recording_consent` field exists, but there's no check to prevent recording when consent is not given.

**Current Behavior:**
- Recording consent is stored in database
- But video recording can still happen even if consent is `false`

**What's Missing:**
- Check `telehealth_recording_consent` before enabling recording in video sessions
- Prevent recording if consent is `false`
- Show warning/error if trying to record without consent

**Files That Need Updates:**
1. Video session endpoints/views
2. Twilio video room creation (if recording is enabled)
3. Frontend video component (should check consent)

**Impact:** ⚠️ **HIGH** - Privacy compliance issue

---

### **3. Progress Sharing Signal May Not Be Connected** ⚠️

**Problem:** Signal is created but may not be properly connected.

**What to Verify:**
- Signal is registered in `users/apps.py` ✅ (Done)
- Signal handler is correct ✅ (Done)
- But need to verify it actually triggers

**Files to Check:**
1. `users/apps.py` - Signal registration
2. `users/signals.py` - Signal handler
3. Test that signal actually fires when progress note is created

**Impact:** 🟡 **MEDIUM** - Feature may not work

---

## 📋 **Summary of Missing Checks**

### **Email Notifications**

**Files:** `core/email_service.py`

**Functions that need preference checks:**
- `send_appointment_confirmation()`
- `send_appointment_reminder_24h()`
- `send_meeting_link_reminder()`
- `send_appointment_cancellation()`
- `send_appointment_rescheduled()`

**Required Check:**
```python
# Before sending email
if hasattr(appointment.patient, 'patient_profile'):
    if not appointment.patient.patient_profile.email_notifications_enabled:
        return {'skipped': True, 'reason': 'Email notifications disabled by patient'}
```

---

### **SMS Notifications**

**Files:** `core/sms_service.py`, `core/whatsapp_service.py`

**Functions that need preference checks:**
- `send_sms_reminder()`
- `send_whatsapp_reminder()`

**Required Check:**
```python
# Before sending SMS/WhatsApp
if hasattr(appointment.patient, 'patient_profile'):
    if not appointment.patient.patient_profile.sms_notifications_enabled:
        return {'skipped': True, 'reason': 'SMS notifications disabled by patient'}
```

---

### **Appointment Reminders**

**Files:** `appointments/tasks.py`

**Tasks that need preference checks:**
- `send_24_hour_reminder()`
- `send_1_hour_reminder()`
- `send_15_minute_reminder()`

**Required Check:**
```python
# Before sending reminder
if hasattr(appointment.patient, 'patient_profile'):
    if not appointment.patient.patient_profile.appointment_reminders_enabled:
        return {'skipped': True, 'reason': 'Appointment reminders disabled by patient'}
```

---

### **Session Recording**

**Files:** Video session views/endpoints

**Required Check:**
```python
# Before enabling recording
if hasattr(appointment.patient, 'patient_profile'):
    if not appointment.patient.patient_profile.telehealth_recording_consent:
        # Disable recording or show error
        return {'error': 'Patient has not consented to session recording'}
```

---

## ✅ **What's Working**

1. ✅ **Preference Storage** - Fields exist in database
2. ✅ **Preference API** - Endpoint works for getting/setting preferences
3. ✅ **Progress Sharing Service** - Service exists and should work
4. ✅ **Signal Registration** - Signal is registered in apps.py

---

## 🔧 **Implementation Priority**

### **Priority 1 (Critical):**
1. **Notification Preference Checks** - Must respect patient preferences
2. **Recording Consent Enforcement** - Privacy compliance requirement

### **Priority 2 (Important):**
3. **Signal Testing** - Verify progress sharing actually works

---

## 📝 **Next Steps**

1. Add preference checks to all notification services
2. Add recording consent check to video session endpoints
3. Test progress sharing signal
4. Update documentation

---

**Last Updated:** 2025-01-19  
**Status:** ⚠️ **3 Items Need Implementation**

