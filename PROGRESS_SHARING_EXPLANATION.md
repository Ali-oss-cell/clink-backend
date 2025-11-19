# Progress Sharing with Emergency Contact - How It Works

## 📋 Current Status

### ✅ What's Implemented

1. **Consent/Preference Field**
   - `share_progress_with_emergency_contact` - Boolean field in PatientProfile
   - Consent date and version tracking
   - Can be toggled via `/api/auth/preferences/` endpoint

2. **Emergency Contact Information**
   - Stored in PatientProfile: `emergency_contact_name`, `emergency_contact_phone`, `emergency_contact_relationship`

### ❌ What's Missing

**The actual sharing functionality is NOT yet implemented.** Currently, the system only stores the consent preference, but doesn't actually send progress updates to emergency contacts.

---

## 🔄 How It Should Work (When Fully Implemented)

### **Step-by-Step Flow:**

```
1. Patient enables sharing
   ↓
   Patient goes to Settings → Preferences
   Toggles "Share progress with emergency contact" = ON
   ↓
   Consent is saved with date/version
   
2. Psychologist creates progress note
   ↓
   After session, psychologist writes progress note
   Progress note is saved to database
   ↓
   System checks: Does patient have sharing enabled?
   ↓
   YES → Trigger sharing task
   NO → Skip sharing
   
3. System shares progress (if consent given)
   ↓
   Create summary (non-sensitive info only)
   Send email/SMS to emergency contact
   Log sharing activity
```

---

## 📧 What Gets Shared

### **Information Included:**
- ✅ Patient name
- ✅ Session date
- ✅ Progress rating (1-10)
- ✅ General update summary (from subjective field, limited to 200 chars)
- ✅ Next steps (from plan field, limited to 200 chars)

### **Information NOT Shared:**
- ❌ Full progress note details
- ❌ Sensitive clinical information
- ❌ Assessment details
- ❌ Specific symptoms or diagnoses
- ❌ Psychologist's clinical impressions

### **Example Email/SMS:**

```
Progress Update for John Smith

Session Date: January 19, 2025
Progress Rating: 7/10

General Update:
John reports feeling more confident in social situations. He has been practicing the techniques discussed in previous sessions and notices improvement in managing anxiety.

Next Steps:
Continue practicing relaxation techniques. Next session scheduled for February 2, 2025. Focus on building on current progress.

---
This is an automated update. If you have concerns, please contact the clinic directly.
```

---

## 🔧 Implementation Needed

To make this feature fully functional, we need:

### **1. Progress Sharing Service**

**File:** `core/progress_sharing_service.py` (NEW)

```python
def share_progress_with_emergency_contact(progress_note):
    """
    Share progress note summary with emergency contact
    
    Args:
        progress_note: ProgressNote instance
    
    Returns:
        dict: Sharing result
    """
    patient = progress_note.patient
    patient_profile = patient.patient_profile
    
    # Check consent
    if not patient_profile.share_progress_with_emergency_contact:
        return {'shared': False, 'reason': 'Patient has not consented'}
    
    # Check if emergency contact exists
    if not patient_profile.emergency_contact_name or not patient_profile.emergency_contact_phone:
        return {'shared': False, 'reason': 'Emergency contact not provided'}
    
    # Create summary (non-sensitive)
    summary = create_progress_summary(progress_note)
    
    # Send via email or SMS
    result = send_progress_update(
        emergency_contact_name=patient_profile.emergency_contact_name,
        emergency_contact_phone=patient_profile.emergency_contact_phone,
        patient_name=patient.get_full_name(),
        summary=summary
    )
    
    return result
```

### **2. Automatic Trigger**

**Option A: Signal (Automatic)**
- When progress note is created, automatically check consent and share

**Option B: Celery Task (Scheduled)**
- Run periodically to share recent progress notes

**Option C: Manual Trigger**
- Psychologist can manually trigger sharing when creating note

---

## 🎯 Recommended Implementation

### **Automatic Sharing via Signal**

**Best approach:** Use Django signals to automatically share when progress note is created.

**Advantages:**
- ✅ Automatic - no manual action needed
- ✅ Immediate - shares right after note is created
- ✅ Reliable - always runs when note is saved

**Implementation:**
1. Create signal handler in `users/signals.py`
2. Connect to `post_save` signal for ProgressNote
3. Check consent before sharing
4. Send email/SMS to emergency contact

---

## 🔒 Privacy & Compliance

### **Privacy Act 1988 Compliance**

**APP 6 - Use/Disclosure:**
- ✅ Explicit consent required (opt-in only)
- ✅ Consent can be withdrawn anytime
- ✅ Limited information shared (summary only)
- ✅ Consent version tracked

**APP 7 - Direct Marketing:**
- ✅ Not marketing - this is health information sharing
- ✅ Patient-initiated consent
- ✅ Can opt-out anytime

### **Best Practices:**
1. **Opt-in Only** - Default is `false`
2. **Limited Information** - Only share summaries, not full notes
3. **Easy Withdrawal** - Patient can disable anytime
4. **Audit Trail** - Log when sharing occurs
5. **Secure Delivery** - Use encrypted email/SMS

---

## 📝 Example Implementation

See the next section for the actual code implementation.

---

## ❓ FAQ

### **Q: When does sharing happen?**
A: When a progress note is created AND the patient has consented to sharing.

### **Q: What if patient withdraws consent?**
A: Future progress notes won't be shared. Past shares are not retracted (they were sent with valid consent).

### **Q: Can emergency contact reply?**
A: The update is one-way. Emergency contact should contact the clinic directly if needed.

### **Q: What if emergency contact info changes?**
A: Patient should update their emergency contact info in their profile. New updates will go to the new contact.

### **Q: Is this HIPAA/Privacy Act compliant?**
A: Yes, as long as:
- Patient explicitly consents
- Only non-sensitive summaries are shared
- Consent can be withdrawn
- Sharing is logged

---

**Last Updated:** 2025-01-19  
**Status:** ⚠️ Consent exists, sharing functionality needs implementation

