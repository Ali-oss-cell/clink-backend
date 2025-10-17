"""
Services models for Psychology Clinic
Handles psychology services, specializations, and psychologist profiles
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Specialization(models.Model):
    """
    Psychology specialization areas (e.g., Anxiety, Depression, ADHD)
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Specialization name (e.g., 'Anxiety Disorders')"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the specialization"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Active specialization offered by the clinic"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'services_specialization'
        verbose_name = 'Specialization'
        verbose_name_plural = 'Specializations'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Service(models.Model):
    """
    Psychology services offered by the clinic
    """
    
    class ServiceType(models.TextChoices):
        INDIVIDUAL = 'individual', 'Individual Therapy'
        COUPLES = 'couples', 'Couples Therapy'
        FAMILY = 'family', 'Family Therapy'
        GROUP = 'group', 'Group Therapy'
        ASSESSMENT = 'assessment', 'Psychological Assessment'
        CONSULTATION = 'consultation', 'Consultation'
    
    name = models.CharField(
        max_length=200,
        help_text="Service name (e.g., 'Individual Therapy Session')"
    )
    
    service_type = models.CharField(
        max_length=20,
        choices=ServiceType.choices,
        default=ServiceType.INDIVIDUAL
    )
    
    description = models.TextField(
        help_text="Detailed service description"
    )
    
    duration_minutes = models.PositiveIntegerField(
        default=50,
        validators=[MinValueValidator(15), MaxValueValidator(180)],
        help_text="Session duration in minutes"
    )
    
    # Pricing
    standard_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=180.00,
        help_text="Standard fee in AUD"
    )
    
    medicare_rebate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=87.45,
        help_text="Medicare rebate amount in AUD"
    )
    
    medicare_item_number = models.CharField(
        max_length=10,
        blank=True,
        help_text="Medicare item number for billing"
    )
    
    # Service Details
    specializations = models.ManyToManyField(
        Specialization,
        blank=True,
        help_text="Relevant specializations for this service"
    )
    
    is_telehealth_available = models.BooleanField(
        default=True,
        help_text="Available via video consultation"
    )
    
    requires_referral = models.BooleanField(
        default=False,
        help_text="Requires GP or specialist referral"
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Service is currently offered"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'services_service'
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.duration_minutes}min)"
    
    @property
    def out_of_pocket_cost(self):
        """Calculate patient out-of-pocket cost after Medicare rebate"""
        return self.standard_fee - self.medicare_rebate


