"""
Celery tasks for appointment notifications and automation
Handles scheduled reminders, video room creation, and cleanup
"""

from celery import shared_task
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import Appointment
from .video_service import get_video_service


@shared_task(name='appointments.send_appointment_reminders')
def send_appointment_reminders():
    """
    Send appointment reminders at scheduled intervals
    
    Runs every hour and sends reminders for:
    - 24 hours before appointment
    - 1 hour before appointment
    - 15 minutes before appointment
    
    Returns:
        dict: Statistics on reminders sent
    """
    now = timezone.now()
    
    # Get all upcoming appointments that need reminders
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=now,
        status__in=['scheduled', 'confirmed']
    ).select_related('patient', 'psychologist')
    
    stats = {
        '24h_reminders': 0,
        '1h_reminders': 0,
        '15min_reminders': 0,
        'errors': 0
    }
    
    for appointment in upcoming_appointments:
        time_until = appointment.appointment_date - now
        
        try:
            # 24-hour reminder
            if timedelta(hours=23, minutes=45) <= time_until <= timedelta(hours=24, minutes=15):
                send_24_hour_reminder.delay(appointment.id)
                stats['24h_reminders'] += 1
            
            # 1-hour reminder
            elif timedelta(minutes=45) <= time_until <= timedelta(hours=1, minutes=15):
                send_1_hour_reminder.delay(appointment.id)
                stats['1h_reminders'] += 1
            
            # 15-minute reminder
            elif timedelta(minutes=10) <= time_until <= timedelta(minutes=20):
                send_15_minute_reminder.delay(appointment.id)
                stats['15min_reminders'] += 1
        
        except Exception as e:
            print(f"Error scheduling reminder for appointment {appointment.id}: {str(e)}")
            stats['errors'] += 1
    
    return stats


@shared_task(name='appointments.send_24_hour_reminder')
def send_24_hour_reminder(appointment_id):
    """
    Send 24-hour reminder email with meeting link
    
    Args:
        appointment_id: Appointment ID
    
    Returns:
        dict: Notification result
    """
    try:
        from core.email_service import send_appointment_reminder_24h
        
        appointment = Appointment.objects.select_related(
            'patient', 'psychologist', 'service'
        ).get(id=appointment_id)
        
        # Create video room if telehealth and doesn't exist
        if appointment.session_type == 'telehealth' and not appointment.video_room_id:
            create_video_room_for_appointment.delay(appointment_id)
        
        # Send email reminder
        result = send_appointment_reminder_24h(appointment)
        
        # TODO: Send WhatsApp reminder
        # send_whatsapp_reminder.delay(appointment_id, '24h')
        
        return result
    
    except Appointment.DoesNotExist:
        return {'error': 'Appointment not found'}
    except Exception as e:
        return {'error': str(e)}


@shared_task(name='appointments.send_1_hour_reminder')
def send_1_hour_reminder(appointment_id):
    """
    Send 1-hour reminder via WhatsApp/SMS
    
    Args:
        appointment_id: Appointment ID
    
    Returns:
        dict: Notification result
    """
    try:
        from core.whatsapp_service import send_whatsapp_reminder
        
        appointment = Appointment.objects.select_related(
            'patient', 'psychologist'
        ).get(id=appointment_id)
        
        # Send WhatsApp reminder
        result = send_whatsapp_reminder(appointment, '1h')
        
        return result
    
    except Appointment.DoesNotExist:
        return {'error': 'Appointment not found'}
    except Exception as e:
        # Fallback to SMS if WhatsApp fails
        try:
            from core.sms_service import send_sms_reminder
            return send_sms_reminder(appointment, '1h')
        except:
            return {'error': str(e)}


@shared_task(name='appointments.send_15_minute_reminder')
def send_15_minute_reminder(appointment_id):
    """
    Send 15-minute final reminder with meeting link
    
    Args:
        appointment_id: Appointment ID
    
    Returns:
        dict: Notification result
    """
    try:
        from core.email_service import send_meeting_link_reminder
        
        appointment = Appointment.objects.select_related(
            'patient', 'psychologist'
        ).get(id=appointment_id)
        
        # Send email with meeting link
        result = send_meeting_link_reminder(appointment)
        
        # Also send WhatsApp
        try:
            from core.whatsapp_service import send_whatsapp_reminder
            send_whatsapp_reminder(appointment, '15min')
        except:
            pass  # Don't fail if WhatsApp fails
        
        return result
    
    except Appointment.DoesNotExist:
        return {'error': 'Appointment not found'}
    except Exception as e:
        return {'error': str(e)}


