"""
Extended Patient models to support Australian psychology clinic intake forms
"""

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class PatientProfile(models.Model):
    """
    Extended patient profile matching the intake form requirements
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )
    
    # Personal Details (from Form 1)
    preferred_name = models.CharField(max_length=100, blank=True)
    gender_identity = models.CharField(max_length=50, blank=True)
    pronouns = models.CharField(max_length=20, blank=True)
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    
    # Referral Information
    referral_source = models.CharField(
        max_length=200,
        blank=True,
        help_text="How did you hear about us?"
    )
    has_gp_referral = models.BooleanField(default=False)
    gp_name = models.CharField(max_length=255, blank=True)
    gp_practice_name = models.CharField(max_length=255, blank=True)
    gp_provider_number = models.CharField(max_length=15, blank=True)
    gp_practice_address = models.TextField(blank=True)
    has_mental_health_care_plan = models.BooleanField(default=False)
    
    # Medical & Mental Health History
    previous_therapy = models.BooleanField(
        default=False,
        help_text="Have you had therapy or counselling before?"
    )
    previous_therapy_details = models.TextField(blank=True)
    
    current_medications = models.TextField(
        blank=True,
        help_text="List current medications"
    )
    
    other_health_professionals = models.TextField(
        blank=True,
        help_text="Other medical or health professionals currently seeing"
    )
    
    medical_conditions = models.TextField(
        blank=True,
        help_text="Significant medical conditions"
    )
    
    # Presenting Concerns
    presenting_concerns = models.TextField(
        blank=True,
        help_text="What brings you to therapy at this time?"
    )
    
    therapy_goals = models.TextField(
        blank=True,
        help_text="What are your goals for therapy?"
    )
    
    # Consent and Agreement
    consent_to_treatment = models.BooleanField(default=False)
    consent_date = models.DateTimeField(null=True, blank=True)
    service_agreement_signed = models.BooleanField(default=False)
    service_agreement_date = models.DateTimeField(null=True, blank=True)
    
    # Telehealth Consent
    consent_to_telehealth = models.BooleanField(default=False)
    telehealth_privacy_acknowledged = models.BooleanField(default=False)
    
    # Client Rights Acknowledgement
    client_rights_acknowledged = models.BooleanField(default=False)
    
    # Status
    intake_completed = models.BooleanField(default=False)
    intake_completion_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_patient_profile'
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'
    
    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"


class ProgressNote(models.Model):
    """
    SOAP Notes for tracking client progress - matches Template 3
    """
    
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='progress_notes',
        limit_choices_to={'role': 'patient'}
    )
    
    psychologist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='written_notes',
        limit_choices_to={'role': 'psychologist'}
    )
    
    session_date = models.DateTimeField()
    session_number = models.PositiveIntegerField()
    
    # SOAP Note Structure
    subjective = models.TextField(
        help_text="Client's report of feelings, thoughts, and symptoms since last session"
    )
    
    objective = models.TextField(
        help_text="Objective observations during session (affect, mood, body language, etc.)"
    )
    
    assessment = models.TextField(
        help_text="Professional interpretation and clinical impression"
    )
    
    plan = models.TextField(
        help_text="Plan for next session, interventions used, homework assigned"
    )
    
    # Additional Clinical Information
    session_type = models.CharField(
        max_length=20,
        choices=[
            ('individual', 'Individual Therapy'),
            ('couples', 'Couples Therapy'),
            ('family', 'Family Therapy'),
            ('group', 'Group Therapy'),
            ('assessment', 'Assessment'),
        ],
        default='individual'
    )
    
    session_duration = models.PositiveIntegerField(
        default=50,
        help_text="Session duration in minutes"
    )
    
    # Progress Tracking
    progress_rating = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 11)],
        null=True,
        blank=True,
        help_text="Progress rating 1-10"
    )
    
    goals_addressed = models.TextField(
        blank=True,
        help_text="Which therapy goals were addressed in this session"
    )
    
    homework_assigned = models.TextField(
        blank=True,
        help_text="Homework or tasks assigned to client"
    )
    
    # Clinical Flags
    risk_assessment_required = models.BooleanField(default=False)
    follow_up_required = models.BooleanField(default=False)
    referral_recommended = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_progress_note'
        verbose_name = 'Progress Note'
        verbose_name_plural = 'Progress Notes'
        ordering = ['-session_date']
        unique_together = ['patient', 'session_number']
    
    def __str__(self):
        return f"Session {self.session_number} - {self.patient.get_full_name()} ({self.session_date.date()})"


class ClientServiceAgreement(models.Model):
    """
    Digital version of the Client Service Agreement & Informed Consent
    """
    
    patient = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='service_agreement',
        limit_choices_to={'role': 'patient'}
    )
    
    psychologist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='client_agreements',
        limit_choices_to={'role': 'psychologist'}
    )
    
    # Agreement Details
    session_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Session fee in AUD"
    )
    
    cancellation_notice_hours = models.PositiveIntegerField(
        default=48,
        help_text="Required cancellation notice in hours"
    )
    
    cancellation_fee_percentage = models.PositiveIntegerField(
        default=100,
        help_text="Cancellation fee as percentage of session cost"
    )
    
    # Consent Acknowledgements
    confidentiality_explained = models.BooleanField(default=False)
    limits_to_confidentiality_explained = models.BooleanField(default=False)
    fees_and_payment_explained = models.BooleanField(default=False)
    cancellation_policy_explained = models.BooleanField(default=False)
    telehealth_privacy_explained = models.BooleanField(default=False)
    client_rights_explained = models.BooleanField(default=False)
    
    # Digital Signature
    client_digital_signature = models.CharField(max_length=255)
    agreement_date = models.DateTimeField()
    ip_address = models.GenericIPAddressField()
    
    # Status
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users_client_service_agreement'
        verbose_name = 'Client Service Agreement'
        verbose_name_plural = 'Client Service Agreements'
    
    def __str__(self):
        return f"Service Agreement - {self.patient.get_full_name()} ({self.agreement_date.date()})"
