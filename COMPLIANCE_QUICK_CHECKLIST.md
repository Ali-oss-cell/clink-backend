# 🇦🇺 Australian Legal Compliance - Quick Checklist

## 🚨 CRITICAL - Must Implement Before Launch

### 1. Privacy Act 1988 Compliance
- [ ] **Privacy Policy** created and published on website
- [ ] **Privacy Policy acceptance** tracked in database (add to PatientProfile)
- [ ] **Data access request** endpoint implemented (APP 12)
- [ ] **Data deletion request** endpoint implemented
- [ ] **Third-party data sharing** documented and disclosed (Twilio, Stripe)

### 2. Data Security
- [ ] **HTTPS/SSL** enabled in production (✅ Already configured)
- [ ] **Database encryption** at rest (implement)
- [ ] **File encryption** for uploaded documents (implement)
- [ ] **Two-factor authentication** for staff accounts (implement)
- [ ] **Regular security audits** scheduled

### 3. AHPRA Compliance
- [ ] **AHPRA expiry monitoring** (Celery task to check monthly)
- [ ] **Automatic suspension** when AHPRA expires
- [ ] **Expiry notifications** sent 30 days before expiry
- [ ] **AHPRA validation** on psychologist registration

### 4. Medicare Compliance
- [ ] **Session limit enforcement** (10 sessions/year per patient)
- [ ] **Referral requirement checking** (GP referral for Medicare)
- [ ] **Item number validation** (only valid MBS numbers)
- [ ] **Provider number verification** (all psychologists have valid numbers)

### 5. Informed Consent
- [ ] **Enhanced consent tracking** (version, date, signature)
- [ ] **Consent withdrawal** mechanism
- [ ] **Parental consent** for minors (under 18)
- [ ] **Telehealth-specific consent** form

---

## ⚠️ IMPORTANT - Implement Within 3 Months

### 6. Record Retention
- [ ] **Retention policy** defined (7 years for adults, until 25 for children)
- [ ] **Automatic cleanup** process (archive, don't delete)
- [ ] **Archive system** for old records

### 7. Data Breach Notification
- [ ] **Breach detection** system
- [ ] **Notification process** (patients within 30 days, OAIC within 72 hours)
- [ ] **Incident response plan** documented

### 8. Professional Indemnity Insurance
- [ ] **Insurance tracking** in PsychologistProfile
- [ ] **Expiry monitoring** (warnings 30 days before)
- [ ] **Verification process** (annual certificate checks)

### 9. Telehealth Compliance
- [ ] **Enhanced telehealth consent** form
- [ ] **Emergency procedures** documented
- [ ] **Technology requirements** guide for patients
- [ ] **Recording consent** (if applicable)

---

## ✅ ALREADY IMPLEMENTED

### What You Have:
- ✅ AHPRA registration number tracking
- ✅ AHPRA expiry date tracking
- ✅ Medicare item number support
- ✅ Medicare rebate calculations
- ✅ Medicare claim processing
- ✅ GST calculation (10%)
- ✅ GST breakdown in invoices
- ✅ ABN field in invoices
- ✅ Basic consent fields (treatment, telehealth)
- ✅ Audit logging system
- ✅ Role-based access control
- ✅ Secure authentication (JWT)
- ✅ HTTPS/SSL configuration

---

## 📋 Quick Implementation Guide

### Step 1: Privacy Policy Acceptance (30 minutes)
```python
# Add to users/models.py - PatientProfile
privacy_policy_accepted = models.BooleanField(default=False)
privacy_policy_accepted_date = models.DateTimeField(null=True, blank=True)
privacy_policy_version = models.CharField(max_length=20, blank=True)
```

### Step 2: AHPRA Expiry Monitoring (1 hour)
```python
# Add Celery task in appointments/tasks.py
@shared_task
def check_ahpra_expiry():
    # Check for expiring registrations
    # Send warnings
    # Suspend expired psychologists
```

### Step 3: Medicare Session Limits (1 hour)
```python
# Add to appointments/booking_views.py
def check_medicare_session_limit(patient, service):
    # Count sessions this year
    # Enforce 10 session limit
    # Return error if limit reached
```

### Step 4: Enhanced Consent (1 hour)
```python
# Update PatientProfile model
consent_to_treatment_version = models.CharField(max_length=20, blank=True)
consent_to_treatment_date = models.DateTimeField(null=True, blank=True)
consent_withdrawn = models.BooleanField(default=False)
parental_consent = models.BooleanField(default=False)  # For minors
```

### Step 5: Data Access Request (2 hours)
```python
# Create DataAccessRequest model
# Create API endpoint for patients to request their data
# Generate data export (JSON/PDF)
```

---

## 🔍 Compliance Audit Questions

### Before Launch, Answer These:

1. **Privacy**
   - [ ] Do you have a Privacy Policy?
   - [ ] Is it accessible to patients?
   - [ ] Do you track when patients accept it?
   - [ ] Can patients request their data?
   - [ ] Can patients delete their data?

2. **Security**
   - [ ] Is all data encrypted in transit?
   - [ ] Is all data encrypted at rest?
   - [ ] Do you have access controls?
   - [ ] Do you monitor for breaches?
   - [ ] Do you have a breach response plan?

3. **AHPRA**
   - [ ] Are all psychologists registered?
   - [ ] Are AHPRA numbers validated?
   - [ ] Are expiry dates tracked?
   - [ ] Do you check for expiring registrations?
   - [ ] Do you suspend expired psychologists?

4. **Medicare**
   - [ ] Are item numbers valid?
   - [ ] Are session limits enforced?
   - [ ] Are referrals checked?
   - [ ] Are rebates calculated correctly?
   - [ ] Are provider numbers valid?

5. **Consent**
   - [ ] Is consent obtained before treatment?
   - [ ] Is consent versioned?
   - [ ] Can consent be withdrawn?
   - [ ] Is parental consent obtained for minors?
   - [ ] Is telehealth consent separate?

6. **Records**
   - [ ] Do you have a retention policy?
   - [ ] Are records retained for 7 years?
   - [ ] Are child records retained until age 25?
   - [ ] Do you have an archive system?

---

## 📞 Who to Contact

### Legal Compliance
- **Healthcare Lawyer**: Review all compliance
- **Privacy Lawyer**: Review Privacy Policy
- **Tax Accountant**: Review GST/tax compliance

### Regulatory Bodies
- **AHPRA**: Registration questions
- **OAIC**: Privacy questions
- **Medicare**: Billing questions

### Professional Bodies
- **APS**: Professional standards
- **State Psychology Board**: State-specific requirements

---

## ⚠️ Legal Disclaimer

**This checklist is a guide only. You must consult with qualified legal professionals to ensure full compliance. Non-compliance can result in:**
- Fines and penalties
- Legal action
- Loss of registration
- Reputation damage
- Patient trust issues

---

## 📚 Full Documentation

See `AUSTRALIAN_LEGAL_COMPLIANCE_GUIDE.md` for complete details on:
- All 13 Australian Privacy Principles
- State-specific Health Records Acts
- Detailed implementation code
- Legal resources and links
- Compliance audit procedures

---

## 🎯 Priority Order

1. **Week 1**: Privacy Policy + Acceptance Tracking
2. **Week 2**: AHPRA Expiry Monitoring
3. **Week 3**: Medicare Session Limits
4. **Week 4**: Enhanced Consent + Data Access Requests
5. **Month 2**: Security Enhancements (encryption, 2FA)
6. **Month 3**: Record Retention + Data Breach Procedures

**Remember: Start with the critical items, then move to important items. Compliance is ongoing!**