@shared_task(name='appointments.send_confirmation_email')
def send_confirmation_email(appointment_id):
    """
    Send appointment confirmation email immediately after booking
    
    Args:
        appointment_id: Appointment ID
    
    Returns:
        dict: Email send result
    """
    try:
        from core.email_service import send_appointment_confirmation
        
        appointment = Appointment.objects.select_related(
            'patient', 'psychologist', 'service'
        ).get(id=appointment_id)
        
        result = send_appointment_confirmation(appointment)
        
        return result
    
    except Appointment.DoesNotExist:
        return {'error': 'Appointment not found'}
    except Exception as e:
        return {'error': str(e)}


@shared_task(name='appointments.create_video_room_for_appointment')
def create_video_room_for_appointment(appointment_id):
    """
    Create Twilio video room for telehealth appointment
    
    Args:
        appointment_id: Appointment ID
    
    Returns:
        dict: Video room details
    """
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Only create for telehealth appointments
        if appointment.session_type != 'telehealth':
            return {'error': 'Not a telehealth appointment'}
        
        # Don't recreate if room already exists
        if appointment.video_room_id:
            video_service = get_video_service()
            room_status = video_service.get_room_status(appointment.video_room_id)
            if room_status.get('status') != 'not_found':
                return {'message': 'Room already exists', 'room_name': appointment.video_room_id}
        
        # Check if patient has consented to recording
        from core.notification_utils import has_recording_consent
        enable_recording = has_recording_consent(appointment.patient)
        
        # Create video room (with recording only if consent given)
        video_service = get_video_service()
        room_data = video_service.create_room(
            appointment_id=appointment_id,
            appointment_date=appointment.appointment_date,
            enable_recording=enable_recording
        )
        
        # Update appointment
        appointment.video_room_id = room_data['room_name']
        appointment.save()
        
        return {
            'message': 'Video room created',
            'room_name': room_data['room_name'],
            'room_sid': room_data['room_sid']
        }
    
    except Appointment.DoesNotExist:
        return {'error': 'Appointment not found'}
    except Exception as e:
        return {'error': str(e)}


@shared_task(name='appointments.cleanup_old_video_rooms')
def cleanup_old_video_rooms():
    """
    Clean up completed video rooms older than 7 days
    
    Returns:
        dict: Cleanup statistics
    """
    try:
        video_service = get_video_service()
        result = video_service.cleanup_old_rooms(days=7)
        
        return result
    
    except Exception as e:
        return {'error': str(e)}


@shared_task(name='appointments.auto_complete_past_appointments')
def auto_complete_past_appointments():
    """
    Automatically mark past appointments as completed
    
    Runs daily to clean up appointments that are:
    - Past their scheduled time by more than 2 hours
    - Still in 'scheduled' or 'confirmed' status
    
    Returns:
        dict: Statistics on appointments updated
    """
    now = timezone.now()
    cutoff_time = now - timedelta(hours=2)
    
    # Find appointments that should be completed
    past_appointments = Appointment.objects.filter(
        appointment_date__lt=cutoff_time,
        status__in=['scheduled', 'confirmed']
    )
    
    updated_count = 0
    
    for appointment in past_appointments:
        appointment.status = 'completed'
        appointment.save()
        updated_count += 1
        
        # Close video room if it exists
        if appointment.video_room_id and appointment.session_type == 'telehealth':
            try:
                video_service = get_video_service()
                room_status = video_service.get_room_status(appointment.video_room_id)
                if room_status.get('status') == 'in-progress':
                    video_service.complete_room(room_status['room_sid'])
            except:
                pass  # Don't fail if video room cleanup fails
    
    return {
        'appointments_completed': updated_count,
        'cutoff_time': cutoff_time.isoformat()
    }


