"""
Services app serializers for Psychology Clinic
Handles psychologist profiles, services, and specializations
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Service, Specialization, PsychologistProfile

User = get_user_model()


class SpecializationSerializer(serializers.ModelSerializer):
    """Serializer for psychological specializations"""
    
    class Meta:
        model = Specialization
        fields = ['id', 'name', 'description', 'is_active']


class ServiceSerializer(serializers.ModelSerializer):
    """Serializer for psychology services"""
    
    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 'standard_fee', 'medicare_rebate',
            'out_of_pocket_cost', 'duration_minutes', 'is_active'
        ]


class PsychologistProfileSerializer(serializers.ModelSerializer):
    """Serializer for psychologist profiles with comprehensive information"""
    
    # Related field serializers
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_phone = serializers.CharField(source='user.phone_number', read_only=True)
    user_gender = serializers.SerializerMethodField()
    specializations_list = SpecializationSerializer(source='specializations', many=True, read_only=True)
    services_list = ServiceSerializer(source='services_offered', many=True, read_only=True)
    
    # Computed fields
    is_ahpra_current = serializers.BooleanField(read_only=True)
    is_insurance_current = serializers.BooleanField(read_only=True)
    insurance_expires_soon = serializers.BooleanField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    patient_cost_after_rebate = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    languages_list = serializers.ListField(read_only=True)
    session_types_list = serializers.ListField(read_only=True)
    insurance_providers_list = serializers.ListField(read_only=True)
    is_highly_rated = serializers.BooleanField(read_only=True)
    experience_level = serializers.CharField(read_only=True)
    
    # Profile image with full URL
    profile_image_url = serializers.SerializerMethodField()
    has_profile_image = serializers.SerializerMethodField()
    
    # Availability field
    next_available_slot = serializers.SerializerMethodField()
    
    class Meta:
        model = PsychologistProfile
        fields = [
            # Basic Information
            'id', 'user', 'user_name', 'user_email', 'user_phone', 'user_gender',
            'display_name', 'profile_image', 'profile_image_url', 'has_profile_image',
            
            # Professional Credentials
            'ahpra_registration_number', 'ahpra_expiry_date', 'is_ahpra_current',
            'title', 'qualifications', 'years_experience', 'experience_level',
            
            # Professional Indemnity Insurance
            'has_professional_indemnity_insurance', 'insurance_provider_name',
            'insurance_policy_number', 'insurance_expiry_date', 'is_insurance_current',
            'insurance_expires_soon', 'insurance_coverage_amount', 'insurance_certificate',
            'insurance_last_verified', 'insurance_notes',
            
            # Practice Information
            'consultation_fee', 'medicare_provider_number', 'medicare_rebate_amount',
            'patient_cost_after_rebate', 'is_accepting_new_patients', 'max_patients_per_day',
            
            # Practice Details
            'practice_name', 'practice_address', 'practice_phone', 'practice_email',
            'personal_website',
            
            # Communication
            'languages_spoken', 'languages_list', 'session_types', 'session_types_list',
            
            # Insurance & Billing
            'insurance_providers', 'insurance_providers_list', 'billing_methods',
            
            # Availability Details
            'working_hours', 'working_days', 'start_time', 'end_time',
            'session_duration_minutes', 'break_between_sessions_minutes',
            'telehealth_available', 'in_person_available', 'next_available_slot',
            
            # Professional Statistics
            'total_patients_seen', 'currently_active_patients', 'sessions_completed',
            'average_rating', 'total_reviews', 'is_highly_rated',
            
            # Profile Content
            'bio', 'is_active_practitioner',
            
            # Relationships
            'specializations', 'specializations_list', 'services_offered', 'services_list',
            
            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_ahpra_registration_number(self, value):
        """Validate AHPRA registration number format"""
        import re
        
        if not value:
            raise serializers.ValidationError("AHPRA registration number is required")
        
        # Remove any spaces, dashes, or hyphens for validation
        cleaned_value = value.replace(' ', '').replace('-', '').replace('_', '').upper()
        
        # AHPRA format: 3 uppercase letters + 10 digits
        # Examples: PSY0001234567, PSY1234567890
        pattern = r'^[A-Z]{3}[0-9]{10}$'
        
        if not re.match(pattern, cleaned_value):
            raise serializers.ValidationError(
                "Invalid AHPRA registration number format. "
                "Expected format: 3 letters (e.g., PSY) followed by 10 digits (e.g., PSY0001234567)"
            )
        
        # Check profession code (for psychologists, should be PSY)
        profession_code = cleaned_value[:3]
        
        # For psychologists, ensure it starts with PSY
        # Check if this is for a psychologist profile
        if hasattr(self, 'instance') and self.instance:
            user = getattr(self.instance, 'user', None)
            if user and user.role == 'psychologist' and profession_code != 'PSY':
                raise serializers.ValidationError(
                    "Psychologists must have an AHPRA number starting with 'PSY'"
                )
        
        # Return cleaned value (normalized format)
        return cleaned_value
    
    def validate_consultation_fee(self, value):
        """Validate consultation fee is positive"""
        if value <= 0:
            raise serializers.ValidationError("Consultation fee must be positive")
        return value
    
    def get_profile_image_url(self, obj):
        """Get full URL for profile image"""
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                try:
                    return request.build_absolute_uri(obj.profile_image.url)
                except Exception:
                    # Fallback to relative URL if absolute URL generation fails
                    return obj.profile_image.url
            return obj.profile_image.url
        return None
    
    def get_has_profile_image(self, obj):
        """Check if psychologist has a profile image"""
        return bool(obj.profile_image)
    
    def get_next_available_slot(self, obj):
        """Get the next available appointment slot"""
        try:
            next_slot = obj.get_next_available_slot()
            if next_slot:
                return next_slot.isoformat()
            return None
        except Exception:
            return None
    
    def get_user_gender(self, obj):
        """Get user gender from the related user"""
        return obj.user.gender if obj.user else None


class PsychologistProfileCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating psychologist profiles"""
    
    class Meta:
        model = PsychologistProfile
        fields = [
            'ahpra_registration_number', 'ahpra_expiry_date',
            'title', 'qualifications', 'years_experience',
            'consultation_fee', 'medicare_provider_number',
            'is_accepting_new_patients', 'max_patients_per_day',
            'bio', 'profile_image', 'specializations', 'services_offered'
        ]
    
    def create(self, validated_data):
        """Create psychologist profile with user relationship"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class PsychologistProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating psychologist profiles - editable fields only"""
    
    # Allow working_days to accept both array and string
    working_days = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = PsychologistProfile
        fields = [
            # Professional Information (Editable)
            'title', 'qualifications', 'years_experience', 'bio',
            
            # Practice Details (Editable)
            'practice_name', 'practice_address', 'practice_phone', 'practice_email', 'personal_website',
            
            # Communication (Editable)
            'languages_spoken', 'session_types',
            
            # Insurance & Billing (Editable)
            'insurance_providers', 'billing_methods', 'medicare_rebate_amount',
            
            # Availability (Editable)
            'working_hours', 'working_days', 'start_time', 'end_time',
            'session_duration_minutes', 'break_between_sessions_minutes',
            'telehealth_available', 'in_person_available',
            
            # Profile & Settings (Editable)
            'profile_image', 'specializations', 'services_offered',
            'is_accepting_new_patients', 'max_patients_per_day', 'is_active_practitioner'
        ]
    
    def validate_working_days(self, value):
        """Convert array to comma-separated string if needed"""
        if isinstance(value, list):
            # Convert array to comma-separated string
            return ','.join(str(day).strip() for day in value if day)
        return value
    
    def update(self, instance, validated_data):
        """Update psychologist profile"""
        # Handle many-to-many relationships
        specializations = validated_data.pop('specializations', None)
        services_offered = validated_data.pop('services_offered', None)
        
        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        # Update many-to-many relationships
        if specializations is not None:
            instance.specializations.set(specializations)
        
        if services_offered is not None:
            instance.services_offered.set(services_offered)
        
        return instance


