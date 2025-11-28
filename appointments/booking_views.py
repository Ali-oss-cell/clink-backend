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
from .time_slot_manager import TimeSlotManager
from audit.utils import log_action

User = get_user_model()


def check_medicare_session_limit(patient, service):
    """
    Check if patient has reached Medicare session limit (10 sessions/year)
    
    Args:
        patient: User instance (patient)
        service: Service instance
    
    Returns:
        tuple: (is_allowed: bool, error_message: str or None, sessions_used: int, sessions_remaining: int)
    """
    from billing.models import MedicareClaim, MedicareItemNumber
    from django.utils import timezone
    
    # If service doesn't have Medicare item number, no limit applies
    if not service.medicare_item_number:
        return True, None, 0, None
    
    # Get Medicare item number model
    try:
        medicare_item = MedicareItemNumber.objects.get(
            item_number=service.medicare_item_number,
            is_active=True
        )
    except MedicareItemNumber.DoesNotExist:
        # Item number doesn't exist in our system, allow booking but log warning
        return True, None, 0, None
    
    # Get current year
    current_year = timezone.now().year
    
    # Count sessions this year - check both:
    # 1. Completed appointments with this Medicare item number
    # 2. Medicare claims (approved or paid)
    from .models import Appointment
    
    # Count completed appointments this year with this service/item number
    completed_appointments = Appointment.objects.filter(
        patient=patient,
        service__medicare_item_number=service.medicare_item_number,
        status='completed',
        appointment_date__year=current_year
    ).count()
    
    # Count Medicare claims this year
    medicare_claims = MedicareClaim.objects.filter(
        patient=patient,
        medicare_item_number=medicare_item,
        claim_date__year=current_year,
        status__in=['approved', 'paid']
    ).count()
    
    # Use the higher count (in case some appointments don't have claims yet)
    sessions_this_year = max(completed_appointments, medicare_claims)
    
    # Check if limit reached
    max_sessions = medicare_item.max_sessions_per_year
    
    if sessions_this_year >= max_sessions:
        return False, f"Medicare session limit reached ({max_sessions} sessions per calendar year). You have used {sessions_this_year} sessions this year.", sessions_this_year, 0
    
    sessions_remaining = max_sessions - sessions_this_year
    
    return True, None, sessions_this_year, sessions_remaining