@shared_task(name='appointments.send_cancellation_email')
def send_cancellation_email(appointment_id, cancelled_by):
    """
    Send cancellation notification email
    
    Args:
        appointment_id: Appointment ID
        cancelled_by: User who cancelled (patient/psychologist)
    
    Returns:
        dict: Email send result
    """
    try:
        from core.email_service import send_appointment_cancelled
        
        appointment = Appointment.objects.select_related(
            'patient', 'psychologist', 'service'
        ).get(id=appointment_id)
        
        result = send_appointment_cancelled(appointment, cancelled_by)
        
        return result
    
    except Appointment.DoesNotExist:
        return {'error': 'Appointment not found'}
    except Exception as e:
        return {'error': str(e)}


@shared_task(name='appointments.send_rescheduled_email')
def send_rescheduled_email(appointment_id, old_date):
    """
    Send rescheduled notification email
    
    Args:
        appointment_id: Appointment ID
        old_date: Previous appointment date/time
    
    Returns:
        dict: Email send result
    """
    try:
        from core.email_service import send_appointment_rescheduled
        
        appointment = Appointment.objects.select_related(
            'patient', 'psychologist', 'service'
        ).get(id=appointment_id)
        
        result = send_appointment_rescheduled(appointment, old_date)
        
        return result
    
    except Appointment.DoesNotExist:
        return {'error': 'Appointment not found'}
    except Exception as e:
        return {'error': str(e)}


@shared_task(name='appointments.check_ahpra_expiry')
def check_ahpra_expiry():
    """
    Check AHPRA registration expiry for all psychologists (AHPRA Compliance)
    
    Runs monthly to:
    - Send warning emails 30 days before expiry
    - Suspend psychologists with expired registrations
    - Cancel future appointments for expired psychologists
    - Notify practice managers
    
    Returns:
        dict: Statistics on checks performed
    """
    from services.models import PsychologistProfile
    from users.models import User
    from audit.utils import log_action
    
    today = timezone.now().date()
    warning_date = today + timedelta(days=30)
    
    stats = {
        'expiring_soon': 0,
        'expired': 0,
        'warnings_sent': 0,
        'suspended': 0,
        'appointments_cancelled': 0,
        'errors': 0
    }
    
    try:
        # Find psychologists with expiring registrations (within 30 days)
        expiring_profiles = PsychologistProfile.objects.filter(
            ahpra_expiry_date__lte=warning_date,
            ahpra_expiry_date__gt=today,
            is_active_practitioner=True
        ).select_related('user')
        
        for profile in expiring_profiles:
            try:
                # Send warning email
                send_ahpra_expiry_warning.delay(profile.id)
                stats['expiring_soon'] += 1
                stats['warnings_sent'] += 1
                
                # Log action
                log_action(
                    user=profile.user,
                    action='ahpra_expiry_warning',
                    obj=profile,
                    metadata={
                        'expiry_date': profile.ahpra_expiry_date.isoformat(),
                        'days_until_expiry': (profile.ahpra_expiry_date - today).days
                    }
                )
            except Exception as e:
                stats['errors'] += 1
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error sending AHPRA expiry warning for {profile.user.email}: {str(e)}')
        
        # Find psychologists with expired registrations
        expired_profiles = PsychologistProfile.objects.filter(
            ahpra_expiry_date__lt=today,
            is_active_practitioner=True
        ).select_related('user')
        
        for profile in expired_profiles:
            try:
                # Suspend psychologist
                profile.is_active_practitioner = False
                profile.save()
                stats['expired'] += 1
                stats['suspended'] += 1
                
                # Cancel future appointments
                cancelled_count = cancel_future_appointments_for_psychologist(profile.user)
                stats['appointments_cancelled'] += cancelled_count
                
                # Send notification
                send_ahpra_expired_notification.delay(profile.id)
                
                # Log action
                log_action(
                    user=profile.user,
                    action='ahpra_expired',
                    obj=profile,
                    metadata={
                        'expiry_date': profile.ahpra_expiry_date.isoformat(),
                        'appointments_cancelled': cancelled_count
                    }
                )
            except Exception as e:
                stats['errors'] += 1
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error suspending psychologist {profile.user.email}: {str(e)}')
        
        return stats
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error in check_ahpra_expiry task: {str(e)}')
        return {'error': str(e), **stats}


