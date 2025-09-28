"""
Core app views - Project-wide utilities and health checks
"""

from django.http import JsonResponse
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import sys

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint for monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Psychology Clinic Backend is running',
        'debug': settings.DEBUG,
        'timezone': settings.TIME_ZONE,
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def version_info(request):
    """Version information endpoint"""
    return JsonResponse({
        'application': 'Psychology Clinic Backend',
        'version': '1.0.0',
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'environment': 'development' if settings.DEBUG else 'production',
    })

def custom_404(request, exception):
    """Custom 404 error handler"""
    return JsonResponse({
        'error': 'Not Found',
        'message': 'The requested resource was not found.',
        'status_code': 404
    }, status=404)

def custom_500(request):
    """Custom 500 error handler"""
    return JsonResponse({
        'error': 'Internal Server Error',
        'message': 'An internal server error occurred.',
        'status_code': 500
    }, status=500)