"""
Services app views - Psychology services and psychologist profiles
"""

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Placeholder views - will be implemented with proper models later

class ServiceViewSet(viewsets.ModelViewSet):
    """Psychology services viewset"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response({
            'message': 'Services list - to be implemented'
        })

class PsychologistViewSet(viewsets.ModelViewSet):
    """Psychologist profiles viewset"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response({
            'message': 'Psychologists list - to be implemented'
        })

class SpecializationViewSet(viewsets.ModelViewSet):
    """Specializations viewset"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response({
            'message': 'Specializations list - to be implemented'
        })

class PsychologistAvailabilityView(APIView):
    """Psychologist availability view"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, psychologist_id):
        return Response({
            'message': f'Availability for psychologist {psychologist_id} - to be implemented'
        })