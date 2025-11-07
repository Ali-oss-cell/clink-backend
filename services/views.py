"""
Services app views - Psychology services and psychologist profiles
Complete implementation with profile management, availability, and specializations
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone

from .models import Service, Specialization, PsychologistProfile
from .serializers import (
    ServiceSerializer, SpecializationSerializer, PsychologistProfileSerializer,
    PsychologistProfileCreateSerializer, PsychologistProfileUpdateSerializer,
    PsychologistProfileImageSerializer, PsychologistAvailabilitySerializer,
    PsychologistListSerializer
)


class ServiceViewSet(viewsets.ModelViewSet):
    """
    Psychology services management
    
    Provides CRUD operations for psychology services including:
    - Individual therapy, couples therapy, assessments
    - Medicare rebate calculations
    - Service pricing and duration
    """
    
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    
    def get_permissions(self):
        """
        Allow public read access, require auth for modifications
        """
        if self.action in ['list', 'retrieve']:
            # Public can view services for booking
            return [permissions.AllowAny()]
        else:
            # Only authenticated users can modify
            return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter services based on user permissions"""
        user = self.request.user
        
        if user.is_authenticated and (user.is_admin_user() or user.is_practice_manager()):
            # Admin and practice managers can see all services
            return Service.objects.all()
        else:
            # Others can only see active services
            return Service.objects.filter(is_active=True)


class SpecializationViewSet(viewsets.ModelViewSet):
    """
    Psychological specializations management
    
    Manages areas of specialization like:
    - Anxiety disorders, depression, ADHD
    - Trauma therapy, couples counseling
    - Child psychology, neuropsychology
    """
    
    queryset = Specialization.objects.filter(is_active=True)
    serializer_class = SpecializationSerializer
    
    def get_permissions(self):
        """
        Allow public read access, require auth for modifications
        """
        if self.action in ['list', 'retrieve']:
            # Public can view specializations
            return [permissions.AllowAny()]
        else:
            # Only authenticated users can modify
            return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter specializations based on user permissions"""
        user = self.request.user
        
        if user.is_authenticated and (user.is_admin_user() or user.is_practice_manager()):
            # Admin and practice managers can see all specializations
            return Specialization.objects.all()
        else:
            # Others can only see active specializations
            return Specialization.objects.filter(is_active=True)


class PsychologistProfileViewSet(viewsets.ModelViewSet):
    """
    Psychologist profile management with comprehensive features
    
    Features:
    - Profile creation and updates
    - Image upload management
    - Specializations and services management
    - Availability settings
    - AHPRA compliance tracking
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter psychologist profiles based on user role"""
        user = self.request.user
        
        if user.is_admin_user() or user.is_practice_manager():
            # Admin and practice managers can see all profiles
            return PsychologistProfile.objects.all()
        elif user.is_psychologist():
            # Psychologists can only see their own profile
            return PsychologistProfile.objects.filter(user=user)
        else:
            # Patients can see active psychologists
            return PsychologistProfile.objects.filter(
                is_active_practitioner=True,
                is_accepting_new_patients=True
            )
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PsychologistProfileCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return PsychologistProfileUpdateSerializer
        elif self.action == 'upload_image':
            return PsychologistProfileImageSerializer
        elif self.action == 'list':
            return PsychologistListSerializer
        return PsychologistProfileSerializer
    
    def perform_create(self, serializer):
        """Create psychologist profile for current user"""
        if not self.request.user.is_psychologist():
            raise permissions.PermissionDenied("Only psychologists can create profiles")
        
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """
        Upload or update psychologist profile image
        
        Handles image upload with validation and storage
        """
        psychologist = self.get_object()
        
        # Check permissions
        if not (request.user == psychologist.user or 
                request.user.is_admin_user() or 
                request.user.is_practice_manager()):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(psychologist, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile image updated successfully',
                'profile_image': psychologist.profile_image.url if psychologist.profile_image else None
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_availability(self, request, pk=None):
        """
        Update psychologist availability settings
        
        Allows updating:
        - Accepting new patients status
        - Maximum patients per day
        - Active practitioner status
        """
        psychologist = self.get_object()
        
        # Check permissions
        if not (request.user == psychologist.user or 
                request.user.is_admin_user() or 
                request.user.is_practice_manager()):
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PsychologistAvailabilitySerializer(psychologist, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Availability settings updated successfully',
                'data': serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """
        Get current user's psychologist profile
        
        Returns the psychologist profile for the authenticated user
        """
        if not request.user.is_psychologist():
            return Response(
                {'error': 'Only psychologists can access this endpoint'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            profile = PsychologistProfile.objects.get(user=request.user)
            serializer = PsychologistProfileSerializer(profile)
            return Response(serializer.data)
        except PsychologistProfile.DoesNotExist:
            return Response(
                {'error': 'Psychologist profile not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get list of psychologists accepting new patients
        
        Returns psychologists who are:
        - Active practitioners
        - Accepting new patients
        - Have current AHPRA registration
        """
        available_psychologists = PsychologistProfile.objects.filter(
            is_active_practitioner=True,
            is_accepting_new_patients=True,
            ahpra_expiry_date__gte=timezone.now().date()
        ).select_related('user').prefetch_related('specializations', 'services_offered')
        
        serializer = PsychologistListSerializer(available_psychologists, many=True)
        return Response(serializer.data)


class PsychologistAvailabilityView(APIView):
    """
    Psychologist availability management
    
    Handles availability checking and management for appointment booking
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, psychologist_id):
        """
        Get availability information for a specific psychologist
        
        Returns:
        - Current availability status
        - Maximum patients per day
        - AHPRA registration status
        - Specializations and services
        """
        try:
            psychologist = PsychologistProfile.objects.get(
                id=psychologist_id,
                is_active_practitioner=True
            )
        except PsychologistProfile.DoesNotExist:
            return Response(
                {'error': 'Psychologist not found or not active'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if psychologist is accepting new patients
        if not psychologist.is_accepting_new_patients:
            return Response({
                'available': False,
                'reason': 'Not currently accepting new patients',
                'psychologist_name': psychologist.display_name
            })
        
        # Check AHPRA registration
        if not psychologist.is_ahpra_current:
            return Response({
                'available': False,
                'reason': 'AHPRA registration expired',
                'psychologist_name': psychologist.display_name
            })
        
        return Response({
            'available': True,
            'psychologist_name': psychologist.display_name,
            'max_patients_per_day': psychologist.max_patients_per_day,
            'consultation_fee': psychologist.consultation_fee,
            'specializations': [
                {'id': spec.id, 'name': spec.name} 
                for spec in psychologist.specializations.all()
            ],
            'services_offered': [
                {'id': service.id, 'name': service.name, 'fee': service.standard_fee}
                for service in psychologist.services_offered.all()
            ]
        })