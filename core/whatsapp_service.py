"""
WhatsApp notification service using Twilio
Handles appointment reminders via WhatsApp with healthcare compliance
"""

from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from .whatsapp_templates import WhatsAppTemplates, MessageValidator
from audit.utils import log_action
import logging

logger = logging.getLogger(__name__)


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
    
    def send_message(self, to_phone, message, user=None, request=None):
        """
        Send WhatsApp message with validation and audit logging
        
        Args:
            to_phone: Recipient phone number (format: +61412345678)
            message: Message content
            user: User object (for audit logging)
            request: Request object (for audit logging)
        
        Returns:
            dict: Message send result
        """
        # Validate message
        validation = MessageValidator.validate_message(message)
        if not validation['valid']:
            logger.error(f"Invalid WhatsApp message: {validation['errors']}")
            return {
                'success': False,
                'error': f"Message validation failed: {', '.join(validation['errors'])}",
                'validation_errors': validation['errors']
            }
        
        # Log warnings if any
        if validation['warnings']:
            logger.warning(f"WhatsApp message warnings: {validation['warnings']}")
        
        try:
            # Ensure phone number has whatsapp: prefix
            if not to_phone.startswith('whatsapp:'):
                to_phone = f'whatsapp:{to_phone}'
            
            # Send message
            message_obj = self.client.messages.create(
                from_=self.whatsapp_from,
                to=to_phone,
                body=message
            )
            
            # Audit log
            log_action(
                user=user,
                action='whatsapp_sent',
                obj=None,
                request=request,
                metadata={
                    'message_sid': message_obj.sid,
                    'to_phone': to_phone,
                    'message_length': len(message),
                    'status': message_obj.status
                }
            )
            
            logger.info(f"WhatsApp message sent successfully: {message_obj.sid}")
            
            return {
                'success': True,
                'message_sid': message_obj.sid,
                'status': message_obj.status,
                'to': to_phone
            }
        
        except TwilioRestException as e:
            logger.error(f"Twilio error sending WhatsApp: {str(e)} (code: {e.code})")
            
            # Audit log failure
            log_action(
                user=user,
                action='whatsapp_failed',
                obj=None,
                request=request,
                metadata={
                    'to_phone': to_phone,
                    'error': str(e),
                    'error_code': e.code
                }
            )
            
            return {
                'success': False,
                'error': str(e),
                'error_code': e.code
            }
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp: {str(e)}")
            
            return {
                'success': False,
                'error': str(e)
            }


