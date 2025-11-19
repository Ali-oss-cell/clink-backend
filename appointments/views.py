"""
Appointments app views - Booking system and scheduling
Complete implementation with appointment management, availability checking, and booking
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib.auth import get_user_model
from datetime import datetime

from .models import Appointment, AvailabilitySlot, TimeSlot, SessionRecording
from .serializers import (
    AppointmentSerializer, AppointmentListSerializer, AppointmentCreateSerializer, AvailabilitySlotSerializer,
    TimeSlotSerializer, BookAppointmentSerializer, AppointmentStatusSerializer,
    PsychologistAvailabilitySerializer, AppointmentSummarySerializer,
    PatientAppointmentDetailSerializer, PsychologistScheduleSerializer,
    SessionRecordingSerializer, SessionRecordingListSerializer
)
from services.models import Service
from audit.utils import log_action

User = get_user_model()


class AppointmentPagination(PageNumberPagination):
    """Custom pagination for appointments list"""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    Complete appointments management with role-based filtering
    
    Provides CRUD operations for appointments with different access levels:
    - Admins/Practice Managers: See all appointments
    - Psychologists: See only their own appointments
    - Patients: See only their own appointments
    """
    
    permission_classes = [IsAuthenticated]
    pagination_class = AppointmentPagination
    
    def get_queryset(self):
        """
        Filter appointments based on user role and permissions
        Supports query parameters: status, psychologist, patient, date_from, date_to
        
        Returns:
            QuerySet: Filtered appointments based on user's role and query parameters
        """
        user = self.request.user
        
        # Base queryset based on role
        if user.is_admin_user() or user.is_practice_manager():
            # Admin and practice managers can see all appointments
            queryset = Appointment.objects.select_related('patient', 'psychologist', 'service').all()
        elif user.is_psychologist():
            # Psychologists can only see their own appointments
            queryset = Appointment.objects.select_related('patient', 'psychologist', 'service').filter(psychologist=user)
        else:
            # Patients can only see their own appointments
            queryset = Appointment.objects.select_related('patient', 'psychologist', 'service').filter(patient=user)
        
        # Apply query parameter filters
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by psychologist ID
        psychologist_id = self.request.query_params.get('psychologist')
        if psychologist_id:
            queryset = queryset.filter(psychologist_id=psychologist_id)
        
        # Filter by patient ID
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date__date__gte=date_from_obj)
            except ValueError:
                pass  # Invalid date format, ignore
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date__date__lte=date_to_obj)
            except ValueError:
                pass  # Invalid date format, ignore
        
        # Order by appointment date (newest first)
        return queryset.order_by('-appointment_date')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            # Use AppointmentListSerializer for list view (admin/manager format)
            return AppointmentListSerializer
        elif self.action == 'create':
            return AppointmentCreateSerializer
        return AppointmentSerializer
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """
        Get upcoming appointments for the current user
        
        Returns appointments that are:
        - In the future (appointment_date >= now)
        - Not completed or cancelled (status in ['scheduled', 'confirmed'])
        - Ordered by appointment date (earliest first)
        """
        queryset = self.get_queryset().filter(
            appointment_date__gte=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).order_by('appointment_date')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """
        Get today's appointments for the current user
        
        Returns all appointments scheduled for today, regardless of status.
        Useful for daily schedule views and dashboard widgets.
        """
        today = timezone.now().date()
        queryset = self.get_queryset().filter(
            appointment_date__date=today
        ).order_by('appointment_date')
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an appointment
        
        Changes appointment status to 'cancelled' and optionally adds cancellation notes.
        Cannot cancel appointments that are already completed or cancelled.
        """
        appointment = self.get_object()
        
        # Prevent cancelling appointments that are already finished
        if appointment.status in ['completed', 'cancelled']:
            return Response(
                {'error': 'Cannot cancel completed or already cancelled appointment'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Store old status for audit log
        old_status = appointment.status
        
        # Update appointment status and add cancellation notes
        appointment.status = 'cancelled'
        appointment.notes = request.data.get('notes', '')
        appointment.save()
        
        # Log appointment cancellation
        log_action(
            user=request.user,
            action='update',
            obj=appointment,
            request=request,
            changes={'status': {'old': old_status, 'new': 'cancelled'}},
            metadata={'cancellation_notes': request.data.get('notes', '')}
        )
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Reschedule an appointment"""
        appointment = self.get_object()
        new_date = request.data.get('appointment_date')
        
        if not new_date:
            return Response(
                {'error': 'New appointment date is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if new time is available
        existing_appointment = Appointment.objects.filter(
            psychologist=appointment.psychologist,
            appointment_date=new_date
        ).exclude(id=appointment.id)
        
        if existing_appointment.exists():
            return Response(
                {'error': 'Psychologist is not available at the new time'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.appointment_date = new_date
        appointment.status = 'scheduled'
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)


class AvailabilitySlotViewSet(viewsets.ModelViewSet):
    """Psychologist availability management"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = AvailabilitySlotSerializer
    
    def get_queryset(self):
        """Filter availability based on user role"""
        user = self.request.user
        
        if user.is_psychologist():
            return AvailabilitySlot.objects.filter(psychologist=user)
        elif user.is_admin_user() or user.is_practice_manager():
            return AvailabilitySlot.objects.all()
        else:
            return AvailabilitySlot.objects.none()
    
    @action(detail=False, methods=['get'])
    def by_psychologist(self, request):
        """Get availability for a specific psychologist"""
        psychologist_id = request.query_params.get('psychologist_id')
        if not psychologist_id:
            return Response(
                {'error': 'psychologist_id parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            psychologist = User.objects.get(id=psychologist_id, role=User.UserRole.PSYCHOLOGIST)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid psychologist ID'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        availability = AvailabilitySlot.objects.filter(
            psychologist=psychologist,
            is_available=True
        )
        
        serializer = self.get_serializer(availability, many=True)
        return Response(serializer.data)


class TimeSlotViewSet(viewsets.ModelViewSet):
    """Available time slots for booking"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = TimeSlotSerializer
    
    def get_queryset(self):
        """Filter time slots based on user role"""
        user = self.request.user
        
        if user.is_psychologist():
            return TimeSlot.objects.filter(psychologist=user)
        elif user.is_admin_user() or user.is_practice_manager():
            return TimeSlot.objects.all()
        else:
            return TimeSlot.objects.filter(is_available=True)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get available time slots"""
        psychologist_id = request.query_params.get('psychologist_id')
        date = request.query_params.get('date')
        
        queryset = TimeSlot.objects.filter(is_available=True)
        
        if psychologist_id:
            queryset = queryset.filter(psychologist_id=psychologist_id)
        
        if date:
            queryset = queryset.filter(date=date)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BookAppointmentView(APIView):
    """Book a new appointment"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = BookAppointmentSerializer(data=request.data)
        
        if serializer.is_valid():
            # Get the psychologist and service
            psychologist = User.objects.get(id=serializer.validated_data['psychologist_id'])
            service = Service.objects.get(id=serializer.validated_data['service_id'])
            
            # Medicare Compliance Checks
            from appointments.booking_views import (
                check_medicare_session_limit,
                check_medicare_referral_requirement,
                validate_medicare_item_number
            )
            
            # 1. Validate Medicare item number
            if service.medicare_item_number:
                is_valid, error_msg, _ = validate_medicare_item_number(service.medicare_item_number)
                if not is_valid:
                    return Response(
                        {'error': error_msg},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # 2. Check session limit
            is_allowed, limit_error, sessions_used, sessions_remaining = check_medicare_session_limit(
                request.user, service
            )
            if not is_allowed:
                return Response(
                    {
                        'error': limit_error,
                        'medicare_limit_info': {
                            'sessions_used': sessions_used,
                            'sessions_remaining': sessions_remaining
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 3. Check referral requirement
            is_valid, referral_error = check_medicare_referral_requirement(request.user, service)
            if not is_valid:
                return Response(
                    {'error': referral_error},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create the appointment
            appointment = Appointment.objects.create(
                patient=request.user,
                psychologist=psychologist,
                service=service,
                appointment_date=serializer.validated_data['appointment_date'],
                duration_minutes=serializer.validated_data['duration_minutes'],
                notes=serializer.validated_data.get('notes', ''),
                status='scheduled'
            )
            
            # Create time slot and link to appointment
            TimeSlot.objects.create(
                psychologist=psychologist,
                date=appointment.appointment_date.date(),
                start_time=appointment.appointment_date,
                end_time=appointment.appointment_date + timezone.timedelta(minutes=appointment.duration_minutes),
                is_available=False,
                appointment=appointment
            )
            
            appointment_serializer = AppointmentSerializer(appointment)
            return Response({
                'message': 'Appointment booked successfully',
                'appointment': appointment_serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CancelAppointmentView(APIView):
    """Cancel an appointment"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Check permissions
            if not (request.user == appointment.patient or 
                   request.user == appointment.psychologist or 
                   request.user.is_admin_user() or 
                   request.user.is_practice_manager()):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            if appointment.status in ['completed', 'cancelled']:
                return Response(
                    {'error': 'Cannot cancel completed or already cancelled appointment'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            appointment.status = 'cancelled'
            appointment.notes = request.data.get('notes', '')
            appointment.save()
            
            # Free up the time slot
            time_slot = TimeSlot.objects.filter(appointment=appointment).first()
            if time_slot:
                time_slot.is_available = True
                time_slot.appointment = None
                time_slot.save()
            
            serializer = AppointmentSerializer(appointment)
            return Response({
                'message': 'Appointment cancelled successfully',
                'appointment': serializer.data
            })
        
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class RescheduleAppointmentView(APIView):
    """Reschedule an appointment"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            new_date = request.data.get('appointment_date')
            
            if not new_date:
                return Response(
                    {'error': 'New appointment date is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check permissions
            if not (request.user == appointment.patient or 
                   request.user == appointment.psychologist or 
                   request.user.is_admin_user() or 
                   request.user.is_practice_manager()):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if new time is available
            existing_appointment = Appointment.objects.filter(
                psychologist=appointment.psychologist,
                appointment_date=new_date
            ).exclude(id=appointment.id)
            
            if existing_appointment.exists():
                return Response(
                    {'error': 'Psychologist is not available at the new time'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update appointment
            appointment.appointment_date = new_date
            appointment.status = 'scheduled'
            appointment.save()
            
            # Update time slot
            time_slot = TimeSlot.objects.filter(appointment=appointment).first()
            if time_slot:
                time_slot.start_time = new_date
                time_slot.end_time = new_date + timezone.timedelta(minutes=appointment.duration_minutes)
                time_slot.save()
            
            serializer = AppointmentSerializer(appointment)
            return Response({
                'message': 'Appointment rescheduled successfully',
                'appointment': serializer.data
            })
        
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CreateVideoRoomView(APIView):
    """Create Twilio video room for appointment"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, appointment_id):
        try:
            from .video_service import get_video_service
            
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Check permissions
            if not (request.user == appointment.patient or 
                   request.user == appointment.psychologist or 
                   request.user.is_admin_user() or 
                   request.user.is_practice_manager()):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if it's a telehealth appointment
            if appointment.session_type != 'telehealth':
                return Response(
                    {'error': 'Video room can only be created for telehealth appointments'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check recording consent if recording is requested
            enable_recording = request.data.get('enable_recording', False)
            if enable_recording:
                from core.notification_utils import has_recording_consent
                if not has_recording_consent(appointment.patient):
                    return Response(
                        {
                            'error': 'Patient has not consented to session recording',
                            'message': 'Recording cannot be enabled without patient consent. Please request consent first.'
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            # Get or create video room
            video_service = get_video_service()
            
            if appointment.video_room_id:
                # Room already exists, get status
                room_status = video_service.get_room_status(appointment.video_room_id)
                if room_status.get('status') != 'not_found':
                    return Response({
                        'message': 'Video room already exists',
                        'room_name': appointment.video_room_id,
                        'room_sid': room_status.get('room_sid'),
                        'status': room_status.get('status'),
                        'meeting_url': video_service._generate_meeting_url(appointment.video_room_id)
                    })
            
            # Create new room (with recording enabled only if consent given)
            room_data = video_service.create_room(
                appointment_id=appointment_id,
                appointment_date=appointment.appointment_date,
                enable_recording=enable_recording
            )
            
            # Update appointment with video room ID
            appointment.video_room_id = room_data['room_name']
            appointment.save()
            
            return Response({
                'message': 'Video room created successfully',
                'room_name': room_data['room_name'],
                'room_sid': room_data['room_sid'],
                'status': room_data['status'],
                'meeting_url': room_data['meeting_url'],
                'appointment_id': appointment_id
            })
        
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create video room: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetVideoAccessTokenView(APIView):
    """Get Twilio access token for joining video room"""
    
    permission_classes = [IsAuthenticated]
    
    def _calculate_token_ttl(self, appointment):
        """
        Calculate token TTL based on appointment duration
        Formula: max(appointment_duration + 30min buffer, 60min minimum, 4hr maximum)
        """
        
        # Get appointment duration in minutes
        duration_minutes = appointment.duration_minutes or 60
        
        # Calculate token validity: duration + 30 minutes buffer
        token_minutes = duration_minutes + 30
        
        # Apply constraints: minimum 60 minutes, maximum 4 hours
        token_minutes = max(token_minutes, 60)  # Minimum 1 hour
        token_minutes = min(token_minutes, 240)  # Maximum 4 hours
        
        return token_minutes / 60.0  # Convert to hours
    
    def get(self, request, appointment_id):
        try:
            from .video_service import get_video_service
            from django.utils import timezone
            
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Check permissions
            if not (request.user == appointment.patient or 
                   request.user == appointment.psychologist):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if video room exists
            if not appointment.video_room_id:
                return Response(
                    {'error': 'No video room found for this appointment'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate smart token expiration
            ttl_hours = self._calculate_token_ttl(appointment)
            expires_in_seconds = int(ttl_hours * 3600)
            
            # Calculate expiration timestamp
            from datetime import timedelta
            expires_at = timezone.now() + timedelta(seconds=expires_in_seconds)
            
            # Generate access token
            video_service = get_video_service()
            user_identity = f"{request.user.id}-{request.user.email}"
            
            access_token = video_service.generate_access_token(
                user_identity=user_identity,
                room_name=appointment.video_room_id,
                ttl_hours=ttl_hours
            )
            
            return Response({
                'access_token': access_token,
                'room_name': appointment.video_room_id,
                'user_identity': user_identity,
                'expires_in': expires_in_seconds,
                'expires_at': expires_at.isoformat(),
                'appointment_id': appointment_id,
                'appointment_duration_minutes': appointment.duration_minutes,
                'token_valid_until': f"{int(ttl_hours * 60)} minutes ({int(ttl_hours)} hours)"
            })
        
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to generate access token: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshVideoAccessTokenView(APIView):
    """Refresh Twilio access token for an active video session"""
    
    permission_classes = [IsAuthenticated]
    
    def _calculate_token_ttl(self, appointment):
        """Calculate token TTL based on appointment duration"""
        
        duration_minutes = appointment.duration_minutes or 60
        token_minutes = duration_minutes + 30
        token_minutes = max(token_minutes, 60)
        token_minutes = min(token_minutes, 240)
        
        return token_minutes / 60.0
    
    def get(self, request, appointment_id):
        try:
            from .video_service import get_video_service
            from django.utils import timezone
            
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Check permissions
            if not (request.user == appointment.patient or 
                   request.user == appointment.psychologist):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if video room exists
            if not appointment.video_room_id:
                return Response(
                    {'error': 'No video room found for this appointment'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Calculate smart token expiration
            from datetime import timedelta
            ttl_hours = self._calculate_token_ttl(appointment)
            expires_in_seconds = int(ttl_hours * 3600)
            expires_at = timezone.now() + timedelta(seconds=expires_in_seconds)
            
            # Generate new access token
            video_service = get_video_service()
            user_identity = f"{request.user.id}-{request.user.email}"
            
            access_token = video_service.generate_access_token(
                user_identity=user_identity,
                room_name=appointment.video_room_id,
                ttl_hours=ttl_hours
            )
            
            return Response({
                'access_token': access_token,
                'room_name': appointment.video_room_id,
                'user_identity': user_identity,
                'expires_in': expires_in_seconds,
                'expires_at': expires_at.isoformat(),
                'appointment_id': appointment_id,
                'refreshed_at': timezone.now().isoformat()
            })
        
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to refresh access token: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DebugVideoTokenView(APIView):
    """Debug endpoint to inspect video token details"""
    
    permission_classes = [IsAuthenticated]
    
    def _calculate_token_ttl(self, appointment):
        """Calculate token TTL based on appointment duration"""
        duration_minutes = appointment.duration_minutes or 60
        token_minutes = duration_minutes + 30
        token_minutes = max(token_minutes, 60)
        token_minutes = min(token_minutes, 240)
        return token_minutes / 60.0
    
    def get(self, request, appointment_id):
        try:
            from .video_service import get_video_service
            from django.utils import timezone
            from datetime import timedelta
            import base64
            import json
            
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Check permissions
            if not (request.user == appointment.patient or 
                   request.user == appointment.psychologist):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if video room exists
            if not appointment.video_room_id:
                return Response(
                    {'error': 'No video room found for this appointment'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Generate access token
            video_service = get_video_service()
            user_identity = f"{request.user.id}-{request.user.email}"
            
            ttl_hours = self._calculate_token_ttl(appointment)
            expires_in_seconds = int(ttl_hours * 3600)
            expires_at = timezone.now() + timedelta(seconds=expires_in_seconds)
            
            access_token = video_service.generate_access_token(
                user_identity=user_identity,
                room_name=appointment.video_room_id,
                ttl_hours=ttl_hours
            )
            
            # Decode token to inspect it (JWT has 3 parts: header.payload.signature)
            try:
                parts = access_token.split('.')
                if len(parts) == 3:
                    # Decode header and payload (base64url)
                    header = json.loads(base64.urlsafe_b64decode(parts[0] + '=='))
                    payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
                    
                    token_info = {
                        'header': header,
                        'payload': {
                            'iss': payload.get('iss'),  # Issuer (Account SID)
                            'sub': payload.get('sub'),  # Subject (API Key SID)
                            'grants': payload.get('grants', {}),
                            'exp': payload.get('exp'),
                            'iat': payload.get('iat'),
                            'jti': payload.get('jti'),
                        }
                    }
                else:
                    token_info = {'error': 'Invalid token format'}
            except Exception as e:
                token_info = {'error': f'Could not decode token: {str(e)}'}
            
            return Response({
                'token': access_token,
                'token_info': token_info,
                'room_name': appointment.video_room_id,
                'user_identity': user_identity,
                'expires_in': expires_in_seconds,
                'expires_at': expires_at.isoformat(),
                'appointment_id': appointment_id,
                'credentials_check': {
                    'account_sid': video_service.account_sid,
                    'api_key': video_service.api_key,
                    'api_key_preview': video_service.api_key[:10] + '...' if video_service.api_key else None,
                }
            })
        
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to generate debug token: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VideoRoomStatusView(APIView):
    """Get video room status and connection information"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, appointment_id):
        try:
            from .video_service import get_video_service
            
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Check permissions
            if not (request.user == appointment.patient or 
                   request.user == appointment.psychologist):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if video room exists
            if not appointment.video_room_id:
                return Response(
                    {'error': 'No video room found for this appointment'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get room status
            video_service = get_video_service()
            room_status = video_service.get_room_status(appointment.video_room_id)
            
            # Get participants if room is active
            participants = []
            if room_status.get('status') == 'in-progress':
                try:
                    participants = video_service.get_room_participants(room_status['room_sid'])
                except:
                    participants = []
            
            return Response({
                'room_name': appointment.video_room_id,
                'room_sid': room_status.get('room_sid'),
                'status': room_status.get('status'),
                'participants_count': len(participants),
                'participants': participants,
                'duration': room_status.get('duration'),
                'created_at': room_status.get('created_at'),
                'appointment_id': appointment_id
            })
        
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to get room status: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VideoRoomParticipantsView(APIView):
    """
    List participants in a video room
    
    GET /api/appointments/video-participants/<appointment_id>/
    
    Query Parameters:
    - status: Filter by status ('connected', 'disconnected', 'reconnecting')
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, appointment_id):
        try:
            from .video_service import get_video_service
            
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Check permissions - only appointment participants or admins
            if not (request.user == appointment.patient or 
                   request.user == appointment.psychologist or
                   request.user.is_admin() or
                   request.user.is_practice_manager()):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if video room exists
            if not appointment.video_room_id:
                return Response(
                    {'error': 'No video room found for this appointment'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get status filter
            status_filter = request.query_params.get('status')  # 'connected', 'disconnected', 'reconnecting'
            
            # Get room status to get room_sid
            video_service = get_video_service()
            room_status = video_service.get_room_status(appointment.video_room_id)
            
            if room_status.get('status') == 'not_found':
                return Response(
                    {'error': 'Video room not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get participants
            participants = video_service.get_room_participants(
                room_status['room_sid'],
                status=status_filter
            )
            
            return Response({
                'appointment_id': appointment_id,
                'room_name': appointment.video_room_id,
                'room_sid': room_status.get('room_sid'),
                'room_status': room_status.get('status'),
                'participants_count': len(participants),
                'participants': participants,
                'filter': {'status': status_filter} if status_filter else None
            })
        
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to get participants: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VideoRoomParticipantDetailView(APIView):
    """
    Get or remove a specific participant from a video room
    
    GET /api/appointments/video-participant/<appointment_id>/<participant_identity_or_sid>/
    POST /api/appointments/video-participant/<appointment_id>/<participant_identity_or_sid>/remove/
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, appointment_id, participant_identity_or_sid):
        """Get details of a specific participant"""
        try:
            from .video_service import get_video_service
            
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Check permissions - only appointment participants or admins
            if not (request.user == appointment.patient or 
                   request.user == appointment.psychologist or
                   request.user.is_admin() or
                   request.user.is_practice_manager()):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if video room exists
            if not appointment.video_room_id:
                return Response(
                    {'error': 'No video room found for this appointment'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get room status to get room_sid
            video_service = get_video_service()
            room_status = video_service.get_room_status(appointment.video_room_id)
            
            if room_status.get('status') == 'not_found':
                return Response(
                    {'error': 'Video room not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get participant
            participant = video_service.get_participant(
                room_status['room_sid'],
                participant_identity_or_sid
            )
            
            return Response({
                'appointment_id': appointment_id,
                'room_name': appointment.video_room_id,
                'room_sid': room_status.get('room_sid'),
                'participant': participant
            })
        
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            error_msg = str(e)
            if '404' in error_msg or 'not found' in error_msg.lower():
                return Response(
                    {'error': 'Participant not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(
                {'error': f'Failed to get participant: {error_msg}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request, appointment_id, participant_identity_or_sid):
        """Remove/kick a participant from the room"""
        try:
            from .video_service import get_video_service
            from audit.utils import log_action
            
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Check permissions - only psychologist or admins can remove participants
            if not (request.user == appointment.psychologist or
                   request.user.is_admin() or
                   request.user.is_practice_manager()):
                return Response(
                    {'error': 'Only psychologists or admins can remove participants'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if video room exists
            if not appointment.video_room_id:
                return Response(
                    {'error': 'No video room found for this appointment'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get room status to get room_sid
            video_service = get_video_service()
            room_status = video_service.get_room_status(appointment.video_room_id)
            
            if room_status.get('status') == 'not_found':
                return Response(
                    {'error': 'Video room not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get participant before removing (to log)
            try:
                participant_before = video_service.get_participant(
                    room_status['room_sid'],
                    participant_identity_or_sid
                )
            except:
                participant_before = None
            
            # Remove participant
            participant = video_service.remove_participant(
                room_status['room_sid'],
                participant_identity_or_sid
            )
            
            # Log the action
            log_action(
                user=request.user,
                action='update',
                obj=appointment,
                request=request,
                metadata={
                    'action': 'remove_participant',
                    'participant_identity': participant.get('identity'),
                    'participant_sid': participant.get('sid'),
                    'room_name': appointment.video_room_id
                }
            )
            
            return Response({
                'message': 'Participant removed successfully',
                'appointment_id': appointment_id,
                'room_name': appointment.video_room_id,
                'room_sid': room_status.get('room_sid'),
                'participant': participant
            })
        
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            error_msg = str(e)
            if '404' in error_msg or 'not found' in error_msg.lower():
                return Response(
                    {'error': 'Participant not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(
                {'error': f'Failed to remove participant: {error_msg}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TwilioStatusCallbackView(APIView):
    """
    Comprehensive webhook endpoint for Twilio Video status callbacks
    
    Handles all Twilio Video events:
    
    Room Events:
    - room-created: Room created
    - room-ended: Room completed
    
    Participant Events:
    - participant-connected: Participant joined
    - participant-disconnected: Participant left
    
    Track Events:
    - track-added: Participant added a Track
    - track-removed: Participant removed a Track
    - track-enabled: Participant unpaused a Track
    - track-disabled: Participant paused a Track
    
    Recording Events:
    - recording-started: Recording for a Track began
    - recording-completed: Recording for a Track completed
    - recording-failed: Failure during a recording operation
    
    Composition Events:
    - composition-started: Media processing task started
    - composition-available: Composition media file ready
    - composition-progress: Progress report (every ~10%)
    - composition-failed: Media processing task failed
    - composition-enqueued: Composition enqueued for processing
    - composition-hook-failed: Hook failed to create composition
    
    This endpoint is called by Twilio via HTTP POST.
    No authentication required (Twilio validates via request signature).
    """
    
    permission_classes = []  # Public endpoint (Twilio calls it)
    authentication_classes = []  # No authentication required
    
    def post(self, request):
        """
        Handle Twilio status callback
        
        Processes all event types from Twilio Video:
        - Room events
        - Participant events
        - Track events
        - Recording events
        - Composition events
        """
        try:
            # Extract common callback data
            event_type = request.data.get('StatusCallbackEvent')
            room_name = request.data.get('RoomName')
            room_sid = request.data.get('RoomSid')
            room_status = request.data.get('RoomStatus')
            timestamp = request.data.get('Timestamp')
            account_sid = request.data.get('AccountSid')
            
            # Log the callback
            import logging
            logger = logging.getLogger('psychology_clinic')
            
            # Try to find the appointment by room name
            # Room names are in format: apt-{appointment_id}-{timestamp}-{random}
            appointment = None
            if room_name and room_name.startswith('apt-'):
                try:
                    appointment_id = int(room_name.split('-')[1])
                    appointment = Appointment.objects.get(id=appointment_id)
                except (ValueError, Appointment.DoesNotExist, IndexError):
                    pass
            
            # Route to appropriate handler based on event type
            if event_type and event_type.startswith('room-'):
                self._handle_room_event(event_type, request.data, appointment, logger)
            elif event_type and event_type.startswith('participant-'):
                self._handle_participant_event(event_type, request.data, appointment, logger)
            elif event_type and event_type.startswith('track-'):
                self._handle_track_event(event_type, request.data, appointment, logger)
            elif event_type and event_type.startswith('recording-'):
                self._handle_recording_event(event_type, request.data, appointment, logger)
            elif event_type and event_type.startswith('composition-'):
                self._handle_composition_event(event_type, request.data, appointment, logger)
            else:
                # Unknown event type - log it
                logger.warning(f"Unknown Twilio event type: {event_type}")
            
            # Log all events
            logger.info(
                f"Twilio Status Callback: {event_type} | "
                f"Room: {room_name} | "
                f"Account: {account_sid} | "
                f"Timestamp: {timestamp}"
            )
            
            # Return success response (Twilio expects 200 OK)
            return Response({
                'status': 'received',
                'event': event_type,
                'room': room_name,
                'timestamp': timestamp
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Log error but still return 200 (Twilio will retry if we return error)
            import logging
            logger = logging.getLogger('psychology_clinic')
            logger.error(f"Error processing Twilio status callback: {str(e)}", exc_info=True)
            
            # Return 200 anyway to prevent Twilio from retrying
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_200_OK)
    
    def _handle_room_event(self, event_type, data, appointment, logger):
        """Handle room-related events"""
        room_name = data.get('RoomName')
        room_sid = data.get('RoomSid')
        room_status = data.get('RoomStatus')
        room_duration = data.get('RoomDuration')
        
        if event_type == 'room-created':
            logger.info(f"Room created: {room_name} (SID: {room_sid})")
            if appointment:
                # Room already associated with appointment
                pass
        
        elif event_type == 'room-ended':
            logger.info(f"Room ended: {room_name} | Duration: {room_duration}s")
            if appointment and appointment.status in ['scheduled', 'confirmed']:
                # Optionally auto-complete appointment when room ends
                # Uncomment if you want this behavior:
                # appointment.status = 'completed'
                # appointment.save()
                # logger.info(f"Auto-completed appointment {appointment.id} after room ended")
                pass
    
    def _handle_participant_event(self, event_type, data, appointment, logger):
        """Handle participant-related events"""
        participant_sid = data.get('ParticipantSid')
        participant_identity = data.get('ParticipantIdentity')
        participant_status = data.get('ParticipantStatus')
        participant_duration = data.get('ParticipantDuration')
        room_name = data.get('RoomName')
        
        if event_type == 'participant-connected':
            logger.info(
                f"Participant connected: {participant_identity} "
                f"(SID: {participant_sid}) in room {room_name}"
            )
            if appointment:
                # You could log this or update appointment notes
                pass
        
        elif event_type == 'participant-disconnected':
            logger.info(
                f"Participant disconnected: {participant_identity} "
                f"(SID: {participant_sid}) | Duration: {participant_duration}s"
            )
            if appointment and participant_duration:
                # You could store session duration
                # Example: Store in appointment notes or separate model
                pass
    
    def _handle_track_event(self, event_type, data, appointment, logger):
        """Handle track-related events (audio/video tracks)"""
        track_sid = data.get('TrackSid')
        track_kind = data.get('TrackKind')  # 'audio', 'video', or 'data'
        participant_sid = data.get('ParticipantSid')
        participant_identity = data.get('ParticipantIdentity')
        room_name = data.get('RoomName')
        
        logger.info(
            f"Track event: {event_type} | "
            f"Kind: {track_kind} | "
            f"Participant: {participant_identity} | "
            f"Room: {room_name}"
        )
        
        # Track events are useful for monitoring media quality
        # You could log these for analytics or troubleshooting
        if appointment:
            # Example: Track when participants enable/disable video/audio
            pass
    
    def _handle_recording_event(self, event_type, data, appointment, logger):
        """Handle recording-related events"""
        recording_sid = data.get('RecordingSid')
        room_sid = data.get('RoomSid')
        room_name = data.get('RoomName')
        participant_sid = data.get('ParticipantSid')
        participant_identity = data.get('ParticipantIdentity')
        track_sid = data.get('SourceSid')
        track_name = data.get('TrackName')
        codec = data.get('Codec')
        container = data.get('Container')
        
        if event_type == 'recording-started':
            from .models import SessionRecording
            from django.utils import timezone
            
            logger.info(
                f"Recording started: {recording_sid} | "
                f"Room: {room_name} | "
                f"Participant: {participant_identity} | "
                f"Track: {track_name} ({codec})"
            )
            
            if appointment:
                # Store initial recording metadata when recording starts
                try:
                    SessionRecording.objects.get_or_create(
                        recording_sid=recording_sid,
                        defaults={
                            'appointment': appointment,
                            'media_uri': '',  # Will be updated when completed
                            'duration': 0,
                            'size': 0,
                            'status': 'started',
                            'participant_identity': participant_identity or ''
                        }
                    )
                except Exception as e:
                    logger.error(f"Error saving recording start metadata: {str(e)}")
        
        elif event_type == 'recording-completed':
            from .models import SessionRecording
            from django.utils import timezone
            
            media_uri = data.get('MediaUri')
            duration = data.get('Duration', 0)
            size = data.get('Size', 0)
            media_external_location = data.get('MediaExternalLocation')
            
            logger.info(
                f"Recording completed: {recording_sid} | "
                f"Duration: {duration}s | "
                f"Size: {size} bytes | "
                f"Media URI: {media_uri}"
            )
            
            if appointment:
                # Store recording metadata in database
                try:
                    recording, created = SessionRecording.objects.get_or_create(
                        recording_sid=recording_sid,
                        defaults={
                            'appointment': appointment,
                            'media_uri': media_uri,
                            'media_external_location': media_external_location or '',
                            'duration': int(duration) if duration else 0,
                            'size': int(size) if size else 0,
                            'status': 'completed',
                            'completed_at': timezone.now(),
                            'participant_identity': participant_identity or ''
                        }
                    )
                    
                    # Update if recording already exists
                    if not created:
                        recording.media_uri = media_uri
                        recording.media_external_location = media_external_location or ''
                        recording.duration = int(duration) if duration else 0
                        recording.size = int(size) if size else 0
                        recording.status = 'completed'
                        recording.completed_at = timezone.now()
                        recording.save()
                    
                    logger.info(f"Recording metadata saved: {recording.id}")
                except Exception as e:
                    logger.error(f"Error saving recording metadata: {str(e)}")
        
        elif event_type == 'recording-failed':
            from .models import SessionRecording
            
            failed_operation = data.get('FailedOperation')
            logger.error(
                f"Recording failed: {recording_sid} | "
                f"Operation: {failed_operation} | "
                f"Room: {room_name}"
            )
            if appointment:
                # Update recording status to failed
                try:
                    recording = SessionRecording.objects.filter(
                        recording_sid=recording_sid
                    ).first()
                    if recording:
                        recording.status = 'failed'
                        recording.save()
                        logger.info(f"Recording status updated to failed: {recording.id}")
                except Exception as e:
                    logger.error(f"Error updating recording status: {str(e)}")
    
    def _handle_composition_event(self, event_type, data, appointment, logger):
        """Handle composition-related events (video compositions)"""
        composition_sid = data.get('CompositionSid')
        room_sid = data.get('RoomSid')
        hook_sid = data.get('HookSid')
        
        if event_type == 'composition-started':
            logger.info(f"Composition started: {composition_sid} | Room: {room_sid}")
            if appointment:
                # Composition processing started
                pass
        
        elif event_type == 'composition-available':
            media_uri = data.get('MediaUri')
            duration = data.get('Duration')
            size = data.get('Size')
            media_external_location = data.get('MediaExternalLocation')
            
            logger.info(
                f"Composition available: {composition_sid} | "
                f"Duration: {duration}s | "
                f"Size: {size} bytes | "
                f"Media URI: {media_uri}"
            )
            if appointment:
                # Store composition URL and metadata
                # You could save this to a Composition model
                pass
        
        elif event_type == 'composition-progress':
            percentage_done = data.get('PercentageDone')
            seconds_remaining = data.get('SecondsRemaining')
            logger.info(
                f"Composition progress: {composition_sid} | "
                f"{percentage_done}% complete | "
                f"{seconds_remaining}s remaining"
            )
        
        elif event_type == 'composition-failed':
            failed_operation = data.get('FailedOperation')
            error_message = data.get('ErrorMessage')
            logger.error(
                f"Composition failed: {composition_sid} | "
                f"Operation: {failed_operation} | "
                f"Error: {error_message}"
            )
        
        elif event_type == 'composition-enqueued':
            logger.info(f"Composition enqueued: {composition_sid} | Hook: {hook_sid}")
        
        elif event_type == 'composition-hook-failed':
            failed_operation = data.get('FailedOperation')
            error_message = data.get('ErrorMessage')
            logger.error(
                f"Composition hook failed: {hook_sid} | "
                f"Operation: {failed_operation} | "
                f"Error: {error_message}"
            )


class UpcomingAppointmentsView(APIView):
    """Get upcoming appointments for the current user"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.is_psychologist():
            appointments = Appointment.objects.filter(
                psychologist=user,
                appointment_date__gte=timezone.now(),
                status__in=['scheduled', 'confirmed']
            ).order_by('appointment_date')
        elif user.is_patient():
            appointments = Appointment.objects.filter(
                patient=user,
                appointment_date__gte=timezone.now(),
                status__in=['scheduled', 'confirmed']
            ).order_by('appointment_date')
        else:
            appointments = Appointment.objects.filter(
                appointment_date__gte=timezone.now(),
                status__in=['scheduled', 'confirmed']
            ).order_by('appointment_date')
        
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


class PsychologistScheduleView(APIView):
    """
    Get psychologist schedule with formatted appointment data
    
    Returns appointments in the exact format expected by the frontend schedule page.
    Supports filtering by date range and status.
    
    GET /api/appointments/psychologist/schedule/
    
    Query Parameters:
    - start_date: Filter appointments from this date (ISO format: YYYY-MM-DD)
    - end_date: Filter appointments until this date (ISO format: YYYY-MM-DD)
    - status: Filter by status (scheduled, confirmed, completed, cancelled, all)
    - page: Page number for pagination (default: 1)
    - page_size: Results per page (default: 50)
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Check if user is a psychologist
        if not user.is_psychologist():
            return Response(
                {'error': 'Only psychologists can access this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        month = request.query_params.get('month')  # Format: YYYY-MM
        year = request.query_params.get('year')    # Format: YYYY
        status_filter = request.query_params.get('status', 'all')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        
        # Base queryset - psychologist's appointments
        queryset = Appointment.objects.filter(
            psychologist=user
        ).select_related(
            'patient',
            'service'
        ).order_by('appointment_date')
        
        # Apply date filters
        if start_date:
            try:
                from datetime import datetime
                start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                start_datetime = timezone.make_aware(start_datetime)
                queryset = queryset.filter(appointment_date__gte=start_datetime)
            except ValueError:
                return Response(
                    {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if end_date:
            try:
                from datetime import datetime, timedelta
                end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                end_datetime = timezone.make_aware(end_datetime) + timedelta(days=1)
                queryset = queryset.filter(appointment_date__lt=end_datetime)
            except ValueError:
                return Response(
                    {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Apply month filter (for calendar view)
        if month:
            try:
                from datetime import datetime
                month_date = datetime.strptime(month, '%Y-%m')
                start_of_month = timezone.make_aware(month_date.replace(day=1))
                if month_date.month == 12:
                    end_of_month = timezone.make_aware(month_date.replace(year=month_date.year + 1, month=1, day=1))
                else:
                    end_of_month = timezone.make_aware(month_date.replace(month=month_date.month + 1, day=1))
                
                queryset = queryset.filter(
                    appointment_date__gte=start_of_month,
                    appointment_date__lt=end_of_month
                )
            except ValueError:
                return Response(
                    {'error': 'Invalid month format. Use YYYY-MM'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Apply year filter
        if year:
            try:
                from datetime import datetime
                year_int = int(year)
                start_of_year = timezone.make_aware(datetime(year_int, 1, 1))
                end_of_year = timezone.make_aware(datetime(year_int + 1, 1, 1))
                
                queryset = queryset.filter(
                    appointment_date__gte=start_of_year,
                    appointment_date__lt=end_of_year
                )
            except ValueError:
                return Response(
                    {'error': 'Invalid year format. Use YYYY'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Apply status filter
        if status_filter != 'all':
            if status_filter in ['scheduled', 'confirmed', 'completed', 'cancelled', 'no_show']:
                queryset = queryset.filter(status=status_filter)
            else:
                return Response(
                    {'error': f'Invalid status filter: {status_filter}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Count total results
        total_count = queryset.count()
        
        # Apply pagination
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_queryset = queryset[start_index:end_index]
        
        # Serialize data
        serializer = PsychologistScheduleSerializer(paginated_queryset, many=True)
        
        # Build pagination URLs
        base_url = request.build_absolute_uri(request.path)
        next_url = None
        previous_url = None
        
        # Calculate if there's a next page
        if end_index < total_count:
            next_page = page + 1
            next_url = f"{base_url}?page={next_page}&page_size={page_size}"
            if status_filter != 'all':
                next_url += f"&status={status_filter}"
            if start_date:
                next_url += f"&start_date={start_date}"
            if end_date:
                next_url += f"&end_date={end_date}"
        
        # Calculate if there's a previous page
        if page > 1:
            previous_page = page - 1
            previous_url = f"{base_url}?page={previous_page}&page_size={page_size}"
            if status_filter != 'all':
                previous_url += f"&status={status_filter}"
            if start_date:
                previous_url += f"&start_date={start_date}"
            if end_date:
                previous_url += f"&end_date={end_date}"
        
        # Build response in expected format
        return Response({
            'count': total_count,
            'next': next_url,
            'previous': previous_url,
            'results': serializer.data
        })


class AppointmentSummaryView(APIView):
    """Get appointment summary statistics"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.is_psychologist():
            appointments = Appointment.objects.filter(psychologist=user)
        elif user.is_patient():
            appointments = Appointment.objects.filter(patient=user)
        else:
            appointments = Appointment.objects.all()
        
        summary = {
            'total_appointments': appointments.count(),
            'upcoming_appointments': appointments.filter(
                appointment_date__gte=timezone.now(),
                status__in=['scheduled', 'confirmed']
            ).count(),
            'completed_appointments': appointments.filter(status='completed').count(),
            'cancelled_appointments': appointments.filter(status='cancelled').count(),
            'next_appointment': None,
            'recent_appointments': []
        }
        
        # Get next appointment
        next_appointment = appointments.filter(
            appointment_date__gte=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).order_by('appointment_date').first()
        
        if next_appointment:
            summary['next_appointment'] = AppointmentSerializer(next_appointment).data
        
        # Get recent appointments
        recent_appointments = appointments.filter(
            appointment_date__lt=timezone.now()
        ).order_by('-appointment_date')[:5]
        
        summary['recent_appointments'] = AppointmentSerializer(recent_appointments, many=True).data
        
        return Response(summary)


class ScheduleManagementView(APIView):
    """
    Advanced schedule management for psychologists
    
    Features:
    - Bulk availability management
    - Recurring appointment support
    - Schedule templates
    - Time slot generation
    - Calendar integration
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get comprehensive schedule information for the current user
        
        Returns:
        - Current availability slots
        - Generated time slots
        - Schedule statistics
        - Upcoming appointments
        """
        user = request.user
        
        if not user.is_psychologist():
            return Response(
                {'error': 'Only psychologists can access schedule management'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get availability slots
        availability_slots = AvailabilitySlot.objects.filter(
            psychologist=user,
            is_available=True
        ).order_by('day_of_week', 'start_time')
        
        # Get time slots for the next 30 days
        from datetime import timedelta
        end_date = timezone.now().date() + timedelta(days=30)
        time_slots = TimeSlot.objects.filter(
            psychologist=user,
            date__gte=timezone.now().date(),
            date__lte=end_date
        ).order_by('date', 'start_time')
        
        # Get upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            psychologist=user,
            appointment_date__gte=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).order_by('appointment_date')[:10]
        
        # Calculate schedule statistics
        total_availability_hours = sum(
            (slot.end_time.hour * 60 + slot.end_time.minute - 
             slot.start_time.hour * 60 - slot.start_time.minute) / 60
            for slot in availability_slots
        )
        
        booked_slots = time_slots.filter(is_available=False).count()
        available_slots = time_slots.filter(is_available=True).count()
        
        schedule_data = {
            'availability_slots': [
                {
                    'id': slot.id,
                    'day_of_week': slot.day_of_week,
                    'day_name': dict(slot.day_of_week.field.choices)[slot.day_of_week],
                    'start_time': slot.start_time,
                    'end_time': slot.end_time,
                    'duration_hours': (slot.end_time.hour * 60 + slot.end_time.minute - 
                                      slot.start_time.hour * 60 - slot.start_time.minute) / 60
                }
                for slot in availability_slots
            ],
            'time_slots': [
                {
                    'id': slot.id,
                    'date': slot.date,
                    'start_time': slot.start_time,
                    'end_time': slot.end_time,
                    'is_available': slot.is_available,
                    'appointment_id': slot.appointment.id if slot.appointment else None
                }
                for slot in time_slots
            ],
            'upcoming_appointments': [
                {
                    'id': apt.id,
                    'patient_name': apt.patient.get_full_name(),
                    'appointment_date': apt.appointment_date,
                    'service_name': apt.service.name if apt.service else 'N/A',
                    'status': apt.status,
                    'duration_minutes': apt.duration_minutes
                }
                for apt in upcoming_appointments
            ],
            'statistics': {
                'total_availability_hours_per_week': total_availability_hours,
                'booked_slots_next_30_days': booked_slots,
                'available_slots_next_30_days': available_slots,
                'utilization_rate': round((booked_slots / (booked_slots + available_slots)) * 100, 1) if (booked_slots + available_slots) > 0 else 0
            }
        }
        
        return Response(schedule_data)
    
    def post(self, request):
        """
        Bulk update availability slots
        
        Allows setting multiple availability slots at once
        """
        user = request.user
        
        if not user.is_psychologist():
            return Response(
                {'error': 'Only psychologists can manage availability'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        availability_data = request.data.get('availability_slots', [])
        
        if not availability_data:
            return Response(
                {'error': 'No availability slots provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Clear existing availability slots for this psychologist
        AvailabilitySlot.objects.filter(psychologist=user).delete()
        
        # Create new availability slots
        created_slots = []
        for slot_data in availability_data:
            slot = AvailabilitySlot.objects.create(
                psychologist=user,
                day_of_week=slot_data['day_of_week'],
                start_time=slot_data['start_time'],
                end_time=slot_data['end_time'],
                is_available=slot_data.get('is_available', True)
            )
            created_slots.append(slot)
        
        # Generate time slots for the next 30 days
        self._generate_time_slots(user)
        
        return Response({
            'message': 'Availability updated successfully',
            'created_slots': len(created_slots),
            'time_slots_generated': True
        })
    
    def _generate_time_slots(self, psychologist):
        """Generate time slots from availability patterns"""
        from datetime import timedelta
        
        # Get availability slots
        availability_slots = AvailabilitySlot.objects.filter(
            psychologist=psychologist,
            is_available=True
        )
        
        # Generate time slots for the next 30 days
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=30)
        
        current_date = start_date
        while current_date <= end_date:
            day_of_week = current_date.weekday()
            
            # Find availability slots for this day
            day_slots = availability_slots.filter(day_of_week=day_of_week)
            
            for slot in day_slots:
                # Create time slot for this day and time
                start_datetime = timezone.datetime.combine(
                    current_date, 
                    slot.start_time
                ).replace(tzinfo=timezone.get_current_timezone())
                
                end_datetime = timezone.datetime.combine(
                    current_date, 
                    slot.end_time
                ).replace(tzinfo=timezone.get_current_timezone())
                
                # Create time slot if it doesn't exist
                TimeSlot.objects.get_or_create(
                    psychologist=psychologist,
                    date=current_date,
                    start_time=start_datetime,
                    end_time=end_datetime,
                    defaults={'is_available': True}
                )
            
            current_date += timedelta(days=1)


class RecurringAppointmentView(APIView):
    """
    Recurring appointment management
    
    Features:
    - Create recurring appointments
    - Manage recurring patterns
    - Bulk operations on recurring appointments
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Create recurring appointments
        
        Creates multiple appointments based on a recurring pattern
        """
        user = request.user
        
        if not user.is_psychologist():
            return Response(
                {'error': 'Only psychologists can create recurring appointments'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get recurring appointment data
        patient_id = request.data.get('patient_id')
        service_id = request.data.get('service_id')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        frequency = request.data.get('frequency')  # 'weekly', 'biweekly', 'monthly'
        day_of_week = request.data.get('day_of_week')  # 0-6 for Monday-Sunday
        time_slot = request.data.get('time_slot')  # '09:00', '10:00', etc.
        duration_minutes = request.data.get('duration_minutes', 60)
        notes = request.data.get('notes', '')
        
        # Validate required fields
        if not all([patient_id, service_id, start_date, end_date, frequency, day_of_week, time_slot]):
            return Response(
                {'error': 'Missing required fields'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            patient = User.objects.get(id=patient_id, role=User.UserRole.PATIENT)
            service = Service.objects.get(id=service_id)
        except (User.DoesNotExist, Service.DoesNotExist):
            return Response(
                {'error': 'Invalid patient or service ID'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse dates
        from datetime import datetime, timedelta
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Generate appointment dates based on frequency
        appointment_dates = []
        current_date = start_date
        
        while current_date <= end_date:
            # Check if current date matches the day of week
            if current_date.weekday() == day_of_week:
                appointment_dates.append(current_date)
            
            # Move to next period based on frequency
            if frequency == 'weekly':
                current_date += timedelta(weeks=1)
            elif frequency == 'biweekly':
                current_date += timedelta(weeks=2)
            elif frequency == 'monthly':
                # Add one month (approximate)
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        # Create appointments
        created_appointments = []
        for appointment_date in appointment_dates:
            # Combine date with time
            appointment_datetime = timezone.datetime.combine(
                appointment_date, 
                datetime.strptime(time_slot, '%H:%M').time()
            ).replace(tzinfo=timezone.get_current_timezone())
            
            # Check if time slot is available
            if not TimeSlot.objects.filter(
                psychologist=user,
                start_time=appointment_datetime,
                is_available=True
            ).exists():
                continue  # Skip if not available
            
            # Create appointment
            appointment = Appointment.objects.create(
                patient=patient,
                psychologist=user,
                service=service,
                appointment_date=appointment_datetime,
                duration_minutes=duration_minutes,
                notes=notes,
                status='scheduled'
            )
            
            # Update time slot
            time_slot_obj = TimeSlot.objects.get(
                psychologist=user,
                start_time=appointment_datetime
            )
            time_slot_obj.is_available = False
            time_slot_obj.appointment = appointment
            time_slot_obj.save()
            
            created_appointments.append(appointment)
        
        return Response({
            'message': f'Created {len(created_appointments)} recurring appointments',
            'appointments_created': len(created_appointments),
            'total_dates_processed': len(appointment_dates),
            'appointments': [
                {
                    'id': apt.id,
                    'appointment_date': apt.appointment_date,
                    'patient_name': apt.patient.get_full_name(),
                    'status': apt.status
                }
                for apt in created_appointments
            ]
        })


class CalendarIntegrationView(APIView):
    """
    Calendar integration for schedule management
    
    Features:
    - Export schedule to calendar formats
    - Import calendar events
    - Sync with external calendars
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Export schedule to calendar format (ICS)
        
        Returns calendar data in ICS format for import into calendar applications
        """
        user = request.user
        
        if not user.is_psychologist():
            return Response(
                {'error': 'Only psychologists can export calendar data'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get appointments for the next 90 days
        from datetime import timedelta
        end_date = timezone.now().date() + timedelta(days=90)
        
        appointments = Appointment.objects.filter(
            psychologist=user,
            appointment_date__date__gte=timezone.now().date(),
            appointment_date__date__lte=end_date
        ).order_by('appointment_date')
        
        # Generate ICS content
        ics_content = self._generate_ics_content(user, appointments)
        
        return Response({
            'calendar_data': ics_content,
            'appointments_count': appointments.count(),
            'date_range': {
                'start': timezone.now().date().isoformat(),
                'end': end_date.isoformat()
            }
        })
    
    def _generate_ics_content(self, psychologist, appointments):
        """Generate ICS calendar content"""
        ics_lines = [
            'BEGIN:VCALENDAR',
            'VERSION:2.0',
            'PRODID:-//Psychology Clinic//Schedule//EN',
            'CALSCALE:GREGORIAN',
            'METHOD:PUBLISH'
        ]
        
        for appointment in appointments:
            start_time = appointment.appointment_date.strftime('%Y%m%dT%H%M%SZ')
            end_time = (appointment.appointment_date + timezone.timedelta(minutes=appointment.duration_minutes)).strftime('%Y%m%dT%H%M%SZ')
            
            ics_lines.extend([
                'BEGIN:VEVENT',
                f'UID:{appointment.id}@psychology-clinic.com',
                f'DTSTART:{start_time}',
                f'DTEND:{end_time}',
                f'SUMMARY:Appointment with {appointment.patient.get_full_name()}',
                f'DESCRIPTION:Service: {appointment.service.name if appointment.service else "N/A"}\\nNotes: {appointment.notes}',
                f'STATUS:{appointment.status.upper()}',
                'END:VEVENT'
            ])
        
        ics_lines.append('END:VCALENDAR')
        
        return '\\n'.join(ics_lines)


class PatientAppointmentsListView(APIView):
    """
    Patient appointments list endpoint with pagination
    
    Returns detailed appointment information for the patient portal
    with formatted dates, psychologist details, and action capabilities
    
    GET /api/appointments/patient/appointments/
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get all appointments for the current patient
        
        Query Parameters:
        - status: Filter by status (upcoming, completed, cancelled, all)
        - page: Page number (default: 1)
        - page_size: Number of results per page (default: 10)
        
        Returns:
        - count: Total number of appointments
        - next: URL to next page (if available)
        - previous: URL to previous page (if available)
        - results: List of appointments with detailed information
        """
        user = request.user
        
        # Get query parameters
        status_filter = request.query_params.get('status', 'all')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        
        # Base queryset - filter by patient
        queryset = Appointment.objects.filter(patient=user).select_related(
            'psychologist',
            'psychologist__psychologist_profile',
            'service'
        ).order_by('-appointment_date')
        
        # Apply status filter
        now = timezone.now()
        if status_filter == 'upcoming':
            queryset = queryset.filter(
                appointment_date__gte=now,
                status__in=['scheduled', 'confirmed']
            )
        elif status_filter == 'completed':
            queryset = queryset.filter(status='completed')
        elif status_filter == 'cancelled':
            queryset = queryset.filter(status='cancelled')
        elif status_filter == 'past':
            queryset = queryset.filter(
                Q(appointment_date__lt=now) | Q(status__in=['completed', 'cancelled', 'no_show'])
            )
        
        # Count total results
        total_count = queryset.count()
        
        # Apply pagination
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_queryset = queryset[start_index:end_index]
        
        # Serialize data
        serializer = PatientAppointmentDetailSerializer(
            paginated_queryset,
            many=True,
            context={'request': request}
        )
        
        # Build pagination URLs
        base_url = request.build_absolute_uri(request.path)
        next_url = None
        previous_url = None
        
        # Calculate if there's a next page
        if end_index < total_count:
            next_page = page + 1
            next_url = f"{base_url}?page={next_page}&page_size={page_size}"
            if status_filter != 'all':
                next_url += f"&status={status_filter}"
        
        # Calculate if there's a previous page
        if page > 1:
            previous_page = page - 1
            previous_url = f"{base_url}?page={previous_page}&page_size={page_size}"
            if status_filter != 'all':
                previous_url += f"&status={status_filter}"
        
        # Build response
        response_data = {
            'count': total_count,
            'next': next_url,
            'previous': previous_url,
            'results': serializer.data
        }
        
        return Response(response_data)


class CompleteSessionView(APIView):
    """
    Complete a therapy session
    
    Updates appointment status to 'completed' and creates a progress note
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, appointment_id):
        """Complete a session and optionally create a progress note"""
        try:
            appointment = Appointment.objects.get(
                id=appointment_id,
                psychologist=request.user
            )
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found or access denied'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if appointment can be completed
        if appointment.status not in ['scheduled', 'confirmed']:
            return Response(
                {'error': f'Cannot complete appointment with status: {appointment.status}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update appointment status
        appointment.status = 'completed'
        appointment.completed_at = timezone.now()
        appointment.save()
        
        # Create progress note if provided
        progress_note_data = request.data.get('progress_note', {})
        if progress_note_data:
            from users.models import ProgressNote
            
            # Validate required fields for SOAP note
            required_fields = ['subjective', 'objective', 'assessment', 'plan']
            missing_fields = [field for field in required_fields if not progress_note_data.get(field)]
            
            if missing_fields:
                return Response(
                    {'error': f'Missing required fields for progress note: {", ".join(missing_fields)}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create progress note
            progress_note = ProgressNote.objects.create(
                psychologist=request.user,
                patient=appointment.patient,
                session_date=appointment.appointment_date,
                subjective=progress_note_data.get('subjective', ''),
                objective=progress_note_data.get('objective', ''),
                assessment=progress_note_data.get('assessment', ''),
                plan=progress_note_data.get('plan', ''),
                progress_rating=progress_note_data.get('progress_rating'),
                notes=progress_note_data.get('notes', '')
            )
            
            # Update psychologist statistics
            psychologist_profile = request.user.psychologist_profile
            psychologist_profile.sessions_completed += 1
            psychologist_profile.save()
        
        # Serialize updated appointment
        from .serializers import PsychologistScheduleSerializer
        serializer = PsychologistScheduleSerializer(appointment)
        
        return Response({
            'message': 'Session completed successfully',
            'appointment': serializer.data
        })


class AppointmentActionsView(APIView):
    """
    Handle appointment actions: cancel, reschedule
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, appointment_id):
        """Handle appointment actions"""
        action = request.data.get('action')
        
        if action not in ['cancel', 'reschedule']:
            return Response(
                {'error': 'Invalid action. Must be "cancel" or "reschedule"'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            appointment = Appointment.objects.get(
                id=appointment_id,
                psychologist=request.user
            )
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found or access denied'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if action == 'cancel':
            return self._cancel_appointment(appointment, request.data)
        elif action == 'reschedule':
            return self._reschedule_appointment(appointment, request.data)
    
    def _cancel_appointment(self, appointment, data):
        """Cancel an appointment"""
        if appointment.status in ['completed', 'cancelled']:
            return Response(
                {'error': f'Cannot cancel appointment with status: {appointment.status}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update appointment status
        appointment.status = 'cancelled'
        appointment.cancellation_reason = data.get('reason', '')
        appointment.cancelled_at = timezone.now()
        appointment.save()
        
        # Serialize updated appointment
        from .serializers import PsychologistScheduleSerializer
        serializer = PsychologistScheduleSerializer(appointment)
        
        return Response({
            'message': 'Appointment cancelled successfully',
            'appointment': serializer.data
        })
    
    def _reschedule_appointment(self, appointment, data):
        """Reschedule an appointment"""
        if appointment.status in ['completed', 'cancelled']:
            return Response(
                {'error': f'Cannot reschedule appointment with status: {appointment.status}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        new_date = data.get('new_date')
        if not new_date:
            return Response(
                {'error': 'new_date is required for rescheduling'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from datetime import datetime
            new_datetime = datetime.fromisoformat(new_date.replace('Z', '+00:00'))
            new_datetime = timezone.make_aware(new_datetime)
        except ValueError:
            return Response(
                {'error': 'Invalid new_date format. Use ISO format'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if new time slot is available
        conflicting_appointments = Appointment.objects.filter(
            psychologist=appointment.psychologist,
            appointment_date=new_datetime,
            status__in=['scheduled', 'confirmed']
        ).exclude(id=appointment.id)
        
        if conflicting_appointments.exists():
            return Response(
                {'error': 'Time slot is not available'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update appointment
        appointment.appointment_date = new_datetime
        appointment.status = 'scheduled'  # Reset to scheduled for confirmation
        appointment.rescheduled_at = timezone.now()
        appointment.reschedule_reason = data.get('reason', '')
        appointment.save()
        
        # Serialize updated appointment
        from .serializers import PsychologistScheduleSerializer
        serializer = PsychologistScheduleSerializer(appointment)
        
        return Response({
            'message': 'Appointment rescheduled successfully',
            'appointment': serializer.data
        })


class SessionRecordingView(APIView):
    """
    Get recording for a specific appointment
    
    GET /api/appointments/{appointment_id}/recording/ - Get recording for appointment
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, appointment_id):
        """Get recording for appointment"""
        try:
            appointment = Appointment.objects.select_related(
                'patient', 'psychologist'
            ).get(id=appointment_id)
            
            # Check permissions
            if not (request.user == appointment.patient or 
                   request.user == appointment.psychologist or 
                   request.user.is_admin_user() or 
                   request.user.is_practice_manager()):
                return Response(
                    {'error': 'Permission denied. You can only access recordings for your own appointments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get recording
            recording = SessionRecording.objects.filter(
                appointment=appointment,
                status='completed'
            ).order_by('-created_at').first()
            
            if not recording:
                return Response(
                    {'error': 'No recording found for this appointment'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Log access
            log_action(
                user=request.user,
                action='view_recording',
                obj=recording,
                request=request,
                metadata={
                    'appointment_id': appointment.id,
                    'recording_id': recording.id,
                    'recording_sid': recording.recording_sid
                }
            )
            
            serializer = SessionRecordingSerializer(recording)
            return Response(serializer.data)
        
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to retrieve recording: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SessionRecordingListView(APIView):
    """
    List all recordings accessible to the current user
    
    GET /api/appointments/recordings/ - List user's recordings
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List recordings based on user role"""
        try:
            # Build query based on user role
            if request.user.is_patient():
                # Patients can only see their own recordings
                recordings = SessionRecording.objects.filter(
                    appointment__patient=request.user,
                    status='completed'
                ).select_related('appointment', 'appointment__patient', 'appointment__psychologist')
            
            elif request.user.is_psychologist():
                # Psychologists can see recordings of their sessions
                recordings = SessionRecording.objects.filter(
                    appointment__psychologist=request.user,
                    status='completed'
                ).select_related('appointment', 'appointment__patient', 'appointment__psychologist')
            
            elif request.user.is_practice_manager() or request.user.is_admin_user():
                # Practice managers and admins can see all recordings
                recordings = SessionRecording.objects.filter(
                    status='completed'
                ).select_related('appointment', 'appointment__patient', 'appointment__psychologist')
            
            else:
                return Response(
                    {'error': 'Invalid user role'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Order by most recent first
            recordings = recordings.order_by('-created_at')
            
            # Pagination
            paginator = PageNumberPagination()
            paginator.page_size = 20
            paginated_recordings = paginator.paginate_queryset(recordings, request)
            
            serializer = SessionRecordingListSerializer(paginated_recordings, many=True)
            
            # Log access
            log_action(
                user=request.user,
                action='list_recordings',
                request=request,
                metadata={
                    'count': len(paginated_recordings) if paginated_recordings else 0,
                    'role': request.user.role
                }
            )
            
            return paginator.get_paginated_response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': f'Failed to retrieve recordings: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SessionRecordingDownloadView(APIView):
    """
    Get download URL for a recording
    
    GET /api/appointments/recordings/{recording_id}/download/ - Get download URL
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, recording_id):
        """Get download URL for recording"""
        try:
            recording = SessionRecording.objects.select_related(
                'appointment', 'appointment__patient', 'appointment__psychologist'
            ).get(id=recording_id)
            
            appointment = recording.appointment
            
            # Check permissions
            if not (request.user == appointment.patient or 
                   request.user == appointment.psychologist or 
                   request.user.is_admin_user() or 
                   request.user.is_practice_manager()):
                return Response(
                    {'error': 'Permission denied. You can only download recordings for your own appointments.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if recording is completed
            if recording.status != 'completed':
                return Response(
                    {'error': f'Recording is not available. Status: {recording.status}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Log download access
            log_action(
                user=request.user,
                action='download_recording',
                obj=recording,
                request=request,
                metadata={
                    'appointment_id': appointment.id,
                    'recording_id': recording.id,
                    'recording_sid': recording.recording_sid
                }
            )
            
            # Return download URL (Twilio media_uri)
            return Response({
                'recording_id': recording.id,
                'appointment_id': appointment.id,
                'download_url': recording.media_uri,
                'external_location': recording.media_external_location,
                'duration': recording.duration,
                'size': recording.size,
                'size_formatted': recording.size_formatted,
                'duration_formatted': recording.duration_formatted,
                'created_at': recording.created_at,
                'completed_at': recording.completed_at,
                'note': 'Use the download_url to access the recording. This URL is provided by Twilio and may require authentication.'
            })
        
        except SessionRecording.DoesNotExist:
            return Response(
                {'error': 'Recording not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to retrieve download URL: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )