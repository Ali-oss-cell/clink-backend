"""
Services app URLs - Psychology services and psychologist profiles
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Main router for services (at root /api/services/)
router = DefaultRouter()
router.register(r'', views.ServiceViewSet, basename='service')

# Separate routers for psychologists and specializations
psychologists_router = DefaultRouter()
psychologists_router.register(r'', views.PsychologistProfileViewSet, basename='psychologist')

specializations_router = DefaultRouter()
specializations_router.register(r'', views.SpecializationViewSet, basename='specialization')

urlpatterns = [
    # Psychologists at /api/services/psychologists/
    path('psychologists/', include(psychologists_router.urls)),
    
    # Specializations at /api/services/specializations/
    path('specializations/', include(specializations_router.urls)),
    
    # Psychologist availability endpoint
    path('psychologists/<int:psychologist_id>/availability/', 
         views.PsychologistAvailabilityView.as_view(), 
         name='psychologist-availability'),
    
    # Services at root /api/services/ (must be last)
    path('', include(router.urls)),
]
