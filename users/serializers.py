"""
Serializers for Psychology Clinic User Management
Supports intake forms, progress notes, and role-based data access
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import PatientProfile, ProgressNote, DataDeletionRequest

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for authentication responses and user management"""
    
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    psychologist_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'role', 'phone_number', 'date_of_birth', 'age', 'is_verified',
            'is_active', 'created_at', 'last_login', 'psychologist_profile'
        ]
        read_only_fields = ['id', 'created_at', 'last_login']
    
    def get_full_name(self, obj):
        """Get full name from first_name and last_name"""
        return obj.get_full_name() or f"{obj.first_name} {obj.last_name}".strip() or obj.email
    
    def get_age(self, obj):
        return obj.age if hasattr(obj, 'age') else None
    
    def get_psychologist_profile(self, obj):
        """Get psychologist profile if user is a psychologist"""
        if obj.role == User.UserRole.PSYCHOLOGIST and hasattr(obj, 'psychologist_profile'):
            try:
                from services.serializers import PsychologistProfileSerializer
                return PsychologistProfileSerializer(obj.psychologist_profile).data
            except:
                return None
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users (admin/practice manager)"""
    
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    full_name = serializers.CharField(write_only=True, required=False, help_text="Alternative to first_name/last_name")
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'username', 'first_name', 'last_name', 'full_name',
            'role', 'phone_number', 'date_of_birth', 'is_verified', 'is_active'
        ]
        extra_kwargs = {
            'username': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }
    
    def validate(self, attrs):
        # Handle full_name if provided
        if 'full_name' in attrs and attrs['full_name']:
            name_parts = attrs['full_name'].strip().split(' ', 1)
            if len(name_parts) == 2:
                attrs['first_name'] = name_parts[0]
                attrs['last_name'] = name_parts[1]
            else:
                attrs['first_name'] = name_parts[0]
                attrs['last_name'] = ''
            del attrs['full_name']
        
        # Validate required fields based on role
        role = attrs.get('role')
        if not attrs.get('first_name') or not attrs.get('last_name'):
            raise serializers.ValidationError({
                'first_name': 'First name is required',
                'last_name': 'Last name is required'
            })
        
        # Generate username from email if not provided
        if not attrs.get('username'):
            email = attrs.get('email', '')
            attrs['username'] = email.split('@')[0] if email else f"user_{User.objects.count() + 1}"
        
        return attrs
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.get('role', User.UserRole.PATIENT)
        
        # Create user
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        # Create profile based on role
        if role == User.UserRole.PATIENT:
            from .models import PatientProfile
            PatientProfile.objects.create(user=user)
        elif role == User.UserRole.PSYCHOLOGIST:
            # Note: Psychologist profile should be created separately via psychologist profile endpoint
            # as it requires AHPRA registration number and other professional details
            pass
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users with psychologist profile support"""
    
    full_name = serializers.CharField(write_only=True, required=False)
    
    # Psychologist profile fields
    ahpra_registration_number = serializers.CharField(required=False, allow_blank=True)
    ahpra_expiry_date = serializers.DateField(required=False, allow_null=True)
    title = serializers.CharField(required=False, allow_blank=True)
    qualifications = serializers.CharField(required=False, allow_blank=True)
    years_experience = serializers.IntegerField(required=False, allow_null=True)
    consultation_fee = serializers.DecimalField(max_digits=8, decimal_places=2, required=False, allow_null=True)
    medicare_provider_number = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    is_accepting_new_patients = serializers.BooleanField(required=False, allow_null=True)
    specializations = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    services_offered = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'full_name', 'phone_number',
            'role', 'is_verified', 'is_active', 'date_of_birth',
            # Psychologist profile fields
            'ahpra_registration_number', 'ahpra_expiry_date', 'title',
            'qualifications', 'years_experience', 'consultation_fee',
            'medicare_provider_number', 'bio', 'is_accepting_new_patients',
            'specializations', 'services_offered'
        ]
    
    def validate(self, attrs):
        """Handle full_name and validate data"""
        # Handle full_name if provided
        if 'full_name' in attrs and attrs['full_name']:
            name_parts = attrs['full_name'].strip().split(' ', 1)
            if len(name_parts) == 2:
                attrs['first_name'] = name_parts[0]
                attrs['last_name'] = name_parts[1]
            else:
                attrs['first_name'] = name_parts[0]
                attrs['last_name'] = ''
            del attrs['full_name']
        
        return attrs
    
    def update(self, instance, validated_data):
        """Update user and psychologist profile if applicable"""
        # Extract psychologist profile fields
        psychologist_fields = {
            'ahpra_registration_number', 'ahpra_expiry_date', 'title',
            'qualifications', 'years_experience', 'consultation_fee',
            'medicare_provider_number', 'bio', 'is_accepting_new_patients',
            'specializations', 'services_offered'
        }
        
        profile_data = {}
        specializations = None
        services_offered = None
        
        for field in psychologist_fields:
            if field in validated_data:
                if field == 'specializations':
                    specializations = validated_data.pop(field)
                elif field == 'services_offered':
                    services_offered = validated_data.pop(field)
                else:
                    profile_data[field] = validated_data.pop(field)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update psychologist profile if user is a psychologist
        if instance.role == User.UserRole.PSYCHOLOGIST and (profile_data or specializations is not None or services_offered is not None):
            try:
                from services.models import PsychologistProfile
                
                # Get or create profile
                try:
                    profile = PsychologistProfile.objects.get(user=instance)
                except PsychologistProfile.DoesNotExist:
                    # Create profile with defaults if it doesn't exist
                    defaults = {}
                    if 'ahpra_registration_number' in profile_data:
                        defaults['ahpra_registration_number'] = profile_data['ahpra_registration_number']
                    if 'ahpra_expiry_date' in profile_data:
                        defaults['ahpra_expiry_date'] = profile_data['ahpra_expiry_date']
                    else:
                        defaults['ahpra_expiry_date'] = timezone.now().date()
                    
                    profile = PsychologistProfile.objects.create(user=instance, **defaults)
                    # Remove from profile_data since we already set them
                    profile_data.pop('ahpra_registration_number', None)
                    profile_data.pop('ahpra_expiry_date', None)
                
                # Update profile fields
                for attr, value in profile_data.items():
                    setattr(profile, attr, value)
                
                if profile_data:
                    profile.save()
                
                # Update many-to-many relationships
                if specializations is not None:
                    profile.specializations.set(specializations)
                if services_offered is not None:
                    profile.services_offered.set(services_offered)
                    
            except Exception as e:
                # If profile update fails, log but don't fail the user update
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error updating psychologist profile: {str(e)}")
        
        return instance


class PatientRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for patient registration - matches intake form"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'first_name', 'last_name',
            'phone_number', 'date_of_birth', 'address_line_1', 'suburb', 
            'state', 'postcode', 'medicare_number'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Generate username from email
        email = validated_data.get('email')
        username = email.split('@')[0]  # Use email prefix as username
        
        user = User.objects.create_user(
            username=username,
            role=User.UserRole.PATIENT,
            **validated_data
        )
        user.set_password(password)
        user.save()
        
        # Create patient profile
        PatientProfile.objects.create(user=user)
        
        return user


class PatientProfileSerializer(serializers.ModelSerializer):
    """Serializer for patient profile - matches intake form fields"""
    
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = PatientProfile
        fields = [
            'user_details', 'preferred_name', 'gender_identity', 'pronouns', 'home_phone',
            'emergency_contact_name', 'emergency_contact_relationship', 
            'emergency_contact_phone', 'referral_source', 'has_gp_referral',
            'gp_name', 'gp_practice_name', 'gp_provider_number', 'gp_address',
            'previous_therapy', 'previous_therapy_details', 'current_medications',
            'medication_list', 'other_health_professionals', 'other_health_details',
            'medical_conditions', 'medical_conditions_details', 'presenting_concerns', 
            'therapy_goals', 
            # Consent fields
            'consent_to_treatment', 'consent_to_treatment_date', 'consent_to_treatment_version',
            'consent_to_telehealth', 'consent_to_telehealth_date', 'consent_to_telehealth_version',
            'telehealth_emergency_protocol_acknowledged', 'telehealth_emergency_acknowledged_date',
            'telehealth_emergency_contact', 'telehealth_emergency_plan',
            'telehealth_tech_requirements_acknowledged', 'telehealth_tech_acknowledged_date',
            'telehealth_recording_consent', 'telehealth_recording_consent_date',
            'telehealth_recording_consent_version',
            # Privacy Policy compliance
            'privacy_policy_accepted', 'privacy_policy_accepted_date', 'privacy_policy_version',
            'consent_to_data_sharing', 'consent_to_data_sharing_date',
            'consent_to_marketing', 'consent_to_marketing_date',
            'consent_withdrawn', 'consent_withdrawn_date', 'consent_withdrawal_reason',
            # Parental consent
            'parental_consent', 'parental_consent_name', 'parental_consent_date', 'parental_consent_signature',
            # Legacy fields
            'client_signature', 'consent_date', 
            'intake_completed', 'created_at'
        ]
        read_only_fields = ['user_details', 'created_at']


