from django.contrib import admin
from .models import Appointment, AvailabilitySlot, TimeSlot, SessionRecording


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'psychologist', 'appointment_date', 'status', 'session_type']
    list_filter = ['status', 'session_type', 'appointment_date']
    search_fields = ['patient__email', 'psychologist__email', 'patient__first_name', 'patient__last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ['psychologist', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available']
    search_fields = ['psychologist__email']


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['psychologist', 'date', 'start_time', 'end_time', 'is_available', 'appointment']
    list_filter = ['is_available', 'date']
    search_fields = ['psychologist__email']


@admin.register(SessionRecording)
class SessionRecordingAdmin(admin.ModelAdmin):
    list_display = ['id', 'appointment', 'recording_sid', 'status', 'duration', 'size', 'created_at', 'completed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['recording_sid', 'appointment__patient__email', 'appointment__psychologist__email']
    readonly_fields = ['recording_sid', 'media_uri', 'media_external_location', 'duration', 'size', 'created_at', 'completed_at']
    
    fieldsets = (
        ('Recording Information', {
            'fields': ('appointment', 'recording_sid', 'status')
        }),
        ('Media Details', {
            'fields': ('media_uri', 'media_external_location', 'duration', 'size', 'participant_identity')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'completed_at')
        }),
    )
