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
from django.utils import timezone

from .models import PatientProfile, ProgressNote
from .serializers import (
    UserSerializer, PatientRegistrationSerializer, PatientProfileSerializer,
    IntakeFormSerializer, ProgressNoteSerializer, ProgressNoteCreateSerializer,
    PsychologistDashboardSerializer, PatientDashboardSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """User management viewset with role-based filtering"""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter users based on role and permissions"""
        user = self.request.user
        
        if user.is_admin_user() or user.is_practice_manager():
            return User.objects.all()
        elif user.is_psychologist():
            # Psychologists can see their patients
            return User.objects.filter(
                Q(role=User.UserRole.PATIENT) | Q(id=user.id)
            )
        else:
            # Patients can only see themselves
            return User.objects.filter(id=user.id)


class CustomLoginView(APIView):
    """Custom login view that accepts email instead of username"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check password
        if not user.check_password(password):
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens
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
        if not request.user.is_psychologist():
            return Response(
                {'error': 'Only psychologists can access this dashboard'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        today = timezone.now().date()
        
        # Get dashboard data
        dashboard_data = {
            'today_appointments': 0,  # Will implement with appointments model
            'total_patients': User.objects.filter(
                role=User.UserRole.PATIENT,
                progress_notes__psychologist=request.user
            ).distinct().count(),
            'pending_notes': 0,  # Will implement with appointments
            'upcoming_sessions': [],  # Will implement with appointments
            'recent_notes': ProgressNote.objects.filter(
                psychologist=request.user
            )[:5]
        }
        
        serializer = PsychologistDashboardSerializer(dashboard_data)
        return Response(serializer.data)


class PatientDashboardView(APIView):
    """Dashboard data for patients"""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
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
        
        dashboard_data = {
            'next_appointment': {},  # Will implement with appointments
            'total_sessions': request.user.progress_notes.count(),
            'intake_completed': patient_profile.intake_completed,
            'outstanding_invoices': 0,  # Will implement with billing
            'recent_progress': []  # Will implement with progress tracking
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