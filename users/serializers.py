"""
Serializers for Psychology Clinic User Management
Supports intake forms, progress notes, and role-based data access
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PatientProfile, ProgressNote

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for authentication responses"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'role', 'phone_number', 'date_of_birth', 'age', 'is_verified',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_age(self, obj):
        return obj.age if hasattr(obj, 'age') else None


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
            'therapy_goals', 'consent_to_treatment', 'consent_to_telehealth',
            'client_signature', 'consent_date', 'intake_completed', 'created_at'
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
            'therapy_goals', 'consent_to_treatment', 'consent_to_telehealth',
            'client_signature', 'consent_date', 'intake_completed'
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
        """
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
