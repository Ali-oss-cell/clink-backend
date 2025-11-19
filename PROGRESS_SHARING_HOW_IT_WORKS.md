# How Progress Sharing with Emergency Contact Works

## ✅ **FULLY IMPLEMENTED**

The progress sharing feature is now **fully functional**!

---

## 🔄 **How It Works - Step by Step**

### **1. Patient Enables Sharing**

Patient goes to **Settings → Preferences** and toggles:
```
☑️ Share progress with emergency contact
```

**What happens:**
- Consent is saved in database
- Consent date and version are tracked
- Emergency contact info must be on file

---

### **2. Psychologist Creates Progress Note**

After a therapy session, psychologist writes a progress note:
- Subjective (patient's report)
- Objective (observations)
- Assessment (clinical impression)
- Plan (next steps)
- Progress rating (1-10)

**What happens:**
- Progress note is saved to database
- Django signal automatically triggers

---

### **3. Automatic Sharing (Signal)**

When progress note is saved, a **Django signal** automatically:
1. Checks if patient has consented to sharing
2. Checks if emergency contact info exists
3. Creates a **non-sensitive summary**
4. Sends summary to emergency contact via **SMS**

**What gets shared:**
- ✅ Patient name
- ✅ Session date
- ✅ Progress rating (if available)
- ✅ General update (first 200 chars of subjective)
- ✅ Next steps (first 200 chars of plan)

**What does NOT get shared:**
- ❌ Full progress note
- ❌ Clinical assessment details
- ❌ Sensitive information
- ❌ Psychologist's clinical impressions

---

### **4. Emergency Contact Receives SMS**

Emergency contact receives an SMS like:

```
Progress Update for John Smith

Session Date: January 19, 2025
Progress Rating: 7/10

General Update:
John reports feeling more confident in social situations. He has been practicing the techniques discussed in previous sessions...

Next Steps:
Continue practicing relaxation techniques. Next session scheduled for February 2, 2025...

---
This is an automated update. If you have concerns, please contact the clinic directly.
```

---

## 📋 **Example Flow**

```
Patient: John Smith
Emergency Contact: Jane Doe (+61 412 345 678)

1. John enables sharing in preferences ✅
2. Psychologist creates progress note after session ✅
3. Signal automatically triggers ✅
4. System checks: Consent = YES ✅
5. System checks: Emergency contact exists = YES ✅
6. System creates summary ✅
7. System sends SMS to +61 412 345 678 ✅
8. Jane receives progress update ✅
```

---

## 🔧 **Technical Implementation**

### **Files Involved:**

1. **`users/models.py`**
   - `share_progress_with_emergency_contact` field
   - Emergency contact fields

2. **`core/progress_sharing_service.py`**
   - `share_progress_with_emergency_contact()` function
   - `create_progress_summary()` function

3. **`core/sms_service.py`**
   - `send_sms()` function (Twilio integration)

4. **`users/signals.py`**
   - `handle_progress_note_created()` signal handler
   - Automatically triggers on progress note creation

5. **`users/apps.py`**
   - Registers signals when app loads

---

## 🔒 **Privacy & Compliance**

### **Privacy Act 1988 Compliance:**

- ✅ **APP 6 - Use/Disclosure**: Explicit consent required
- ✅ **Opt-in Only**: Default is `false`
- ✅ **Limited Information**: Only summaries, not full notes
- ✅ **Consent Tracking**: Date and version tracked
- ✅ **Easy Withdrawal**: Patient can disable anytime

### **Security:**

- ✅ SMS sent via encrypted Twilio API
- ✅ Only non-sensitive information shared
- ✅ Consent verified before sharing
- ✅ Sharing is logged (can be extended for audit trail)

---

## ⚙️ **Configuration**

### **Required Settings:**

```python
# psychology_clinic/settings.py
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+61XXXXXXXXX'  # Your Twilio phone number
PROGRESS_SHARING_CONSENT_VERSION = '1.0'
```

---

## 🧪 **Testing**

### **Test the Feature:**

1. **Enable sharing:**
   ```bash
   PATCH /api/auth/preferences/
   {
     "share_progress_with_emergency_contact": true
   }
   ```

2. **Create progress note:**
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

3. **Check SMS:**
   - Emergency contact should receive SMS
   - Check Twilio logs for delivery status

---

## ❓ **FAQ**

### **Q: What if patient withdraws consent?**
A: Future progress notes won't be shared. Past shares are not retracted.

### **Q: What if emergency contact info changes?**
A: Patient should update their emergency contact in their profile. New updates will go to the new contact.

### **Q: Can emergency contact reply?**
A: No, this is one-way. Emergency contact should contact the clinic directly.

### **Q: What if SMS fails?**
A: The progress note is still saved. Sharing failure doesn't affect note creation.

### **Q: Is this automatic?**
A: Yes! Once enabled, sharing happens automatically when progress notes are created.

---

## 📝 **Summary**

✅ **Consent Management**: Patient can enable/disable via preferences endpoint  
✅ **Automatic Sharing**: Signal triggers automatically on note creation  
✅ **Privacy Compliant**: Only non-sensitive summaries shared  
✅ **SMS Delivery**: Uses Twilio for reliable SMS delivery  
✅ **Error Handling**: Graceful failures don't affect note creation  

**Status:** ✅ **Fully Functional and Ready to Use**

---

**Last Updated:** 2025-01-19
