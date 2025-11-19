"""
WhatsApp notification service using Twilio
Handles appointment reminders via WhatsApp
"""

from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException


class WhatsAppService:
    """
    Service for sending WhatsApp messages via Twilio
    
    Features:
    - Send appointment reminders
    - Send meeting links
    - Track message delivery
    """
    
    def __init__(self):
        """Initialize Twilio client"""
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.whatsapp_from = settings.TWILIO_WHATSAPP_FROM
        
        if not all([self.account_sid, self.auth_token, self.whatsapp_from]):
            raise ValueError(
                "Twilio WhatsApp not configured. Please set TWILIO_ACCOUNT_SID, "
                "TWILIO_AUTH_TOKEN, and TWILIO_WHATSAPP_FROM in settings."
            )
        
        self.client = Client(self.account_sid, self.auth_token)
    
    def send_message(self, to_phone, message):
        """
        Send WhatsApp message
        
        Args:
            to_phone: Recipient phone number (format: +61412345678)
            message: Message content
        
        Returns:
            dict: Message send result
        """
        try:
            # Ensure phone number has whatsapp: prefix
            if not to_phone.startswith('whatsapp:'):
                to_phone = f'whatsapp:{to_phone}'
            
            message_obj = self.client.messages.create(
                from_=self.whatsapp_from,
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


def send_whatsapp_reminder(appointment, reminder_type='24h'):
    """
    Send appointment reminder via WhatsApp to BOTH patient and psychologist
    
    Args:
        appointment: Appointment instance
        reminder_type: Type of reminder ('24h', '1h', '15min')
    
    Returns:
        dict: Message send result for both recipients
    """
    from core.notification_utils import should_send_sms_notification, should_send_appointment_reminder
    
    patient = appointment.patient
    psychologist = appointment.psychologist
    
    results = {'patient': {}, 'psychologist': {}}
    
    # Check if patient wants reminders and SMS/WhatsApp notifications
    # Note: WhatsApp uses SMS preferences since it's a messaging channel
    patient_wants_reminders = should_send_appointment_reminder(patient)
    patient_wants_sms = should_send_sms_notification(patient)
    
    # Format appointment date/time
    appt_datetime = appointment.appointment_date.strftime('%A, %B %d at %I:%M %p')
    
    # Create message based on reminder type
    if reminder_type == '24h':
        message = f"""
🔔 Appointment Reminder

Hello {patient.first_name},

Your appointment is tomorrow:
📅 {appt_datetime}
👨‍⚕️ {psychologist.get_full_name()}
⏱️ {appointment.duration_minutes} minutes
"""
        
        if appointment.session_type == 'telehealth' and appointment.video_room_id:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            meeting_url = f"{frontend_url}/video-session/{appointment.video_room_id}"
            message += f"\n🎥 Video Link:\n{meeting_url}\n"
            message += "\n💡 Tip: Join 5 minutes early!"
        else:
            if hasattr(psychologist, 'psychologist_profile'):
                location = psychologist.psychologist_profile.practice_name or "Clinic"
            else:
                location = "Clinic"
            message += f"\n📍 Location: {location}"
        
        message += "\n\nSee you tomorrow! 👋"
    
    elif reminder_type == '1h':
        message = f"""
⏰ Starting in 1 Hour

Hello {patient.first_name},

Your appointment starts at {appointment.appointment_date.strftime('%I:%M %p')}
👨‍⚕️ {psychologist.get_full_name()}
"""
        
        if appointment.session_type == 'telehealth' and appointment.video_room_id:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            meeting_url = f"{frontend_url}/video-session/{appointment.video_room_id}"
            message += f"\n🎥 Join here:\n{meeting_url}"
        else:
            message += "\n📍 Please head to the clinic now."
        
        message += "\n\nReady when you are! ✨"
    
    elif reminder_type == '15min':
        message = f"""
🚀 Starting in 15 Minutes!

Hello {patient.first_name},

Your session is about to begin!
"""
        
        if appointment.session_type == 'telehealth' and appointment.video_room_id:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            meeting_url = f"{frontend_url}/video-session/{appointment.video_room_id}"
            message += f"\n🎥 Join now:\n{meeting_url}\n\n"
            message += "💡 Test your camera & mic!"
        
        message += "\n\nSee you soon! 👋"
    
    else:
        return {
            'success': False,
            'error': 'Invalid reminder type'
        }
    
    # Save patient message for sending
    message_patient = message
    
    # ========== SEND TO PATIENT ==========
    if not patient_wants_reminders or not patient_wants_sms:
        results['patient'] = {
            'success': False,
            'skipped': True,
            'reason': 'Appointment reminders or SMS notifications disabled by patient',
            'patient_id': patient.id
        }
    elif patient.phone_number:
        try:
            whatsapp_service = WhatsAppService()
            results['patient'] = whatsapp_service.send_message(patient.phone_number, message_patient)
        except Exception as e:
            results['patient'] = {
                'success': False,
                'error': str(e)
            }
    else:
        results['patient'] = {
            'success': False,
            'error': 'Patient phone number not available'
        }
    
    # ========== SEND TO PSYCHOLOGIST ==========
    # Create psychologist message
    if reminder_type == '24h':
        message_psychologist = f"""
🔔 Session Reminder

Hello Dr. {psychologist.last_name},

You have a session tomorrow:
📅 {appt_datetime}
👤 Patient: {patient.get_full_name()}
⏱️ {appointment.duration_minutes} minutes
"""
        
        if appointment.session_type == 'telehealth' and appointment.video_room_id:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            meeting_url = f"{frontend_url}/video-session/{appointment.video_room_id}"
            message_psychologist += f"\n🎥 Video Link:\n{meeting_url}\n"
            message_psychologist += "\n💡 Join 5 minutes early to prepare."
        
        if appointment.notes:
            message_psychologist += f"\n📝 Notes: {appointment.notes[:100]}..."
        
        message_psychologist += "\n\nSee you tomorrow! 👋"
    
    elif reminder_type == '1h':
        message_psychologist = f"""
⏰ Session in 1 Hour

Hello Dr. {psychologist.last_name},

Your session starts at {appointment.appointment_date.strftime('%I:%M %p')}
👤 Patient: {patient.get_full_name()}
"""
        
        if appointment.session_type == 'telehealth' and appointment.video_room_id:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            meeting_url = f"{frontend_url}/video-session/{appointment.video_room_id}"
            message_psychologist += f"\n🎥 Join here:\n{meeting_url}"
        
        message_psychologist += "\n\nReady when you are! ✨"
    
    elif reminder_type == '15min':
        message_psychologist = f"""
🚀 Starting in 15 Minutes!

Hello Dr. {psychologist.last_name},

Your session is about to begin!
👤 Patient: {patient.get_full_name()}
"""
        
        if appointment.session_type == 'telehealth' and appointment.video_room_id:
            frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
            meeting_url = f"{frontend_url}/video-session/{appointment.video_room_id}"
            message_psychologist += f"\n🎥 Join now:\n{meeting_url}"
        
        message_psychologist += "\n\nSee you soon! 👋"
    
    # Send to psychologist
    if psychologist.phone_number:
        try:
            whatsapp_service = WhatsAppService()
            results['psychologist'] = whatsapp_service.send_message(
                psychologist.phone_number,
                message_psychologist
            )
        except Exception as e:
            results['psychologist'] = {
                'success': False,
                'error': str(e)
            }
    else:
        results['psychologist'] = {
            'success': False,
            'error': 'Psychologist phone number not available'
        }
    
    # Return combined results
    results['reminder_type'] = reminder_type
    results['success'] = results['patient'].get('success', False) or results['psychologist'].get('success', False)
    
    return results


def send_whatsapp_cancellation(appointment):
    """
    Send appointment cancellation notification via WhatsApp
    
    Args:
        appointment: Appointment instance
    
    Returns:
        dict: Message send result
    """
    patient = appointment.patient
    
    if not patient.phone_number:
        return {
            'success': False,
            'error': 'Patient phone number not available'
        }
    
    appt_datetime = appointment.appointment_date.strftime('%A, %B %d at %I:%M %p')
    
    message = f"""
❌ Appointment Cancelled

Hello {patient.first_name},

Your appointment on {appt_datetime} has been cancelled.

Would you like to book a new appointment?

Thank you,
Psychology Clinic 🏥
"""
    
    try:
        whatsapp_service = WhatsAppService()
        return whatsapp_service.send_message(patient.phone_number, message)
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def test_whatsapp_configuration(test_phone_number):
    """
    Test WhatsApp configuration
    
    Args:
        test_phone_number: Phone number to send test message to
    
    Returns:
        dict: Test result
    """
    try:
        whatsapp_service = WhatsAppService()
        
        message = """
✅ Test Message

This is a test message from Psychology Clinic.
If you receive this, WhatsApp notifications are working correctly!

🎉 All systems go!
"""
        
        result = whatsapp_service.send_message(test_phone_number, message)
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

