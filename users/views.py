"""
Users app views - Authentication and user management for Psychology Clinic
Supports intake forms, progress notes, and role-based dashboards
"""

from django.contrib.auth import get_user_model  # type: ignore
from rest_framework import viewsets, status, permissions  # type: ignore
from rest_framework.decorators import action  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.views import APIView  # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny  # type: ignore
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore
from rest_framework.filters import SearchFilter, OrderingFilter  # type: ignore
from rest_framework.pagination import PageNumberPagination  # type: ignore
from django_filters.rest_framework import DjangoFilterBackend  # type: ignore
from django.db.models import Q, Count  # type: ignore
from django.db import models  # type: ignore
from django.utils import timezone  # type: ignore
from datetime import timedelta  # type: ignore

from .models import PatientProfile, ProgressNote
from appointments.models import Appointment
from audit.utils import log_action

# Import billing models for financial calculations
try:
    from billing.models import Invoice, Payment, MedicareClaim
    BILLING_AVAILABLE = True
except ImportError:
    BILLING_AVAILABLE = False
    Invoice = None
    Payment = None
    MedicareClaim = None

# Import services models for psychologist profiles
try:
    from services.models import PsychologistProfile
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False
    PsychologistProfile = None
from .serializers import (
    UserSerializer, UserUpdateSerializer, PatientRegistrationSerializer, PatientProfileSerializer,
    IntakeFormSerializer, ProgressNoteSerializer, ProgressNoteCreateSerializer,
    PsychologistDashboardSerializer, PatientDashboardSerializer
)

User = get_user_model()


