"""
Custom User models for Psychology Clinic
Supports role-based access for Australian healthcare compliance
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from .managers import UserManager


class User(AbstractUser):
    """
    Custom User model with role-based permissions for psychology clinic
    
    Extends Django's AbstractUser to support multiple user types:
    - Patients: Can book appointments, complete intake forms
    - Psychologists: Can manage appointments, write progress notes
    - Practice Managers: Can manage all clinic operations
    - Admins: Full system access
    """
    
    class UserRole(models.TextChoices):
        """User role choices for the psychology clinic"""
        PATIENT = 'patient', 'Patient'
        PSYCHOLOGIST = 'psychologist', 'Psychologist'
        PRACTICE_MANAGER = 'practice_manager', 'Practice Manager'
        ADMIN = 'admin', 'Admin'
    
    # Basic Information
    email = models.EmailField(
        unique=True,
        help_text="Primary email address for login and communication"
    )
    
    # Australian phone number validation
    phone_regex = RegexValidator(
        regex=r'^\+?61[0-9]{9}$|^0[0-9]{9}$',
        message="Phone number must be in Australian format: +61XXXXXXXXX or 0XXXXXXXXX"
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=15, 
        blank=True,
        help_text="Australian phone number format (+61XXXXXXXXX or 0XXXXXXXXX)"
    )
    
    # Role and Status
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PATIENT,
        help_text="User role determines dashboard access and permissions"
    )
    
    is_verified = models.BooleanField(
        default=False,
        help_text="Email verification status - required for full system access"
    )
    
    # Welcome email tracking
    welcome_email_sent = models.BooleanField(default=False, help_text="Whether welcome email was successfully sent")
    welcome_email_sent_at = models.DateTimeField(null=True, blank=True, help_text="When welcome email was sent")
    welcome_email_attempts = models.IntegerField(default=0, help_text="Number of attempts to send welcome email")
    welcome_email_last_error = models.TextField(blank=True, null=True, help_text="Last error when sending welcome email")
    
    # Profile Information
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        help_text="Date of birth for age calculation and healthcare records"
    )
    
    gender = models.CharField(
        max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('non_binary', 'Non-Binary'),
            ('prefer_not_to_say', 'Prefer not to say'),
        ],
        blank=True,
        help_text="Gender identification"
    )
    
    address_line_1 = models.CharField(
        max_length=255, 
        blank=True,
        help_text="Street address line 1"
    )
    suburb = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Suburb or city"
    )
    
    # Australian states and territories
    state = models.CharField(
        max_length=3,
        choices=[
            ('NSW', 'New South Wales'),
            ('VIC', 'Victoria'),
            ('QLD', 'Queensland'),
            ('WA', 'Western Australia'),
            ('SA', 'South Australia'),
            ('TAS', 'Tasmania'),
            ('ACT', 'Australian Capital Territory'),
            ('NT', 'Northern Territory'),
        ],
        blank=True,
        help_text="Australian state or territory"
    )
    postcode = models.CharField(
        max_length=4, 
        blank=True,
        help_text="Australian postcode (4 digits)"
    )
    
    # Healthcare Information
    medicare_number = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        help_text="Medicare number for healthcare billing"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Soft Delete (for data deletion requests - APP 13)
    is_deleted = models.BooleanField(
        default=False,
        help_text="Soft delete flag - data is archived, not permanently deleted"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when data was soft-deleted/archived"
    )
    deletion_request = models.ForeignKey(
        'DataDeletionRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='deleted_users',
        help_text="Reference to the deletion request that triggered this deletion"
    )
    
    # Django settings
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = UserManager()
    
    class Meta:
        db_table = 'users_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email}) - {self.get_role_display()}"
    
    @property
    def age(self):
        """
        Calculate age from date_of_birth
        
        Returns:
            int or None: Age in years, or None if date_of_birth is not set
        """
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
    
    # Role checking methods for permission control
    def is_patient(self):
        """Check if user is a patient"""
        return self.role == self.UserRole.PATIENT
    
    def is_psychologist(self):
        """Check if user is a psychologist"""
        return self.role == self.UserRole.PSYCHOLOGIST
    
    def is_practice_manager(self):
        """Check if user is a practice manager"""
        return self.role == self.UserRole.PRACTICE_MANAGER
    
    def is_admin_user(self):
        """Check if user is an admin"""
        return self.role == self.UserRole.ADMIN


class PatientProfile(models.Model):
    """Extended patient profile matching Australian psychology clinic intake forms"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )
    
    # Personal Details
    preferred_name = models.CharField(max_length=100, blank=True)
    gender_identity = models.CharField(max_length=50, blank=True)
    pronouns = models.CharField(max_length=20, blank=True)
    home_phone = models.CharField(max_length=15, blank=True, help_text="Home phone number")
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    
    # Referral Information
    referral_source = models.CharField(max_length=200, blank=True)
    has_gp_referral = models.BooleanField(default=False)
    gp_name = models.CharField(max_length=255, blank=True)
    gp_practice_name = models.CharField(max_length=255, blank=True)
    gp_provider_number = models.CharField(max_length=20, blank=True)
    gp_address = models.TextField(blank=True)
    
    # Medical History
    previous_therapy = models.BooleanField(default=False)
    previous_therapy_details = models.TextField(blank=True)
    current_medications = models.BooleanField(default=False)
    medication_list = models.TextField(blank=True)
    other_health_professionals = models.BooleanField(default=False)
    other_health_details = models.TextField(blank=True)
    medical_conditions = models.BooleanField(default=False)
    medical_conditions_details = models.TextField(blank=True)
    
    # Presenting Concerns
    presenting_concerns = models.TextField(blank=True)
    therapy_goals = models.TextField(blank=True)
    
    # Consent & Legal
    consent_to_treatment = models.BooleanField(default=False)
    consent_to_treatment_date = models.DateTimeField(null=True, blank=True, help_text="Date treatment consent was given")
    consent_to_treatment_version = models.CharField(max_length=20, blank=True, help_text="Version of consent form accepted")
    
    consent_to_telehealth = models.BooleanField(default=False)
    consent_to_telehealth_date = models.DateTimeField(null=True, blank=True, help_text="Date telehealth consent was given")
    consent_to_telehealth_version = models.CharField(max_length=20, blank=True, help_text="Version of telehealth consent form")
    telehealth_emergency_protocol_acknowledged = models.BooleanField(default=False, help_text="Patient confirmed understanding of emergency procedures for telehealth sessions")
    telehealth_emergency_acknowledged_date = models.DateTimeField(null=True, blank=True, help_text="Date emergency procedures were acknowledged")
    telehealth_emergency_contact = models.CharField(max_length=255, blank=True, help_text="Emergency contact for telehealth sessions")
    telehealth_emergency_plan = models.TextField(blank=True, help_text="Patient's plan if telehealth session is interrupted or crisis occurs")
    telehealth_tech_requirements_acknowledged = models.BooleanField(default=False, help_text="Patient confirmed they meet telehealth technical requirements")
    telehealth_tech_acknowledged_date = models.DateTimeField(null=True, blank=True, help_text="Date technical requirements were acknowledged")
    telehealth_recording_consent = models.BooleanField(default=False, help_text="Patient consented to telehealth session recording (if applicable)")
    telehealth_recording_consent_date = models.DateTimeField(null=True, blank=True, help_text="Date recording consent was given")
    telehealth_recording_consent_version = models.CharField(max_length=20, blank=True, help_text="Version of recording consent accepted")
    
    # Privacy Policy Compliance (Privacy Act 1988 - APP 1)
    privacy_policy_accepted = models.BooleanField(default=False, help_text="Patient has accepted Privacy Policy")
    privacy_policy_accepted_date = models.DateTimeField(null=True, blank=True, help_text="Date Privacy Policy was accepted")
    privacy_policy_version = models.CharField(max_length=20, blank=True, help_text="Version of Privacy Policy accepted")
    
    # Data Sharing Consent (APP 7, APP 8)
    consent_to_data_sharing = models.BooleanField(default=False, help_text="Consent to share data with third parties (Twilio, Stripe)")
    consent_to_data_sharing_date = models.DateTimeField(null=True, blank=True)
    
    consent_to_marketing = models.BooleanField(default=False, help_text="Consent to receive marketing communications (APP 7)")
    consent_to_marketing_date = models.DateTimeField(null=True, blank=True)
    
    # Communication Preferences
    email_notifications_enabled = models.BooleanField(default=True, help_text="Patient prefers to receive email notifications")
    sms_notifications_enabled = models.BooleanField(default=False, help_text="Patient prefers to receive SMS notifications")
    appointment_reminders_enabled = models.BooleanField(default=True, help_text="Patient prefers to receive appointment reminders")
    
    # Privacy Preferences
    share_progress_with_emergency_contact = models.BooleanField(default=False, help_text="Patient consents to sharing progress updates with emergency contact")
    share_progress_consent_date = models.DateTimeField(null=True, blank=True, help_text="Date progress sharing consent was given")
    share_progress_consent_version = models.CharField(max_length=20, blank=True, help_text="Version of progress sharing consent")
    
    # Consent Withdrawal (APP 7)
    consent_withdrawn = models.BooleanField(default=False, help_text="Patient has withdrawn consent")
    consent_withdrawn_date = models.DateTimeField(null=True, blank=True)
    consent_withdrawal_reason = models.TextField(blank=True, help_text="Reason for consent withdrawal")
    
    # Parental Consent (for minors under 18)
    parental_consent = models.BooleanField(default=False, help_text="Parental consent obtained for minor")
    parental_consent_name = models.CharField(max_length=255, blank=True, help_text="Name of parent/guardian giving consent")
    parental_consent_date = models.DateTimeField(null=True, blank=True)
    parental_consent_signature = models.CharField(max_length=255, blank=True)
    
    # Legacy fields (keeping for backward compatibility)
    client_signature = models.CharField(max_length=255, blank=True)
    consent_date = models.DateField(null=True, blank=True)
    
    intake_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"