@shared_task(name='appointments.check_insurance_expiry')
def check_insurance_expiry():
    """
    Check Professional Indemnity Insurance expiry for all psychologists
    
    Runs monthly to:
    - Send warning emails 30 days before expiry
    - Suspend psychologists with expired insurance
    - Cancel future appointments for psychologists without insurance
    - Notify practice managers
    
    Returns:
        dict: Statistics on checks performed
    """
    from services.models import PsychologistProfile
    from users.models import User
    from audit.utils import log_action
    
    today = timezone.now().date()
    warning_date = today + timedelta(days=30)
    
    stats = {
        'expiring_soon': 0,
        'expired': 0,
        'warnings_sent': 0,
        'suspended': 0,
        'appointments_cancelled': 0,
        'errors': 0
    }
    
    try:
        # Find psychologists with expiring insurance (within 30 days)
        expiring_profiles = PsychologistProfile.objects.filter(
            has_professional_indemnity_insurance=True,
            insurance_expiry_date__lte=warning_date,
            insurance_expiry_date__gt=today,
            is_active_practitioner=True
        ).select_related('user')
        
        for profile in expiring_profiles:
            try:
                # Send warning email
                send_insurance_expiry_warning.delay(profile.id)
                stats['expiring_soon'] += 1
                stats['warnings_sent'] += 1
                
                # Log action
                log_action(
                    user=profile.user,
                    action='insurance_expiry_warning',
                    obj=profile,
                    metadata={
                        'expiry_date': profile.insurance_expiry_date.isoformat() if profile.insurance_expiry_date else None,
                        'days_until_expiry': (profile.insurance_expiry_date - today).days if profile.insurance_expiry_date else None
                    }
                )
            except Exception as e:
                stats['errors'] += 1
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error sending insurance expiry warning for {profile.user.email}: {str(e)}')
        
        # Find psychologists with expired insurance
        expired_profiles = PsychologistProfile.objects.filter(
            has_professional_indemnity_insurance=True,
            insurance_expiry_date__lt=today,
            is_active_practitioner=True
        ).select_related('user')
        
        for profile in expired_profiles:
            try:
                # Suspend psychologist
                profile.is_active_practitioner = False
                profile.has_professional_indemnity_insurance = False
                profile.save()
                stats['expired'] += 1
                stats['suspended'] += 1
                
                # Cancel future appointments
                cancelled_count = cancel_future_appointments_for_psychologist(profile.user)
                stats['appointments_cancelled'] += cancelled_count
                
                # Send notification
                send_insurance_expired_notification.delay(profile.id)
                
                # Log action
                log_action(
                    user=profile.user,
                    action='insurance_expired',
                    obj=profile,
                    metadata={
                        'expiry_date': profile.insurance_expiry_date.isoformat() if profile.insurance_expiry_date else None,
                        'appointments_cancelled': cancelled_count
                    }
                )
            except Exception as e:
                stats['errors'] += 1
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error suspending psychologist {profile.user.email}: {str(e)}')
        
        return stats
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Error in check_insurance_expiry task: {str(e)}')
        return {'error': str(e), **stats}


@shared_task(name='appointments.send_insurance_expiry_warning')
def send_insurance_expiry_warning(psychologist_profile_id):
    """
    Send Professional Indemnity Insurance expiry warning email to psychologist
    
    Args:
        psychologist_profile_id: PsychologistProfile ID
    
    Returns:
        dict: Email send result
    """
    try:
        from services.models import PsychologistProfile
        from core.email_service import send_insurance_expiry_warning_email
        
        profile = PsychologistProfile.objects.select_related('user').get(id=psychologist_profile_id)
        
        if not profile.insurance_expiry_date:
            return {'error': 'Insurance expiry date not set'}
        
        days_until_expiry = (profile.insurance_expiry_date - timezone.now().date()).days
        
        result = send_insurance_expiry_warning_email(profile, days_until_expiry)
        
        return result
    
    except PsychologistProfile.DoesNotExist:
        return {'error': 'Psychologist profile not found'}
    except Exception as e:
        return {'error': str(e)}


