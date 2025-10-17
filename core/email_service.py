"""
Email notification service for Psychology Clinic
Handles all email communications including appointment reminders and confirmations
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def send_appointment_confirmation(appointment):
    """
    Send appointment confirmation email immediately after booking
    
    Args:
        appointment: Appointment instance
    
    Returns:
        dict: Email send result
    """
    patient = appointment.patient
    psychologist = appointment.psychologist
    
    # Format appointment details
    appointment_datetime = appointment.appointment_date.strftime('%A, %B %d, %Y at %I:%M %p')
    
    subject = f"Appointment Confirmed - {appointment_datetime}"
    
    # Plain text version
    message = f"""
Hello {patient.first_name},

Your appointment has been confirmed!

Appointment Details:
-------------------
Date & Time: {appointment_datetime}
Psychologist: {psychologist.get_full_name()}
Session Type: {appointment.get_session_type_display()}
Duration: {appointment.duration_minutes} minutes

"""
    
    if appointment.session_type == 'in_person':
        # Add location for in-person appointments
        if hasattr(psychologist, 'psychologist_profile'):
            location = psychologist.psychologist_profile.practice_address or "Clinic location will be provided"
        else:
            location = "Clinic location will be provided"
        message += f"Location: {location}\n\n"
    else:
        message += "A video meeting link will be sent 24 hours before your appointment.\n\n"
    
    message += """
What to Expect:
- You will receive a reminder 24 hours before your appointment
- Please arrive/join 5 minutes early
- If you need to cancel or reschedule, please do so at least 24 hours in advance

If you have any questions, please contact us.

Thank you,
Psychology Clinic Team
"""
    
    try:
        # Send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient.email],
            fail_silently=False,
        )
        
        return {
            'success': True,
            'recipient': patient.email,
            'subject': subject
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def send_appointment_reminder_24h(appointment):
    """
    Send 24-hour reminder with meeting link (for telehealth)
    Sends to BOTH patient and psychologist
    
    Args:
        appointment: Appointment instance
    
    Returns:
        dict: Email send result
    """
    patient = appointment.patient
    psychologist = appointment.psychologist
    
    appointment_datetime = appointment.appointment_date.strftime('%A, %B %d, %Y at %I:%M %p')
    
    # Send to PATIENT
    subject_patient = f"Reminder: Appointment Tomorrow - {appointment.appointment_date.strftime('%I:%M %p')}"
    
    message_patient = f"""
Hello {patient.first_name},

This is a reminder about your upcoming appointment tomorrow.

Appointment Details:
-------------------
Date & Time: {appointment_datetime}
Psychologist: {psychologist.get_full_name()}
Session Type: {appointment.get_session_type_display()}
Duration: {appointment.duration_minutes} minutes

"""
    
    if appointment.session_type == 'telehealth':
        # Include meeting link for telehealth
        if appointment.video_room_id:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            meeting_url = f"{frontend_url}/video-session/{appointment.video_room_id}"
            message += f"""
Video Meeting Link:
{meeting_url}

Important: Please test your camera and microphone before the appointment.
Join 5 minutes early to ensure everything is working properly.

"""
        else:
            message += "Video meeting link will be available soon.\n\n"
    else:
        # Location for in-person
        if hasattr(psychologist, 'psychologist_profile'):
            location = psychologist.psychologist_profile.practice_address or "Clinic"
        else:
            location = "Clinic"
        message += f"Location: {location}\n\n"
    
    message += """
Preparation Tips:
- Have your notes or questions ready
- Ensure you're in a quiet, private space (for telehealth)
- Arrive/join 5 minutes early

If you need to cancel or reschedule, please do so as soon as possible.

See you tomorrow!

Psychology Clinic Team
"""
    
    # Send email to patient
    try:
        send_mail(
            subject=subject_patient,
            message=message_patient,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient.email],
            fail_silently=False,
        )
        
        patient_sent = True
    except Exception as e:
        patient_sent = False
        patient_error = str(e)
    
    # Send to PSYCHOLOGIST
    subject_psychologist = f"Reminder: Session Tomorrow - {appointment.appointment_date.strftime('%I:%M %p')} with {patient.get_full_name()}"
    
    message_psychologist = f"""
Hello Dr. {psychologist.last_name},

This is a reminder about your upcoming session tomorrow.

Session Details:
-------------------
Date & Time: {appointment_datetime}
Patient: {patient.get_full_name()}
Session Type: {appointment.get_session_type_display()}
Duration: {appointment.duration_minutes} minutes

"""
    
    if appointment.session_type == 'telehealth':
        if appointment.video_room_id:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            meeting_url = f"{frontend_url}/video-session/{appointment.video_room_id}"
            message_psychologist += f"""
Video Meeting Link:
{meeting_url}

The patient will join using the same link.
Please join 5 minutes early to prepare.

"""
        else:
            message_psychologist += "Video meeting link will be available soon.\n\n"
    else:
        message_psychologist += f"Session will be held at your practice location.\n\n"
    
    message_psychologist += """
