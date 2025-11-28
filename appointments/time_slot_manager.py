"""
Improved Time Slot Management System

Handles time slot generation, availability checking, and conflict prevention
"""

from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta, time as dt_time
from .models import TimeSlot, Appointment
from services.models import PsychologistProfile


class TimeSlotManager:
    """
    Manages time slot generation and availability for psychologists
    """
    
    @staticmethod
    def generate_slots_for_psychologist(psychologist, start_date, end_date, force_regenerate=False):
        """
        Generate or update time slots for a psychologist in a date range
        
        Args:
            psychologist: User instance (psychologist)
            start_date: Start date for slot generation
            end_date: End date for slot generation
            force_regenerate: If True, regenerate even if slots exist
        
        Returns:
            QuerySet of TimeSlot objects
        """
        try:
            profile = psychologist.psychologist_profile
        except PsychologistProfile.DoesNotExist:
            return TimeSlot.objects.none()
        
        # Check if working hours are set
        if not profile.working_days or not profile.start_time or not profile.end_time:
            return TimeSlot.objects.none()
        
        # Check if slots already exist (unless forcing regeneration)
        if not force_regenerate:
            existing_slots = TimeSlot.objects.filter(
                psychologist=psychologist,
                date__gte=start_date,
                date__lte=end_date
            )
            if existing_slots.exists():
                # Update availability based on existing appointments
                TimeSlotManager._update_slot_availability(psychologist, start_date, end_date)
                return existing_slots
        
        # Parse working days
        working_days_list = [day.strip() for day in profile.working_days.split(',')]
        day_name_to_number = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }
        
        working_day_numbers = [
            day_name_to_number.get(day) 
            for day in working_days_list 
            if day in day_name_to_number
        ]
        
        if not working_day_numbers:
            return TimeSlot.objects.none()
        
        # Get existing appointments to avoid conflicts
        existing_appointments = Appointment.objects.filter(
            psychologist=psychologist,
            appointment_date__gte=timezone.datetime.combine(start_date, dt_time.min),
            appointment_date__lte=timezone.datetime.combine(end_date, dt_time.max),
            status__in=['scheduled', 'confirmed']
        ).values_list('appointment_date', 'duration_minutes')
        
        # Create a set of booked times for quick lookup
        booked_times = set()
        for appt_date, duration in existing_appointments:
            appt_start = appt_date
            appt_end = appt_date + timedelta(minutes=duration)
            booked_times.add((appt_start, appt_end))
        
        # Generate slots
        session_duration = profile.session_duration_minutes
        break_duration = profile.break_between_sessions_minutes
        slots_created = 0
        now = timezone.now()
        tomorrow = now.date() + timedelta(days=1)
        
        # Ensure we start from tomorrow (not today)
        if start_date < tomorrow:
            start_date = tomorrow
        
        current_date = start_date
        while current_date <= end_date:
            # Check if this is a working day
            if current_date.weekday() in working_day_numbers:
                # Generate time slots for this day
                current_time = profile.start_time
                end_time = profile.end_time
                
                while current_time < end_time:
                    # Calculate slot times
                    start_datetime = timezone.datetime.combine(
                        current_date, current_time
                    ).replace(tzinfo=timezone.get_current_timezone())
                    
                    end_datetime = start_datetime + timedelta(minutes=session_duration)
                    
                    # Check if end time exceeds working hours
                    if end_datetime.time() > end_time:
                        break
                    
                    # Skip if in the past or today (only show from tomorrow)
                    if start_datetime.date() < tomorrow:
                        # Move to next slot
                        total_minutes = session_duration + break_duration
                        current_time = (
                            datetime.combine(current_date, current_time) + 
                            timedelta(minutes=total_minutes)
                        ).time()
                        continue
                    
                    # Check if this slot conflicts with existing appointment
                    is_conflict = False
                    for booked_start, booked_end in booked_times:
                        # Check for overlap
                        if not (end_datetime <= booked_start or start_datetime >= booked_end):
                            is_conflict = True
                            break
                    
                    # Create or update time slot
                    slot, created = TimeSlot.objects.get_or_create(
                        psychologist=psychologist,
                        start_time=start_datetime,
                        defaults={
                            'date': current_date,
                            'end_time': end_datetime,
                            'is_available': not is_conflict
                        }
                    )
                    
                    # Update if slot exists
                    if not created:
                        slot.date = current_date
                        slot.end_time = end_datetime
                        slot.is_available = not is_conflict
                        slot.save()
                    
                    if created:
                        slots_created += 1
                    
                    # Move to next slot
                    total_minutes = session_duration + break_duration
                    current_time = (
                        datetime.combine(current_date, current_time) + 
                        timedelta(minutes=total_minutes)
                    ).time()
            
            current_date += timedelta(days=1)
        
        # Return all slots in range
        return TimeSlot.objects.filter(
            psychologist=psychologist,
            date__gte=start_date,
            date__lte=end_date
        )
    
    @staticmethod
    def _update_slot_availability(psychologist, start_date, end_date):
        """
        Update availability of existing slots based on current appointments
        """
        # Get all appointments in range
        appointments = Appointment.objects.filter(
            psychologist=psychologist,
            appointment_date__gte=timezone.datetime.combine(start_date, dt_time.min),
            appointment_date__lte=timezone.datetime.combine(end_date, dt_time.max),
            status__in=['scheduled', 'confirmed']
        )
        
        # Get all slots in range
        slots = TimeSlot.objects.filter(
            psychologist=psychologist,
            date__gte=start_date,
            date__lte=end_date
        )
        
        # Mark slots as unavailable if they conflict with appointments
        for slot in slots:
            is_conflict = False
            for appointment in appointments:
                appt_start = appointment.appointment_date
                appt_end = appointment.appointment_date + timedelta(minutes=appointment.duration_minutes)
                
                # Check for overlap
                if not (slot.end_time <= appt_start or slot.start_time >= appt_end):
                    is_conflict = True
                    # Link slot to appointment if not already linked
                    if slot.appointment != appointment:
                        slot.appointment = appointment
                    break
            
            # Update slot availability
            if is_conflict and slot.is_available:
                slot.is_available = False
                slot.save()
            elif not is_conflict and not slot.is_available and slot.appointment is None:
                # Slot is free but marked unavailable - make it available
                slot.is_available = True
                slot.save()
    
    @staticmethod
    def check_slot_availability(psychologist, start_time, end_time):
        """
        Check if a time slot is available for booking
        
        Args:
            psychologist: User instance (psychologist)
            start_time: Start datetime
            end_time: End datetime
        
        Returns:
            tuple: (is_available: bool, conflict_reason: str or None)
        """
        # Check for existing appointments
        conflicting_appointments = Appointment.objects.filter(
            psychologist=psychologist,
            appointment_date__lt=end_time,
            status__in=['scheduled', 'confirmed']
        ).filter(
            Q(appointment_date__gte=start_time) |
            Q(appointment_date__lt=end_time)
        )
        
        # Check for exact overlap
        for appointment in conflicting_appointments:
            appt_start = appointment.appointment_date
            appt_end = appointment.appointment_date + timedelta(minutes=appointment.duration_minutes)
            
            # Check for overlap
            if not (end_time <= appt_start or start_time >= appt_end):
                return False, f"Conflicts with existing appointment at {appt_start}"
        
        # Check if time slot exists and is available
        try:
            slot = TimeSlot.objects.get(
                psychologist=psychologist,
                start_time=start_time
            )
            if not slot.is_available:
                return False, "Time slot is not available"
            if slot.appointment:
                return False, "Time slot is already booked"
        except TimeSlot.DoesNotExist:
            # Slot doesn't exist - check if it's within working hours
            try:
                profile = psychologist.psychologist_profile
                slot_date = start_time.date()
                slot_time = start_time.time()
                
                # Check if it's a working day
                working_days_list = [day.strip() for day in profile.working_days.split(',')]
                day_name_to_number = {
                    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                    'Friday': 4, 'Saturday': 5, 'Sunday': 6
                }
                
                day_name = slot_date.strftime('%A')
                if day_name not in working_days_list:
                    return False, f"{day_name} is not a working day"
                
                # Check if time is within working hours
                if slot_time < profile.start_time or slot_time >= profile.end_time:
                    return False, f"Time {slot_time} is outside working hours ({profile.start_time} - {profile.end_time})"
                
                # Slot doesn't exist but is within working hours - allow it
                return True, None
            except PsychologistProfile.DoesNotExist:
                return False, "Psychologist profile not found"
        
        return True, None
    
    @staticmethod
    def mark_slot_as_booked(slot, appointment):
        """
        Mark a time slot as booked and link it to an appointment
        """
        slot.is_available = False
        slot.appointment = appointment
        slot.save()
    
    @staticmethod
    def mark_slot_as_available(slot):
        """
        Mark a time slot as available (e.g., when appointment is cancelled)
        """
        slot.is_available = True
        slot.appointment = None
        slot.save()
    
    @staticmethod
    def cleanup_past_slots(days_old=7):
        """
        Delete time slots that are older than specified days
        
        Args:
            days_old: Delete slots older than this many days (default: 7)
        """
        cutoff_date = timezone.now() - timedelta(days=days_old)
        deleted_count = TimeSlot.objects.filter(
            date__lt=cutoff_date.date()
        ).delete()[0]
        return deleted_count
    
    @staticmethod
    def generate_slots_for_all_psychologists(days_ahead=90):
        """
        Generate time slots for all active psychologists
        
        Args:
            days_ahead: How many days ahead to generate slots (default: 90)
        
        Returns:
            dict with statistics
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        psychologists = User.objects.filter(
            role=User.UserRole.PSYCHOLOGIST
        ).select_related('psychologist_profile')
        
        stats = {
            'total_psychologists': psychologists.count(),
            'processed': 0,
            'slots_created': 0,
            'errors': []
        }
        
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=days_ahead)
        
        for psychologist in psychologists:
            try:
                slots = TimeSlotManager.generate_slots_for_psychologist(
                    psychologist, start_date, end_date
                )
                stats['processed'] += 1
                stats['slots_created'] += slots.count()
            except Exception as e:
                stats['errors'].append({
                    'psychologist_id': psychologist.id,
                    'error': str(e)
                })
        
        return stats