def send_whatsapp_reminder(appointment, reminder_type='24h'):
    """
    Send appointment reminder via WhatsApp to BOTH patient and psychologist
    Uses professional templates with validation
    
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
    appt_time = appointment.appointment_date.strftime('%I:%M %p')
    
    # Get video link if applicable
    video_link = None
    if appointment.session_type == 'telehealth' and appointment.video_room_id:
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        video_link = f"{frontend_url}/video-session/{appointment.video_room_id}"
    
    # Get location for in-person sessions
    location = None
    if appointment.session_type != 'telehealth':
        if hasattr(psychologist, 'psychologist_profile'):
            location = psychologist.psychologist_profile.practice_name or "Tailored Psychology Clinic"
        else:
            location = "Tailored Psychology Clinic"
    
    # Create message based on reminder type using professional templates
    if reminder_type == '24h':
        message_patient = WhatsAppTemplates.appointment_reminder_24h(
            patient_name=patient.first_name,
            appointment_date=appt_datetime,
            psychologist_name=psychologist.get_full_name(),
            duration=appointment.duration_minutes,
            session_type=appointment.session_type,
            video_link=video_link,
            location=location
        )
    
    elif reminder_type == '1h':
        message_patient = WhatsAppTemplates.appointment_reminder_1h(
            patient_name=patient.first_name,
            appointment_time=appt_time,
            psychologist_name=psychologist.get_full_name(),
            session_type=appointment.session_type,
            video_link=video_link
        )
    
    elif reminder_type == '15min':
        message_patient = WhatsAppTemplates.appointment_reminder_15min(
            patient_name=patient.first_name,
            session_type=appointment.session_type,
            video_link=video_link
        )
    
    else:
        logger.error(f"Invalid reminder type: {reminder_type}")
        return {
            'success': False,
            'error': 'Invalid reminder type'
        }
    
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
            results['patient'] = whatsapp_service.send_message(
                patient.phone_number, 
                message_patient,
                user=patient
            )
        except Exception as e:
            logger.error(f"Error sending WhatsApp to patient: {str(e)}")
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
    # Create psychologist message using professional templates
    if reminder_type == '24h':
        message_psychologist = WhatsAppTemplates.psychologist_session_reminder_24h(
            psychologist_name=psychologist.last_name,
            appointment_date=appt_datetime,
            patient_name=patient.get_full_name(),
            duration=appointment.duration_minutes,
            session_type=appointment.session_type,
            video_link=video_link,
            notes=getattr(appointment, 'notes', None)
        )
    
    elif reminder_type == '1h':
        message_psychologist = WhatsAppTemplates.psychologist_session_reminder_1h(
            psychologist_name=psychologist.last_name,
            appointment_time=appt_time,
            patient_name=patient.get_full_name(),
            session_type=appointment.session_type,
            video_link=video_link
        )
    
    elif reminder_type == '15min':
        # Use same template structure for 15min
        message_psychologist = f"""🚀 Starting in 15 Minutes!

Hello Dr. {psychologist.last_name},

Your session is about to begin!
👤 Patient: {patient.get_full_name()}
"""
        
        if video_link:
            message_psychologist += f"\n🎥 Join now:\n{video_link}"
        
        message_psychologist += "\n\nTailored Psychology"
    
    # Send to psychologist (always send, no preference check for staff)
    if psychologist.phone_number:
        try:
            whatsapp_service = WhatsAppService()
            results['psychologist'] = whatsapp_service.send_message(
                psychologist.phone_number,
                message_psychologist,
                user=psychologist
            )
        except Exception as e:
            logger.error(f"Error sending WhatsApp to psychologist: {str(e)}")
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


def send_whatsapp_cancellation(appointment, cancellation_reason=None):
    """
    Send appointment cancellation notification via WhatsApp
    Uses professional template
    
    Args:
        appointment: Appointment instance
        cancellation_reason: Optional reason for cancellation
    
    Returns:
        dict: Message send result
    """
    from core.notification_utils import should_send_sms_notification
    
    patient = appointment.patient
    
    # Check if patient wants SMS/WhatsApp notifications
    if not should_send_sms_notification(patient):
        return {
            'success': False,
            'skipped': True,
            'reason': 'SMS notifications disabled by patient'
        }
    
    if not patient.phone_number:
        return {
            'success': False,
            'error': 'Patient phone number not available'
        }
    
    appt_datetime = appointment.appointment_date.strftime('%A, %B %d at %I:%M %p')
    
    # Use professional template
    message = WhatsAppTemplates.appointment_cancelled(
        patient_name=patient.first_name,
        appointment_date=appt_datetime,
        cancellation_reason=cancellation_reason
    )
    
    try:
        whatsapp_service = WhatsAppService()
        return whatsapp_service.send_message(
            patient.phone_number, 
            message,
            user=patient
        )
    
    except Exception as e:
        logger.error(f"Error sending cancellation WhatsApp: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }


def test_whatsapp_configuration(test_phone_number):
    """
    Test WhatsApp configuration
    Uses professional template
    
    Args:
        test_phone_number: Phone number to send test message to
    
    Returns:
        dict: Test result
    """
    try:
        whatsapp_service = WhatsAppService()
        
        # Use professional template
        message = WhatsAppTemplates.test_message()
        
        result = whatsapp_service.send_message(test_phone_number, message)
        return result
    
    except Exception as e:
        logger.error(f"WhatsApp configuration test failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