class IntakeFormSerializer(serializers.ModelSerializer):
    """
    Complete intake form serializer for React frontend
    
    Handles both user fields (pre-filled from login) and patient profile fields.
    Includes validation for Australian healthcare compliance.
    """
    
    # User fields (pre-filled from login)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(read_only=True)
    phone_number = serializers.CharField(required=True)
    date_of_birth = serializers.DateField(required=True)
    address_line_1 = serializers.CharField(required=True)
    suburb = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    postcode = serializers.CharField(required=True)
    medicare_number = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = PatientProfile
        fields = [
            # User fields (pre-filled from login)
            'first_name', 'last_name', 'email', 'phone_number', 'date_of_birth',
            'address_line_1', 'suburb', 'state', 'postcode', 'medicare_number',
            
            # Patient profile fields (user must complete)
            'preferred_name', 'gender_identity', 'pronouns', 'home_phone',
            'emergency_contact_name', 'emergency_contact_relationship', 
            'emergency_contact_phone', 'referral_source', 'has_gp_referral',
            'gp_name', 'gp_practice_name', 'gp_provider_number', 'gp_address',
            'previous_therapy', 'previous_therapy_details', 'current_medications',
            'medication_list', 'other_health_professionals', 'other_health_details',
            'medical_conditions', 'medical_conditions_details', 'presenting_concerns', 
            'therapy_goals', 
            # Consent fields
            'consent_to_treatment', 'consent_to_treatment_date', 'consent_to_treatment_version',
            'consent_to_telehealth', 'consent_to_telehealth_date', 'consent_to_telehealth_version',
            'telehealth_emergency_protocol_acknowledged', 'telehealth_emergency_acknowledged_date',
            'telehealth_emergency_contact', 'telehealth_emergency_plan',
            'telehealth_tech_requirements_acknowledged', 'telehealth_tech_acknowledged_date',
            'telehealth_recording_consent', 'telehealth_recording_consent_date',
            'telehealth_recording_consent_version',
            # Privacy Policy compliance
            'privacy_policy_accepted', 'privacy_policy_accepted_date', 'privacy_policy_version',
            'consent_to_data_sharing', 'consent_to_data_sharing_date',
            'consent_to_marketing', 'consent_to_marketing_date',
            'consent_withdrawn', 'consent_withdrawn_date', 'consent_withdrawal_reason',
            # Parental consent
            'parental_consent', 'parental_consent_name', 'parental_consent_date', 'parental_consent_signature',
            # Legacy fields
            'client_signature', 'consent_date', 
            'intake_completed'
        ]
    
    def to_representation(self, instance):
        """Custom representation to include user fields"""
        data = super().to_representation(instance)
        
        # Add user fields to the representation
        user = instance.user
        data.update({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone_number': user.phone_number,
            'date_of_birth': user.date_of_birth,
            'address_line_1': user.address_line_1,
            'suburb': user.suburb,
            'state': user.state,
            'postcode': user.postcode,
            'medicare_number': user.medicare_number,
        })
        
        return data
    
    def update(self, instance, validated_data):
        """
        Update both user and patient profile fields
        
        Handles updating user fields (first_name, last_name, etc.) and
        patient profile fields (preferred_name, emergency_contact, etc.)
        Automatically sets privacy policy and consent versions/dates for compliance.
        """
        from django.conf import settings
        from django.utils import timezone
        
        # Extract user fields from validated_data
        user_data = {}
        user_fields = ['first_name', 'last_name', 'phone_number', 'date_of_birth',
                      'address_line_1', 'suburb', 'state', 'postcode', 'medicare_number']
        
        for field in user_fields:
            if field in validated_data:
                user_data[field] = validated_data.pop(field)
        
        # Update user fields
        if user_data:
            for key, value in user_data.items():
                setattr(instance.user, key, value)
            instance.user.save()
        
        # Handle privacy policy acceptance (APP 1 compliance)
        if validated_data.get('privacy_policy_accepted') and not instance.privacy_policy_accepted:
            validated_data['privacy_policy_accepted_date'] = timezone.now()
            validated_data['privacy_policy_version'] = getattr(settings, 'PRIVACY_POLICY_VERSION', '1.0')
        
        # Handle consent to treatment with version tracking
        if validated_data.get('consent_to_treatment') and not instance.consent_to_treatment:
            validated_data['consent_to_treatment_date'] = timezone.now()
            validated_data['consent_to_treatment_version'] = getattr(settings, 'CONSENT_FORM_VERSION', '1.0')
        
        # Handle consent to telehealth with version tracking
        if validated_data.get('consent_to_telehealth') and not instance.consent_to_telehealth:
            validated_data['consent_to_telehealth_date'] = timezone.now()
            validated_data['consent_to_telehealth_version'] = getattr(settings, 'TELEHEALTH_CONSENT_VERSION', '1.0')
        
        # Telehealth emergency protocol acknowledgement
        if validated_data.get('telehealth_emergency_protocol_acknowledged') and not instance.telehealth_emergency_protocol_acknowledged:
            validated_data['telehealth_emergency_acknowledged_date'] = timezone.now()
        
        # Telehealth technical requirements acknowledgement
        if validated_data.get('telehealth_tech_requirements_acknowledged') and not instance.telehealth_tech_requirements_acknowledged:
            validated_data['telehealth_tech_acknowledged_date'] = timezone.now()
        
        # Telehealth recording consent
        if validated_data.get('telehealth_recording_consent') and not instance.telehealth_recording_consent:
            validated_data['telehealth_recording_consent_date'] = timezone.now()
            validated_data['telehealth_recording_consent_version'] = getattr(settings, 'TELEHEALTH_RECORDING_CONSENT_VERSION', '1.0')
        
        # Handle data sharing consent
        if validated_data.get('consent_to_data_sharing') and not instance.consent_to_data_sharing:
            validated_data['consent_to_data_sharing_date'] = timezone.now()
        
        # Handle marketing consent
        if validated_data.get('consent_to_marketing') and not instance.consent_to_marketing:
            validated_data['consent_to_marketing_date'] = timezone.now()
        
        # Handle consent withdrawal
        if validated_data.get('consent_withdrawn') and not instance.consent_withdrawn:
            validated_data['consent_withdrawn_date'] = timezone.now()
            # When consent is withdrawn, set all consent flags to False
            validated_data['consent_to_treatment'] = False
            validated_data['consent_to_telehealth'] = False
            validated_data['telehealth_emergency_protocol_acknowledged'] = False
            validated_data['telehealth_emergency_acknowledged_date'] = None
            validated_data['telehealth_tech_requirements_acknowledged'] = False
            validated_data['telehealth_tech_acknowledged_date'] = None
            validated_data['telehealth_recording_consent'] = False
            validated_data['telehealth_recording_consent_date'] = None
            validated_data['telehealth_recording_consent_version'] = ''
            validated_data['consent_to_data_sharing'] = False
            validated_data['consent_to_marketing'] = False
        
        # Handle parental consent
        if validated_data.get('parental_consent') and not instance.parental_consent:
            validated_data['parental_consent_date'] = timezone.now()
        
        # Update patient profile fields
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        
        return instance
    
    def validate_postcode(self, value):
        """Validate Australian postcode format"""
        if value and not value.isdigit():
            raise serializers.ValidationError("Postcode must be numeric")
        if value and len(value) != 4:
            raise serializers.ValidationError("Australian postcode must be 4 digits")
        return value
    
    def validate_phone_number(self, value):
        """Validate Australian phone number format"""
        if value:
            # Remove spaces and dashes
            cleaned = value.replace(' ', '').replace('-', '')
            # Check if it starts with +61 or 0
            if not (cleaned.startswith('+61') or cleaned.startswith('0')):
                raise serializers.ValidationError(
                    "Phone number must be in Australian format: +61XXXXXXXXX or 0XXXXXXXXX"
                )
        return value
    
    def validate_state(self, value):
        """Validate Australian state/territory"""
        valid_states = ['NSW', 'VIC', 'QLD', 'WA', 'SA', 'TAS', 'ACT', 'NT']
        if value and value not in valid_states:
            raise serializers.ValidationError(
                f"State must be one of: {', '.join(valid_states)}"
            )
        return value
    
    def validate_consent_to_treatment(self, value):
        """Validate consent to treatment is given"""
        if not value:
            raise serializers.ValidationError(
                "Consent to treatment is required to proceed"
            )
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        # Check if GP referral details are provided when has_gp_referral is True
        if attrs.get('has_gp_referral', False):
            if not attrs.get('gp_name'):
                raise serializers.ValidationError(
                    "GP name is required when GP referral is indicated"
                )
            if not attrs.get('gp_practice_name'):
                raise serializers.ValidationError(
                    "GP practice name is required when GP referral is indicated"
                )
        
        # Check if emergency contact details are provided
        if attrs.get('emergency_contact_name') and not attrs.get('emergency_contact_phone'):
            raise serializers.ValidationError(
                "Emergency contact phone is required when emergency contact name is provided"
            )
        
        return attrs


