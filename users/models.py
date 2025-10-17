"""
Custom User models for Psychology Clinic
Supports role-based access for Australian healthcare compliance
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


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
    
    # Django settings
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
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
    consent_to_telehealth = models.BooleanField(default=False)
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
