# 🇦🇺 Australian Legal Compliance Guide for Psychology Clinic

## Overview

This guide ensures your psychology clinic backend complies with all Australian legal requirements for healthcare providers. **Non-compliance can result in severe penalties, legal action, and loss of registration.**

---

## 📋 Table of Contents

1. [Privacy Act 1988 (Australian Privacy Principles)](#1-privacy-act-1988)
2. [AHPRA Registration & Compliance](#2-ahpra-compliance)
3. [Medicare Compliance](#3-medicare-compliance)
4. [Health Records Act (State-Specific)](#4-health-records-act)
5. [Data Security & Encryption](#5-data-security)
6. [Record Retention Requirements](#6-record-retention)
7. [Informed Consent](#7-informed-consent)
8. [Telehealth Regulations](#8-telehealth-compliance)
9. [Data Breach Notification](#9-data-breach-notification)
10. [Professional Indemnity Insurance](#10-professional-indemnity)
11. [GST & Tax Compliance](#11-gst-compliance)
12. [Implementation Checklist](#12-implementation-checklist)

---

## 1. Privacy Act 1988 (Australian Privacy Principles)

### ✅ Current Implementation Status

**What You Have:**
- ✅ Patient consent fields in `PatientProfile` model
- ✅ Audit logging for data access
- ✅ Role-based access control
- ✅ Secure authentication (JWT)

**What You Need to Add:**
- ⚠️ Privacy Policy acceptance tracking
- ⚠️ Data access request handling
- ⚠️ Data deletion request handling
- ⚠️ Third-party data sharing agreements
- ⚠️ Privacy impact assessments

### 📝 Required Implementation

#### 1.1 Privacy Policy Acceptance

**Add to User/PatientProfile Model:**
```python
# In users/models.py - PatientProfile
privacy_policy_accepted = models.BooleanField(default=False)
privacy_policy_accepted_date = models.DateTimeField(null=True, blank=True)
privacy_policy_version = models.CharField(max_length=20, blank=True)
```

#### 1.2 Data Access Requests (APP 12)

**Create New Model:**
```python
# In users/models.py
class DataAccessRequest(models.Model):
    """Handle patient requests to access their data (APP 12)"""
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    request_type = models.CharField(
        max_length=20,
        choices=[
            ('access', 'Access My Data'),
            ('correction', 'Correct My Data'),
            ('deletion', 'Delete My Data'),
        ]
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    completed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
```

#### 1.3 Third-Party Data Sharing Tracking

**Add to settings.py:**
```python
# Track all third-party services that receive patient data
THIRD_PARTY_DATA_SHARING = {
    'twilio': {
        'purpose': 'Video calls and SMS notifications',
        'data_shared': ['name', 'phone_number', 'email'],
        'location': 'United States',
        'safeguards': 'Encrypted transmission, GDPR compliant',
    },
    'stripe': {
        'purpose': 'Payment processing',
        'data_shared': ['name', 'email', 'payment_amount'],
        'location': 'United States',
        'safeguards': 'PCI DSS compliant',
    },
}
```

### 🔒 Australian Privacy Principles (APPs) Checklist

- [ ] **APP 1**: Open and transparent management of personal information
  - [ ] Privacy Policy published and accessible
  - [ ] Privacy Policy version tracked per user
  - [ ] Privacy Policy updated when practices change

- [ ] **APP 2**: Anonymity and pseudonymity
  - [ ] Option to use pseudonym where possible

- [ ] **APP 3**: Collection of solicited personal information
  - [ ] Only collect necessary information
  - [ ] Collect directly from individual where possible

- [ ] **APP 4**: Dealing with unsolicited personal information
  - [ ] Process for handling unsolicited information

- [ ] **APP 5**: Notification of collection
  - [ ] Notify patients when collecting information
  - [ ] Explain purpose of collection

- [ ] **APP 6**: Use or disclosure
  - [ ] Only use/disclose for primary purpose
  - [ ] Track all disclosures

- [ ] **APP 7**: Direct marketing
  - [ ] Opt-in consent for marketing
  - [ ] Easy opt-out mechanism

- [ ] **APP 8**: Cross-border disclosure
  - [ ] Notify patients if data sent overseas
  - [ ] Ensure overseas recipient has adequate protection

- [ ] **APP 9**: Adoption, use or disclosure of government identifiers
  - [ ] Don't use Medicare number as primary identifier

- [ ] **APP 10**: Quality of personal information
  - [ ] Ensure data is accurate and up-to-date

- [ ] **APP 11**: Security of personal information
  - [ ] Encrypt data at rest and in transit
  - [ ] Access controls
  - [ ] Regular security audits

- [ ] **APP 12**: Access to personal information
  - [ ] Provide access within 30 days
  - [ ] API endpoint for data export

- [ ] **APP 13**: Correction of personal information
  - [ ] Allow patients to correct their data
  - [ ] Notify third parties of corrections

---

## 2. AHPRA Compliance

### ✅ Current Implementation Status

**What You Have:**
- ✅ AHPRA registration number tracking in `PsychologistProfile`
- ✅ AHPRA expiry date tracking
- ✅ `is_ahpra_current` property to check validity

**What You Need to Add:**
- ⚠️ AHPRA expiry notifications
- ⚠️ Automatic suspension when AHPRA expires
- ⚠️ AHPRA registration verification
- ⚠️ Professional development tracking

### 📝 Required Implementation

#### 2.1 AHPRA Expiry Monitoring

**Add Celery Task:**
```python
# In appointments/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from services.models import PsychologistProfile

@shared_task
def check_ahpra_expiry():
    """Check for psychologists with expiring AHPRA registrations"""
    today = timezone.now().date()
    warning_date = today + timedelta(days=30)
    
    # Find psychologists with expiring registrations
    expiring = PsychologistProfile.objects.filter(
        ahpra_expiry_date__lte=warning_date,
        ahpra_expiry_date__gt=today,
        is_active_practitioner=True
    )
    
    for profile in expiring:
        # Send notification email
        send_ahpra_expiry_warning(profile)
    
    # Find expired registrations
    expired = PsychologistProfile.objects.filter(
        ahpra_expiry_date__lt=today,
        is_active_practitioner=True
    )
    
    for profile in expired:
        # Suspend psychologist
        profile.is_active_practitioner = False
        profile.save()
        # Cancel future appointments
        cancel_future_appointments(profile.user)
        send_ahpra_expired_notification(profile)
```

#### 2.2 AHPRA Registration Verification

**Add Validation:**
```python
# In services/models.py - PsychologistProfile
def validate_ahpra_registration(self):
    """Validate AHPRA registration number format"""
    # AHPRA format: Usually 8 digits or alphanumeric
    import re
    pattern = r'^[A-Z0-9]{6,10}$'
    if not re.match(pattern, self.ahpra_registration_number):
        raise ValidationError('Invalid AHPRA registration number format')
```

### 🔒 AHPRA Compliance Checklist

- [ ] **Registration Tracking**
  - [ ] All psychologists have AHPRA number
  - [ ] AHPRA expiry dates are current
  - [ ] Automatic expiry checking (30 days warning)

- [ ] **Practice Restrictions**
  - [ ] Psychologists with expired AHPRA cannot see patients
  - [ ] Future appointments cancelled when AHPRA expires
  - [ ] Clear notification to patients

- [ ] **Professional Standards**
  - [ ] Code of conduct compliance
  - [ ] Continuing professional development tracking
  - [ ] Professional indemnity insurance verification

---

## 3. Medicare Compliance

### ✅ Current Implementation Status

**What You Have:**
- ✅ Medicare item number tracking
- ✅ Medicare rebate calculations
- ✅ Medicare claim processing
- ✅ Medicare Safety Net tracking
- ✅ Provider number tracking

**What You Need to Add:**
- ⚠️ Medicare item number validation
- ⚠️ Session limit enforcement (10 sessions/year)
- ⚠️ Referral requirement checking
- ⚠️ Bulk billing support

### 📝 Required Implementation

#### 3.1 Session Limit Enforcement

**Add to Appointment Booking:**
```python
# In appointments/booking_views.py
def check_medicare_session_limit(patient, service):
    """Check if patient has reached Medicare session limit"""
    from django.utils import timezone
    from billing.models import MedicareClaim
    
    current_year = timezone.now().year
    item_number = service.medicare_item_number
    
    if not item_number:
        return True, None
    
    # Get Medicare item number model
    from billing.models import MedicareItemNumber
    try:
        medicare_item = MedicareItemNumber.objects.get(
            item_number=item_number
        )
    except MedicareItemNumber.DoesNotExist:
        return True, None
    
    # Count sessions this year
    sessions_this_year = MedicareClaim.objects.filter(
        patient=patient,
        medicare_item_number=medicare_item,
        claim_date__year=current_year,
        status__in=['approved', 'paid']
    ).count()
    
    if sessions_this_year >= medicare_item.max_sessions_per_year:
        return False, f"Medicare limit reached ({medicare_item.max_sessions_per_year} sessions/year)"
    
    return True, None
```

#### 3.2 Referral Requirement Checking

**Add Validation:**
```python
# In appointments/booking_views.py
def validate_medicare_referral(patient, service):
    """Validate GP referral for Medicare-eligible services"""
    from billing.models import MedicareItemNumber
    
    item_number = service.medicare_item_number
    if not item_number:
        return True, None
    
    try:
        medicare_item = MedicareItemNumber.objects.get(
            item_number=item_number
        )
    except MedicareItemNumber.DoesNotExist:
        return True, None
    
    if medicare_item.requires_referral:
        # Check if patient has GP referral
        patient_profile = patient.patient_profile
        if not patient_profile.has_gp_referral:
            return False, "GP referral required for Medicare rebate"
        
        # Check referral is still valid (usually 12 months)
        # Add referral_date field to PatientProfile if not exists
    
    return True, None
```

### 🔒 Medicare Compliance Checklist

- [ ] **Item Number Validation**
  - [ ] Only valid MBS item numbers used
  - [ ] Item numbers match service type
  - [ ] Item numbers are current (not obsolete)

- [ ] **Session Limits**
  - [ ] Enforce 10 sessions per calendar year limit
  - [ ] Track sessions per patient per year
  - [ ] Warn when approaching limit

- [ ] **Referral Requirements**
  - [ ] Check for GP referral when required
  - [ ] Validate referral is current (within 12 months)
  - [ ] Store referral details

- [ ] **Billing Accuracy**
  - [ ] Correct rebate amounts
  - [ ] Safety net calculations
  - [ ] Out-of-pocket calculations

- [ ] **Provider Numbers**
  - [ ] All psychologists have provider numbers
  - [ ] Provider numbers are valid
  - [ ] Provider numbers match service location

---

## 4. Health Records Act (State-Specific)

### 📍 State-Specific Requirements

#### Victoria - Health Records Act 2001
- [ ] Health Privacy Principles (HPPs) compliance
- [ ] Patient access to health records
- [ ] Record retention: 7 years for adults, until age 25 for children
- [ ] Secure storage requirements

#### New South Wales - Health Records and Information Privacy Act 2002
- [ ] Health Privacy Principles compliance
- [ ] Patient access rights
- [ ] Record retention: 7 years minimum

#### Queensland - Information Privacy Act 2009
- [ ] National Privacy Principles
- [ ] Health information handling
- [ ] Record retention: 7 years

#### Other States
- [ ] Check state-specific requirements
- [ ] Implement state-specific privacy principles

### 📝 Required Implementation

#### 4.1 Record Retention Policy

**Add to settings.py:**
```python
# Record Retention Policy (years)
RECORD_RETENTION_POLICY = {
    'adult_patient_records': 7,  # Years after last contact
    'child_patient_records': 25,  # Until age 25
    'financial_records': 7,  # Years
    'audit_logs': 7,  # Years
    'appointment_records': 7,  # Years
}
```

#### 4.2 Automatic Record Deletion

**Add Celery Task:**
```python
# In appointments/tasks.py
@shared_task
def cleanup_expired_records():
    """Delete records past retention period"""
    from django.utils import timezone
    from datetime import timedelta
    from users.models import PatientProfile, ProgressNote
    
    retention_years = settings.RECORD_RETENTION_POLICY['adult_patient_records']
    cutoff_date = timezone.now() - timedelta(days=retention_years * 365)
    
    # Find patients with no activity after cutoff
    inactive_patients = User.objects.filter(
        role=User.UserRole.PATIENT,
        patient_appointments__appointment_date__lt=cutoff_date
    ).distinct()
    
    # Archive or delete (check legal requirements first!)
    # Note: May need to archive instead of delete for legal reasons
```

---

## 5. Data Security

### ✅ Current Implementation Status

**What You Have:**
- ✅ HTTPS/SSL in production
- ✅ JWT authentication
- ✅ Role-based access control
- ✅ Password hashing (Django default)

**What You Need to Add:**
- ⚠️ Data encryption at rest
- ⚠️ Database encryption
- ⚠️ File encryption for uploaded documents
- ⚠️ Regular security audits
- ⚠️ Two-factor authentication (2FA)
- ⚠️ IP whitelisting for admin access

### 📝 Required Implementation

#### 5.1 Database Encryption

**Add to settings.py:**
```python
# Database encryption (use encrypted database or field-level encryption)
# For PostgreSQL with pgcrypto:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'OPTIONS': {
#             'options': '-c default_transaction_isolation=serializable'
#         },
#     }
# }

# For sensitive fields, use django-encrypted-model-fields
# INSTALLED_APPS += ['encrypted_model_fields']
```

#### 5.2 File Encryption

**Add to models with file uploads:**
```python
# Use encrypted storage for sensitive files
from django.core.files.storage import FileSystemStorage
from encrypted_model_fields.fields import EncryptedCharField

class EncryptedFileField(models.FileField):
    """File field with encryption"""
    # Implement encryption wrapper
    pass
```

#### 5.3 Two-Factor Authentication

**Install django-otp:**
```bash
pip install django-otp qrcode
```

**Add to settings.py:**
```python
INSTALLED_APPS += [
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
]

MIDDLEWARE += [
    'django_otp.middleware.OTPMiddleware',
]
```

### 🔒 Data Security Checklist

- [ ] **Encryption**
  - [ ] Data encrypted in transit (HTTPS/TLS)
  - [ ] Data encrypted at rest (database encryption)
  - [ ] File uploads encrypted
  - [ ] Backup encryption

- [ ] **Access Control**
  - [ ] Strong password requirements
  - [ ] Two-factor authentication for staff
  - [ ] Role-based access control
  - [ ] IP whitelisting for admin

- [ ] **Monitoring**
  - [ ] Failed login attempt tracking
  - [ ] Unusual access pattern detection
  - [ ] Regular security audits
  - [ ] Intrusion detection

- [ ] **Backup & Recovery**
  - [ ] Regular encrypted backups
  - [ ] Off-site backup storage
  - [ ] Disaster recovery plan
  - [ ] Backup testing

---

## 6. Record Retention

### 📝 Required Implementation

#### 6.1 Retention Policy Model

**Add to users/models.py:**
```python
class RecordRetentionPolicy(models.Model):
    """Track record retention requirements"""
    record_type = models.CharField(max_length=50, unique=True)
    retention_years = models.PositiveIntegerField()
    retention_until_age = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="For children, retain until this age"
    )
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.record_type}: {self.retention_years} years"
```

### 🔒 Record Retention Checklist

- [ ] **Adult Records**: 7 years after last contact
- [ ] **Child Records**: Until age 25
- [ ] **Financial Records**: 7 years
- [ ] **Audit Logs**: 7 years minimum
- [ ] **Appointment Records**: 7 years
- [ ] **Progress Notes**: 7 years (or until age 25 for children)
- [ ] **Invoices**: 7 years (tax requirement)
- [ ] **Medicare Claims**: 7 years

---

## 7. Informed Consent

### ✅ Current Implementation Status

**What You Have:**
- ✅ `consent_to_treatment` field
- ✅ `consent_to_telehealth` field
- ✅ `consent_date` field
- ✅ `client_signature` field

**What You Need to Add:**
- ⚠️ Consent version tracking
- ⚠️ Consent withdrawal mechanism
- ⚠️ Detailed consent documentation
- ⚠️ Parental consent for minors

### 📝 Required Implementation

#### 7.1 Enhanced Consent Model

**Update PatientProfile:**
```python
# In users/models.py - PatientProfile
consent_to_treatment = models.BooleanField(default=False)
consent_to_treatment_date = models.DateTimeField(null=True, blank=True)
consent_to_treatment_version = models.CharField(max_length=20, blank=True)

consent_to_telehealth = models.BooleanField(default=False)
consent_to_telehealth_date = models.DateTimeField(null=True, blank=True)
consent_to_telehealth_version = models.CharField(max_length=20, blank=True)

consent_to_data_sharing = models.BooleanField(default=False)
consent_to_data_sharing_date = models.DateTimeField(null=True, blank=True)

consent_to_marketing = models.BooleanField(default=False)
consent_to_marketing_date = models.DateTimeField(null=True, blank=True)

consent_withdrawn = models.BooleanField(default=False)
consent_withdrawn_date = models.DateTimeField(null=True, blank=True)
consent_withdrawal_reason = models.TextField(blank=True)

# For minors
parental_consent = models.BooleanField(default=False)
parental_consent_name = models.CharField(max_length=255, blank=True)
parental_consent_date = models.DateTimeField(null=True, blank=True)
parental_consent_signature = models.CharField(max_length=255, blank=True)
```

### 🔒 Informed Consent Checklist

- [ ] **Treatment Consent**
  - [ ] Obtained before first session
  - [ ] Version tracked
  - [ ] Date recorded
  - [ ] Signature captured

- [ ] **Telehealth Consent**
  - [ ] Separate consent for video calls
  - [ ] Risks explained
  - [ ] Technology requirements explained

- [ ] **Data Sharing Consent**
  - [ ] Third-party sharing explained
  - [ ] Opt-in required
  - [ ] Easy opt-out mechanism

- [ ] **Marketing Consent**
  - [ ] Opt-in only
  - [ ] Easy unsubscribe
  - [ ] Separate from treatment consent

- [ ] **Minors**
  - [ ] Parental consent required
  - [ ] Age verification
  - [ ] Consent from both parents if applicable

---

## 8. Telehealth Compliance

### ✅ Current Implementation Status

**What You Have:**
- ✅ Telehealth session type support
- ✅ Video call integration (Twilio)
- ✅ Consent to telehealth field

**What You Need to Add:**
- ⚠️ Telehealth-specific consent form
- ⚠️ Technology requirements documentation
- ⚠️ Emergency procedures for telehealth
- ⚠️ Recording consent (if applicable)

### 📝 Required Implementation

#### 8.1 Telehealth Consent Form

**Create TelehealthConsent Model:**
```python
# In appointments/models.py
class TelehealthConsent(models.Model):
    """Detailed telehealth consent"""
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    
    # Technology
    understands_technology_requirements = models.BooleanField(default=False)
    has_adequate_internet = models.BooleanField(default=False)
    has_private_location = models.BooleanField(default=False)
    
    # Risks
    understands_technical_failures = models.BooleanField(default=False)
    understands_privacy_risks = models.BooleanField(default=False)
    understands_emergency_limitations = models.BooleanField(default=False)
    
    # Emergency
    emergency_contact_provided = models.BooleanField(default=False)
    understands_emergency_procedures = models.BooleanField(default=False)
    
    # Recording
    consent_to_recording = models.BooleanField(default=False)
    recording_purpose = models.TextField(blank=True)
    
    consent_date = models.DateTimeField(auto_now_add=True)
    signature = models.CharField(max_length=255)
```

### 🔒 Telehealth Compliance Checklist

- [ ] **Technology Requirements**
  - [ ] Minimum internet speed documented
  - [ ] Device requirements explained
  - [ ] Software requirements provided

- [ ] **Privacy & Security**
  - [ ] Encrypted video platform (Twilio ✅)
  - [ ] Secure connection required
  - [ ] Private location recommended

- [ ] **Emergency Procedures**
  - [ ] Emergency contact on file
  - [ ] Local emergency services contact info
  - [ ] Procedure for technical failures

- [ ] **Recording**
  - [ ] Explicit consent for recording
  - [ ] Purpose of recording explained
  - [ ] Storage and retention policy

- [ ] **Medicare Requirements**
  - [ ] Telehealth item numbers used correctly
  - [ ] Session duration requirements met
  - [ ] Appropriate for patient condition

---

## 9. Data Breach Notification

### 📝 Required Implementation

#### 9.1 Data Breach Model

**Create DataBreach Model:**
```python
# In users/models.py
class DataBreach(models.Model):
    """Track data breaches for notification requirements"""
    breach_date = models.DateTimeField()
    discovered_date = models.DateTimeField(auto_now_add=True)
    breach_type = models.CharField(
        max_length=50,
        choices=[
            ('unauthorized_access', 'Unauthorized Access'),
            ('data_loss', 'Data Loss'),
            ('cyber_attack', 'Cyber Attack'),
            ('human_error', 'Human Error'),
            ('system_failure', 'System Failure'),
        ]
    )
    affected_patients = models.ManyToManyField(User, blank=True)
    data_types_affected = models.TextField()
    severity = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('critical', 'Critical'),
        ]
    )
    description = models.TextField()
    containment_action = models.TextField()
    notification_sent = models.BooleanField(default=False)
    notification_date = models.DateTimeField(null=True, blank=True)
    oaic_notified = models.BooleanField(default=False)  # OAIC = Office of Australian Information Commissioner
    oaic_notification_date = models.DateTimeField(null=True, blank=True)
    resolved = models.BooleanField(default=False)
    resolved_date = models.DateTimeField(null=True, blank=True)
```

#### 9.2 Breach Notification Process

**Add to views:**
```python
# In users/views.py
def notify_data_breach(breach):
    """Notify affected patients and OAIC of data breach"""
    from django.utils import timezone
    
    # Notify affected patients within 30 days
    for patient in breach.affected_patients.all():
        send_breach_notification_email(patient, breach)
    
    # Notify OAIC if serious breach (within 72 hours)
    if breach.severity in ['high', 'critical']:
        notify_oaic(breach)
        breach.oaic_notified = True
        breach.oaic_notification_date = timezone.now()
    
    breach.notification_sent = True
    breach.notification_date = timezone.now()
    breach.save()
```

### 🔒 Data Breach Notification Checklist

- [ ] **Detection**
  - [ ] Monitoring system in place
  - [ ] Incident response plan
  - [ ] Breach assessment process

- [ ] **Notification**
  - [ ] Notify affected patients within 30 days
  - [ ] Notify OAIC within 72 hours (serious breaches)
  - [ ] Document all notifications

- [ ] **Containment**
  - [ ] Immediate containment actions
  - [ ] Prevent further breaches
  - [ ] Secure affected systems

- [ ] **Remediation**
  - [ ] Fix vulnerabilities
  - [ ] Improve security measures
  - [ ] Update policies

---

## 10. Professional Indemnity Insurance

### 📝 Required Implementation

#### 10.1 Insurance Tracking Model

**Add to PsychologistProfile:**
```python
# In services/models.py - PsychologistProfile
professional_indemnity_insurance = models.BooleanField(default=False)
insurance_provider = models.CharField(max_length=200, blank=True)
insurance_policy_number = models.CharField(max_length=100, blank=True)
insurance_expiry_date = models.DateField(null=True, blank=True)
insurance_coverage_amount = models.DecimalField(
    max_digits=12,
    decimal_places=2,
    null=True,
    blank=True,
    help_text="Coverage amount in AUD"
)

@property
def is_insurance_current(self):
    """Check if professional indemnity insurance is current"""
    if not self.professional_indemnity_insurance:
        return False
    if self.insurance_expiry_date:
        return self.insurance_expiry_date >= timezone.now().date()
    return True
```

### 🔒 Professional Indemnity Checklist

- [ ] **Insurance Requirements**
  - [ ] All psychologists have current insurance
  - [ ] Minimum coverage: $10M (check AHPRA requirements)
  - [ ] Insurance expiry tracked
  - [ ] Automatic expiry warnings

- [ ] **Verification**
  - [ ] Insurance certificates on file
  - [ ] Regular verification (annual)
  - [ ] Suspension if insurance lapses

---

## 11. GST & Tax Compliance

### ✅ Current Implementation Status

**What You Have:**
- ✅ GST calculation (10%)
- ✅ GST breakdown in invoices
- ✅ ABN field in invoices

**What You Need to Add:**
- ⚠️ GST registration verification
- ⚠️ Tax invoice requirements
- ⚠️ BAS (Business Activity Statement) reporting

### 📝 Required Implementation

#### 11.1 Tax Invoice Requirements

**Ensure invoices include:**
- [ ] ABN (Australian Business Number)
- [ ] "Tax Invoice" label
- [ ] GST amount clearly shown
- [ ] GST-inclusive total
- [ ] Business name and address
- [ ] Invoice date
- [ ] Description of services

**Current Invoice Model ✅ Already includes these**

#### 11.2 GST Registration

**Add to settings.py:**
```python
# GST Configuration
GST_REGISTERED = config('GST_REGISTERED', default=True, cast=bool)
ABN = config('ABN', default='')
GST_NUMBER = config('GST_NUMBER', default='')
```

### 🔒 GST & Tax Compliance Checklist

- [ ] **GST Registration**
  - [ ] Registered for GST (if turnover > $75k)
  - [ ] ABN displayed on invoices
  - [ ] GST number (if applicable)

- [ ] **Tax Invoices**
  - [ ] All invoices are tax invoices
  - [ ] GST amount shown separately
  - [ ] GST-inclusive pricing
  - [ ] ABN included

- [ ] **Record Keeping**
  - [ ] All invoices retained (7 years)
  - [ ] BAS records maintained
  - [ ] Financial records accurate

---

## 12. Implementation Checklist

### 🔴 Critical (Must Implement Before Launch)

- [ ] **Privacy Compliance**
  - [ ] Privacy Policy created and published
  - [ ] Privacy Policy acceptance tracked
  - [ ] Data access request system
  - [ ] Data deletion request system

- [ ] **Security**
  - [ ] HTTPS/SSL enabled in production
  - [ ] Database encryption
  - [ ] File encryption for sensitive documents
  - [ ] Two-factor authentication for staff

- [ ] **AHPRA**
  - [ ] AHPRA expiry monitoring
  - [ ] Automatic suspension on expiry
  - [ ] Expiry notifications

- [ ] **Medicare**
  - [ ] Session limit enforcement
  - [ ] Referral requirement checking
  - [ ] Item number validation

- [ ] **Consent**
  - [ ] Enhanced consent tracking
  - [ ] Consent versioning
  - [ ] Consent withdrawal mechanism

### 🟡 Important (Implement Within 3 Months)

- [ ] **Record Retention**
  - [ ] Retention policy implemented
  - [ ] Automatic cleanup process
  - [ ] Archive system

- [ ] **Data Breach**
  - [ ] Breach detection system
  - [ ] Notification process
  - [ ] Incident response plan

- [ ] **Telehealth**
  - [ ] Enhanced telehealth consent
  - [ ] Emergency procedures documented
  - [ ] Technology requirements guide

- [ ] **Professional Indemnity**
  - [ ] Insurance tracking
  - [ ] Expiry monitoring
  - [ ] Verification process

### 🟢 Recommended (Implement Within 6 Months)

- [ ] **Advanced Security**
  - [ ] IP whitelisting
  - [ ] Advanced monitoring
  - [ ] Penetration testing

- [ ] **Compliance Reporting**
  - [ ] Compliance dashboard
  - [ ] Regular audits
  - [ ] Compliance reports

---

## 📚 Legal Resources

### Key Legislation
- **Privacy Act 1988 (Cth)**: https://www.oaic.gov.au/privacy/privacy-legislation
- **Health Records Act 2001 (Vic)**: https://www.health.vic.gov.au/health-privacy
- **AHPRA Guidelines**: https://www.ahpra.gov.au/
- **Medicare Benefits Schedule**: https://www.mbsonline.gov.au/

### Regulatory Bodies
- **OAIC** (Office of Australian Information Commissioner): https://www.oaic.gov.au/
- **AHPRA** (Australian Health Practitioner Regulation Agency): https://www.ahpra.gov.au/
- **Medicare Australia**: https://www.servicesaustralia.gov.au/medicare

### Professional Bodies
- **APS** (Australian Psychological Society): https://www.psychology.org.au/
- **AHPRA Psychology Board**: https://www.psychologyboard.gov.au/

---

## ⚠️ Legal Disclaimer

**This guide is for informational purposes only and does not constitute legal advice. You must consult with a qualified legal professional specializing in Australian healthcare law to ensure full compliance with all applicable regulations.**

**Key Recommendations:**
1. **Engage a healthcare lawyer** to review your compliance
2. **Consult with AHPRA** for registration requirements
3. **Review OAIC guidelines** for privacy compliance
4. **Regular compliance audits** (annual minimum)
5. **Keep up-to-date** with changing regulations

---

## 📞 Support & Questions

For questions about this compliance guide:
1. Review the specific section above
2. Consult the legal resources listed
3. Engage a qualified legal professional
4. Contact relevant regulatory bodies

**Remember: Compliance is an ongoing process, not a one-time task!**

