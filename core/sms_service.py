"""
SMS notification service using Twilio
Handles SMS messages for notifications and progress sharing
"""

from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


def send_sms(to_phone, message):
    """
    Send SMS message via Twilio
    
    Args:
        to_phone: Recipient phone number (format: +61412345678)
        message: Message content (max 1600 characters)
    
    Returns:
        dict: Message send result
    """
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    from_phone = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
    
    if not all([account_sid, auth_token, from_phone]):
        return {
            'success': False,
            'error': 'Twilio SMS not configured. Please set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER in settings.'
        }
    
    try:
        client = Client(account_sid, auth_token)
        
        # Truncate message if too long (SMS limit is 1600 chars)
        if len(message) > 1600:
            message = message[:1597] + "..."
        
        message_obj = client.messages.create(
            from_=from_phone,
            to=to_phone,
            body=message
        )
        
        return {
            'success': True,
            'message_sid': message_obj.sid,
            'status': message_obj.status,
            'to': to_phone
        }
    
    except TwilioRestException as e:
        return {
            'success': False,
            'error': str(e),
            'error_code': e.code
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def send_sms_reminder(appointment, reminder_type='1h'):
    """
    Send appointment reminder via SMS
    
    Args:
        appointment: Appointment instance
        reminder_type: Type of reminder ('1h', '24h', etc.)
    
    Returns:
        dict: SMS send result
    """
    from core.notification_utils import should_send_sms_notification, should_send_appointment_reminder
    
    patient = appointment.patient
    psychologist = appointment.psychologist
    
    # Check if patient wants reminders and SMS notifications
    if not should_send_appointment_reminder(patient):
        return {
            'success': False,
            'skipped': True,
            'reason': 'Appointment reminders disabled by patient',
            'patient_id': patient.id
        }
    
    if not should_send_sms_notification(patient):
        return {
            'success': False,
            'skipped': True,
            'reason': 'SMS notifications disabled by patient',
            'patient_id': patient.id
        }
    
    if not patient.phone_number:
        return {
            'success': False,
            'error': 'Patient phone number not available'
        }
    
    # Format appointment date/time
    appt_datetime = appointment.appointment_date.strftime('%A, %B %d at %I:%M %p')
    
    # Create message based on reminder type
    if reminder_type == '1h':
        message = f"""
Appointment Reminder

Hello {patient.first_name},

Your appointment starts in 1 hour:
📅 {appt_datetime}
👨‍⚕️ {psychologist.get_full_name()}
"""
        
        if appointment.session_type == 'telehealth' and appointment.video_room_id:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            meeting_url = f"{frontend_url}/video-session/{appointment.video_room_id}"
            message += f"\n🎥 Join here: {meeting_url}"
        else:
            message += "\n📍 Please head to the clinic now."
        
        message += "\n\nSee you soon!"
    
    else:
        message = f"""
Appointment Reminder

Hello {patient.first_name},

Your appointment is scheduled for:
📅 {appt_datetime}
👨‍⚕️ {psychologist.get_full_name()}

See you then!
"""
    
    return send_sms(patient.phone_number, message)

