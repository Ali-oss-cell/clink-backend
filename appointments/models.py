"""
Appointments models for Psychology Clinic
Handles appointment booking, availability, and time slot management
"""

from django.db import models
from users.models import User
from services.models import Service


class Appointment(models.Model):
    """
    Core appointment model for psychology clinic sessions
    
    This model represents a scheduled appointment between a patient and psychologist.
    Includes status tracking, video room integration, and appointment management.
    """
    
    # Core relationships - patient and psychologist are both User instances
    patient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='patient_appointments',
        help_text="Patient attending the appointment"
    )
    psychologist = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='psychologist_appointments',
        help_text="Psychologist conducting the session"
    )
    service = models.ForeignKey(
        'services.Service', 
        on_delete=models.CASCADE,
        help_text="Type of service being provided (therapy, assessment, etc.)"
    )
    
    # Appointment timing and duration
    appointment_date = models.DateTimeField(
        help_text="Date and time of the appointment"
    )
    duration_minutes = models.PositiveIntegerField(
        default=60,
        help_text="Duration of the appointment in minutes"
    )
    
    # Status tracking for appointment lifecycle
    status = models.CharField(
        max_length=20, 
        choices=[
            ('scheduled', 'Scheduled'),      # Initial booking
            ('confirmed', 'Confirmed'),      # Patient confirmed attendance
            ('completed', 'Completed'),     # Session finished
            ('cancelled', 'Cancelled'),     # Appointment cancelled
            ('no_show', 'No Show')          # Patient didn't attend
        ],
        default='scheduled',
        help_text="Current status of the appointment"
    )
    
    # Session type
    session_type = models.CharField(
        max_length=20,
        choices=[
            ('telehealth', 'Telehealth'),
            ('in_person', 'In-Person')
        ],
        default='telehealth',
        help_text="Type of session (telehealth or in-person)"
    )
    
    # Additional information
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about the appointment"
    )
    video_room_id = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Twilio video room ID for telehealth sessions"
    )
    
    # Timestamps for audit trail
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Prevent double-booking: one psychologist can't have two appointments at same time
        unique_together = ['psychologist', 'appointment_date']
        # Order appointments by date for easy querying
        ordering = ['appointment_date']
    
    def __str__(self):
        return f"{self.patient.get_full_name()} - {self.psychologist.get_full_name()} - {self.appointment_date}"


class AvailabilitySlot(models.Model):
    """
    Psychologist availability for recurring weekly schedules
    
    This model defines when a psychologist is available for appointments
    on a recurring weekly basis. Used to generate available time slots.
    """
    
    psychologist = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        help_text="Psychologist whose availability this represents"
    )
    
    # Day of week (0=Monday, 6=Sunday) - matches Python datetime.weekday()
    day_of_week = models.IntegerField(
        choices=[
            (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
            (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
        ],
        help_text="Day of the week for this availability slot"
    )
    
    # Time range for this availability slot
    start_time = models.TimeField(
        help_text="Start time of availability (e.g., 09:00)"
    )
    end_time = models.TimeField(
        help_text="End time of availability (e.g., 17:00)"
    )
    
    # Availability toggle
    is_available = models.BooleanField(
        default=True,
        help_text="Whether this time slot is currently available for booking"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent duplicate availability slots for same psychologist/day/time
        unique_together = ['psychologist', 'day_of_week', 'start_time']

    def __str__(self):
        day_name = dict(self.day_of_week.field.choices)[self.day_of_week]
        return f"{self.psychologist.get_full_name()} - {day_name} {self.start_time}-{self.end_time}"
    

class TimeSlot(models.Model):
    """
    Specific time slots available for booking on particular dates
    
    This model represents actual bookable time slots generated from
    AvailabilitySlot patterns. Each slot can be booked by one appointment.
    """
    
    psychologist = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        help_text="Psychologist whose time slot this is"
    )
    
    # Specific date for this time slot
    date = models.DateField(
        help_text="Date of this time slot"
    )
    
    # Exact start and end times (datetime for precise scheduling)
    start_time = models.DateTimeField(
        help_text="Exact start time of the slot"
    )
    end_time = models.DateTimeField(
        help_text="Exact end time of the slot"
    )
    
    # Booking status
    is_available = models.BooleanField(
        default=True,
        help_text="Whether this slot is available for booking"
    )
    
    # Link to appointment if booked
    appointment = models.OneToOneField(
        Appointment, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Appointment that has booked this time slot"
    )
    
    class Meta:
        # Prevent duplicate time slots for same psychologist and time
        unique_together = ['psychologist', 'start_time']

    def __str__(self):
        return f"{self.psychologist.get_full_name()} - {self.date} {self.start_time.time()}-{self.end_time.time()}"
            