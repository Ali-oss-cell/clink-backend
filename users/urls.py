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
from appointments import booking_views

# Router for auth endpoints (includes progress notes)
auth_router = DefaultRouter()
auth_router.register(r'progress-notes', views.ProgressNoteViewSet, basename='progress-note')

# Router for user management endpoints
users_router = DefaultRouter()
users_router.register(r'', views.UserViewSet, basename='user')  # Empty string for /api/users/

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
    
    # Privacy & Consent Compliance (Privacy Act 1988)
    path('privacy-policy/', views.PrivacyPolicyAcceptanceView.as_view(), name='privacy-policy'),
    path('telehealth-consent/', views.TelehealthConsentView.as_view(), name='telehealth-consent'),
    path('preferences/', views.PatientPreferencesView.as_view(), name='patient-preferences'),
    path('third-party-data-sharing/', views.ThirdPartyDataSharingView.as_view(), name='third-party-data-sharing'),
    path('consent/withdraw/', views.ConsentWithdrawalView.as_view(), name='consent-withdraw'),
    path('data-access-request/', views.DataAccessRequestView.as_view(), name='data-access-request'),
    path('data-access-request', views.DataAccessRequestView.as_view(), name='data-access-request-no-slash'),  # Without trailing slash
    
    # Data Deletion Request (APP 13)
    path('data-deletion-request/', views.DataDeletionRequestView.as_view(), name='data-deletion-request'),
    path('data-deletion-request/<int:request_id>/cancel/', views.DataDeletionRequestCancelView.as_view(), name='data-deletion-request-cancel'),
    path('data-deletion-requests/', views.DataDeletionRequestListView.as_view(), name='data-deletion-requests-list'),
    path('data-deletion-requests/<int:request_id>/review/', views.DataDeletionRequestReviewView.as_view(), name='data-deletion-request-review'),
    
    # Intake Forms
    path('intake-form/', views.IntakeFormView.as_view(), name='intake-form'),
    
    # Role-based Dashboards
    path('dashboard/psychologist/', views.PsychologistDashboardView.as_view(), name='psychologist-dashboard'),
    path('psychologist/dashboard/', views.PsychologistDashboardView.as_view(), name='psychologist-dashboard-alt'),  # Alias for frontend
    path('dashboard/patient/', views.PatientDashboardView.as_view(), name='patient-dashboard'),
    path('dashboard/practice-manager/', views.PracticeManagerDashboardView.as_view(), name='practice-manager-dashboard'),
    path('practice-manager/dashboard/', views.PracticeManagerDashboardView.as_view(), name='practice-manager-dashboard-alt'),  # Alias for frontend
    path('dashboard/admin/', views.AdminDashboardView.as_view(), name='admin-dashboard'),
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin-dashboard-alt'),  # Alias for frontend
    
    # Admin System Management
    path('admin/settings/', views.SystemSettingsView.as_view(), name='admin-settings'),
    path('admin/analytics/', views.SystemAnalyticsView.as_view(), name='admin-analytics'),
    path('admin/create-user/', views.AdminCreateUserView.as_view(), name='admin-create-user'),
    
    # Enhanced Patient Management
    path('patients/', views.PatientManagementView.as_view(), name='patient-management'),
    path('patients/<int:patient_id>/', views.PatientDetailView.as_view(), name='patient-detail'),
    path('patients/<int:patient_id>/progress/', views.PatientProgressView.as_view(), name='patient-progress'),
    
    # Appointments endpoints (alias for frontend compatibility)
    path('appointments/available-slots/', booking_views.PsychologistAvailableTimeSlotsView.as_view(), name='auth-available-time-slots'),
    path('appointments/calendar-view/', booking_views.CalendarAvailabilityView.as_view(), name='auth-calendar-availability'),
    path('appointments/book-enhanced/', booking_views.BookAppointmentEnhancedView.as_view(), name='auth-book-appointment-enhanced'),
    path('appointments/booking-summary/', booking_views.AppointmentBookingSummaryView.as_view(), name='auth-booking-summary'),
    
    # ViewSets for auth endpoints (must be last to avoid conflicts)
    path('', include(auth_router.urls)),
]

# Separate URL patterns for /api/users/ endpoint
users_urlpatterns = [
    # User ViewSet at root
    path('', include(users_router.urls)),
]