def check_medicare_referral_requirement(patient, service):
    """
    Check if GP referral is required for Medicare-eligible service
    
    Args:
        patient: User instance (patient)
        service: Service instance
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    from billing.models import MedicareItemNumber
    
    # If service doesn't have Medicare item number, no referral required
    if not service.medicare_item_number:
        return True, None
    
    # Get Medicare item number model
    try:
        medicare_item = MedicareItemNumber.objects.get(
            item_number=service.medicare_item_number,
            is_active=True
        )
    except MedicareItemNumber.DoesNotExist:
        return True, None
    
    # Check if referral is required
    if medicare_item.requires_referral:
        # Check if patient has GP referral
        try:
            patient_profile = patient.patient_profile
            if not patient_profile.has_gp_referral:
                return False, "GP referral is required for Medicare rebate. Please provide a referral from your GP before booking."
            
            # TODO: Check if referral is still valid (usually 12 months)
            # For now, just check if referral exists
            
        except AttributeError:
            return False, "Patient profile not found. Please complete your profile."
    
    return True, None


def validate_medicare_item_number(item_number):
    """
    Validate Medicare item number exists and is active
    
    Args:
        item_number: Medicare item number string
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None, medicare_item: MedicareItemNumber or None)
    """
    from billing.models import MedicareItemNumber
    
    if not item_number:
        return True, None, None
    
    try:
        medicare_item = MedicareItemNumber.objects.get(
            item_number=item_number,
            is_active=True
        )
        return True, None, medicare_item
    except MedicareItemNumber.DoesNotExist:
        return False, f"Invalid Medicare item number: {item_number}. This item number is not active or does not exist.", None


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
        
        # Validate dates - start from tomorrow (not today)
        tomorrow = timezone.now().date() + timedelta(days=1)
        if start_date < tomorrow:
            start_date = tomorrow
        
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
        
        # Generate or retrieve time slots using improved manager
        time_slots = TimeSlotManager.generate_slots_for_psychologist(
            psychologist, 
            start_date, 
            end_date
        )
        
        # Filter available slots - only show slots from tomorrow onwards
        tomorrow_start = timezone.datetime.combine(
            timezone.now().date() + timedelta(days=1),
            timezone.datetime.min.time()
        ).replace(tzinfo=timezone.get_current_timezone())
        
        available_slots = time_slots.filter(
            is_available=True,
            start_time__gte=tomorrow_start
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
        
        # Ensure tomorrow is included even if it has no slots
        tomorrow = timezone.now().date() + timedelta(days=1)
        tomorrow_key = tomorrow.isoformat()
        
        if tomorrow_key not in slots_by_date and tomorrow <= end_date:
            slots_by_date[tomorrow_key] = {
                'date': tomorrow_key,
                'day_name': tomorrow.strftime('%A'),
                'slots': []
            }
        
        # Convert to sorted list
        available_dates = sorted(slots_by_date.values(), key=lambda x: x['date'])
        
        # Update start_date to reflect actual start (tomorrow)
        actual_start_date = tomorrow if tomorrow <= end_date else start_date
        
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
                'start_date': actual_start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'available_dates': available_dates,
            'total_available_slots': available_slots.count()
        })
    


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
        
        # Ensure we don't query past dates - start from tomorrow
        tomorrow = now.date() + timedelta(days=1)
        if start_date < tomorrow:
            start_date = tomorrow
        
        # Get time slots for the month - only from tomorrow onwards
        tomorrow_start = timezone.datetime.combine(
            tomorrow,
            timezone.datetime.min.time()
        ).replace(tzinfo=timezone.get_current_timezone())
        
        time_slots = TimeSlot.objects.filter(
            psychologist=psychologist,
            date__gte=start_date,
            date__lte=end_date,
            is_available=True,
            start_time__gte=tomorrow_start
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
                psychologist=psychologist
            )
        except TimeSlot.DoesNotExist:
            return Response(
                {'error': 'Time slot not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate time slot is in the future
        if time_slot.start_time <= timezone.now():
            return Response(
                {'error': 'Cannot book appointments in the past'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check availability using improved manager
        is_available, conflict_reason = TimeSlotManager.check_slot_availability(
            psychologist,
            time_slot.start_time,
            time_slot.end_time
        )
        
        if not is_available:
            return Response(
                {'error': conflict_reason or 'Time slot is not available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Medicare Compliance Checks
        # 1. Validate Medicare item number (if service has one)
        if service.medicare_item_number:
            is_valid, error_msg, medicare_item = validate_medicare_item_number(service.medicare_item_number)
            if not is_valid:
                return Response(
                    {'error': error_msg},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # 2. Check Medicare session limit (10 sessions/year)
        is_allowed, limit_error, sessions_used, sessions_remaining = check_medicare_session_limit(
            request.user, service
        )
        if not is_allowed:
            return Response(
                {
                    'error': limit_error,
                    'medicare_limit_info': {
                        'sessions_used': sessions_used,
                        'sessions_remaining': sessions_remaining,
                        'limit_reached': True
                    }
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 3. Check GP referral requirement (if Medicare-eligible)
        is_valid, referral_error = check_medicare_referral_requirement(request.user, service)
        if not is_valid:
            return Response(
                {'error': referral_error},
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
            
            # Mark time slot as booked using improved manager
            TimeSlotManager.mark_slot_as_booked(time_slot, appointment)
            
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
            
            # Prepare response with Medicare info
            booking_details = {
                'psychologist_name': psychologist.get_full_name(),
                'service_name': service.name,
                'session_type': session_type,
                'appointment_date': time_slot.start_time.isoformat(),
                'duration_minutes': service.duration_minutes,
                'consultation_fee': str(service.standard_fee),
                'medicare_rebate': str(service.medicare_rebate),
                'out_of_pocket_cost': str(service.out_of_pocket_cost)
            }
            
            # Add Medicare session limit info if applicable
            if service.medicare_item_number and sessions_remaining is not None:
                booking_details['medicare_limit_info'] = {
                    'sessions_used': sessions_used,
                    'sessions_remaining': sessions_remaining,
                    'max_sessions_per_year': 10
                }
            
            return Response({
                'message': 'Appointment booked successfully',
                'appointment': appointment_data,
                'booking_details': booking_details
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': f'Failed to create appointment: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class MedicareSessionLimitCheckView(APIView):
    """
    Check Medicare session limit for a specific service before booking
    
    GET /api/appointments/medicare-limit-check/?service_id=1
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        service_id = request.query_params.get('service_id')
        
        if not service_id:
            return Response(
                {'error': 'service_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            return Response(
                {'error': 'Service not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check Medicare session limit
        is_allowed, error_msg, sessions_used, sessions_remaining = check_medicare_session_limit(
            request.user, service
        )
        
        response_data = {
            'service_id': service.id,
            'service_name': service.name,
            'medicare_item_number': service.medicare_item_number,
            'is_allowed': is_allowed,
            'sessions_used': sessions_used,
            'sessions_remaining': sessions_remaining,
            'max_sessions': 10,
            'current_year': timezone.now().year
        }
        
        if not is_allowed:
            response_data['error'] = error_msg
        
        return Response(response_data)


class MedicareSessionInfoView(APIView):
    """
    Get patient's Medicare session information for current year
    
    GET /api/appointments/medicare-session-info/
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from billing.models import MedicareItemNumber, MedicareClaim
        from .models import Appointment
        
        current_year = timezone.now().year
        
        # Get all Medicare-eligible services the patient has used
        services_with_medicare = Service.objects.filter(
            medicare_item_number__isnull=False
        ).distinct()
        
        session_info = []
        total_sessions_used = 0
        
        for service in services_with_medicare:
            # Count sessions for this service
            completed_appointments = Appointment.objects.filter(
                patient=request.user,
                service=service,
                status='completed',
                appointment_date__year=current_year
            ).count()
            
            # Count Medicare claims
            try:
                medicare_item = MedicareItemNumber.objects.get(
                    item_number=service.medicare_item_number,
                    is_active=True
                )
                medicare_claims = MedicareClaim.objects.filter(
                    patient=request.user,
                    medicare_item_number=medicare_item,
                    claim_date__year=current_year,
                    status__in=['approved', 'paid']
                ).count()
            except MedicareItemNumber.DoesNotExist:
                medicare_claims = 0
            
            sessions_used = max(completed_appointments, medicare_claims)
            sessions_remaining = max(0, 10 - sessions_used)
            
            if sessions_used > 0 or service.medicare_item_number:
                session_info.append({
                    'service_id': service.id,
                    'service_name': service.name,
                    'item_number': service.medicare_item_number,
                    'sessions_used': sessions_used,
                    'sessions_remaining': sessions_remaining,
                    'max_sessions': 10
                })
            
            total_sessions_used = max(total_sessions_used, sessions_used)
        
        # Overall summary
        overall_sessions_remaining = max(0, 10 - total_sessions_used)
        
        return Response({
            'current_year': current_year,
            'sessions_used': total_sessions_used,
            'sessions_remaining': overall_sessions_remaining,
            'max_sessions': 10,
            'limit_reached': total_sessions_used >= 10,
            'services': session_info
        })


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