@shared_task(name='appointments.send_insurance_expired_notification')
def send_insurance_expired_notification(psychologist_profile_id):
    """
    Send Professional Indemnity Insurance expired notification to psychologist and practice managers
    
    Args:
        psychologist_profile_id: PsychologistProfile ID
    
    Returns:
        dict: Notification result
    """
    try:
        from services.models import PsychologistProfile
        from users.models import User
        from core.email_service import send_insurance_expired_email
        
        profile = PsychologistProfile.objects.select_related('user').get(id=psychologist_profile_id)
        psychologist = profile.user
        
        # Send email to psychologist
        result = send_insurance_expired_email(profile, notify_manager=False)
        
        # Send email to all practice managers
        practice_managers = User.objects.filter(
            role=User.UserRole.PRACTICE_MANAGER,
            is_active=True
        )
        
        for manager in practice_managers:
            try:
                send_insurance_expired_email(profile, notify_manager=True, manager=manager)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f'Error sending insurance expired notification to manager {manager.email}: {str(e)}')
        
        return result
    
    except PsychologistProfile.DoesNotExist:
        return {'error': 'Psychologist profile not found'}
    except Exception as e:
        return {'error': str(e)}


@shared_task(name='appointments.send_ahpra_expiry_warning')
def send_ahpra_expiry_warning(psychologist_profile_id):
    """
    Send AHPRA expiry warning email to psychologist
    
    Args:
        psychologist_profile_id: PsychologistProfile ID
    
    Returns:
        dict: Email send result
    """
    try:
        from services.models import PsychologistProfile
        from core.email_service import send_ahpra_expiry_warning_email
        
        profile = PsychologistProfile.objects.select_related('user').get(id=psychologist_profile_id)
        
        days_until_expiry = (profile.ahpra_expiry_date - timezone.now().date()).days
        
        result = send_ahpra_expiry_warning_email(profile, days_until_expiry)
        
        return result
    
    except PsychologistProfile.DoesNotExist:
        return {'error': 'Psychologist profile not found'}
    except Exception as e:
        return {'error': str(e)}


@shared_task(name='appointments.send_ahpra_expired_notification')
def send_ahpra_expired_notification(psychologist_profile_id):
    """
    Send AHPRA expired notification to psychologist and practice managers
    
    Args:
        psychologist_profile_id: PsychologistProfile ID
    
    Returns:
        dict: Notification result
    """
    try:
        from services.models import PsychologistProfile
        from users.models import User
        from core.email_service import send_ahpra_expired_email
        
        profile = PsychologistProfile.objects.select_related('user').get(id=psychologist_profile_id)
        
        # Send to psychologist
        result = send_ahpra_expired_email(profile)
        
        # Also notify practice managers
        practice_managers = User.objects.filter(role=User.UserRole.PRACTICE_MANAGER)
        for manager in practice_managers:
            try:
                send_ahpra_expired_email(profile, notify_manager=True, manager=manager)
            except:
                pass  # Don't fail if manager notification fails
        
        return result
    
    except PsychologistProfile.DoesNotExist:
        return {'error': 'Psychologist profile not found'}
    except Exception as e:
        return {'error': str(e)}


def cancel_future_appointments_for_psychologist(psychologist):
    """
    Cancel all future appointments for a psychologist (when AHPRA expires)
    
    Args:
        psychologist: User instance (psychologist)
    
    Returns:
        int: Number of appointments cancelled
    """
    from django.utils import timezone
    
    now = timezone.now()
    
    # Find all future appointments
    future_appointments = Appointment.objects.filter(
        psychologist=psychologist,
        appointment_date__gt=now,
        status__in=['scheduled', 'confirmed']
    ).select_related('patient')
    
    cancelled_count = 0
    
    for appointment in future_appointments:
        appointment.status = 'cancelled'
        appointment.cancelled_at = now
        appointment.cancellation_reason = 'AHPRA registration expired. Please contact the clinic for rescheduling.'
        appointment.save()
        cancelled_count += 1
        
        # Send cancellation notification to patient
        try:
            send_cancellation_email.delay(appointment.id, cancelled_by='system')
        except:
            pass  # Don't fail if email fails
    
    return cancelled_count