class PsychologistProfileImageSerializer(serializers.ModelSerializer):
    """Serializer for updating psychologist profile image"""
    
    class Meta:
        model = PsychologistProfile
        fields = ['profile_image']
    
    def update(self, instance, validated_data):
        """Update only the profile image"""
        instance.profile_image = validated_data.get('profile_image', instance.profile_image)
        instance.save()
        return instance


class PsychologistAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for psychologist availability settings"""
    
    class Meta:
        model = PsychologistProfile
        fields = [
            'is_accepting_new_patients', 'max_patients_per_day',
            'is_active_practitioner'
        ]


class PsychologistAdminUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin/system updates - includes statistics and AHPRA"""
    
    class Meta:
        model = PsychologistProfile
        fields = [
            # AHPRA Information (Admin Only)
            'ahpra_registration_number', 'ahpra_expiry_date',
            
            # Professional Fees (Admin Only)
            'consultation_fee', 'medicare_provider_number',
            
            # Statistics (System Generated)
            'total_patients_seen', 'currently_active_patients', 'sessions_completed',
            'average_rating', 'total_reviews',
            
            # Status (Admin Only)
            'is_active_practitioner'
        ]


class PsychologistPublicSerializer(serializers.ModelSerializer):
    """Serializer for public/patient view - read-only comprehensive profile"""
    
    # Related field serializers
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_gender = serializers.CharField(source='user.gender', read_only=True)
    display_name = serializers.CharField(read_only=True)
    specializations_list = SpecializationSerializer(source='specializations', many=True, read_only=True)
    services_list = ServiceSerializer(source='services_offered', many=True, read_only=True)
    
    # Computed fields
    is_ahpra_current = serializers.BooleanField(read_only=True)
    patient_cost_after_rebate = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    languages_list = serializers.ListField(read_only=True)
    session_types_list = serializers.ListField(read_only=True)
    insurance_providers_list = serializers.ListField(read_only=True)
    is_highly_rated = serializers.BooleanField(read_only=True)
    experience_level = serializers.CharField(read_only=True)
    working_days_list = serializers.ListField(read_only=True)
    
    # Profile image fields
    profile_image_url = serializers.SerializerMethodField()
    has_profile_image = serializers.SerializerMethodField()
    
    # Availability fields
    next_available_slot = serializers.SerializerMethodField()
    
    class Meta:
        model = PsychologistProfile
        fields = [
            # Basic Information (Public)
            'id', 'user_name', 'user_gender', 'display_name', 'title', 'profile_image', 'profile_image_url', 'has_profile_image',
            
            # Professional Credentials (Public)
            'ahpra_registration_number', 'qualifications', 'years_experience', 'experience_level', 'is_ahpra_current',
            
            # Practice Information (Public)
            'consultation_fee', 'medicare_rebate_amount', 'patient_cost_after_rebate',
            'is_accepting_new_patients', 'is_active_practitioner',
            
            # Practice Details (Public)
            'practice_name', 'practice_address', 'practice_phone', 'practice_email', 'personal_website',
            
            # Communication (Public)
            'languages_spoken', 'languages_list', 'session_types', 'session_types_list',
            
            # Insurance & Billing (Public)
            'insurance_providers', 'insurance_providers_list', 'billing_methods',
            
            # Availability (Public)
            'working_hours', 'working_days', 'working_days_list', 'start_time', 'end_time',
            'session_duration_minutes', 'break_between_sessions_minutes',
            'telehealth_available', 'in_person_available', 'next_available_slot',
            
            # Professional Statistics (Public)
            'total_patients_seen', 'average_rating', 'total_reviews', 'is_highly_rated',
            
            # Profile Content (Public)
            'bio',
            
            # Relationships (Public)
            'specializations_list', 'services_list'
        ]
    
    def get_profile_image_url(self, obj):
        """Get full URL for profile image"""
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                try:
                    return request.build_absolute_uri(obj.profile_image.url)
                except Exception:
                    # Fallback to relative URL if absolute URL generation fails
                    return obj.profile_image.url
            return obj.profile_image.url
        return None
    
    def get_has_profile_image(self, obj):
        """Check if psychologist has a profile image"""
        return bool(obj.profile_image)
    
    def get_next_available_slot(self, obj):
        """Get the next available appointment slot"""
        try:
            next_slot = obj.get_next_available_slot()
            if next_slot:
                return next_slot.isoformat()
            return None
        except Exception:
            return None
    
    def get_next_available_slot(self, obj):
        """Get the next available appointment slot"""
        try:
            next_slot = obj.get_next_available_slot()
            if next_slot:
                return next_slot.isoformat()
            return None
        except Exception:
            return None


