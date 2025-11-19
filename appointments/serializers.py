"""
Appointment serializers for Psychology Clinic
Handles appointment booking, availability, and scheduling
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Appointment, AvailabilitySlot, TimeSlot, SessionRecording
from users.models import User
from services.models import Service


class AppointmentListSerializer(serializers.ModelSerializer):
    """Serializer for appointment list view (admin/manager) - Frontend ready format"""
    
    patient_name = serializers.SerializerMethodField()
    psychologist_name = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    appointment_date = serializers.SerializerMethodField()
    appointment_time = serializers.SerializerMethodField()
    
    # Timer fields for session countdown and duration
    session_start_time = serializers.SerializerMethodField()
    session_end_time = serializers.SerializerMethodField()
    time_until_start_seconds = serializers.SerializerMethodField()
    time_remaining_seconds = serializers.SerializerMethodField()
    session_status = serializers.SerializerMethodField()
    can_join_session = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'psychologist', 'psychologist_name',
            'service', 'service_name', 'appointment_date', 'appointment_time',
            'duration_minutes', 'status', 'status_display', 'session_type',
            'session_start_time', 'session_end_time', 'time_until_start_seconds',
            'time_remaining_seconds', 'session_status', 'can_join_session',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        """Get patient full name safely"""
        if obj.patient:
            return obj.patient.get_full_name() or obj.patient.email
        return None
    
    def get_psychologist_name(self, obj):
        """Get psychologist full name safely"""
        if obj.psychologist:
            return obj.psychologist.get_full_name() or obj.psychologist.email
        return None
    
    def get_service_name(self, obj):
        """Get service name safely"""
        if obj.service:
            return obj.service.name
        return None
    
    def get_appointment_date(self, obj):
        """Return date in YYYY-MM-DD format"""
        if obj.appointment_date:
            return obj.appointment_date.date().isoformat()
        return None
    
    def get_appointment_time(self, obj):
        """Return time in HH:MM:SS format"""
        if obj.appointment_date:
            return obj.appointment_date.time().strftime('%H:%M:%S')
        return None
    
    def get_session_start_time(self, obj):
        """Return session start time as ISO format string"""
        if obj.appointment_date:
            return obj.appointment_date.isoformat()
        return None
    
    def get_session_end_time(self, obj):
        """Return session end time as ISO format string"""
        if obj.appointment_date and obj.duration_minutes:
            from datetime import timedelta
            end_time = obj.appointment_date + timedelta(minutes=obj.duration_minutes)
            return end_time.isoformat()
        return None
    
    def get_time_until_start_seconds(self, obj):
        """
        Calculate seconds until session starts
        Returns negative if session has already started
        """
        if not obj.appointment_date:
            return None
        
        from django.utils import timezone
        now = timezone.now()
        time_until = (obj.appointment_date - now).total_seconds()
        return int(time_until)
    
    def get_time_remaining_seconds(self, obj):
        """
        Calculate seconds remaining in session
        Returns None if session hasn't started or has ended
        """
        if not obj.appointment_date or not obj.duration_minutes:
            return None
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        start_time = obj.appointment_date
        end_time = start_time + timedelta(minutes=obj.duration_minutes)
        
        # If session hasn't started yet
        if now < start_time:
            return None
        
        # If session has ended
        if now >= end_time:
            return 0
        
        # Session is in progress
        time_remaining = (end_time - now).total_seconds()
        return int(time_remaining)
    
    def get_session_status(self, obj):
        """
        Return session status for timer display
        - 'upcoming': Session hasn't started yet
        - 'starting_soon': Starts in less than 5 minutes
        - 'in_progress': Session is currently happening
        - 'ended': Session has ended
        """
        if not obj.appointment_date or not obj.duration_minutes:
            return 'unknown'
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        start_time = obj.appointment_date
        end_time = start_time + timedelta(minutes=obj.duration_minutes)
        
        # Session has ended
        if now >= end_time:
            return 'ended'
        
        # Session is in progress
        if now >= start_time:
            return 'in_progress'
        
        # Session hasn't started - check if starting soon
        time_until_start = (start_time - now).total_seconds()
        if time_until_start <= 300:  # 5 minutes
            return 'starting_soon'
        
        return 'upcoming'
    
    def get_can_join_session(self, obj):
        """
        Check if user can join the video session
        - Can join 5 minutes before start time
        - Can join during session
        - Cannot join after session ends
        """
        if obj.session_type != 'telehealth' or not obj.video_room_id:
            return False
        
        if not obj.appointment_date or not obj.duration_minutes:
            return False
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        start_time = obj.appointment_date
        end_time = start_time + timedelta(minutes=obj.duration_minutes)
        
        # Can join 5 minutes before start
        join_window_start = start_time - timedelta(minutes=5)
        
        # Can join if within join window
        return join_window_start <= now <= end_time


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointment data with related information"""
    
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    psychologist_name = serializers.CharField(source='psychologist.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    formatted_date = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Timer fields for session countdown and duration
    session_start_time = serializers.SerializerMethodField()
    session_end_time = serializers.SerializerMethodField()
    time_until_start_seconds = serializers.SerializerMethodField()
    time_remaining_seconds = serializers.SerializerMethodField()
    session_status = serializers.SerializerMethodField()
    can_join_session = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'psychologist', 'psychologist_name',
            'service', 'service_name', 'appointment_date', 'formatted_date',
            'duration_minutes', 'duration_hours', 'status', 'status_display',
            'session_type', 'session_start_time', 'session_end_time',
            'time_until_start_seconds', 'time_remaining_seconds', 'session_status',
            'can_join_session', 'notes', 'video_room_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_formatted_date(self, obj):
        """Format appointment date for display"""
        return obj.appointment_date.strftime('%d/%m/%Y %I:%M %p')
    
    def get_duration_hours(self, obj):
        """Convert duration to hours for display"""
        return round(obj.duration_minutes / 60, 1)
    
    def get_session_start_time(self, obj):
        """Return session start time as ISO format string"""
        if obj.appointment_date:
            return obj.appointment_date.isoformat()
        return None
    
    def get_session_end_time(self, obj):
        """Return session end time as ISO format string"""
        if obj.appointment_date and obj.duration_minutes:
            from datetime import timedelta
            end_time = obj.appointment_date + timedelta(minutes=obj.duration_minutes)
            return end_time.isoformat()
        return None
    
    def get_time_until_start_seconds(self, obj):
        """
        Calculate seconds until session starts
        Returns negative if session has already started
        """
        if not obj.appointment_date:
            return None
        
        from django.utils import timezone
        now = timezone.now()
        time_until = (obj.appointment_date - now).total_seconds()
        return int(time_until)
    
    def get_time_remaining_seconds(self, obj):
        """
        Calculate seconds remaining in session
        Returns None if session hasn't started or has ended
        """
        if not obj.appointment_date or not obj.duration_minutes:
            return None
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        start_time = obj.appointment_date
        end_time = start_time + timedelta(minutes=obj.duration_minutes)
        
        # If session hasn't started yet
        if now < start_time:
            return None
        
        # If session has ended
        if now >= end_time:
            return 0
        
        # Session is in progress
        time_remaining = (end_time - now).total_seconds()
        return int(time_remaining)
    
    def get_session_status(self, obj):
        """
        Return session status for timer display
        - 'upcoming': Session hasn't started yet
        - 'starting_soon': Starts in less than 5 minutes
        - 'in_progress': Session is currently happening
        - 'ended': Session has ended
        """
        if not obj.appointment_date or not obj.duration_minutes:
            return 'unknown'
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        start_time = obj.appointment_date
        end_time = start_time + timedelta(minutes=obj.duration_minutes)
        
        # Session has ended
        if now >= end_time:
            return 'ended'
        
        # Session is in progress
        if now >= start_time:
            return 'in_progress'
        
        # Session hasn't started - check if starting soon
        time_until_start = (start_time - now).total_seconds()
        if time_until_start <= 300:  # 5 minutes
            return 'starting_soon'
        
        return 'upcoming'
    
    def get_can_join_session(self, obj):
        """
        Check if user can join the video session
        - Can join 5 minutes before start time
        - Can join during session
        - Cannot join after session ends
        """
        if obj.session_type != 'telehealth' or not obj.video_room_id:
            return False
        
        if not obj.appointment_date or not obj.duration_minutes:
            return False
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        start_time = obj.appointment_date
        end_time = start_time + timedelta(minutes=obj.duration_minutes)
        
        # Can join 5 minutes before start
        join_window_start = start_time - timedelta(minutes=5)
        
        # Can join if within join window
        return join_window_start <= now <= end_time
    
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


class PsychologistScheduleSerializer(serializers.ModelSerializer):
    """
    Serializer for psychologist schedule page
    Returns appointments in the exact format expected by the frontend
    """
    
    patient_id = serializers.IntegerField(source='patient.id', read_only=True)
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    formatted_date = serializers.SerializerMethodField()
    formatted_time = serializers.SerializerMethodField()
    meeting_link = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    
    # Timer fields for session countdown and duration
    session_start_time = serializers.SerializerMethodField()
    session_end_time = serializers.SerializerMethodField()
    time_until_start_seconds = serializers.SerializerMethodField()
    time_remaining_seconds = serializers.SerializerMethodField()
    session_status = serializers.SerializerMethodField()
    can_join_session = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id',
            'patient_id',
            'patient_name',
            'service_name',
            'appointment_date',
            'formatted_date',
            'formatted_time',
            'duration_minutes',
            'session_type',
            'status',
            'session_start_time',
            'session_end_time',
            'time_until_start_seconds',
            'time_remaining_seconds',
            'session_status',
            'can_join_session',
            'notes',
            'location',
            'meeting_link'
        ]
        read_only_fields = ['id', 'patient_id', 'patient_name', 'service_name']
    
    def get_formatted_date(self, obj):
        """Format date as "20 Jul 2024" """
        return obj.appointment_date.strftime('%d %b %Y')
    
    def get_formatted_time(self, obj):
        """Format time as "10:00 AM" """
        return obj.appointment_date.strftime('%I:%M %p').lstrip('0')
    
    def get_meeting_link(self, obj):
        """Generate meeting link from video_room_id if telehealth"""
        if obj.session_type == 'telehealth' and obj.video_room_id:
            # Generate meeting link from video room ID
            # Adjust this URL format based on your video service (Twilio, Zoom, etc.)
            from django.conf import settings
            base_url = getattr(settings, 'VIDEO_MEETING_BASE_URL', 'https://meet.psychologyclinic.com.au')
            return f"{base_url}/{obj.video_room_id}"
        return None
    
    def get_session_start_time(self, obj):
        """Return session start time as ISO format string"""
        if obj.appointment_date:
            return obj.appointment_date.isoformat()
        return None
    
    def get_session_end_time(self, obj):
        """Return session end time as ISO format string"""
        if obj.appointment_date and obj.duration_minutes:
            from datetime import timedelta
            end_time = obj.appointment_date + timedelta(minutes=obj.duration_minutes)
            return end_time.isoformat()
        return None
    
    def get_time_until_start_seconds(self, obj):
        """
        Calculate seconds until session starts
        Returns negative if session has already started
        """
        if not obj.appointment_date:
            return None
        
        from django.utils import timezone
        now = timezone.now()
        time_until = (obj.appointment_date - now).total_seconds()
        return int(time_until)
    
    def get_time_remaining_seconds(self, obj):
        """
        Calculate seconds remaining in session
        Returns None if session hasn't started or has ended
        """
        if not obj.appointment_date or not obj.duration_minutes:
            return None
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        start_time = obj.appointment_date
        end_time = start_time + timedelta(minutes=obj.duration_minutes)
        
        # If session hasn't started yet
        if now < start_time:
            return None
        
        # If session has ended
        if now >= end_time:
            return 0
        
        # Session is in progress
        time_remaining = (end_time - now).total_seconds()
        return int(time_remaining)
    
    def get_session_status(self, obj):
        """
        Return session status for timer display
        - 'upcoming': Session hasn't started yet
        - 'starting_soon': Starts in less than 5 minutes
        - 'in_progress': Session is currently happening
        - 'ended': Session has ended
        """
        if not obj.appointment_date or not obj.duration_minutes:
            return 'unknown'
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        start_time = obj.appointment_date
        end_time = start_time + timedelta(minutes=obj.duration_minutes)
        
        # Session has ended
        if now >= end_time:
            return 'ended'
        
        # Session is in progress
        if now >= start_time:
            return 'in_progress'
        
        # Session hasn't started - check if starting soon
        time_until_start = (start_time - now).total_seconds()
        if time_until_start <= 300:  # 5 minutes
            return 'starting_soon'
        
        return 'upcoming'
    
    def get_can_join_session(self, obj):
        """
        Check if user can join the video session
        - Can join 5 minutes before start time
        - Can join during session
        - Cannot join after session ends
        """
        if obj.session_type != 'telehealth' or not obj.video_room_id:
            return False
        
        if not obj.appointment_date or not obj.duration_minutes:
            return False
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        start_time = obj.appointment_date
        end_time = start_time + timedelta(minutes=obj.duration_minutes)
        
        # Can join 5 minutes before start
        join_window_start = start_time - timedelta(minutes=5)
        
        # Can join if within join window
        return join_window_start <= now <= end_time
    
    def get_location(self, obj):
        """Get location if in-person appointment"""
        if obj.session_type == 'in_person':
            # You can customize this based on your location field or psychologist's location
            # For now, return a default or psychologist's office location
            if hasattr(obj.psychologist, 'psychologist_profile'):
                profile = obj.psychologist.psychologist_profile
                if hasattr(profile, 'office_address'):
                    return profile.office_address
            return "Clinic Office"  # Default location
        return None


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
    
    # Timer fields for session countdown and duration
    session_start_time = serializers.SerializerMethodField()
    session_end_time = serializers.SerializerMethodField()
    time_until_start_seconds = serializers.SerializerMethodField()
    time_remaining_seconds = serializers.SerializerMethodField()
    session_status = serializers.SerializerMethodField()
    can_join_session = serializers.SerializerMethodField()
    
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
            'cancellation_deadline',
            'session_start_time',
            'session_end_time',
            'time_until_start_seconds',
            'time_remaining_seconds',
            'session_status',
            'can_join_session'
        ]
    
    def get_formatted_date(self, obj):
        """Format date as "Sat, 15 Nov 2025" """
        return obj.appointment_date.strftime('%a, %d %b %Y')
    
    def get_formatted_time(self, obj):
        """Format time as HH:MM AM/PM"""
        return obj.appointment_date.strftime('%I:%M %p')
    
    def get_psychologist(self, obj):
        """Get psychologist details with profile information"""
        psychologist = obj.psychologist
        profile_image_url = None
        title_prefix = "Dr"
        professional_title = "Clinical Psychologist"
        
        # Get profile image and title if available
        if hasattr(psychologist, 'psychologist_profile'):
            profile = psychologist.psychologist_profile
            if profile.profile_image:
                request = self.context.get('request')
                if request:
                    profile_image_url = request.build_absolute_uri(profile.profile_image.url)
            if profile.title:
                title_prefix = profile.title
            # You can customize professional_title based on profile if needed
        
        return {
            'name': f"{title_prefix}. {psychologist.get_full_name()}",
            'title': professional_title,
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
    
    def get_session_start_time(self, obj):
        """Return session start time as ISO format string"""
        if obj.appointment_date:
            return obj.appointment_date.isoformat()
        return None
    
    def get_session_end_time(self, obj):
        """Return session end time as ISO format string"""
        if obj.appointment_date and obj.duration_minutes:
            from datetime import timedelta
            end_time = obj.appointment_date + timedelta(minutes=obj.duration_minutes)
            return end_time.isoformat()
        return None
    
    def get_time_until_start_seconds(self, obj):
        """
        Calculate seconds until session starts
        Returns negative if session has already started
        """
        if not obj.appointment_date:
            return None
        
        from django.utils import timezone
        now = timezone.now()
        time_until = (obj.appointment_date - now).total_seconds()
        return int(time_until)
    
    def get_time_remaining_seconds(self, obj):
        """
        Calculate seconds remaining in session
        Returns None if session hasn't started or has ended
        """
        if not obj.appointment_date or not obj.duration_minutes:
            return None
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        start_time = obj.appointment_date
        end_time = start_time + timedelta(minutes=obj.duration_minutes)
        
        # If session hasn't started yet
        if now < start_time:
            return None
        
        # If session has ended
        if now >= end_time:
            return 0
        
        # Session is in progress
        time_remaining = (end_time - now).total_seconds()
        return int(time_remaining)
    
    def get_session_status(self, obj):
        """
        Return session status for timer display
        - 'upcoming': Session hasn't started yet
        - 'starting_soon': Starts in less than 5 minutes
        - 'in_progress': Session is currently happening
        - 'ended': Session has ended
        """
        if not obj.appointment_date or not obj.duration_minutes:
            return 'unknown'
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        start_time = obj.appointment_date
        end_time = start_time + timedelta(minutes=obj.duration_minutes)
        
        # Session has ended
        if now >= end_time:
            return 'ended'
        
        # Session is in progress
        if now >= start_time:
            return 'in_progress'
        
        # Session hasn't started - check if starting soon
        time_until_start = (start_time - now).total_seconds()
        if time_until_start <= 300:  # 5 minutes
            return 'starting_soon'
        
        return 'upcoming'
    
    def get_can_join_session(self, obj):
        """
        Check if user can join the video session
        - Can join 5 minutes before start time
        - Can join during session
        - Cannot join after session ends
        """
        if obj.session_type != 'telehealth' or not obj.video_room_id:
            return False
        
        if not obj.appointment_date or not obj.duration_minutes:
            return False
        
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        start_time = obj.appointment_date
        end_time = start_time + timedelta(minutes=obj.duration_minutes)
        
        # Can join 5 minutes before start
        join_window_start = start_time - timedelta(minutes=5)
        
        # Can join if within join window
        return join_window_start <= now <= end_time


class SessionRecordingSerializer(serializers.ModelSerializer):
    """Serializer for session recording metadata"""
    
    appointment_id = serializers.IntegerField(source='appointment.id', read_only=True)
    patient_name = serializers.SerializerMethodField()
    psychologist_name = serializers.SerializerMethodField()
    duration_formatted = serializers.CharField(source='duration_formatted', read_only=True)
    size_formatted = serializers.CharField(source='size_formatted', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = SessionRecording
        fields = [
            'id',
            'appointment_id',
            'recording_sid',
            'media_uri',
            'media_external_location',
            'duration',
            'duration_formatted',
            'size',
            'size_formatted',
            'status',
            'status_display',
            'participant_identity',
            'created_at',
            'completed_at',
            'patient_name',
            'psychologist_name',
        ]
        read_only_fields = [
            'id', 'recording_sid', 'media_uri', 'media_external_location',
            'duration', 'size', 'status', 'created_at', 'completed_at'
        ]
    
    def get_patient_name(self, obj):
        """Get patient name"""
        if obj.appointment and obj.appointment.patient:
            return obj.appointment.patient.get_full_name()
        return None
    
    def get_psychologist_name(self, obj):
        """Get psychologist name"""
        if obj.appointment and obj.appointment.psychologist:
            return obj.appointment.psychologist.get_full_name()
        return None


class SessionRecordingListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing recordings"""
    
    appointment_date = serializers.DateTimeField(source='appointment.appointment_date', read_only=True)
    patient_name = serializers.SerializerMethodField()
    psychologist_name = serializers.SerializerMethodField()
    duration_formatted = serializers.CharField(source='duration_formatted', read_only=True)
    size_formatted = serializers.CharField(source='size_formatted', read_only=True)
    
    class Meta:
        model = SessionRecording
        fields = [
            'id',
            'recording_sid',
            'appointment_date',
            'patient_name',
            'psychologist_name',
            'duration',
            'duration_formatted',
            'size',
            'size_formatted',
            'status',
            'created_at',
            'completed_at',
        ]
    
    def get_patient_name(self, obj):
        """Get patient name"""
        if obj.appointment and obj.appointment.patient:
            return obj.appointment.patient.get_full_name()
        return None
    
    def get_psychologist_name(self, obj):
        """Get psychologist name"""
        if obj.appointment and obj.appointment.psychologist:
            return obj.appointment.psychologist.get_full_name()
        return None