class ProgressNote(models.Model):
    """SOAP Notes for tracking client progress"""
    
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progress_notes'
    )
    
    psychologist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='written_notes'
    )
    
    session_date = models.DateTimeField()
    session_number = models.PositiveIntegerField()
    
    # SOAP Structure
    subjective = models.TextField()
    objective = models.TextField()
    assessment = models.TextField()
    plan = models.TextField()
    
    session_duration = models.PositiveIntegerField(default=50)
    progress_rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 11)],
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-session_date']
        unique_together = ['patient', 'session_number']
    
    def __str__(self):
        return f"Session {self.session_number} - {self.patient.get_full_name()}"


class DataDeletionRequest(models.Model):
    """
    Data Deletion Request (Privacy Act 1988 - APP 13 compliance)
    
    Tracks patient requests to delete their personal information.
    Uses soft delete/archiving to comply with legal retention requirements.
    """
    
    class RequestStatus(models.TextChoices):
        """Status of deletion request"""
        PENDING = 'pending', 'Pending Review'
        APPROVED = 'approved', 'Approved - Scheduled for Deletion'
        REJECTED = 'rejected', 'Rejected'
        COMPLETED = 'completed', 'Completed - Data Archived'
        CANCELLED = 'cancelled', 'Cancelled by Patient'
    
    class RejectionReason(models.TextChoices):
        """Common reasons for rejecting deletion requests"""
        LEGAL_RETENTION = 'legal_retention', 'Legal retention period not met (7 years for adults, until 25 for children)'
        ACTIVE_APPOINTMENTS = 'active_appointments', 'Patient has active or upcoming appointments'
        UNPAID_INVOICES = 'unpaid_invoices', 'Patient has unpaid invoices'
        LEGAL_OBLIGATION = 'legal_obligation', 'Legal obligation to retain records (court order, investigation)'
        OTHER = 'other', 'Other (specified in notes)'
    
    # Patient making the request
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='deletion_requests',
        help_text="Patient requesting data deletion"
    )
    
    # Request details
    request_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time deletion was requested"
    )
    
    reason = models.TextField(
        blank=True,
        help_text="Patient's reason for requesting deletion"
    )
    
    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.PENDING,
        help_text="Current status of the deletion request"
    )
    
    # Review details (admin/practice manager)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_deletion_requests',
        help_text="Admin or practice manager who reviewed the request"
    )
    
    reviewed_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time request was reviewed"
    )
    
    rejection_reason = models.CharField(
        max_length=50,
        choices=RejectionReason.choices,
        blank=True,
        help_text="Reason for rejection (if rejected)"
    )
    
    rejection_notes = models.TextField(
        blank=True,
        help_text="Additional notes about rejection or approval"
    )
    
    # Deletion execution
    scheduled_deletion_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when data will be archived/deleted (respects retention policy)"
    )
    
    deletion_completed_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date when data was actually archived/deleted"
    )
    
    # Retention policy compliance
    retention_period_years = models.PositiveIntegerField(
        default=7,
        help_text="Number of years data must be retained (7 for adults, until age 25 for children)"
    )
    
    earliest_deletion_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Earliest date data can be deleted based on retention policy"
    )
    
    # Metadata
    notes = models.TextField(
        blank=True,
        help_text="Internal notes about the deletion request"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-request_date']
        verbose_name = 'Data Deletion Request'
        verbose_name_plural = 'Data Deletion Requests'
    
    def __str__(self):
        return f"Deletion Request - {self.patient.get_full_name()} ({self.status})"
    
    def calculate_earliest_deletion_date(self):
        """
        Calculate the earliest date data can be deleted based on retention policy.
        - Adults: 7 years after last appointment or last contact
        - Children: Until age 25
        """
        from django.utils import timezone
        from datetime import timedelta
        
        patient = self.patient
        patient_profile = getattr(patient, 'patient_profile', None)
        
        # Check if patient is a minor (under 18)
        if patient.date_of_birth:
            age = (timezone.now().date() - patient.date_of_birth).days // 365
            if age < 18:
                # Child: retain until age 25
                years_until_25 = 25 - age
                self.retention_period_years = years_until_25
                self.earliest_deletion_date = timezone.now() + timedelta(days=years_until_25 * 365)
                return self.earliest_deletion_date
        
        # Adult: 7 years after last contact
        from appointments.models import Appointment
        last_appointment = Appointment.objects.filter(
            patient=patient
        ).order_by('-appointment_date').first()
        
        if last_appointment:
            last_contact_date = last_appointment.appointment_date
        else:
            # Use account creation date if no appointments
            last_contact_date = patient.date_joined
        
        self.retention_period_years = 7
        self.earliest_deletion_date = last_contact_date + timedelta(days=7 * 365)
        return self.earliest_deletion_date
    
    def can_be_deleted_now(self):
        """Check if data can be deleted now based on retention policy"""
        from django.utils import timezone
        if not self.earliest_deletion_date:
            self.calculate_earliest_deletion_date()
        return timezone.now() >= self.earliest_deletion_date
