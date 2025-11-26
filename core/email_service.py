"""
Email notification service for Psychology Clinic
Handles all email communications including appointment reminders and confirmations
Uses SendGrid (via Twilio) for email delivery
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

# SendGrid imports (optional - falls back to Django SMTP if not configured)
try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

# Requests for direct API calls (fallback)
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


def send_email_via_sendgrid(to_email, subject, message, html_message=None):
    """
    Send email using SendGrid API (via Twilio)
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        message: Plain text message
        html_message: Optional HTML message
    
    Returns:
        dict: Send result
    """
    sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', None)
    
    # If SendGrid not configured, fall back to Django SMTP
    if not sendgrid_api_key or not SENDGRID_AVAILABLE:
        return send_email_via_django(to_email, subject, message, html_message)
    
    try:
        sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
        
        from_email = Email(
            getattr(settings, 'SENDGRID_FROM_EMAIL', 'noreply@yourclinic.com.au'),
            getattr(settings, 'SENDGRID_FROM_NAME', 'Psychology Clinic')
        )
        to_email_obj = To(to_email)
        
        # Create email content
        if html_message:
            content = Content("text/html", html_message)
        else:
            content = Content("text/plain", message)
        
        mail = Mail(from_email, to_email_obj, subject, content)
        
        # Send email with timeout handling
        import socket
        original_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(30)  # 30 second timeout
        try:
            response = sg.send(mail)
        finally:
            socket.setdefaulttimeout(original_timeout)  # Restore original timeout
        
        return {
            'success': True,
            'status_code': response.status_code,
            'recipient': to_email,
            'method': 'sendgrid'
        }
    
    except (socket.timeout, Exception) as e:
        # If SendGrid library times out, try direct API call with requests
        try:
            return send_email_via_sendgrid_direct(to_email, subject, message, html_message)
        except Exception:
            # Final fallback to Django SMTP
            return send_email_via_django(to_email, subject, message, html_message)


def send_email_via_sendgrid_direct(to_email, subject, message, html_message=None):
    """
    Send email using SendGrid API directly via requests (fallback if library times out)
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        message: Plain text message
        html_message: Optional HTML message
    
    Returns:
        dict: Send result
    """
    sendgrid_api_key = getattr(settings, 'SENDGRID_API_KEY', None)
    from_email = getattr(settings, 'SENDGRID_FROM_EMAIL', 'noreply@yourclinic.com.au')
    from_name = getattr(settings, 'SENDGRID_FROM_NAME', 'Psychology Clinic')
    
    if not sendgrid_api_key:
        raise ValueError("SENDGRID_API_KEY not configured")
    
    if not REQUESTS_AVAILABLE:
        raise ImportError("requests library not available")
    
    try:
        
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {sendgrid_api_key}",
            "Content-Type": "application/json"
        }
        
        # Build email data
        email_data = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": from_email, "name": from_name},
            "subject": subject,
            "content": []
        }
        
        # Add content
        if html_message:
            email_data["content"].append({
                "type": "text/html",
                "value": html_message
            })
        email_data["content"].append({
            "type": "text/plain",
            "value": message
        })
        
        # Send via requests with longer timeout
        response = requests.post(url, headers=headers, json=email_data, timeout=60)
        
        if response.status_code in [200, 202]:
            return {
                'success': True,
                'status_code': response.status_code,
                'recipient': to_email,
                'method': 'sendgrid_direct_api'
            }
        else:
            raise Exception(f"SendGrid API error: {response.status_code} - {response.text}")
            
    except requests.exceptions.Timeout:
        raise Exception("SendGrid API timeout (60 seconds)")
    except Exception as e:
        raise Exception(f"SendGrid direct API error: {str(e)}")


def send_email_via_django(to_email, subject, message, html_message=None):
    """
    Send email using Django's SMTP backend (fallback)
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        message: Plain text message
        html_message: Optional HTML message
    
    Returns:
        dict: Send result
    """
    try:
        if html_message:
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
        else:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
        
        return {
            'success': True,
            'recipient': to_email,
            'method': 'django_smtp'
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'method': 'django_smtp'
        }


def send_appointment_confirmation(appointment):
    """
    Send appointment confirmation email immediately after booking
    
    Args:
        appointment: Appointment instance
    
    Returns:
        dict: Email send result
    """
    from core.notification_utils import should_send_email_notification
    
    patient = appointment.patient
    psychologist = appointment.psychologist
    
    # Check if patient wants email notifications
    if not should_send_email_notification(patient):
        return {
            'success': False,
            'skipped': True,
            'reason': 'Email notifications disabled by patient',
            'patient_id': patient.id
        }
    
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
    
    # Send email via SendGrid (or Django SMTP fallback)
    result = send_email_via_sendgrid(
        to_email=patient.email,
        subject=subject,
        message=message
    )
    
    result['subject'] = subject
    return result


def send_appointment_reminder_24h(appointment):
    """
    Send 24-hour reminder with meeting link (for telehealth)
    Sends to BOTH patient and psychologist
    
    Args:
        appointment: Appointment instance
    
    Returns:
        dict: Email send result
    """
    from core.notification_utils import should_send_email_notification, should_send_appointment_reminder
    
    patient = appointment.patient
    psychologist = appointment.psychologist
    
    # Check if patient wants reminders and email notifications
    if not should_send_appointment_reminder(patient):
        return {
            'success': False,
            'skipped': True,
            'reason': 'Appointment reminders disabled by patient',
            'patient_id': patient.id
        }
    
    if not should_send_email_notification(patient):
        return {
            'success': False,
            'skipped': True,
            'reason': 'Email notifications disabled by patient',
            'patient_id': patient.id
        }
    
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
        send_email_via_sendgrid(
            to_email=patient.email,
            subject=subject_patient,
            message=message_patient
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
        send_email_via_sendgrid(
            to_email=psychologist.email,
            subject=subject_psychologist,
            message=message_psychologist
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
    from core.notification_utils import should_send_email_notification, should_send_appointment_reminder
    
    patient = appointment.patient
    
    # Check if patient wants reminders and email notifications
    if not should_send_appointment_reminder(patient):
        return {
            'success': False,
            'skipped': True,
            'reason': 'Appointment reminders disabled by patient',
            'patient_id': patient.id
        }
    
    if not should_send_email_notification(patient):
        return {
            'success': False,
            'skipped': True,
            'reason': 'Email notifications disabled by patient',
            'patient_id': patient.id
        }
    
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
        result = send_email_via_sendgrid(
            to_email=patient.email,
            subject=subject,
            message=message
        )
        
        result['type'] = '15min_reminder'
        return result
    
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
    from core.notification_utils import should_send_email_notification
    
    patient = appointment.patient
    psychologist = appointment.psychologist
    
    # Check if patient wants email notifications
    if not should_send_email_notification(patient):
        return {
            'success': False,
            'skipped': True,
            'reason': 'Email notifications disabled by patient',
            'patient_id': patient.id
        }
    
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
        result = send_email_via_sendgrid(
            to_email=patient.email,
            subject=subject,
            message=message
        )
        
        result['type'] = 'cancellation'
        return result
    
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
    from core.notification_utils import should_send_email_notification
    
    patient = appointment.patient
    psychologist = appointment.psychologist
    
    # Check if patient wants email notifications
    if not should_send_email_notification(patient):
        return {
            'success': False,
            'skipped': True,
            'reason': 'Email notifications disabled by patient',
            'patient_id': patient.id
        }
    
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
        result = send_email_via_sendgrid(
            to_email=patient.email,
            subject=subject,
            message=message
        )
        
        result['type'] = 'rescheduled'
        return result
    
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
        result = send_email_via_sendgrid(
            to_email=test_email,
            subject='Psychology Clinic - Email Configuration Test',
            message='If you receive this email, your email configuration is working correctly!'
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


def send_ahpra_expiry_warning_email(profile, days_until_expiry):
    """
    Send AHPRA expiry warning email to psychologist
    
    Args:
        profile: PsychologistProfile instance
        days_until_expiry: Number of days until AHPRA expires
    
    Returns:
        dict: Email send result
    """
    psychologist = profile.user
    
    subject = f"⚠️ AHPRA Registration Expiring Soon - {days_until_expiry} Days Remaining"
    
    expiry_date = profile.ahpra_expiry_date.strftime('%B %d, %Y')
    
    message = f"""