class UserListPagination(PageNumberPagination):
    """Custom pagination for user list endpoint"""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class AdminCreateUserView(APIView):
    """
    Simple endpoint for admin to create users (practice manager or psychologist)
    
    POST /api/auth/admin/create-user/
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a new user (admin only)"""
        # Check permissions
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Only administrators can create users'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get data
        email = request.data.get('email')
        password = request.data.get('password')
        full_name = request.data.get('full_name') or request.data.get('name')
        role = request.data.get('role')
        phone_number = request.data.get('phone_number', '')
        
        # Validate required fields
        if not email or not password or not full_name or not role:
            return Response(
                {'error': 'Missing required fields: email, password, full_name, role'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate role
        valid_roles = ['practice_manager', 'psychologist', 'admin']
        if role not in valid_roles:
            return Response(
                {'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If psychologist, validate AHPRA fields
        if role == 'psychologist':
            ahpra_registration_number = request.data.get('ahpra_registration_number')
            ahpra_expiry_date = request.data.get('ahpra_expiry_date')
            
            if not ahpra_registration_number:
                return Response(
                    {'error': 'AHPRA registration number is required for psychologists'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not ahpra_expiry_date:
                return Response(
                    {'error': 'AHPRA expiry date is required for psychologists'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Split full_name into first_name and last_name
        name_parts = full_name.strip().split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Generate username from email
        username = email.split('@')[0]
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'User with this email already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                role=role,
                is_verified=True,
                is_active=True
            )
            
            # Create psychologist profile if role is psychologist
            if role == 'psychologist':
                from services.models import PsychologistProfile
                from datetime import datetime
                
                # Parse AHPRA expiry date
                try:
                    if isinstance(ahpra_expiry_date, str):
                        expiry_date = datetime.strptime(ahpra_expiry_date, '%Y-%m-%d').date()
                    else:
                        expiry_date = ahpra_expiry_date
                except (ValueError, TypeError):
                    return Response(
                        {'error': 'Invalid AHPRA expiry date format. Use YYYY-MM-DD'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Check if AHPRA number already exists
                if PsychologistProfile.objects.filter(ahpra_registration_number=ahpra_registration_number).exists():
                    return Response(
                        {'error': 'AHPRA registration number already exists'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Get optional psychologist fields
                title = request.data.get('title', 'Dr')
                qualifications = request.data.get('qualifications', '')
                years_experience = request.data.get('years_experience', 0)
                consultation_fee = request.data.get('consultation_fee', 180.00)
                medicare_provider_number = request.data.get('medicare_provider_number', '')
                bio = request.data.get('bio', '')
                is_accepting_new_patients = request.data.get('is_accepting_new_patients', True)
                
                # Create psychologist profile with all details
                psychologist_profile = PsychologistProfile.objects.create(
                    user=user,
                    ahpra_registration_number=ahpra_registration_number,
                    ahpra_expiry_date=expiry_date,
                    title=title,
                    qualifications=qualifications,
                    years_experience=years_experience,
                    consultation_fee=consultation_fee,
                    medicare_provider_number=medicare_provider_number,
                    bio=bio,
                    is_accepting_new_patients=is_accepting_new_patients
                )
                
                # Handle specializations if provided
                specializations = request.data.get('specializations', [])
                if specializations:
                    psychologist_profile.specializations.set(specializations)
                
                # Handle services if provided
                services = request.data.get('services_offered', [])
                if services:
                    psychologist_profile.services_offered.set(services)
            
            # Log user creation
            log_action(
                user=request.user,
                action='create',
                obj=user,
                request=request,
                metadata={'created_role': role}
            )
            
            return Response(
                {
                    'message': f'{role.replace("_", " ").title()} created successfully',
                    'user': UserSerializer(user).data
                }, 
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return Response(
                {'error': f'Error creating user: {str(e)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class UserViewSet(viewsets.ModelViewSet):
    """
    User management viewset with role-based filtering, search, and pagination
    
    Provides different access levels based on user role:
    - Admins/Practice Managers: Can see all users
    - Psychologists: Can see their patients and themselves
    - Patients: Can only see themselves
    
    Query Parameters:
    - role: Filter by role (admin, psychologist, practice_manager, patient)
    - search: Search by name or email
    - is_verified: Filter by verification status (true/false)
    - is_active: Filter by active status (true/false)
    - page: Page number for pagination
    - page_size: Items per page (default: 100)
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = UserListPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_verified', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'username']
    ordering_fields = ['created_at', 'last_login', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']  # Default ordering
    
    def get_queryset(self):
        """
        Filter users based on role and permissions, then apply query filters
        
        Returns:
            QuerySet: Filtered users based on current user's role and query parameters
        """
        user = self.request.user
        queryset = User.objects.all()
        
        # Apply role-based access control
        if user.is_admin_user() or user.is_practice_manager():
            # Admin and practice managers can see all users
            queryset = User.objects.all()
        elif user.is_psychologist():
            # Psychologists can see their patients and themselves
            queryset = User.objects.filter(
                Q(role=User.UserRole.PATIENT) | Q(id=user.id)
            )
        else:
            # Patients can only see themselves
            queryset = User.objects.filter(id=user.id)
        
        # Apply additional filters from query parameters
        # These are handled by DjangoFilterBackend, but we can add custom logic here if needed
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Get single user with psychologist profile if applicable"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update user (PUT) - full update"""
        return self._update_user(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """Update user (PATCH) - partial update"""
        return self._update_user(request, partial=True, *args, **kwargs)
    
    def _update_user(self, request, partial=False, *args, **kwargs):
        """Internal method to handle user updates with permission checks"""
        instance = self.get_object()
        user = request.user
        
        # Permission checks
        if not (user.is_admin_user() or user.is_practice_manager()):
            return Response(
                {'error': 'You do not have permission to update users'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Practice managers cannot update admins
        if user.is_practice_manager() and instance.is_admin_user():
            return Response(
                {'error': 'Practice managers cannot update administrators'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Practice managers cannot change roles
        if user.is_practice_manager() and 'role' in request.data:
            return Response(
                {'error': 'Practice managers cannot change user roles'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Admins cannot change another user to admin
        if user.is_admin_user() and request.data.get('role') == 'admin' and instance.id != user.id:
            return Response(
                {'error': 'Cannot change another user to admin role'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Store old values for audit log
        old_data = {
            'email': instance.email,
            'role': instance.role,
            'is_active': instance.is_active,
            'is_verified': instance.is_verified,
        }
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Get new values for audit log
        updated_instance = User.objects.get(pk=instance.pk)
        new_data = {
            'email': updated_instance.email,
            'role': updated_instance.role,
            'is_active': updated_instance.is_active,
            'is_verified': updated_instance.is_verified,
        }
        
        # Calculate changes for audit log
        changes = {}
        for key in old_data:
            if old_data[key] != new_data[key]:
                changes[key] = {
                    'old': old_data[key],
                    'new': new_data[key]
                }
        
        # Log the update action
        if changes:
            log_action(
                user=request.user,
                action='update',
                obj=updated_instance,
                changes=changes,
                request=request
            )
        
        # Return updated user with full serializer
        response_serializer = UserSerializer(updated_instance)
        return Response(response_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete user (admin only) with safety checks"""
        instance = self.get_object()
        user = request.user
        
        # Only admins can delete users
        if not user.is_admin_user():
            return Response(
                {'error': 'Only administrators can delete users'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Safety checks
        errors = []
        
        # Check for active appointments
        if SERVICES_AVAILABLE:
            active_appointments = Appointment.objects.filter(
                Q(patient=instance) | Q(psychologist=instance),
                status__in=['scheduled', 'confirmed']
            ).exists()
            if active_appointments:
                errors.append("User has active appointments")
        
        # Check for unpaid invoices
        if BILLING_AVAILABLE and Invoice:
            unpaid_invoices = Invoice.objects.filter(
                patient=instance,
                status__in=['pending', 'overdue']
            ).exists()
            if unpaid_invoices:
                errors.append("User has unpaid invoices")
        
        # Check if this is the only admin
        if instance.is_admin_user():
            admin_count = User.objects.filter(role=User.UserRole.ADMIN, is_active=True).count()
            if admin_count <= 1:
                errors.append("Cannot delete the only active administrator")
        
        if errors:
            return Response(
                {'error': 'Cannot delete user. ' + ' '.join(errors)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log the deletion before deleting
        log_action(
            user=request.user,
            action='delete',
            obj=instance,
            request=request,
            metadata={'deleted_user_email': instance.email}
        )
        
        # Delete the user
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomLoginView(APIView):
    """
    Custom login view that accepts email instead of username
    
    Provides JWT token-based authentication for the psychology clinic.
    Returns access and refresh tokens along with user information.
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Authenticate user with email and password
        
        Returns:
            Response: JWT tokens and user data on success, error on failure
        """
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Validate required fields
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find user by email (case-insensitive)
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify password
        if not user.check_password(password):
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens for authenticated user
        refresh = RefreshToken.for_user(user)
        
        # Log successful login
        log_action(
            user=user,
            action='login',
            request=request,
            metadata={'login_method': 'email_password'}
        )
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })


class PatientRegistrationView(APIView):
    """Patient registration with intake form initialization"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PatientRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Patient registered successfully',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IntakeFormView(APIView):
    """Digital intake form for patients"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get patient's intake form data"""
        if not request.user.is_patient():
            return Response(
                {'error': 'Only patients can access intake forms'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            patient_profile = request.user.patient_profile
            serializer = IntakeFormSerializer(patient_profile)
            return Response(serializer.data)
        except PatientProfile.DoesNotExist:
            # Create profile if it doesn't exist
            patient_profile = PatientProfile.objects.create(user=request.user)
            serializer = IntakeFormSerializer(patient_profile)
            return Response(serializer.data)
    
    def post(self, request):
        """Submit intake form data"""
        if not request.user.is_patient():
            return Response(
                {'error': 'Only patients can submit intake forms'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        patient_profile, created = PatientProfile.objects.get_or_create(
            user=request.user
        )
        
        serializer = IntakeFormSerializer(
            patient_profile, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            # Mark intake as completed
            patient_profile.intake_completed = True
            patient_profile.save()
            
            return Response({
                'message': 'Intake form submitted successfully',
                'intake_completed': True,
                'profile': {
                    'id': patient_profile.id,
                    'preferred_name': patient_profile.preferred_name,
                    'intake_completed': patient_profile.intake_completed,
                    'created_at': patient_profile.created_at
                }
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request):
        """Update intake form data"""
        if not request.user.is_patient():
            return Response(
                {'error': 'Only patients can update intake forms'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        patient_profile, created = PatientProfile.objects.get_or_create(
            user=request.user
        )
        
        serializer = IntakeFormSerializer(
            patient_profile, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Intake form updated successfully',
                'data': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProgressNoteViewSet(viewsets.ModelViewSet):
    """SOAP Notes management for psychologists"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter progress notes based on user role"""
        user = self.request.user
        
        if user.is_psychologist():
            # Get psychologist's notes, ordered by patient name (last_name, first_name)
            # then by session date (newest first) for same patient
            return ProgressNote.objects.filter(
                psychologist=user
            ).select_related('patient').order_by(
                'patient__last_name',
                'patient__first_name',
                '-session_date'  # Newest first for same patient
            )
        elif user.is_practice_manager() or user.is_admin_user():
            # Managers/Admins see all notes, ordered by patient name
            return ProgressNote.objects.all().select_related('patient').order_by(
                'patient__last_name',
                'patient__first_name',
                '-session_date'
            )
        else:
            # Patients see their own notes, ordered by session date
            return ProgressNote.objects.filter(
                patient=user
            ).order_by('-session_date')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProgressNoteCreateSerializer
        return ProgressNoteSerializer
    
    @action(detail=False, methods=['get'])
    def by_patient(self, request):
        """Get progress notes for a specific patient"""
        patient_id = request.query_params.get('patient_id')
        if not patient_id:
            return Response(
                {'error': 'patient_id parameter required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check permissions
        if not (request.user.is_psychologist() or 
                request.user.is_practice_manager() or 
                request.user.is_admin_user()):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        notes = ProgressNote.objects.filter(patient_id=patient_id)
        serializer = ProgressNoteSerializer(notes, many=True)
        return Response(serializer.data)


class PsychologistDashboardView(APIView):
    """Dashboard data for psychologists"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get comprehensive dashboard data for psychologists
        
        Returns real-time statistics including:
        - Today's appointments count
        - Total patients count
        - Upcoming sessions
        - Recent progress notes
        - Quick action data
        """
        if not request.user.is_psychologist():
            return Response(
                {'error': 'Only psychologists can access this dashboard'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = timezone.now().date()
        now = timezone.now()
        
        # Calculate start and end of week (Monday to Sunday)
        from datetime import timedelta, datetime, time
        days_since_monday = today.weekday()
        week_start_date = today - timedelta(days=days_since_monday)
        week_end_date = week_start_date + timedelta(days=7)
        
        # Convert to datetime objects
        week_start = timezone.make_aware(datetime.combine(week_start_date, time.min))
        week_end = timezone.make_aware(datetime.combine(week_end_date, time.min))
        
        # Calculate start and end of current month
        month_start_date = today.replace(day=1)
        if month_start_date.month == 12:
            month_end_date = month_start_date.replace(year=month_start_date.year + 1, month=1)
        else:
            month_end_date = month_start_date.replace(month=month_start_date.month + 1)
        
        # Convert to datetime objects
        month_start = timezone.make_aware(datetime.combine(month_start_date, time.min))
        month_end = timezone.make_aware(datetime.combine(month_end_date, time.min))
        
        # Get today's appointments
        today_appointments = Appointment.objects.filter(
            psychologist=request.user,
            appointment_date__date=today
        )
        today_appointments_count = today_appointments.count()
        completed_sessions_today = today_appointments.filter(status='completed').count()
        
        # Get upcoming appointments this week
        upcoming_this_week = Appointment.objects.filter(
            psychologist=request.user,
            appointment_date__gte=week_start,
            appointment_date__lt=week_end,
            status__in=['scheduled', 'confirmed']
        )
        upcoming_appointments_this_week = upcoming_this_week.count()
        
        # Get patient statistics
        total_patients_count = User.objects.filter(
            role=User.UserRole.PATIENT,
            progress_notes__psychologist=request.user
        ).distinct().count()
        
        # Active patients (patients with appointments in last 90 days or upcoming)
        active_date_threshold = now - timedelta(days=90)
        active_patients_count = User.objects.filter(
            role=User.UserRole.PATIENT
        ).filter(
            Q(patient_appointments__psychologist=request.user, 
              patient_appointments__appointment_date__gte=active_date_threshold) |
            Q(patient_appointments__psychologist=request.user,
              patient_appointments__status__in=['scheduled', 'confirmed'])
        ).distinct().count()
        
        # Get recent progress notes (last 5)
        recent_notes_list = ProgressNote.objects.filter(
            psychologist=request.user
        ).select_related('patient').order_by('-created_at')[:5]
        
        recent_notes = [
            {
                'id': note.id,
                'patient_name': note.patient.get_full_name(),
                'session_number': note.session_number,
                'session_date': note.session_date.isoformat() if note.session_date else None,
                'progress_rating': note.progress_rating,
                'created_at': note.created_at.isoformat() if note.created_at else None
            }
            for note in recent_notes_list
        ]
        
        # Calculate pending notes (completed appointments without progress notes)
        completed_without_notes = Appointment.objects.filter(
            psychologist=request.user,
            status='completed',
            completed_at__isnull=False
        ).exclude(
            id__in=ProgressNote.objects.filter(
                psychologist=request.user
            ).values_list('patient__patient_appointments__id', flat=True)
        )
        
        # Better calculation: appointments completed in last 7 days without notes
        recent_completed = Appointment.objects.filter(
            psychologist=request.user,
            status='completed',
            completed_at__gte=now - timedelta(days=7)
        )
        
        pending_notes_count = 0
        for apt in recent_completed:
            # Check if there's a note for this appointment
            has_note = ProgressNote.objects.filter(
                psychologist=request.user,
                patient=apt.patient,
                session_date__date=apt.appointment_date.date()
            ).exists()
            if not has_note:
                pending_notes_count += 1
        
        # Calculate monthly stats
        appointments_this_month = Appointment.objects.filter(
            psychologist=request.user,
            appointment_date__gte=month_start,
            appointment_date__lt=month_end
        )
        total_appointments_this_month = appointments_this_month.count()
        
        # Get average rating from progress notes
        progress_ratings = ProgressNote.objects.filter(
            psychologist=request.user
        ).exclude(progress_rating__isnull=True).values_list('progress_rating', flat=True)
        
        average_rating = None
        if progress_ratings:
            average_rating = sum(progress_ratings) / len(progress_ratings)
            average_rating = round(average_rating, 1)
        
        # Sessions completed this week
        sessions_completed_this_week = Appointment.objects.filter(
            psychologist=request.user,
            status='completed',
            completed_at__gte=week_start,
            completed_at__lt=week_end
        ).count()
        
        # Build response matching frontend format
        dashboard_data = {
            'today_appointments_count': today_appointments_count,
            'upcoming_appointments_this_week': upcoming_appointments_this_week,
            'recent_notes': recent_notes,
            'active_patients_count': active_patients_count,
            'total_patients_count': total_patients_count,
            'pending_notes_count': pending_notes_count,
            'completed_sessions_today': completed_sessions_today,
            'stats': {
                'total_appointments_this_month': total_appointments_this_month,
                'average_rating': average_rating,
                'sessions_completed_this_week': sessions_completed_this_week
            }
        }
        
        return Response(dashboard_data)


class PatientDashboardView(APIView):
    """Dashboard data for patients"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get comprehensive dashboard data for patients
        
        Returns real-time information including:
        - Next appointment details
        - Session history
        - Intake form status
        - Progress tracking
        - Quick actions
        """
        if not request.user.is_patient():
            return Response(
                {'error': 'Only patients can access this dashboard'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get patient profile
        try:
            patient_profile = request.user.patient_profile
        except PatientProfile.DoesNotExist:
            patient_profile = PatientProfile.objects.create(user=request.user)
        
        now = timezone.now()
        
        # Get real appointment data
        next_appointment = Appointment.objects.filter(
            patient=request.user,
            appointment_date__gte=now,
            status__in=['scheduled', 'confirmed']
        ).order_by('appointment_date').first()
        
        # Get appointment statistics
        total_appointments = Appointment.objects.filter(patient=request.user).count()
        completed_appointments = Appointment.objects.filter(
            patient=request.user, 
            status='completed'
        ).count()
        
        # Get recent progress notes
        recent_notes = ProgressNote.objects.filter(
            patient=request.user
        ).order_by('-session_date')[:3]
        
        # Get comprehensive dashboard data
        dashboard_data = {
            # Next appointment details
            'next_appointment': {
                'id': next_appointment.id if next_appointment else None,
                'appointment_date': next_appointment.appointment_date if next_appointment else None,
                'psychologist_name': next_appointment.psychologist.get_full_name() if next_appointment else None,
                'service_name': next_appointment.service.name if next_appointment and next_appointment.service else None,
                'status': next_appointment.status if next_appointment else None,
                'duration_minutes': next_appointment.duration_minutes if next_appointment else None,
                'video_room_id': next_appointment.video_room_id if next_appointment else None
            } if next_appointment else {},
            
            # Session statistics
            'total_sessions': request.user.progress_notes.count(),
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'intake_completed': patient_profile.intake_completed,
            
            # Recent progress tracking
            'recent_progress': [
                {
                    'id': note.id,
                    'session_date': note.session_date,
                    'session_number': note.session_number,
                    'progress_rating': note.progress_rating,
                    'psychologist_name': note.psychologist.get_full_name(),
                    'created_at': note.created_at
                }
                for note in recent_notes
            ],
            
            # Quick actions and status
            'quick_actions': {
                'can_book_appointment': True,
                'can_complete_intake': not patient_profile.intake_completed,
                'can_view_progress': request.user.progress_notes.count() > 0,
                'has_upcoming_appointment': next_appointment is not None
            },
            
            # Placeholder for future billing integration
            'outstanding_invoices': 0,  # Will implement with billing system
            'recent_invoices': []  # Will implement with billing system
        }
        
        serializer = PatientDashboardSerializer(dashboard_data)
        return Response(serializer.data)


class PracticeManagerDashboardView(APIView):
    """Dashboard data for practice managers"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get comprehensive dashboard data for practice managers
        
        Returns clinic-wide statistics including:
        - Appointment statistics
        - Revenue and financial data
        - Staff and patient statistics
        - Recent activity
        """
        if not (request.user.is_practice_manager() or request.user.is_admin_user()):
            return Response(
                {'error': 'Only practice managers and admins can access this dashboard'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = timezone.now().date()
        now = timezone.now()
        
        # Calculate date ranges
        from datetime import timedelta, datetime, time
        days_since_monday = today.weekday()
        week_start_date = today - timedelta(days=days_since_monday)
        week_end_date = week_start_date + timedelta(days=7)
        week_start = timezone.make_aware(datetime.combine(week_start_date, time.min))
        week_end = timezone.make_aware(datetime.combine(week_end_date, time.min))
        
        month_start_date = today.replace(day=1)
        if month_start_date.month == 12:
            month_end_date = month_start_date.replace(year=month_start_date.year + 1, month=1)
        else:
            month_end_date = month_start_date.replace(month=month_start_date.month + 1)
        month_start = timezone.make_aware(datetime.combine(month_start_date, time.min))
        month_end = timezone.make_aware(datetime.combine(month_end_date, time.min))
        
        # Appointment Statistics
        today_appointments = Appointment.objects.filter(appointment_date__date=today)
        today_appointments_count = today_appointments.count()
        completed_sessions_today = today_appointments.filter(status='completed').count()
        cancelled_appointments_today = today_appointments.filter(status='cancelled').count()
        
        this_week_appointments = Appointment.objects.filter(
            appointment_date__gte=week_start,
            appointment_date__lt=week_end
        )
        this_week_appointments_count = this_week_appointments.count()
        
        this_month_appointments = Appointment.objects.filter(
            appointment_date__gte=month_start,
            appointment_date__lt=month_end
        )
        this_month_appointments_count = this_month_appointments.count()
        
        # Patient Statistics
        total_patients = User.objects.filter(role=User.UserRole.PATIENT).count()
        new_patients_this_month = User.objects.filter(
            role=User.UserRole.PATIENT,
            created_at__gte=month_start
        ).count()
        
        # Active patients (patients with appointments in last 90 days or upcoming)
        active_date_threshold = now - timedelta(days=90)
        active_patients = User.objects.filter(role=User.UserRole.PATIENT).filter(
            Q(patient_appointments__appointment_date__gte=active_date_threshold) |
            Q(patient_appointments__status__in=['scheduled', 'confirmed'])
        ).distinct().count()
        
        # Staff Statistics
        total_psychologists = User.objects.filter(role=User.UserRole.PSYCHOLOGIST).count()
        total_practice_managers = User.objects.filter(role=User.UserRole.PRACTICE_MANAGER).count()
        
        # Financial Statistics (if billing is available)
        today_revenue = 0.00
        this_week_revenue = 0.00
        this_month_revenue = 0.00
        pending_invoices = 0
        total_revenue = 0.00
        
        if BILLING_AVAILABLE and Invoice:
            from django.db.models import Sum
            from decimal import Decimal
            
            # Today's revenue
            today_invoices = Invoice.objects.filter(
                service_date=today,
                status=Invoice.InvoiceStatus.PAID
            )
            today_revenue_sum = today_invoices.aggregate(total=Sum('total_amount'))['total']
            today_revenue = float(today_revenue_sum) if today_revenue_sum else 0.00
            
            # This week's revenue
            week_invoices = Invoice.objects.filter(
                service_date__gte=week_start_date,
                service_date__lt=week_end_date,
                status=Invoice.InvoiceStatus.PAID
            )
            week_revenue_sum = week_invoices.aggregate(total=Sum('total_amount'))['total']
            this_week_revenue = float(week_revenue_sum) if week_revenue_sum else 0.00
            
            # This month's revenue
            month_invoices = Invoice.objects.filter(
                service_date__gte=month_start_date,
                service_date__lt=month_end_date,
                status=Invoice.InvoiceStatus.PAID
            )
            month_revenue_sum = month_invoices.aggregate(total=Sum('total_amount'))['total']
            this_month_revenue = float(month_revenue_sum) if month_revenue_sum else 0.00
            
            # Pending invoices
            pending_invoices = Invoice.objects.filter(
                status__in=[Invoice.InvoiceStatus.SENT, Invoice.InvoiceStatus.DRAFT]
            ).count()
            
            # Total revenue
            total_invoices = Invoice.objects.filter(status=Invoice.InvoiceStatus.PAID)
            total_revenue_sum = total_invoices.aggregate(total=Sum('total_amount'))['total']
            total_revenue = float(total_revenue_sum) if total_revenue_sum else 0.00
        
        # Recent Appointments (last 10)
        recent_appointments_list = Appointment.objects.all().select_related(
            'patient', 'psychologist', 'service'
        ).order_by('-appointment_date')[:10]
        
        recent_appointments = [
            {
                'id': apt.id,
                'patient_name': apt.patient.get_full_name(),
                'psychologist_name': apt.psychologist.get_full_name(),
                'service_name': apt.service.name if apt.service else 'N/A',
                'appointment_date': apt.appointment_date.isoformat(),
                'status': apt.status,
                'session_type': apt.session_type
            }
            for apt in recent_appointments_list
        ]
        
        # Upcoming Appointments (next 10)
        upcoming_appointments_list = Appointment.objects.filter(
            appointment_date__gte=now,
            status__in=['scheduled', 'confirmed']
        ).select_related('patient', 'psychologist', 'service').order_by('appointment_date')[:10]
        
        upcoming_appointments = [
            {
                'id': apt.id,
                'patient_name': apt.patient.get_full_name(),
                'psychologist_name': apt.psychologist.get_full_name(),
                'service_name': apt.service.name if apt.service else 'N/A',
                'appointment_date': apt.appointment_date.isoformat(),
                'status': apt.status,
                'session_type': apt.session_type
            }
            for apt in upcoming_appointments_list
        ]
        
        # Top Psychologists (by appointment count)
        top_psychologists = User.objects.filter(
            role=User.UserRole.PSYCHOLOGIST
        ).annotate(
            appointment_count=Count('psychologist_appointments')
        ).order_by('-appointment_count')[:5]
        
        top_psychologists_list = [
            {
                'id': psych.id,
                'name': psych.get_full_name(),
                'email': psych.email,
                'appointment_count': psych.appointment_count
            }
            for psych in top_psychologists
        ]
        
        # Recent Invoices (if billing available)
        recent_invoices = []
        if BILLING_AVAILABLE and Invoice:
            recent_invoices_list = Invoice.objects.all().select_related(
                'patient', 'appointment'
            ).order_by('-created_at')[:10]
            
            recent_invoices = [
                {
                    'id': inv.id,
                    'invoice_number': inv.invoice_number,
                    'patient_name': inv.patient.get_full_name(),
                    'total_amount': float(inv.total_amount),
                    'status': inv.status,
                    'service_date': inv.service_date.isoformat() if inv.service_date else None
                }
                for inv in recent_invoices_list
            ]
        
        # Build comprehensive dashboard data
        dashboard_data = {
            'stats': {
                'today_appointments': today_appointments_count,
                'this_week_appointments': this_week_appointments_count,
                'this_month_appointments': this_month_appointments_count,
                'completed_sessions_today': completed_sessions_today,
                'cancelled_appointments_today': cancelled_appointments_today,
                'total_patients': total_patients,
                'active_patients': active_patients,
                'new_patients_this_month': new_patients_this_month,
                'total_psychologists': total_psychologists,
                'total_practice_managers': total_practice_managers,
                'today_revenue': today_revenue,
                'this_week_revenue': this_week_revenue,
                'this_month_revenue': this_month_revenue,
                'total_revenue': total_revenue,
                'pending_invoices': pending_invoices
            },
            'recent_appointments': recent_appointments,
            'upcoming_appointments': upcoming_appointments,
            'top_psychologists': top_psychologists_list,
            'recent_invoices': recent_invoices
        }
        
        return Response(dashboard_data)


class AdminDashboardView(APIView):
    """Dashboard data for system administrators"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get comprehensive dashboard data for system administrators
        
        Returns system-wide statistics including:
        - User statistics
        - System health metrics
        - Overall system activity
        """
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Only administrators can access this dashboard'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = timezone.now().date()
        now = timezone.now()
        
        # Calculate date ranges
        from datetime import timedelta, datetime, time
        month_start_date = today.replace(day=1)
        if month_start_date.month == 12:
            month_end_date = month_start_date.replace(year=month_start_date.year + 1, month=1)
        else:
            month_end_date = month_start_date.replace(month=month_start_date.month + 1)
        month_start = timezone.make_aware(datetime.combine(month_start_date, time.min))
        
        # User Statistics
        total_users = User.objects.count()
        total_patients = User.objects.filter(role=User.UserRole.PATIENT).count()
        total_psychologists = User.objects.filter(role=User.UserRole.PSYCHOLOGIST).count()
        total_practice_managers = User.objects.filter(role=User.UserRole.PRACTICE_MANAGER).count()
        total_admins = User.objects.filter(role=User.UserRole.ADMIN).count()
        
        # New users this month
        new_users_this_month = User.objects.filter(created_at__gte=month_start).count()
        new_patients_this_month = User.objects.filter(
            role=User.UserRole.PATIENT,
            created_at__gte=month_start
        ).count()
        new_psychologists_this_month = User.objects.filter(
            role=User.UserRole.PSYCHOLOGIST,
            created_at__gte=month_start
        ).count()
        
        # Verified users
        verified_users = User.objects.filter(is_verified=True).count()
        unverified_users = User.objects.filter(is_verified=False).count()
        
        # Appointment Statistics
        total_appointments = Appointment.objects.count()
        completed_appointments = Appointment.objects.filter(status='completed').count()
        scheduled_appointments = Appointment.objects.filter(status__in=['scheduled', 'confirmed']).count()
        cancelled_appointments = Appointment.objects.filter(status='cancelled').count()
        
        # Progress Notes Statistics
        total_progress_notes = ProgressNote.objects.count()
        
        # Financial Statistics (if billing available)
        total_invoices = 0
        total_revenue = 0.00
        total_medicare_claims = 0
        
        if BILLING_AVAILABLE:
            if Invoice:
                from django.db.models import Sum
                total_invoices = Invoice.objects.count()
                total_revenue_sum = Invoice.objects.filter(
                    status=Invoice.InvoiceStatus.PAID
                ).aggregate(total=Sum('total_amount'))['total']
                total_revenue = float(total_revenue_sum) if total_revenue_sum else 0.00
            
            if MedicareClaim:
                total_medicare_claims = MedicareClaim.objects.count()
        
        # Recent Users (last 10)
        recent_users_list = User.objects.all().order_by('-created_at')[:10]
        recent_users = [
            {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email,
                'role': user.role,
                'is_verified': user.is_verified,
                'created_at': user.created_at.isoformat()
            }
            for user in recent_users_list
        ]
        
        # System Health (basic metrics)
        system_health = {
            'status': 'good',
            'total_users': total_users,
            'total_appointments': total_appointments,
            'active_patients': User.objects.filter(
                role=User.UserRole.PATIENT,
                patient_appointments__status__in=['scheduled', 'confirmed']
            ).distinct().count(),
            'verified_users_percentage': round((verified_users / total_users * 100), 2) if total_users > 0 else 0
        }
        
        # Build comprehensive dashboard data
        dashboard_data = {
            'stats': {
                'total_users': total_users,
                'total_patients': total_patients,
                'total_psychologists': total_psychologists,
                'total_practice_managers': total_practice_managers,
                'total_admins': total_admins,
                'new_users_this_month': new_users_this_month,
                'new_patients_this_month': new_patients_this_month,
                'new_psychologists_this_month': new_psychologists_this_month,
                'verified_users': verified_users,
                'unverified_users': unverified_users,
                'total_appointments': total_appointments,
                'completed_appointments': completed_appointments,
                'scheduled_appointments': scheduled_appointments,
                'cancelled_appointments': cancelled_appointments,
                'total_progress_notes': total_progress_notes,
                'total_invoices': total_invoices,
                'total_revenue': total_revenue,
                'total_medicare_claims': total_medicare_claims
            },
            'system_health': system_health,
            'recent_users': recent_users
        }
        
        return Response(dashboard_data)


class SystemSettingsView(APIView):
    """System settings management for administrators"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get current system settings
        
        Returns clinic information and system configuration
        """
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Only administrators can access system settings'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.conf import settings
        
        # Get clinic information from settings or use defaults
        settings_data = {
            'clinic': {
                'name': getattr(settings, 'CLINIC_NAME', 'Psychology Clinic'),
                'address': getattr(settings, 'CLINIC_ADDRESS', ''),
                'phone': getattr(settings, 'CLINIC_PHONE', ''),
                'email': getattr(settings, 'CLINIC_EMAIL', ''),
                'website': getattr(settings, 'CLINIC_WEBSITE', ''),
                'abn': getattr(settings, 'CLINIC_ABN', ''),
            },
            'system': {
                'timezone': str(settings.TIME_ZONE),
                'language': settings.LANGUAGE_CODE,
                'gst_rate': float(getattr(settings, 'GST_RATE', 0.10)),
                'medicare_provider_number': getattr(settings, 'MEDICARE_PROVIDER_NUMBER', ''),
                'ahpra_registration_number': getattr(settings, 'AHPRA_REGISTRATION_NUMBER', ''),
            },
            'notifications': {
                'email_enabled': getattr(settings, 'EMAIL_NOTIFICATIONS_ENABLED', True),
                'sms_enabled': getattr(settings, 'SMS_NOTIFICATIONS_ENABLED', False),
                'whatsapp_enabled': getattr(settings, 'WHATSAPP_NOTIFICATIONS_ENABLED', False),
            },
            'billing': {
                'default_payment_method': getattr(settings, 'DEFAULT_PAYMENT_METHOD', 'card'),
                'invoice_terms_days': getattr(settings, 'INVOICE_TERMS_DAYS', 30),
                'auto_generate_invoices': getattr(settings, 'AUTO_GENERATE_INVOICES', True),
            }
        }
        
        return Response(settings_data)
    
    def put(self, request):
        """
        Update system settings
        
        Note: This updates Django settings at runtime.
        For production, consider using a Settings model or environment variables.
        """
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Only administrators can update system settings'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # For now, return a message indicating settings should be updated via environment variables
        # In production, you might want to create a Settings model to store these values
        return Response(
            {
                'message': 'Settings update via API is not fully implemented. '
                          'Please update settings via environment variables or Django settings file.',
                'note': 'For production, consider implementing a Settings model to store these values in the database.'
            },
            status=status.HTTP_200_OK
        )


class SystemAnalyticsView(APIView):
    """System analytics and statistics for administrators"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get comprehensive system analytics
        
        Query Parameters:
        - start_date: Start date for date range (YYYY-MM-DD)
        - end_date: End date for date range (YYYY-MM-DD)
        - period: Predefined period ('today', 'week', 'month', 'year', 'all')
        """
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Only administrators can access system analytics'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        from datetime import timedelta, datetime, time
        from django.db.models import Count, Sum, Avg, Q
        
        now = timezone.now()
        today = now.date()
        
        # Get date range from query parameters
        period = request.query_params.get('period', 'month')
        start_date_param = request.query_params.get('start_date')
        end_date_param = request.query_params.get('end_date')
        
        # Calculate date range
        if start_date_param and end_date_param:
            try:
                start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date()
                start_datetime = timezone.make_aware(datetime.combine(start_date, time.min))
                end_datetime = timezone.make_aware(datetime.combine(end_date, time.max))
            except ValueError:
                return Response(
                    {'error': 'Invalid date format. Use YYYY-MM-DD'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif period == 'today':
            start_datetime = timezone.make_aware(datetime.combine(today, time.min))
            end_datetime = timezone.make_aware(datetime.combine(today, time.max))
        elif period == 'week':
            days_since_monday = today.weekday()
            week_start_date = today - timedelta(days=days_since_monday)
            start_datetime = timezone.make_aware(datetime.combine(week_start_date, time.min))
            end_datetime = now
        elif period == 'month':
            month_start_date = today.replace(day=1)
            start_datetime = timezone.make_aware(datetime.combine(month_start_date, time.min))
            end_datetime = now
        elif period == 'year':
            year_start_date = today.replace(month=1, day=1)
            start_datetime = timezone.make_aware(datetime.combine(year_start_date, time.min))
            end_datetime = now
        else:  # 'all'
            start_datetime = None
            end_datetime = None
        
        # User Analytics
        user_filter = Q()
        if start_datetime:
            user_filter = Q(created_at__gte=start_datetime)
            if end_datetime:
                user_filter &= Q(created_at__lte=end_datetime)
        
        total_users = User.objects.filter(user_filter).count() if start_datetime else User.objects.count()
        users_by_role = User.objects.filter(user_filter if start_datetime else Q()).values('role').annotate(
            count=Count('id')
        )
        
        # User growth over time (daily breakdown)
        user_growth = []
        if start_datetime and end_datetime:
            current_date = start_datetime.date()
            while current_date <= min(end_datetime.date(), today):
                date_users = User.objects.filter(
                    created_at__date=current_date
                ).count()
                user_growth.append({
                    'date': current_date.isoformat(),
                    'count': date_users
                })
                current_date += timedelta(days=1)
        
        # Appointment Analytics
        appointment_filter = Q()
        if start_datetime:
            appointment_filter = Q(appointment_date__gte=start_datetime)
            if end_datetime:
                appointment_filter &= Q(appointment_date__lte=end_datetime)
        
        total_appointments = Appointment.objects.filter(appointment_filter).count() if start_datetime else Appointment.objects.count()
        appointments_by_status = Appointment.objects.filter(
            appointment_filter if start_datetime else Q()
        ).values('status').annotate(count=Count('id'))
        
        appointments_by_type = Appointment.objects.filter(
            appointment_filter if start_datetime else Q()
        ).values('session_type').annotate(count=Count('id'))
        
        # Appointment trends (daily breakdown)
        appointment_trends = []
        if start_datetime and end_datetime:
            current_date = start_datetime.date()
            while current_date <= min(end_datetime.date(), today):
                date_appointments = Appointment.objects.filter(
                    appointment_date__date=current_date
                ).count()
                appointment_trends.append({
                    'date': current_date.isoformat(),
                    'count': date_appointments
                })
                current_date += timedelta(days=1)
        
        # Financial Analytics
        financial_data = {
            'total_revenue': 0.00,
            'total_invoices': 0,
            'paid_invoices': 0,
            'pending_invoices': 0,
            'total_medicare_claims': 0
        }
        
        if BILLING_AVAILABLE:
            invoice_filter = Q()
            if start_datetime:
                invoice_filter = Q(service_date__gte=start_datetime.date())
                if end_datetime:
                    invoice_filter &= Q(service_date__lte=end_datetime.date())
            
            if Invoice:
                invoices = Invoice.objects.filter(invoice_filter if start_datetime else Q())
                financial_data['total_invoices'] = invoices.count()
                financial_data['paid_invoices'] = invoices.filter(status=Invoice.InvoiceStatus.PAID).count()
                financial_data['pending_invoices'] = invoices.filter(
                    status__in=[Invoice.InvoiceStatus.SENT, Invoice.InvoiceStatus.DRAFT]
                ).count()
                
                revenue_sum = invoices.filter(status=Invoice.InvoiceStatus.PAID).aggregate(
                    total=Sum('total_amount')
                )['total']
                financial_data['total_revenue'] = float(revenue_sum) if revenue_sum else 0.00
            
            if MedicareClaim:
                claim_filter = Q()
                if start_datetime:
                    claim_filter = Q(claim_date__gte=start_datetime.date())
                    if end_datetime:
                        claim_filter &= Q(claim_date__lte=end_datetime.date())
                financial_data['total_medicare_claims'] = MedicareClaim.objects.filter(
                    claim_filter if start_datetime else Q()
                ).count()
        
        # Progress Notes Analytics
        notes_filter = Q()
        if start_datetime:
            notes_filter = Q(created_at__gte=start_datetime)
            if end_datetime:
                notes_filter &= Q(created_at__lte=end_datetime)
        
        total_progress_notes = ProgressNote.objects.filter(
            notes_filter if start_datetime else Q()
        ).count()
        
        # Average progress rating
        avg_rating = ProgressNote.objects.filter(
            notes_filter if start_datetime else Q(),
            progress_rating__isnull=False
        ).aggregate(avg=Avg('progress_rating'))['avg']
        
        # Performance Metrics
        active_patients = User.objects.filter(
            role=User.UserRole.PATIENT,
            patient_appointments__status__in=['scheduled', 'confirmed']
        ).distinct().count()
        
        verified_users = User.objects.filter(is_verified=True).count()
        total_users_all = User.objects.count()
        verification_rate = round((verified_users / total_users_all * 100), 2) if total_users_all > 0 else 0
        
        # Build analytics response
        analytics_data = {
            'period': {
                'type': period,
                'start_date': start_datetime.date().isoformat() if start_datetime else None,
                'end_date': end_datetime.date().isoformat() if end_datetime else None
            },
            'users': {
                'total': total_users,
                'by_role': list(users_by_role),
                'growth': user_growth,
                'verified_count': verified_users,
                'verification_rate': verification_rate
            },
            'appointments': {
                'total': total_appointments,
                'by_status': list(appointments_by_status),
                'by_type': list(appointments_by_type),
                'trends': appointment_trends
            },
            'financial': financial_data,
            'progress_notes': {
                'total': total_progress_notes,
                'average_rating': round(float(avg_rating), 2) if avg_rating else None
            },
            'performance': {
                'active_patients': active_patients,
                'total_users': total_users_all,
                'verification_rate': verification_rate
            }
        }
        
        return Response(analytics_data)


class ProfileView(APIView):
    """User profile management"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'data': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PatientManagementView(APIView):
    """
    Enhanced patient management for psychologists and practice managers
    
    Features:
    - Patient list with search and filter
    - Patient progress tracking
    - Communication tools
    - Patient profile management
    - Appointment history per patient
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get patient list with search and filter capabilities
        
        Query parameters:
        - search: Search by name, email, or phone
        - status: Filter by appointment status
        - last_visit: Filter by last visit date
        - sort: Sort by registration date, last appointment
        - page: Pagination
        """
        user = request.user
        
        # Check permissions
        if not (user.is_psychologist() or user.is_practice_manager() or user.is_admin_user()):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get base queryset
        if user.is_psychologist():
            # Psychologists can only see their patients
            patients = User.objects.filter(
                role=User.UserRole.PATIENT,
                progress_notes__psychologist=user
            ).distinct()
        else:
            # Practice managers and admins can see all patients
            patients = User.objects.filter(role=User.UserRole.PATIENT)
        
        # Apply search filter
        search_query = request.query_params.get('search', '')
        if search_query:
            patients = patients.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )
        
        # Apply status filter (based on last appointment)
        status_filter = request.query_params.get('status', '')
        if status_filter:
            if status_filter == 'active':
                # Patients with recent appointments
                from datetime import timedelta
                recent_date = timezone.now().date() - timedelta(days=30)
                patients = patients.filter(
                    patient_appointments__appointment_date__gte=recent_date
                ).distinct()
            elif status_filter == 'inactive':
                # Patients without recent appointments
                from datetime import timedelta
                recent_date = timezone.now().date() - timedelta(days=30)
                patients = patients.exclude(
                    patient_appointments__appointment_date__gte=recent_date
                ).distinct()
        
        # Apply sorting
        sort_by = request.query_params.get('sort', 'created_at')
        if sort_by == 'last_appointment':
            patients = patients.annotate(
                last_appointment_date=models.Max('patient_appointments__appointment_date')
            ).order_by('-last_appointment_date')
        else:
            patients = patients.order_by('-created_at')
        
        # Get patient data with additional information
        patient_data = []
        for patient in patients[:50]:  # Limit to 50 patients for performance
            try:
                patient_profile = patient.patient_profile
            except PatientProfile.DoesNotExist:
                patient_profile = None
            
            # Get appointment statistics
            total_appointments = patient.patient_appointments.count()
            completed_appointments = patient.patient_appointments.filter(status='completed').count()
            upcoming_appointments = patient.patient_appointments.filter(
                appointment_date__gte=timezone.now(),
                status__in=['scheduled', 'confirmed']
            ).count()
            last_appointment = patient.patient_appointments.order_by('-appointment_date').first()
            next_appointment = patient.patient_appointments.filter(
                appointment_date__gte=timezone.now(),
                status__in=['scheduled', 'confirmed']
            ).order_by('appointment_date').first()
            
            # Get progress notes statistics
            progress_notes = patient.progress_notes.all()
            progress_notes_count = progress_notes.count()
            
            # Calculate average progress rating
            progress_ratings = [note.progress_rating for note in progress_notes if note.progress_rating]
            average_progress_rating = sum(progress_ratings) / len(progress_ratings) if progress_ratings else None
            
            # Get last progress rating
            last_note = progress_notes.order_by('-session_date').first()
            last_progress_rating = last_note.progress_rating if last_note and last_note.progress_rating else None
            
            # Determine patient status
            patient_status = 'inactive'
            if total_appointments > 0:
                if last_appointment:
                    days_since_last = (timezone.now().date() - last_appointment.appointment_date.date()).days
                    if days_since_last <= 30:
                        patient_status = 'active'
                    elif completed_appointments > 0 and not upcoming_appointments:
                        patient_status = 'completed'
            
            # Format date of birth
            dob_str = patient.date_of_birth.strftime('%Y-%m-%d') if patient.date_of_birth else None
            
            # Get full name with fallback
            full_name = patient.get_full_name() or f"{patient.first_name or ''} {patient.last_name or ''}".strip() or 'N/A'
            
            patient_data.append({
                'id': patient.id,  # Numeric ID as required
                'name': full_name,
                'fullName': full_name,  # Alias for frontend compatibility
                'firstName': patient.first_name or '',
                'first_name': patient.first_name or '',  # Keep both formats
                'lastName': patient.last_name or '',
                'last_name': patient.last_name or '',  # Keep both formats
                'email': patient.email or '',
                'emailAddress': patient.email or '',  # Alias for frontend compatibility
                'phone': patient.phone_number or '',
                'phone_number': patient.phone_number or '',  # Keep both for compatibility
                'date_of_birth': dob_str,
                'dateOfBirth': dob_str,  # Keep both formats
                'age': patient.age,
                'gender': patient.gender if hasattr(patient, 'gender') else (patient_profile.gender_identity if patient_profile else None),
                'gender_identity': patient_profile.gender_identity if patient_profile else None,
                'intake_completed': patient_profile.intake_completed if patient_profile else False,
                'total_sessions': progress_notes_count,
                'totalSessions': progress_notes_count,  # Keep both formats
                'completed_sessions': completed_appointments,
                'completedSessions': completed_appointments,  # Keep both formats
                'upcoming_sessions': upcoming_appointments,
                'upcomingSessions': upcoming_appointments,  # Keep both formats
                'progress_notes_count': progress_notes_count,
                'last_progress_rating': last_progress_rating,
                'lastProgressRating': last_progress_rating,  # Keep both formats
                'average_progress_rating': round(average_progress_rating, 1) if average_progress_rating else None,
                'averageProgressRating': round(average_progress_rating, 1) if average_progress_rating else None,  # Keep both formats
                'last_appointment': last_appointment.appointment_date.isoformat() if last_appointment else None,
                'lastAppointment': last_appointment.appointment_date.isoformat() if last_appointment else None,  # Keep both formats
                'last_session_date': last_note.session_date.isoformat() if last_note else None,
                'lastSessionDate': last_note.session_date.isoformat() if last_note else None,  # Keep both formats
                'next_appointment': next_appointment.appointment_date.isoformat() if next_appointment else None,
                'nextAppointment': next_appointment.appointment_date.isoformat() if next_appointment else None,  # Keep both formats
                'therapy_goals': patient_profile.therapy_goals if patient_profile else None,
                'therapyFocus': patient_profile.therapy_goals if patient_profile else None,  # Keep both formats
                'presenting_concerns': patient_profile.presenting_concerns if patient_profile else None,
                'status': patient_status,
                'registered_date': patient.created_at.date().isoformat() if patient.created_at else None,
                'registeredDate': patient.created_at.date().isoformat() if patient.created_at else None,  # Keep both formats
                'created_at': patient.created_at.isoformat() if patient.created_at else None,
                'is_verified': patient.is_verified
            })
        
        # Return in format expected by frontend (with both formats for compatibility)
        return Response({
            'count': len(patient_data),
            'total_count': len(patient_data),  # Keep both
            'results': patient_data,  # Frontend expects this
            'patients': patient_data,  # Keep for backward compatibility
            'filters_applied': {
                'search': search_query,
                'status': status_filter,
                'sort': sort_by
            }
        })


class PatientDetailView(APIView):
    """
    Individual patient profile and management
    
    Provides detailed patient information including:
    - Complete patient profile
    - Appointment history
    - Progress notes
    - Communication tools
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, patient_id):
        """
        Get detailed patient information
        
        Returns comprehensive patient data for management
        """
        user = request.user
        
        # Check permissions
        if not (user.is_psychologist() or user.is_practice_manager() or user.is_admin_user()):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            patient = User.objects.get(id=patient_id, role=User.UserRole.PATIENT)
        except User.DoesNotExist:
            return Response(
                {'error': 'Patient not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Additional permission check for psychologists
        if user.is_psychologist():
            # Psychologists can only see their own patients
            if not patient.progress_notes.filter(psychologist=user).exists():
                return Response(
                    {'error': 'Permission denied - not your patient'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Get patient profile
        try:
            patient_profile = patient.patient_profile
        except PatientProfile.DoesNotExist:
            patient_profile = None
        
        # Get appointment history
        appointments = patient.patient_appointments.order_by('-appointment_date')[:10]
        appointment_history = [
            {
                'id': apt.id,
                'appointment_date': apt.appointment_date,
                'psychologist_name': apt.psychologist.get_full_name(),
                'service_name': apt.service.name if apt.service else 'N/A',
                'status': apt.status,
                'duration_minutes': apt.duration_minutes,
                'notes': apt.notes
            }
            for apt in appointments
        ]
        
        # Get progress notes
        progress_notes = patient.progress_notes.order_by('-session_date')[:5]
        recent_progress = [
            {
                'id': note.id,
                'session_date': note.session_date,
                'session_number': note.session_number,
                'psychologist_name': note.psychologist.get_full_name(),
                'progress_rating': note.progress_rating,
                'subjective': note.subjective[:100] + '...' if len(note.subjective) > 100 else note.subjective,
                'created_at': note.created_at
            }
            for note in progress_notes
        ]
        
        # Calculate statistics
        total_appointments = patient.patient_appointments.count()
        completed_appointments = patient.patient_appointments.filter(status='completed').count()
        cancelled_appointments = patient.patient_appointments.filter(status='cancelled').count()
        
        # Get next appointment
        next_appointment = patient.patient_appointments.filter(
            appointment_date__gte=timezone.now(),
            status__in=['scheduled', 'confirmed']
        ).order_by('appointment_date').first()
        
        patient_detail = {
            'patient': {
                'id': patient.id,
                'name': patient.get_full_name(),
                'email': patient.email,
                'phone_number': patient.phone_number,
                'date_of_birth': patient.date_of_birth,
                'age': patient.age,
                'address': {
                    'line_1': patient.address_line_1,
                    'suburb': patient.suburb,
                    'state': patient.state,
                    'postcode': patient.postcode
                },
                'medicare_number': patient.medicare_number,
                'is_verified': patient.is_verified,
                'created_at': patient.created_at
            },
            'profile': {
                'preferred_name': patient_profile.preferred_name if patient_profile else None,
                'gender_identity': patient_profile.gender_identity if patient_profile else None,
                'pronouns': patient_profile.pronouns if patient_profile else None,
                'emergency_contact': {
                    'name': patient_profile.emergency_contact_name if patient_profile else None,
                    'relationship': patient_profile.emergency_contact_relationship if patient_profile else None,
                    'phone': patient_profile.emergency_contact_phone if patient_profile else None
                },
                'referral_info': {
                    'source': patient_profile.referral_source if patient_profile else None,
                    'has_gp_referral': patient_profile.has_gp_referral if patient_profile else False,
                    'gp_name': patient_profile.gp_name if patient_profile else None
                },
                'intake_completed': patient_profile.intake_completed if patient_profile else False,
                'presenting_concerns': patient_profile.presenting_concerns if patient_profile else None,
                'therapy_goals': patient_profile.therapy_goals if patient_profile else None
            } if patient_profile else None,
            'statistics': {
                'total_appointments': total_appointments,
                'completed_appointments': completed_appointments,
                'cancelled_appointments': cancelled_appointments,
                'progress_notes_count': patient.progress_notes.count(),
                'last_appointment_date': patient.patient_appointments.order_by('-appointment_date').first().appointment_date if patient.patient_appointments.exists() else None
            },
            'next_appointment': {
                'id': next_appointment.id,
                'appointment_date': next_appointment.appointment_date,
                'psychologist_name': next_appointment.psychologist.get_full_name(),
                'service_name': next_appointment.service.name if next_appointment.service else None,
                'status': next_appointment.status,
                'duration_minutes': next_appointment.duration_minutes
            } if next_appointment else None,
            'appointment_history': appointment_history,
            'recent_progress': recent_progress
        }
        
        return Response(patient_detail)


class PatientProgressView(APIView):
    """
    Patient progress tracking and management
    
    Provides tools for tracking patient progress including:
    - Progress notes history
    - Progress ratings over time
    - Session summaries
    - Progress analytics
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, patient_id):
        """
        Get patient progress tracking data
        
        Returns comprehensive progress information
        """
        user = request.user
        
        # Check permissions
        if not (user.is_psychologist() or user.is_practice_manager() or user.is_admin_user()):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            patient = User.objects.get(id=patient_id, role=User.UserRole.PATIENT)
        except User.DoesNotExist:
            return Response(
                {'error': 'Patient not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Additional permission check for psychologists
        if user.is_psychologist():
            if not patient.progress_notes.filter(psychologist=user).exists():
                return Response(
                    {'error': 'Permission denied - not your patient'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Get all progress notes for this patient
        progress_notes = patient.progress_notes.order_by('session_date')
        
        # Calculate progress statistics
        total_sessions = progress_notes.count()
        if total_sessions > 0:
            avg_progress_rating = progress_notes.filter(
                progress_rating__isnull=False
            ).aggregate(avg_rating=models.Avg('progress_rating'))['avg_rating'] or 0
            
            latest_rating = progress_notes.filter(
                progress_rating__isnull=False
            ).order_by('-session_date').first()
            latest_rating_value = latest_rating.progress_rating if latest_rating else None
        else:
            avg_progress_rating = 0
            latest_rating_value = None
        
        # Get progress over time
        progress_over_time = [
            {
                'session_number': note.session_number,
                'session_date': note.session_date,
                'progress_rating': note.progress_rating,
                'psychologist_name': note.psychologist.get_full_name(),
                'duration': note.session_duration
            }
            for note in progress_notes.filter(progress_rating__isnull=False)
        ]
        
        # Get recent sessions
        recent_sessions = progress_notes.order_by('-session_date')[:5]
        recent_sessions_data = [
            {
                'id': note.id,
                'session_number': note.session_number,
                'session_date': note.session_date,
                'progress_rating': note.progress_rating,
                'psychologist_name': note.psychologist.get_full_name(),
                'subjective': note.subjective[:200] + '...' if len(note.subjective) > 200 else note.subjective,
                'objective': note.objective[:200] + '...' if len(note.objective) > 200 else note.objective,
                'assessment': note.assessment[:200] + '...' if len(note.assessment) > 200 else note.assessment,
                'plan': note.plan[:200] + '...' if len(note.plan) > 200 else note.plan
            }
            for note in recent_sessions
        ]
        
        progress_data = {
            'patient_name': patient.get_full_name(),
            'total_sessions': total_sessions,
            'average_progress_rating': round(avg_progress_rating, 1) if avg_progress_rating else None,
            'latest_rating': latest_rating_value,
            'progress_over_time': progress_over_time,
            'recent_sessions': recent_sessions_data,
            'progress_summary': {
                'first_session': progress_notes.first().session_date if progress_notes.exists() else None,
                'last_session': progress_notes.last().session_date if progress_notes.exists() else None,
                'total_duration_hours': sum(note.session_duration for note in progress_notes) / 60,
                'sessions_with_ratings': progress_notes.filter(progress_rating__isnull=False).count()
            }
        }
        
        return Response(progress_data)


# Legacy views for compatibility
class RegisterView(APIView):
    """Redirect to patient registration"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        return PatientRegistrationView().post(request)


class ChangePasswordView(APIView):
    """Change user password"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {'error': 'Both old_password and new_password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not request.user.check_password(old_password):
            return Response(
                {'error': 'Current password is incorrect'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.set_password(new_password)
        request.user.save()
        
        return Response({'message': 'Password changed successfully'})