"""
Appointments app views - Booking system and scheduling
Complete implementation with appointment management, availability checking, and booking
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count
from django.contrib.auth import get_user_model

from .models import Appointment, AvailabilitySlot, TimeSlot
from .serializers import (
    AppointmentSerializer, AppointmentCreateSerializer, AvailabilitySlotSerializer,
    TimeSlotSerializer, BookAppointmentSerializer, AppointmentStatusSerializer,
    PsychologistAvailabilitySerializer, AppointmentSummarySerializer,
    PatientAppointmentDetailSerializer, PsychologistScheduleSerializer
)
from services.models import Service

User = get_user_model()


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    Complete appointments management with role-based filtering
    
    Provides CRUD operations for appointments with different access levels:
    - Admins/Practice Managers: See all appointments
    - Psychologists: See only their own appointments
    - Patients: See only their own appointments
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter appointments based on user role and permissions
        
        Returns:
            QuerySet: Filtered appointments based on user's role
        """
        user = self.request.user
        
        if user.is_admin_user() or user.is_practice_manager():
            # Admin and practice managers can see all appointments
            return Appointment.objects.all()
        elif user.is_psychologist():
            # Psychologists can only see their own appointments
            return Appointment.objects.filter(psychologist=user)
        else:
            # Patients can only see their own appointments
            return Appointment.objects.filter(patient=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
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
        
        # Update appointment status and add cancellation notes
        appointment.status = 'cancelled'
        appointment.notes = request.data.get('notes', '')
        appointment.save()
        
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
            
            # Create new room
            room_data = video_service.create_room(
                appointment_id=appointment_id,
                appointment_date=appointment.appointment_date
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
            
            # Generate access token
            video_service = get_video_service()
            user_identity = f"{request.user.id}-{request.user.email}"
            
            access_token = video_service.generate_access_token(
                user_identity=user_identity,
                room_name=appointment.video_room_id,
                ttl_hours=2  # Token valid for 2 hours
            )
            
            return Response({
                'access_token': access_token,
                'room_name': appointment.video_room_id,
                'user_identity': user_identity,
                'expires_in': 7200,  # 2 hours in seconds
                'appointment_id': appointment_id
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