Dear {psychologist.get_full_name()},

This is an important reminder that your AHPRA registration is expiring soon.

Registration Details:
---------------------
AHPRA Number: {profile.ahpra_registration_number}
Expiry Date: {expiry_date}
Days Remaining: {days_until_expiry}

Action Required:
----------------
Please renew your AHPRA registration before the expiry date to continue practicing.

If your registration expires:
- You will be automatically suspended from the system
- All future appointments will be cancelled
- You will not be able to see patients until registration is renewed

Once you have renewed your registration, please update your profile in the system with:
- New AHPRA expiry date
- Updated registration number (if changed)

If you have already renewed your registration, please update your profile immediately.

If you have any questions, please contact the practice manager.

Thank you,
Psychology Clinic Team
"""
    
    try:
        result = send_email_via_sendgrid(
            to_email=psychologist.email,
            subject=subject,
            message=message
        )
        
        result['subject'] = subject
        result['days_until_expiry'] = days_until_expiry
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def send_ahpra_expired_email(profile, notify_manager=False, manager=None):
    """
    Send AHPRA expired notification email
    
    Args:
        profile: PsychologistProfile instance
        notify_manager: If True, send to practice manager instead of psychologist
        manager: Practice manager User instance (if notify_manager=True)
    
    Returns:
        dict: Email send result
    """
    psychologist = profile.user
    expiry_date = profile.ahpra_expiry_date.strftime('%B %d, %Y')
    
    if notify_manager and manager:
        # Email to practice manager
        subject = f"🚨 AHPRA Registration Expired - {psychologist.get_full_name()}"
        recipient = manager.email
        
        message = f"""
Dear {manager.get_full_name()},

This is to notify you that a psychologist's AHPRA registration has expired.

Psychologist Details:
---------------------
Name: {psychologist.get_full_name()}
Email: {psychologist.email}
AHPRA Number: {profile.ahpra_registration_number}
Expiry Date: {expiry_date}

Actions Taken:
--------------
- Psychologist has been automatically suspended
- All future appointments have been cancelled
- Patients have been notified of cancellations

Action Required:
----------------
Please contact the psychologist to:
1. Verify if registration has been renewed
2. Update the profile with new expiry date if renewed
3. Reactivate the psychologist account once registration is confirmed

If registration has not been renewed, the psychologist cannot practice until it is renewed.

Thank you,
Psychology Clinic System
"""
    else:
        # Email to psychologist
        subject = "🚨 AHPRA Registration Expired - Account Suspended"
        recipient = psychologist.email
        
        message = f"""
Dear {psychologist.get_full_name()},

Your AHPRA registration has expired and your account has been suspended.

Registration Details:
---------------------
AHPRA Number: {profile.ahpra_registration_number}
Expiry Date: {expiry_date}

Actions Taken:
--------------
- Your account has been automatically suspended
- All future appointments have been cancelled
- Patients have been notified of cancellations

Action Required:
----------------
To reactivate your account:
1. Renew your AHPRA registration
2. Contact the practice manager
3. Update your profile with the new AHPRA expiry date
4. Your account will be reactivated once registration is confirmed

You cannot see patients until your AHPRA registration is renewed and your account is reactivated.

If you have already renewed your registration, please contact the practice manager immediately to update your profile.

If you have any questions, please contact the practice manager.

Thank you,
Psychology Clinic Team
"""
    
    try:
        result = send_email_via_sendgrid(
            to_email=recipient,
            subject=subject,
            message=message
        )
        
        result['subject'] = subject
        result['notify_manager'] = notify_manager
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def send_insurance_expiry_warning_email(profile, days_until_expiry):
    """
    Send Professional Indemnity Insurance expiry warning email to psychologist
    
    Args:
        profile: PsychologistProfile instance
        days_until_expiry: Number of days until insurance expires
    
    Returns:
        dict: Email send result
    """
    psychologist = profile.user
    
    subject = f"⚠️ Professional Indemnity Insurance Expiring Soon - {days_until_expiry} Days Remaining"
    
    expiry_date = profile.insurance_expiry_date.strftime('%B %d, %Y') if profile.insurance_expiry_date else 'N/A'
    coverage_amount = f"${profile.insurance_coverage_amount:,.2f} AUD" if profile.insurance_coverage_amount else 'N/A'
    
    message = f"""
Dear {psychologist.get_full_name()},

This is an important reminder that your Professional Indemnity Insurance is expiring soon.

Insurance Details:
------------------
Provider: {profile.insurance_provider_name or 'N/A'}
Policy Number: {profile.insurance_policy_number or 'N/A'}
Expiry Date: {expiry_date}
Days Remaining: {days_until_expiry}
Coverage Amount: {coverage_amount}

Action Required:
----------------
Please renew your Professional Indemnity Insurance before the expiry date to continue practicing.

It is a legal requirement for all practicing psychologists to maintain current Professional Indemnity Insurance coverage.

Steps to Renew:
1. Contact your insurance provider to renew your policy
2. Upload the new insurance certificate to your profile
3. Update the expiry date in your profile
4. Contact the practice manager if you need assistance

If you have any questions, please contact the practice manager.

Thank you,
Psychology Clinic Team
"""
    
    try:
        result = send_email_via_sendgrid(
            to_email=psychologist.email,
            subject=subject,
            message=message
        )
        
        result['subject'] = subject
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def send_insurance_expired_email(profile, notify_manager=False, manager=None):
    """
    Send Professional Indemnity Insurance expired notification email
    
    Args:
        profile: PsychologistProfile instance
        notify_manager: If True, send to practice manager instead of psychologist
        manager: Practice manager User instance (if notify_manager=True)
    
    Returns:
        dict: Email send result
    """
    psychologist = profile.user
    expiry_date = profile.insurance_expiry_date.strftime('%B %d, %Y') if profile.insurance_expiry_date else 'N/A'
    
    if notify_manager and manager:
        # Email to practice manager
        subject = f"🚨 Professional Indemnity Insurance Expired - {psychologist.get_full_name()}"
        recipient = manager.email
        
        message = f"""