class PsychologistListSerializer(serializers.ModelSerializer):
    """Simplified serializer for psychologist listings"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_gender = serializers.CharField(source='user.gender', read_only=True)
    display_name = serializers.CharField(read_only=True)
    specializations_list = SpecializationSerializer(source='specializations', many=True, read_only=True)
    services_list = ServiceSerializer(source='services_offered', many=True, read_only=True)
    
    # Computed fields
    is_ahpra_current = serializers.BooleanField(read_only=True)
    experience_level = serializers.CharField(read_only=True)
    working_days_list = serializers.ListField(read_only=True)
    session_types_list = serializers.ListField(read_only=True)
    patient_cost_after_rebate = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    
    # Profile image fields
    profile_image_url = serializers.SerializerMethodField()
    has_profile_image = serializers.SerializerMethodField()
    
    # Availability field
    next_available_slot = serializers.SerializerMethodField()
    
    class Meta:
        model = PsychologistProfile
        fields = [
            # Basic Info
            'id', 'user_name', 'user_gender', 'display_name', 'title', 
            'profile_image', 'profile_image_url', 'has_profile_image',
            
            # Professional Details
            'ahpra_registration_number', 'is_ahpra_current', 'qualifications', 
            'years_experience', 'experience_level',
            
            # Pricing
            'consultation_fee', 'medicare_rebate_amount', 'patient_cost_after_rebate',
            
            # Availability
            'is_accepting_new_patients', 'telehealth_available', 'in_person_available',
            'working_days', 'working_days_list', 'start_time', 'end_time',
            'session_types', 'session_types_list', 'next_available_slot',
            
            # Profile
            'bio', 'average_rating', 'total_reviews',
            
            # Relationships
            'specializations_list', 'services_list', 'is_active_practitioner'
        ]
    
    def get_profile_image_url(self, obj):
        """Get full URL for profile image"""
        if obj.profile_image:
            request = self.context.get('request')
            if request:
                try:
                    return request.build_absolute_uri(obj.profile_image.url)
                except Exception:
                    # Fallback to relative URL if absolute URL generation fails
                    return obj.profile_image.url
            return obj.profile_image.url
        return None
    
    def get_has_profile_image(self, obj):
        """Check if psychologist has a profile image"""
        return bool(obj.profile_image)
    
    def get_next_available_slot(self, obj):
        """Get the next available appointment slot"""
        try:
            next_slot = obj.get_next_available_slot()
            if next_slot:
                return next_slot.isoformat()
            return None
        except Exception:
            return None