class ProgressNoteSerializer(serializers.ModelSerializer):
    """SOAP Notes serializer for psychologists"""
    
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    psychologist_name = serializers.CharField(source='psychologist.get_full_name', read_only=True)
    session_date_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = ProgressNote
        fields = [
            'id', 'patient', 'patient_name', 'psychologist', 'psychologist_name',
            'session_date', 'session_date_formatted', 'session_number',
            'subjective', 'objective', 'assessment', 'plan',
            'session_duration', 'progress_rating', 'created_at'
        ]
        read_only_fields = ['id', 'patient_name', 'psychologist_name', 'created_at']
    
    def get_session_date_formatted(self, obj):
        return obj.session_date.strftime('%d/%m/%Y %I:%M %p')


class ProgressNoteCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating progress notes"""
    
    class Meta:
        model = ProgressNote
        fields = [
            'patient', 'session_date', 'session_number',
            'subjective', 'objective', 'assessment', 'plan',
            'session_duration', 'progress_rating'
        ]
    
    def create(self, validated_data):
        # Set psychologist from request user
        validated_data['psychologist'] = self.context['request'].user
        return super().create(validated_data)


class PsychologistDashboardSerializer(serializers.Serializer):
    """Dashboard data for psychologists"""
    
    # Today's statistics
    today_appointments = serializers.IntegerField()
    completed_today = serializers.IntegerField()
    pending_today = serializers.IntegerField()
    
    # Overall statistics
    total_patients = serializers.IntegerField()
    total_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    
    # Data arrays
    upcoming_sessions = serializers.ListField()
    recent_notes = serializers.ListField()
    
    # Quick actions
    quick_actions = serializers.DictField()


class PatientDashboardSerializer(serializers.Serializer):
    """Dashboard data for patients"""
    
    next_appointment = serializers.DictField()
    total_sessions = serializers.IntegerField()
    intake_completed = serializers.BooleanField()
    outstanding_invoices = serializers.IntegerField()
    recent_progress = serializers.ListField()


class DataDeletionRequestSerializer(serializers.ModelSerializer):
    """Serializer for data deletion requests (APP 13)"""
    
    patient_name = serializers.SerializerMethodField()
    patient_email = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()
    can_be_deleted_now = serializers.SerializerMethodField()
    
    class Meta:
        model = DataDeletionRequest
        fields = [
            'id', 'patient', 'patient_name', 'patient_email',
            'request_date', 'reason', 'status',
            'reviewed_by', 'reviewed_by_name', 'reviewed_date',
            'rejection_reason', 'rejection_notes',
            'scheduled_deletion_date', 'deletion_completed_date',
            'retention_period_years', 'earliest_deletion_date',
            'can_be_deleted_now', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'request_date', 'reviewed_by', 'reviewed_date',
            'scheduled_deletion_date', 'deletion_completed_date',
            'earliest_deletion_date', 'created_at', 'updated_at'
        ]
    
    def get_patient_name(self, obj):
        return obj.patient.get_full_name() if obj.patient else None
    
    def get_patient_email(self, obj):
        return obj.patient.email if obj.patient else None
    
    def get_reviewed_by_name(self, obj):
        return obj.reviewed_by.get_full_name() if obj.reviewed_by else None
    
    def get_can_be_deleted_now(self, obj):
        return obj.can_be_deleted_now()


class DataDeletionRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating data deletion requests (patient use)"""
    
    class Meta:
        model = DataDeletionRequest
        fields = ['reason']
    
    def create(self, validated_data):
        """Create deletion request for the authenticated patient"""
        request = self.context.get('request')
        if not request or not request.user.is_patient():
            raise serializers.ValidationError('Only patients can request data deletion')
        
        # Check if there's already a pending request
        existing_request = DataDeletionRequest.objects.filter(
            patient=request.user,
            status__in=[DataDeletionRequest.RequestStatus.PENDING, DataDeletionRequest.RequestStatus.APPROVED]
        ).first()
        
        if existing_request:
            raise serializers.ValidationError(
                f'You already have a {existing_request.get_status_display().lower()} deletion request. '
                f'Request ID: {existing_request.id}'
            )
        
        # Calculate earliest deletion date
        deletion_request = DataDeletionRequest.objects.create(
            patient=request.user,
            **validated_data
        )
        deletion_request.calculate_earliest_deletion_date()
        deletion_request.save()
        
        return deletion_request