Dear {manager.get_full_name()},

This is to notify you that a psychologist's Professional Indemnity Insurance has expired.

Psychologist Details:
---------------------
Name: {psychologist.get_full_name()}
Email: {psychologist.email}
Provider: {profile.insurance_provider_name or 'N/A'}
Policy Number: {profile.insurance_policy_number or 'N/A'}
Expiry Date: {expiry_date}

Action Required:
----------------
The psychologist has been suspended from seeing patients until insurance is renewed.

Please contact the psychologist immediately to:
1. Confirm insurance renewal status
2. Update their profile with new insurance details
3. Reactivate their account once insurance is confirmed

This is a critical compliance issue that must be resolved immediately.

Thank you,
Psychology Clinic Team
"""
    else:
        # Email to psychologist
        subject = f"🚨 Professional Indemnity Insurance Expired - Action Required"
        recipient = psychologist.email
        
        message = f"""
Dear {psychologist.get_full_name()},

URGENT: Your Professional Indemnity Insurance has expired.

Insurance Details:
------------------
Provider: {profile.insurance_provider_name or 'N/A'}
Policy Number: {profile.insurance_policy_number or 'N/A'}
Expiry Date: {expiry_date}

Your Account Status:
--------------------
Your account has been suspended. You cannot see patients until your insurance is renewed.

Action Required IMMEDIATELY:
----------------------------
1. Renew your Professional Indemnity Insurance immediately
2. Contact the practice manager
3. Upload the new insurance certificate to your profile
4. Update your profile with the new insurance expiry date
5. Your account will be reactivated once insurance is confirmed

You cannot see patients until your Professional Indemnity Insurance is renewed and your account is reactivated.

If you have already renewed your insurance, please contact the practice manager immediately to update your profile.

If you have any questions, please contact the practice manager.

Thank you,
Psychology Clinic Team
"""
    
    try:
        result = send_email_via_sendgrid(
            to_email=recipient,
            subject=subject,
            message=message
        )
        
        result['subject'] = subject
        result['notify_manager'] = notify_manager
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def send_welcome_email(user):
    """
    Send welcome email to newly registered user
    
    Args:
        user: User instance (newly created)
    
    Returns:
        dict: Email send result
    """
    from django.conf import settings
    from users.models import User
    
    user_name = user.get_full_name() or user.first_name or "there"
    role_display = user.get_role_display()
    
    subject = f"Welcome to Tailored Psychology - Your Account is Ready!"
    
    # Customize message based on role
    if user.role == User.UserRole.PATIENT:
        message = f"""
Hello {user_name},

Welcome to Tailored Psychology! We're excited to have you as part of our community.

Your account has been successfully created. Here's what you can do next:

Getting Started:
---------------
1. Complete your intake form - This helps us understand your needs better
2. Browse available psychologists - Find the right match for you
3. Book your first appointment - Schedule a session that works for you
4. Access your dashboard - View appointments, progress notes, and resources

Your Account Details:
--------------------
Email: {user.email}
Role: {role_display}

Need Help?
----------
If you have any questions or need assistance, please don't hesitate to contact us.

We're here to support you on your journey to better mental health.

Welcome aboard!

Best regards,
The Tailored Psychology Team
"""
    elif user.role == User.UserRole.PSYCHOLOGIST:
        message = f"""
Hello Dr. {user.last_name or user_name},

Welcome to Tailored Psychology! We're thrilled to have you join our team.

Your account has been successfully created. Here's what you can do next:

Getting Started:
---------------
1. Complete your psychologist profile - Add your AHPRA details and qualifications
2. Set your availability - Let patients know when you're available
3. Review your dashboard - Access patient information and appointments
4. Start seeing patients - Begin your practice with us

Your Account Details:
--------------------
Email: {user.email}
Role: {role_display}

Important:
----------
Please ensure your AHPRA registration and professional indemnity insurance are up to date in your profile.

If you have any questions or need assistance, please contact the practice manager.

Welcome to the team!

Best regards,
The Tailored Psychology Team
"""
    else:
        # For practice managers and admins
        message = f"""
Hello {user_name},

Welcome to Tailored Psychology! Your account has been successfully created.

Your Account Details:
--------------------
Email: {user.email}
Role: {role_display}

You now have access to the administrative dashboard where you can:
- Manage users and appointments
- View system analytics
- Handle billing and payments
- Monitor system health

If you have any questions, please don't hesitate to reach out.

Welcome aboard!

Best regards,
The Tailored Psychology Team
"""
    
    try:
        result = send_email_via_sendgrid(
            to_email=user.email,
            subject=subject,
            message=message
        )
        
        result['type'] = 'welcome_email'
        result['user_id'] = user.id
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'type': 'welcome_email'
        }

