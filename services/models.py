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