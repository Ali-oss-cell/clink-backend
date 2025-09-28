"""
Appointments app URLs - Booking system and scheduling
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.AppointmentViewSet, basename='appointment')
router.register(r'slots', views.AvailabilitySlotViewSet, basename='availability-slot')

urlpatterns = [
    path('', include(router.urls)),
    path('book/', views.BookAppointmentView.as_view(), name='book-appointment'),
    path('<int:appointment_id>/cancel/', views.CancelAppointmentView.as_view(), name='cancel-appointment'),
    path('<int:appointment_id>/reschedule/', views.RescheduleAppointmentView.as_view(), name='reschedule-appointment'),
    path('<int:appointment_id>/video-room/', views.CreateVideoRoomView.as_view(), name='create-video-room'),
    path('upcoming/', views.UpcomingAppointmentsView.as_view(), name='upcoming-appointments'),
]