Patient Notes: """ + (appointment.notes if appointment.notes else "None") + """

Have a great session!

Psychology Clinic Team
"""
    
    # Send email to psychologist
    try:
        send_mail(
            subject=subject_psychologist,
            message=message_psychologist,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[psychologist.email],
            fail_silently=False,
        )
        
        psychologist_sent = True
    except Exception as e:
        psychologist_sent = False
        psychologist_error = str(e)
    
    # Return combined result
    return {
        'success': patient_sent or psychologist_sent,
        'patient_sent': patient_sent,
        'psychologist_sent': psychologist_sent,
        'patient_email': patient.email if patient_sent else None,
        'psychologist_email': psychologist.email if psychologist_sent else None,
        'errors': {
            'patient': patient_error if not patient_sent else None,
            'psychologist': psychologist_error if not psychologist_sent else None
        },
        'type': '24h_reminder'
    }


def send_meeting_link_reminder(appointment):
    """
    Send final reminder 15 minutes before with meeting link
    
    Args:
        appointment: Appointment instance
    
    Returns:
        dict: Email send result
    """
    patient = appointment.patient
    
    subject = f"Starting Soon: Your Appointment in 15 Minutes"
    
    if appointment.session_type == 'telehealth' and appointment.video_room_id:
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        meeting_url = f"{frontend_url}/video-session/{appointment.video_room_id}"
        
        message = f"""
Hello {patient.first_name},

Your appointment is starting in 15 minutes!

Join your video session here:
{meeting_url}

Tips:
✓ Test your camera and microphone
✓ Find a quiet, private space
✓ Have your notes ready

See you soon!

Psychology Clinic Team
"""
    else:
        message = f"""
Hello {patient.first_name},

Your appointment is starting in 15 minutes!

Please make your way to the clinic now.

See you soon!

Psychology Clinic Team
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient.email],
            fail_silently=False,
        )
        
        return {
            'success': True,
            'recipient': patient.email,
            'type': '15min_reminder'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def send_appointment_cancelled(appointment, cancelled_by):
    """
    Send cancellation notification
    
    Args:
        appointment: Appointment instance
        cancelled_by: Who cancelled ('patient' or 'psychologist')
    
    Returns:
        dict: Email send result
    """
    patient = appointment.patient
    psychologist = appointment.psychologist
    
    appointment_datetime = appointment.appointment_date.strftime('%A, %B %d, %Y at %I:%M %p')
    
    subject = f"Appointment Cancelled - {appointment_datetime}"
    
    message = f"""
Hello {patient.first_name},

Your appointment has been cancelled.

Cancelled Appointment:
--------------------
Date & Time: {appointment_datetime}
Psychologist: {psychologist.get_full_name()}
Session Type: {appointment.get_session_type_display()}

"""
    
    if cancelled_by == 'psychologist':
        message += """
This appointment was cancelled by your psychologist.
We apologize for any inconvenience.

"""
    
    message += """
Would you like to book a new appointment?
Please visit our booking page or contact us directly.

Thank you,
Psychology Clinic Team
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient.email],
            fail_silently=False,
        )
        
        return {
            'success': True,
            'recipient': patient.email,
            'type': 'cancellation'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def send_appointment_rescheduled(appointment, old_date):
    """
    Send rescheduled notification
    
    Args:
        appointment: Appointment instance (with new date)
        old_date: Previous appointment datetime
    
    Returns:
        dict: Email send result
    """
    patient = appointment.patient
    psychologist = appointment.psychologist
    
    old_datetime = old_date.strftime('%A, %B %d, %Y at %I:%M %p')
    new_datetime = appointment.appointment_date.strftime('%A, %B %d, %Y at %I:%M %p')
    
    subject = f"Appointment Rescheduled - New Time: {new_datetime}"
    
    message = f"""
Hello {patient.first_name},

Your appointment has been rescheduled.

Previous Time: {old_datetime}
New Time: {new_datetime}

Appointment Details:
-------------------
Psychologist: {psychologist.get_full_name()}
Session Type: {appointment.get_session_type_display()}
Duration: {appointment.duration_minutes} minutes

"""
    
    if appointment.session_type == 'telehealth':
        message += "A video meeting link will be sent 24 hours before your new appointment time.\n\n"
    
    message += """
You will receive reminders for your new appointment time.

If you have any questions, please contact us.

Thank you,
Psychology Clinic Team
"""
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient.email],
            fail_silently=False,
        )
        
        return {
            'success': True,
            'recipient': patient.email,
            'type': 'rescheduled'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def test_email_configuration():
    """
    Test email configuration by sending a test email
    
    Returns:
        dict: Test result
    """
    test_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com')
    
    try:
        send_mail(
            subject='Psychology Clinic - Email Configuration Test',
            message='If you receive this email, your email configuration is working correctly!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        return {
            'success': True,
            'message': 'Test email sent successfully',
            'from_email': settings.DEFAULT_FROM_EMAIL
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'email_backend': settings.EMAIL_BACKEND
        }

