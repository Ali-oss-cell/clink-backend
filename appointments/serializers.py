"""
Appointment serializers for Psychology Clinic
Handles appointment booking, availability, and scheduling
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Appointment, AvailabilitySlot, TimeSlot
from users.models import User
from services.models import Service


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointment data with related information"""
    
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    psychologist_name = serializers.CharField(source='psychologist.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    formatted_date = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'psychologist', 'psychologist_name',
            'service', 'service_name', 'appointment_date', 'formatted_date',
            'duration_minutes', 'duration_hours', 'status', 'status_display',
            'session_type', 'notes', 'video_room_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_formatted_date(self, obj):
        """Format appointment date for display"""
        return obj.appointment_date.strftime('%d/%m/%Y %I:%M %p')
    
    def get_duration_hours(self, obj):
        """Convert duration to hours for display"""
        return round(obj.duration_minutes / 60, 1)
    
    def validate_appointment_date(self, value):
        """Validate appointment date is in the future"""
        if value <= timezone.now():
            raise serializers.ValidationError("Appointment date must be in the future")
        return value
    
    def validate(self, data):
        """Validate appointment data"""
        # Check if psychologist is available at the requested time
        psychologist = data.get('psychologist')
        appointment_date = data.get('appointment_date')
        
        if psychologist and appointment_date:
            # Check for existing appointments at the same time
            existing_appointment = Appointment.objects.filter(
                psychologist=psychologist,
                appointment_date=appointment_date
            ).exclude(id=self.instance.id if self.instance else None)
            
            if existing_appointment.exists():
                raise serializers.ValidationError(
                    "Psychologist is not available at this time"
                )
        
        return data


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new appointments"""
    
    class Meta:
        model = Appointment
        fields = [
            'patient', 'psychologist', 'service', 'appointment_date',
            'duration_minutes', 'notes'
        ]
    
    def validate_appointment_date(self, value):
        """Validate appointment date"""
        if value <= timezone.now():
            raise serializers.ValidationError("Appointment date must be in the future")
        
        # Check if appointment is during business hours (9 AM - 5 PM)
        if value.hour < 9 or value.hour >= 17:
            raise serializers.ValidationError("Appointments must be between 9 AM and 5 PM")
        
        return value
    
    def validate(self, data):
        """Validate appointment creation"""
        psychologist = data.get('psychologist')
        appointment_date = data.get('appointment_date')
        
        if psychologist and appointment_date:
            # Check if psychologist has availability on this day
            day_of_week = appointment_date.weekday()
            availability = AvailabilitySlot.objects.filter(
                psychologist=psychologist,
                day_of_week=day_of_week,
                is_available=True
            ).exists()
            
            if not availability:
                raise serializers.ValidationError(
                    "Psychologist is not available on this day"
                )
        
        return data


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    """Serializer for psychologist availability slots"""
    
    psychologist_name = serializers.CharField(source='psychologist.get_full_name', read_only=True)
    day_name = serializers.SerializerMethodField()
    formatted_time = serializers.SerializerMethodField()
    
    class Meta:
        model = AvailabilitySlot
        fields = [
            'id', 'psychologist', 'psychologist_name', 'day_of_week', 'day_name',
            'start_time', 'end_time', 'formatted_time', 'is_available', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_day_name(self, obj):
        """Get day name from day_of_week number"""
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[obj.day_of_week]
    
    def get_formatted_time(self, obj):
        """Format time range for display"""
        return f"{obj.start_time.strftime('%I:%M %p')} - {obj.end_time.strftime('%I:%M %p')}"


class TimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for available time slots"""
    
    psychologist_name = serializers.CharField(source='psychologist.get_full_name', read_only=True)
    appointment_details = AppointmentSerializer(source='appointment', read_only=True)
    formatted_datetime = serializers.SerializerMethodField()
    is_booked = serializers.SerializerMethodField()
    
    class Meta:
        model = TimeSlot
        fields = [
            'id', 'psychologist', 'psychologist_name', 'date', 'start_time', 'end_time',
            'formatted_datetime', 'is_available', 'is_booked', 'appointment', 'appointment_details'
        ]
        read_only_fields = ['id']
    
    def get_formatted_datetime(self, obj):
        """Format datetime for display"""
        return obj.start_time.strftime('%d/%m/%Y %I:%M %p')
    
    def get_is_booked(self, obj):
        """Check if time slot is booked"""
        return obj.appointment is not None


class BookAppointmentSerializer(serializers.Serializer):
    """Serializer for booking appointments"""
    
    psychologist_id = serializers.IntegerField()
    service_id = serializers.IntegerField()
    appointment_date = serializers.DateTimeField()
    duration_minutes = serializers.IntegerField(default=60)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_appointment_date(self, value):
        """Validate appointment date"""
        if value <= timezone.now():
            raise serializers.ValidationError("Appointment date must be in the future")
        return value
    
    def validate(self, data):
        """Validate booking data"""
        psychologist_id = data.get('psychologist_id')
        appointment_date = data.get('appointment_date')
        
        # Check if psychologist exists
        try:
            psychologist = User.objects.get(id=psychologist_id, role=User.UserRole.PSYCHOLOGIST)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid psychologist ID")
        
        # Check if psychologist is available
        day_of_week = appointment_date.weekday()
        availability = AvailabilitySlot.objects.filter(
            psychologist=psychologist,
            day_of_week=day_of_week,
            is_available=True
        ).exists()
        
        if not availability:
            raise serializers.ValidationError("Psychologist is not available on this day")
        
        # Check for existing appointment
        existing_appointment = Appointment.objects.filter(
            psychologist=psychologist,
            appointment_date=appointment_date
        ).exists()
        
        if existing_appointment:
            raise serializers.ValidationError("Time slot is already booked")
        
        return data


class AppointmentStatusSerializer(serializers.Serializer):
    """Serializer for updating appointment status"""
    
    status = serializers.ChoiceField(choices=Appointment._meta.get_field('status').choices)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_status(self, value):
        """Validate status transition"""
        # Add business logic for status transitions here
        return value


class PsychologistAvailabilitySerializer(serializers.Serializer):
    """Serializer for psychologist availability data"""
    
    psychologist_id = serializers.IntegerField()
    date = serializers.DateField()
    available_slots = TimeSlotSerializer(many=True, read_only=True)
    
    def validate_date(self, value):
        """Validate date is in the future"""
        if value < timezone.now().date():
            raise serializers.ValidationError("Date must be in the future")
        return value


class AppointmentSummarySerializer(serializers.Serializer):
    """Serializer for appointment summary data"""
    
    total_appointments = serializers.IntegerField()
    upcoming_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    cancelled_appointments = serializers.IntegerField()
    next_appointment = AppointmentSerializer(read_only=True)
    recent_appointments = AppointmentSerializer(many=True, read_only=True)


class PatientAppointmentDetailSerializer(serializers.ModelSerializer):
    """
    Detailed appointment serializer for patient portal
    Provides comprehensive appointment information with formatted fields
    """
    
    formatted_date = serializers.SerializerMethodField()
    formatted_time = serializers.SerializerMethodField()
    psychologist = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    meeting_link = serializers.SerializerMethodField()
    can_reschedule = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    reschedule_deadline = serializers.SerializerMethodField()
    cancellation_deadline = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id',
            'appointment_date',
            'formatted_date',
            'formatted_time',
            'duration_minutes',
            'session_type',
            'status',
            'psychologist',
            'location',
            'meeting_link',
            'notes',
            'can_reschedule',
            'can_cancel',
            'reschedule_deadline',
            'cancellation_deadline'
        ]
    
    def get_formatted_date(self, obj):
        """Format date as YYYY-MM-DD"""
        return obj.appointment_date.strftime('%Y-%m-%d')
    
    def get_formatted_time(self, obj):
        """Format time as HH:MM AM/PM"""
        return obj.appointment_date.strftime('%I:%M %p')
    
    def get_psychologist(self, obj):
        """Get psychologist details with profile information"""
        psychologist = obj.psychologist
        profile_image_url = None
        title = "Psychologist"
        
        # Get profile image if available
        if hasattr(psychologist, 'psychologist_profile'):
            profile = psychologist.psychologist_profile
            if profile.profile_image:
                request = self.context.get('request')
                if request:
                    profile_image_url = request.build_absolute_uri(profile.profile_image.url)
            title = profile.title or "Dr"
        
        return {
            'name': f"{title}. {psychologist.get_full_name()}",
            'title': "Clinical Psychologist",
            'profile_image_url': profile_image_url
        }
    
    def get_location(self, obj):
        """Get appointment location based on session type"""
        if obj.session_type == 'in_person':
            # Get psychologist's practice address if available
            if hasattr(obj.psychologist, 'psychologist_profile'):
                profile = obj.psychologist.psychologist_profile
                if profile.practice_name:
                    return f"{profile.practice_name}"
            return "MindWell Clinic"
        return None
    
    def get_meeting_link(self, obj):
        """Get meeting link for telehealth sessions"""
        if obj.session_type == 'telehealth' and obj.video_room_id:
            # Generate meeting link based on video room ID
            request = self.context.get('request')
            if request:
                base_url = request.build_absolute_uri('/').rstrip('/')
                return f"{base_url}/video-session/{obj.video_room_id}"
        return None
    
    def get_can_reschedule(self, obj):
        """Check if appointment can be rescheduled (at least 48 hours before)"""
        if obj.status in ['completed', 'cancelled', 'no_show']:
            return False
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        reschedule_deadline = obj.appointment_date - timedelta(hours=48)
        return now < reschedule_deadline
    
    def get_can_cancel(self, obj):
        """Check if appointment can be cancelled (at least 24 hours before)"""
        if obj.status in ['completed', 'cancelled', 'no_show']:
            return False
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        cancellation_deadline = obj.appointment_date - timedelta(hours=24)
        return now < cancellation_deadline
    
    def get_reschedule_deadline(self, obj):
        """Get reschedule deadline (48 hours before appointment)"""
        from datetime import timedelta
        deadline = obj.appointment_date - timedelta(hours=48)
        return deadline.isoformat()
    
    def get_cancellation_deadline(self, obj):
        """Get cancellation deadline (24 hours before appointment)"""
        from datetime import timedelta
        deadline = obj.appointment_date - timedelta(hours=24)
        return deadline.isoformat()
    
    def get_status(self, obj):
        """
        Map database status to frontend status
        - scheduled/confirmed -> 'upcoming'
        - completed -> 'completed'
        - cancelled -> 'cancelled'
        - no_show -> 'no_show'
        """
        from django.utils import timezone
        
        if obj.status in ['scheduled', 'confirmed']:
            # Check if appointment is in the past
            if obj.appointment_date < timezone.now():
                return 'past'
            return 'upcoming'
        elif obj.status == 'completed':
            return 'completed'
        elif obj.status == 'cancelled':
            return 'cancelled'
        elif obj.status == 'no_show':
            return 'no_show'
        
        return 'upcoming'
