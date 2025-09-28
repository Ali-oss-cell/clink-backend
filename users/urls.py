"""
Users app URLs - Authentication and user management with intake forms
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'progress-notes', views.ProgressNoteViewSet, basename='progress-note')

urlpatterns = [
    # JWT Authentication
    path('login/', views.CustomLoginView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # User registration and management
    path('register/', views.RegisterView.as_view(), name='user-register'),
    path('register/patient/', views.PatientRegistrationView.as_view(), name='patient-register'),
    path('profile/', views.ProfileView.as_view(), name='user-profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    
    # Intake Forms
    path('intake-form/', views.IntakeFormView.as_view(), name='intake-form'),
    
    # Role-based Dashboards
    path('dashboard/psychologist/', views.PsychologistDashboardView.as_view(), name='psychologist-dashboard'),
    path('dashboard/patient/', views.PatientDashboardView.as_view(), name='patient-dashboard'),
    
    # ViewSets
    path('', include(router.urls)),
]