class PsychologistProfile(models.Model):
    """
    Extended profile for Psychologist users with AHPRA compliance
    """
    
    user = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        related_name='psychologist_profile'
    )
    
    # AHPRA Registration
    ahpra_registration_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="AHPRA registration number"
    )
    
    ahpra_expiry_date = models.DateField(
        help_text="AHPRA registration expiry date"
    )
    
    # Professional Information
    title = models.CharField(
        max_length=10,
        choices=[
            ('Dr', 'Dr'),
            ('Mr', 'Mr'),
            ('Ms', 'Ms'),
            ('Mrs', 'Mrs'),
        ],
        default='Ms'
    )
    
    qualifications = models.TextField(
        help_text="Professional qualifications and certifications"
    )
    
    specializations = models.ManyToManyField(
        Specialization,
        blank=True,
        help_text="Areas of psychological specialization"
    )
    
    services_offered = models.ManyToManyField(
        Service,
        blank=True,
        help_text="Services this psychologist provides"
    )
    
    years_experience = models.PositiveIntegerField(
        default=0,
        help_text="Years of professional experience"
    )
    
    # Practice Information
    consultation_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=180.00,
        help_text="Standard consultation fee in AUD"
    )
    
    medicare_provider_number = models.CharField(
        max_length=15,
        blank=True,
        help_text="Medicare provider number for rebates"
    )
    
    # Availability
    is_accepting_new_patients = models.BooleanField(
        default=True,
        help_text="Currently accepting new patients"
    )
    
    max_patients_per_day = models.PositiveIntegerField(
        default=8,
        help_text="Maximum number of patients per day"
    )
    
    # Profile and Bio
    bio = models.TextField(
        blank=True,
        help_text="Professional biography for patient portal"
    )
    
    profile_image = models.ImageField(
        upload_to='psychologist_profiles/',
        blank=True,
        null=True
    )
    
    # Practice Details
    practice_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Name of the practice or clinic"
    )
    
    practice_address = models.TextField(
        blank=True,
        help_text="Practice address"
    )
    
    practice_phone = models.CharField(
        max_length=15,
        blank=True,
        help_text="Practice phone number"
    )
    
    practice_email = models.EmailField(
        blank=True,
        help_text="Practice email address"
    )
    
    personal_website = models.URLField(
        blank=True,
        help_text="Personal or professional website"
    )
    
    # Communication
    languages_spoken = models.CharField(
        max_length=200,
        blank=True,
        help_text="Languages spoken (comma-separated)"
    )
    
    session_types = models.CharField(
        max_length=200,
        blank=True,
        help_text="Types of sessions offered (Individual, Couples, Group)"
    )
    
    # Insurance & Billing
    insurance_providers = models.CharField(
        max_length=300,
        blank=True,
        help_text="Insurance providers accepted (comma-separated)"
    )
    
    billing_methods = models.CharField(
        max_length=300,
        blank=True,
        help_text="Billing methods available"
    )
    
    medicare_rebate_amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=87.45,
        help_text="Medicare rebate amount in AUD"
    )
    
    # Availability Details
    working_hours = models.CharField(
        max_length=100,
        blank=True,
        help_text="Working hours (e.g., 'Monday-Friday, 9AM-5PM')"
    )
    
    working_days = models.CharField(
        max_length=200,
        blank=True,
        help_text="Working days (comma-separated: Monday,Tuesday,Wednesday)"
    )
    
    start_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Standard start time for work day"
    )
    
    end_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Standard end time for work day"
    )
    
    session_duration_minutes = models.PositiveIntegerField(
        default=50,
        help_text="Standard session duration in minutes"
    )
    
    break_between_sessions_minutes = models.PositiveIntegerField(
        default=10,
        help_text="Break between sessions in minutes"
    )
    
    telehealth_available = models.BooleanField(
        default=True,
        help_text="Available for telehealth sessions"
    )
    
    in_person_available = models.BooleanField(
        default=True,
        help_text="Available for in-person sessions"
    )
    
    # Professional Statistics
    total_patients_seen = models.PositiveIntegerField(
        default=0,
        help_text="Total number of patients seen"
    )
    
    currently_active_patients = models.PositiveIntegerField(
        default=0,
        help_text="Currently active patients"
    )
    
    sessions_completed = models.PositiveIntegerField(
        default=0,
        help_text="Total sessions completed"
    )
    
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        help_text="Average patient rating (0-5)"
    )
    
    total_reviews = models.PositiveIntegerField(
        default=0,
        help_text="Total number of reviews"
    )
    
    # Status
    is_active_practitioner = models.BooleanField(
        default=True,
        help_text="Active practitioner status"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'services_psychologist_profile'
        verbose_name = 'Psychologist Profile'
        verbose_name_plural = 'Psychologist Profiles'
    
    def __str__(self):
        return f"{self.title} {self.user.get_full_name()}"
    
    @property
    def is_ahpra_current(self):
        """Check if AHPRA registration is current"""
        return self.ahpra_expiry_date >= timezone.now().date()
    
    @property
    def display_name(self):
        """Professional display name"""
        return f"{self.title} {self.user.get_full_name()}"
    
    @property
    def patient_cost_after_rebate(self):
        """Calculate patient out-of-pocket cost after Medicare rebate"""
        from decimal import Decimal
        return float(self.consultation_fee) - float(self.medicare_rebate_amount)
    
    @property
    def languages_list(self):
        """Return languages as a list"""
        if self.languages_spoken:
            return [lang.strip() for lang in self.languages_spoken.split(',')]
        return []
    
    @property
    def session_types_list(self):
        """Return session types as a list"""
        if self.session_types:
            return [session.strip() for session in self.session_types.split(',')]
        return []
    
    @property
    def insurance_providers_list(self):
        """Return insurance providers as a list"""
        if self.insurance_providers:
            return [provider.strip() for provider in self.insurance_providers.split(',')]
        return []
    
    @property
    def is_highly_rated(self):
        """Check if psychologist has high ratings"""
        return self.average_rating >= 4.5 and self.total_reviews >= 10
    
    @property
    def experience_level(self):
        """Return experience level based on years"""
        if self.years_experience >= 10:
            return "Senior"
        elif self.years_experience >= 5:
            return "Experienced"
        elif self.years_experience >= 2:
            return "Mid-level"
        else:
            return "Junior"
    
    @property
    def working_days_list(self):
        """Return working days as a list"""
        if self.working_days:
            return [day.strip() for day in self.working_days.split(',')]
        return []
    
    def get_next_available_slot(self, service_id=None):
        """
        Get the next available appointment slot for this psychologist
        
        Args:
            service_id: Optional service ID to filter by
            
        Returns:
            datetime or None: Next available slot datetime
        """
        from appointments.models import TimeSlot
        from django.utils import timezone
        
        # Get available time slots starting from now
        now = timezone.now()
        available_slots = TimeSlot.objects.filter(
            availability_slot__psychologist=self.user,
            is_available=True,
            start_time__gte=now
        ).order_by('start_time')
        
        if available_slots.exists():
            return available_slots.first().start_time
        return None