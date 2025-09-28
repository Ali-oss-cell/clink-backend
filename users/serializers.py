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
    """Complete intake form serializer for React frontend"""
    
    # User fields (pre-filled from login)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number')
    date_of_birth = serializers.DateField(source='user.date_of_birth')
    address_line_1 = serializers.CharField(source='user.address_line_1')
    suburb = serializers.CharField(source='user.suburb')
    state = serializers.CharField(source='user.state')
    postcode = serializers.CharField(source='user.postcode')
    medicare_number = serializers.CharField(source='user.medicare_number')
    
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
    
    def update(self, instance, validated_data):
        # Update user fields
        user_data = {}
        user_fields = ['first_name', 'last_name', 'phone_number', 'date_of_birth',
                      'address_line_1', 'suburb', 'state', 'postcode', 'medicare_number']
        
        for field in user_fields:
            if field in validated_data:
                user_data[field] = validated_data.pop(field)
        
        if user_data:
            for key, value in user_data.items():
                setattr(instance.user, key, value)
            instance.user.save()
        
        # Update patient profile fields
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        
        return instance


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
    
    today_appointments = serializers.IntegerField()
    total_patients = serializers.IntegerField()
    pending_notes = serializers.IntegerField()
    upcoming_sessions = serializers.ListField()
    recent_notes = ProgressNoteSerializer(many=True)


class PatientDashboardSerializer(serializers.Serializer):
    """Dashboard data for patients"""
    
    next_appointment = serializers.DictField()
    total_sessions = serializers.IntegerField()
    intake_completed = serializers.BooleanField()
    outstanding_invoices = serializers.IntegerField()
    recent_progress = serializers.ListField()
