"""
Appointments app URLs - Complete appointment booking and scheduling system
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import booking_views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')
router.register(r'availability', views.AvailabilitySlotViewSet, basename='availability')
router.register(r'time-slots', views.TimeSlotViewSet, basename='time-slot')

# Filter router URLs to exclude the API root view (which shows endpoint links)
# The root view is the one that matches empty string and shows all endpoints
router_urls = []
for url in router.urls:
    # Skip the API root view (it's the one that shows endpoint links)
    # We identify it by checking if it's a simple root pattern
    pattern_str = str(url.pattern)
    if pattern_str == '^$' or (pattern_str.startswith('^$') and 'format' not in pattern_str):
        continue  # Skip root view
    router_urls.append(url)

urlpatterns = [
    # Direct route for /api/appointments/ to return list (for frontend) - MUST be first
    path('', views.AppointmentViewSet.as_view({'get': 'list'}), name='appointment-list'),
    
    # Include router URLs (detail at /appointments/{id}/, update, delete, etc.)
    *router_urls,
    
    # Custom appointment actions
    path('book/', views.BookAppointmentView.as_view(), name='book-appointment'),
    path('cancel/<int:appointment_id>/', views.CancelAppointmentView.as_view(), name='cancel-appointment'),
    path('reschedule/<int:appointment_id>/', views.RescheduleAppointmentView.as_view(), name='reschedule-appointment'),
    path('video-room/<int:appointment_id>/', views.CreateVideoRoomView.as_view(), name='create-video-room'),
    path('video-token/<int:appointment_id>/', views.GetVideoAccessTokenView.as_view(), name='get-video-token'),
    path('upcoming/', views.UpcomingAppointmentsView.as_view(), name='upcoming-appointments'),
    path('summary/', views.AppointmentSummaryView.as_view(), name='appointment-summary'),
    
    # Enhanced Schedule Management
    path('schedule/', views.ScheduleManagementView.as_view(), name='schedule-management'),
    path('recurring/', views.RecurringAppointmentView.as_view(), name='recurring-appointments'),
    path('calendar/', views.CalendarIntegrationView.as_view(), name='calendar-integration'),
    
    # Enhanced Booking Flow APIs
    path('available-slots/', booking_views.PsychologistAvailableTimeSlotsView.as_view(), name='available-time-slots'),
    path('calendar-view/', booking_views.CalendarAvailabilityView.as_view(), name='calendar-availability'),
    path('book-enhanced/', booking_views.BookAppointmentEnhancedView.as_view(), name='book-appointment-enhanced'),
    path('booking-summary/', booking_views.AppointmentBookingSummaryView.as_view(), name='booking-summary'),
    
    # Patient Portal API
    path('patient/appointments/', views.PatientAppointmentsListView.as_view(), name='patient-appointments-list'),
    
    # Psychologist Schedule API
    path('psychologist/schedule/', views.PsychologistScheduleView.as_view(), name='psychologist-schedule'),
    path('complete-session/<int:appointment_id>/', views.CompleteSessionView.as_view(), name='complete-session'),
    path('appointment-actions/<int:appointment_id>/', views.AppointmentActionsView.as_view(), name='appointment-actions'),
]