"""
Appointment Booking Views - Complete booking flow API
Handles psychologist selection, time slot viewing, and appointment booking
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta, time as dt_time

from .models import Appointment, AvailabilitySlot, TimeSlot
from services.models import PsychologistProfile, Service
from .serializers import AppointmentSerializer, TimeSlotSerializer
from audit.utils import log_action

User = get_user_model()


class PsychologistAvailableTimeSlotsView(APIView):
    """
    Get available time slots for a specific psychologist
    
    Query Parameters:
    - psychologist_id (required): ID of the psychologist
    - start_date (required): Start date for availability (YYYY-MM-DD)
    - end_date (optional): End date for availability (defaults to 30 days from start_date)
    - service_id (optional): Filter by service type
    - session_type (optional): Filter by telehealth or in_person
    """
    
    permission_classes = [AllowAny]  # Public endpoint for browsing
    
    def get(self, request):
        # Get query parameters
        psychologist_id = request.query_params.get('psychologist_id')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        service_id = request.query_params.get('service_id')
        session_type = request.query_params.get('session_type')
        
        # Validate required parameters
        if not psychologist_id:
            return Response(
                {'error': 'psychologist_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not start_date_str:
            return Response(
                {'error': 'start_date parameter is required (format: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Parse dates
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Invalid start_date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid end_date format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            end_date = start_date + timedelta(days=30)
        
        # Validate dates
        if start_date < timezone.now().date():
            start_date = timezone.now().date()
        
        if end_date < start_date:
            return Response(
                {'error': 'end_date must be after start_date'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get psychologist
        try:
            psychologist = User.objects.get(id=psychologist_id, role=User.UserRole.PSYCHOLOGIST)
            psychologist_profile = PsychologistProfile.objects.get(user=psychologist)
        except (User.DoesNotExist, PsychologistProfile.DoesNotExist):
            return Response(
                {'error': 'Psychologist not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if psychologist is accepting new patients
        if not psychologist_profile.is_accepting_new_patients:
            return Response({
                'psychologist_id': psychologist_id,
                'psychologist_name': psychologist.get_full_name(),
                'is_accepting_new_patients': False,
                'available_dates': [],
                'message': 'This psychologist is not currently accepting new patients'
            })
        
        # Check session type availability
        if session_type:
            if session_type == 'telehealth' and not psychologist_profile.telehealth_available:
                return Response(
                    {'error': 'This psychologist does not offer telehealth sessions'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            elif session_type == 'in_person' and not psychologist_profile.in_person_available:
                return Response(
                    {'error': 'This psychologist does not offer in-person sessions'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Generate or retrieve time slots
        time_slots = self._get_or_generate_time_slots(
            psychologist, 
            psychologist_profile, 
            start_date, 
            end_date
        )
        
        # Filter available slots
        available_slots = time_slots.filter(
            is_available=True,
            start_time__gte=timezone.now()
        ).order_by('start_time')
        
        # Group slots by date
        slots_by_date = {}
        for slot in available_slots:
            date_key = slot.date.isoformat()
            if date_key not in slots_by_date:
                slots_by_date[date_key] = {
                    'date': date_key,
                    'day_name': slot.date.strftime('%A'),
                    'slots': []
                }
            
            slots_by_date[date_key]['slots'].append({
                'id': slot.id,
                'start_time': slot.start_time.isoformat(),
                'end_time': slot.end_time.isoformat(),
                'start_time_formatted': slot.start_time.strftime('%I:%M %p'),
                'end_time_formatted': slot.end_time.strftime('%I:%M %p'),
                'is_available': slot.is_available
            })
        
        # Convert to sorted list
        available_dates = sorted(slots_by_date.values(), key=lambda x: x['date'])
        
        return Response({
            'psychologist_id': psychologist_id,
            'psychologist_name': psychologist.get_full_name(),
            'psychologist_title': psychologist_profile.title,
            'is_accepting_new_patients': psychologist_profile.is_accepting_new_patients,
            'telehealth_available': psychologist_profile.telehealth_available,
            'in_person_available': psychologist_profile.in_person_available,
            'consultation_fee': str(psychologist_profile.consultation_fee),
            'medicare_rebate_amount': str(psychologist_profile.medicare_rebate_amount),
            'patient_cost_after_rebate': psychologist_profile.patient_cost_after_rebate,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'available_dates': available_dates,
            'total_available_slots': available_slots.count()
        })
    
    def _get_or_generate_time_slots(self, psychologist, profile, start_date, end_date):
        """
        Get existing time slots or generate them from availability pattern
        """
        # Check if we have time slots in this range
        existing_slots = TimeSlot.objects.filter(
            psychologist=psychologist,
            date__gte=start_date,
            date__lte=end_date
        )
        
        if existing_slots.exists():
            return existing_slots
        
        # Generate time slots from working hours
        if not profile.working_days or not profile.start_time or not profile.end_time:
            # Return empty queryset if no working hours defined
            return TimeSlot.objects.none()
        
        # Generate time slots
        working_days_list = [day.strip() for day in profile.working_days.split(',')]
        day_name_to_number = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        
        working_day_numbers = [
            day_name_to_number.get(day) 
            for day in working_days_list 
            if day in day_name_to_number
        ]
        
        # Generate slots for each day in range
        current_date = start_date
        session_duration = profile.session_duration_minutes
        break_duration = profile.break_between_sessions_minutes
        
        while current_date <= end_date:
            # Check if this is a working day
            if current_date.weekday() in working_day_numbers:
                # Generate time slots for this day
                current_time = profile.start_time
                end_time = profile.end_time
                
                while current_time < end_time:
                    # Calculate end time for this slot
                    start_datetime = timezone.datetime.combine(
                        current_date, current_time
                    ).replace(tzinfo=timezone.get_current_timezone())
                    
                    # Add session duration
                    end_datetime = start_datetime + timedelta(minutes=session_duration)
                    
                    # Check if end time exceeds working hours
                    if end_datetime.time() > end_time:
                        break
                    
                    # Skip if in the past
                    if start_datetime > timezone.now():
                        # Create time slot
                        TimeSlot.objects.get_or_create(
                            psychologist=psychologist,
                            start_time=start_datetime,
                            defaults={
                                'date': current_date,
                                'end_time': end_datetime,
                                'is_available': True
                            }
                        )
                    
                    # Move to next slot (session duration + break)
                    total_minutes = session_duration + break_duration
                    current_time = (
                        datetime.combine(current_date, current_time) + 
                        timedelta(minutes=total_minutes)
                    ).time()
            
            current_date += timedelta(days=1)
        
        # Return the generated/existing slots
        return TimeSlot.objects.filter(
            psychologist=psychologist,
            date__gte=start_date,
            date__lte=end_date
        )


class CalendarAvailabilityView(APIView):
    """
    Get calendar view of available dates (simplified for calendar display)
    
    Query Parameters:
    - psychologist_id (required): ID of the psychologist
    - month (optional): Month to view (1-12, defaults to current month)
    - year (optional): Year to view (defaults to current year)
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        psychologist_id = request.query_params.get('psychologist_id')
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        
        if not psychologist_id:
            return Response(
                {'error': 'psychologist_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or default month/year
        now = timezone.now()
        try:
            month = int(month) if month else now.month
            year = int(year) if year else now.year
        except ValueError:
            return Response(
                {'error': 'Invalid month or year'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate month/year
        if month < 1 or month > 12:
            return Response(
                {'error': 'Month must be between 1 and 12'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get psychologist
        try:
            psychologist = User.objects.get(id=psychologist_id, role=User.UserRole.PSYCHOLOGIST)
            psychologist_profile = PsychologistProfile.objects.get(user=psychologist)
        except (User.DoesNotExist, PsychologistProfile.DoesNotExist):
            return Response(
                {'error': 'Psychologist not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate date range for the month
        from calendar import monthrange
        _, last_day = monthrange(year, month)
        start_date = datetime(year, month, 1).date()
        end_date = datetime(year, month, last_day).date()
        
        # Ensure we don't query past dates
        if start_date < now.date():
            start_date = now.date()
        
        # Get time slots for the month
        time_slots = TimeSlot.objects.filter(
            psychologist=psychologist,
            date__gte=start_date,
            date__lte=end_date,
            is_available=True,
            start_time__gte=now
        ).values('date').distinct()
        
        available_dates = [slot['date'].isoformat() for slot in time_slots]
        
        return Response({
            'psychologist_id': psychologist_id,
            'psychologist_name': psychologist.get_full_name(),
            'month': month,
            'year': year,
            'available_dates': available_dates,
            'total_available_days': len(available_dates)
        })


class BookAppointmentEnhancedView(APIView):
    """
    Enhanced appointment booking with full validation
    
    POST Body:
    {
        "psychologist_id": 1,
        "service_id": 1,
        "time_slot_id": 123,
        "session_type": "telehealth" or "in_person",
        "notes": "Optional notes"
    }
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Extract data
        psychologist_id = request.data.get('psychologist_id')
        service_id = request.data.get('service_id')
        time_slot_id = request.data.get('time_slot_id')
        session_type = request.data.get('session_type', 'telehealth')
        notes = request.data.get('notes', '')
        
        # Validate required fields
        if not all([psychologist_id, service_id, time_slot_id]):
            return Response(
                {'error': 'psychologist_id, service_id, and time_slot_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate session type
        if session_type not in ['telehealth', 'in_person']:
            return Response(
                {'error': 'session_type must be either "telehealth" or "in_person"'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get psychologist
        try:
            psychologist = User.objects.get(id=psychologist_id, role=User.UserRole.PSYCHOLOGIST)
            psychologist_profile = PsychologistProfile.objects.get(user=psychologist)
        except (User.DoesNotExist, PsychologistProfile.DoesNotExist):
            return Response(
                {'error': 'Psychologist not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate session type availability
        if session_type == 'telehealth' and not psychologist_profile.telehealth_available:
            return Response(
                {'error': 'This psychologist does not offer telehealth sessions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif session_type == 'in_person' and not psychologist_profile.in_person_available:
            return Response(
                {'error': 'This psychologist does not offer in-person sessions'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get service
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response(
                {'error': 'Service not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get time slot
        try:
            time_slot = TimeSlot.objects.get(
                id=time_slot_id,
                psychologist=psychologist,
                is_available=True
            )
        except TimeSlot.DoesNotExist:
            return Response(
                {'error': 'Time slot not found or no longer available'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate time slot is in the future
        if time_slot.start_time <= timezone.now():
            return Response(
                {'error': 'Cannot book appointments in the past'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create appointment
        try:
            appointment = Appointment.objects.create(
                patient=request.user,
                psychologist=psychologist,
                service=service,
                appointment_date=time_slot.start_time,
                duration_minutes=service.duration_minutes,
                session_type=session_type,
                notes=notes,
                status='scheduled'
            )
            
            # Mark time slot as booked
            time_slot.is_available = False
            time_slot.appointment = appointment
            time_slot.save()
            
            # Log appointment creation
            log_action(
                user=request.user,
                action='create',
                obj=appointment,
                request=request,
                metadata={
                    'psychologist_id': psychologist.id,
                    'service_id': service.id,
                    'session_type': session_type
                }
            )
            
            # Serialize response
            appointment_data = AppointmentSerializer(appointment).data
            
            return Response({
                'message': 'Appointment booked successfully',
                'appointment': appointment_data,
                'booking_details': {
                    'psychologist_name': psychologist.get_full_name(),
                    'service_name': service.name,
                    'session_type': session_type,
                    'appointment_date': time_slot.start_time.isoformat(),
                    'duration_minutes': service.duration_minutes,
                    'consultation_fee': str(service.standard_fee),
                    'medicare_rebate': str(service.medicare_rebate),
                    'out_of_pocket_cost': str(service.out_of_pocket_cost)
                }
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': f'Failed to create appointment: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AppointmentBookingSummaryView(APIView):
    """
    Get booking summary for payment page
    
    Query Parameters:
    - appointment_id (required): ID of the booked appointment
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        appointment_id = request.query_params.get('appointment_id')
        
        if not appointment_id:
            return Response(
                {'error': 'appointment_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            appointment = Appointment.objects.get(id=appointment_id, patient=request.user)
        except Appointment.DoesNotExist:
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get psychologist profile
        psychologist_profile = PsychologistProfile.objects.get(user=appointment.psychologist)
        
        return Response({
            'appointment_id': appointment.id,
            'status': appointment.status,
            'patient': {
                'name': appointment.patient.get_full_name(),
                'email': appointment.patient.email,
                'phone': appointment.patient.phone_number
            },
            'psychologist': {
                'id': appointment.psychologist.id,
                'name': appointment.psychologist.get_full_name(),
                'title': psychologist_profile.title,
                'qualifications': psychologist_profile.qualifications,
                'ahpra_number': psychologist_profile.ahpra_registration_number,
                'profile_image_url': request.build_absolute_uri(psychologist_profile.profile_image.url) if psychologist_profile.profile_image else None
            },
            'service': {
                'id': appointment.service.id,
                'name': appointment.service.name,
                'description': appointment.service.description,
                'duration_minutes': appointment.duration_minutes
            },
            'session': {
                'type': appointment.session_type,
                'appointment_date': appointment.appointment_date.isoformat(),
                'formatted_date': appointment.appointment_date.strftime('%A, %d %B %Y'),
                'formatted_time': appointment.appointment_date.strftime('%I:%M %p'),
                'video_room_id': appointment.video_room_id if appointment.session_type == 'telehealth' else None
            },
            'pricing': {
                'consultation_fee': str(appointment.service.standard_fee),
                'medicare_rebate': str(appointment.service.medicare_rebate),
                'out_of_pocket_cost': str(appointment.service.out_of_pocket_cost),
                'medicare_item_number': appointment.service.medicare_item_number
            },
            'notes': appointment.notes,
            'created_at': appointment.created_at.isoformat()
        })

