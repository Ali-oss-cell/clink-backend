"""
Users app views - Authentication and user management for Psychology Clinic
Supports intake forms, progress notes, and role-based dashboards
"""

from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q, Count
from django.db import models
from django.utils import timezone

from .models import PatientProfile, ProgressNote
from appointments.models import Appointment
from .serializers import (
    UserSerializer, PatientRegistrationSerializer, PatientProfileSerializer,
    IntakeFormSerializer, ProgressNoteSerializer, ProgressNoteCreateSerializer,
    PsychologistDashboardSerializer, PatientDashboardSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    User management viewset with role-based filtering
    
    Provides different access levels based on user role:
    - Admins/Practice Managers: Can see all users
    - Psychologists: Can see their patients and themselves
    - Patients: Can only see themselves
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter users based on role and permissions
        
        Returns:
            QuerySet: Filtered users based on current user's role
        """
        user = self.request.user
        
        if user.is_admin_user() or user.is_practice_manager():
            # Admin and practice managers can see all users
            return User.objects.all()
        elif user.is_psychologist():
            # Psychologists can see their patients and themselves
            return User.objects.filter(
                Q(role=User.UserRole.PATIENT) | Q(id=user.id)
            )
        else:
            # Patients can only see themselves
            return User.objects.filter(id=user.id)


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
            return ProgressNote.objects.filter(psychologist=user)
        elif user.is_practice_manager() or user.is_admin_user():
            return ProgressNote.objects.all()
        else:
            # Patients can see their own notes
            return ProgressNote.objects.filter(patient=user)
    
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
        
        # Get real appointment data
        today_appointments = Appointment.objects.filter(
            psychologist=request.user,
            appointment_date__date=today
        )
        
        upcoming_appointments = Appointment.objects.filter(
            psychologist=request.user,
            appointment_date__gte=now,
            status__in=['scheduled', 'confirmed']
        ).order_by('appointment_date')[:5]
        
        # Get patient statistics
        total_patients = User.objects.filter(
            role=User.UserRole.PATIENT,
            progress_notes__psychologist=request.user
        ).distinct().count()
        
        # Get recent progress notes
        recent_notes = ProgressNote.objects.filter(
            psychologist=request.user
        ).order_by('-created_at')[:5]
        
        # Calculate statistics
        completed_today = today_appointments.filter(status='completed').count()
        pending_today = today_appointments.filter(status__in=['scheduled', 'confirmed']).count()
        
        # Get comprehensive dashboard data
        dashboard_data = {
            # Today's statistics
            'today_appointments': today_appointments.count(),
            'completed_today': completed_today,
            'pending_today': pending_today,
            
            # Overall statistics
            'total_patients': total_patients,
            'total_appointments': Appointment.objects.filter(psychologist=request.user).count(),
            'completed_appointments': Appointment.objects.filter(
                psychologist=request.user, 
                status='completed'
            ).count(),
            
            # Upcoming sessions with details
            'upcoming_sessions': [
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
            
            # Recent progress notes
            'recent_notes': [
                {
                    'id': note.id,
                    'patient_name': note.patient.get_full_name(),
                    'session_date': note.session_date,
                    'session_number': note.session_number,
                    'progress_rating': note.progress_rating,
                    'created_at': note.created_at
                }
                for note in recent_notes
            ],
            
            # Quick actions data
            'quick_actions': {
                'can_book_appointment': True,
                'can_view_patients': total_patients > 0,
                'can_write_notes': True,
                'pending_notes_count': 0  # Will implement with appointment notes
            }
        }
        
        serializer = PsychologistDashboardSerializer(dashboard_data)
        return Response(serializer.data)


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
            last_appointment = patient.patient_appointments.order_by('-appointment_date').first()
            
            # Get progress notes count
            progress_notes_count = patient.progress_notes.count()
            
            patient_data.append({
                'id': patient.id,
                'name': patient.get_full_name(),
                'email': patient.email,
                'phone_number': patient.phone_number,
                'date_of_birth': patient.date_of_birth,
                'age': patient.age,
                'intake_completed': patient_profile.intake_completed if patient_profile else False,
                'total_appointments': total_appointments,
                'completed_appointments': completed_appointments,
                'progress_notes_count': progress_notes_count,
                'last_appointment': {
                    'date': last_appointment.appointment_date if last_appointment else None,
                    'status': last_appointment.status if last_appointment else None,
                    'psychologist_name': last_appointment.psychologist.get_full_name() if last_appointment else None
                } if last_appointment else None,
                'created_at': patient.created_at,
                'is_verified': patient.is_verified
            })
        
        return Response({
            'patients': patient_data,
            'total_count': len(patient_data),
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