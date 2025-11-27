"""
Professional WhatsApp message templates for Psychology Clinic
All messages are compliant with healthcare communication standards
"""

from django.conf import settings
from typing import Dict, Any


class WhatsAppTemplates:
    """
    Professional message templates for WhatsApp communications
    
    Features:
    - Healthcare-compliant messaging
    - Professional tone
    - Clear call-to-actions
    - Privacy-conscious
    """
    
    @staticmethod
    def appointment_reminder_24h(patient_name: str, appointment_date: str, 
                                  psychologist_name: str, duration: int,
                                  session_type: str, video_link: str = None,
                                  location: str = None) -> str:
        """24-hour appointment reminder"""
        
        message = f"""🔔 Appointment Reminder

Hello {patient_name},

Your appointment is scheduled for tomorrow:

📅 {appointment_date}
👨‍⚕️ {psychologist_name}
⏱️ {duration} minutes
"""
        
        if session_type == 'telehealth' and video_link:
            message += f"""
💻 Telehealth Session
🎥 Video Link: {video_link}

💡 Please join 5 minutes early to test your connection.
"""
        elif location:
            message += f"""
📍 Location: {location}

Please arrive 5 minutes before your appointment time.
"""
        
        message += """
If you need to reschedule, please contact us as soon as possible.

Warm regards,
Tailored Psychology Team"""
        
        return message
    
    @staticmethod
    def appointment_reminder_1h(patient_name: str, appointment_time: str,
                                psychologist_name: str, session_type: str,
                                video_link: str = None) -> str:
        """1-hour appointment reminder"""
        
        message = f"""⏰ Appointment in 1 Hour

Hello {patient_name},

Your session starts at {appointment_time}
👨‍⚕️ {psychologist_name}
"""
        
        if session_type == 'telehealth' and video_link:
            message += f"""
🎥 Join your telehealth session:
{video_link}

💡 Test your camera and microphone before joining.
"""
        else:
            message += """
📍 Please head to the clinic now.
"""
        
        message += """
See you soon!
Tailored Psychology"""
        
        return message
    
    @staticmethod
    def appointment_reminder_15min(patient_name: str, session_type: str,
                                   video_link: str = None) -> str:
        """15-minute appointment reminder"""
        
        message = f"""🚀 Session Starting in 15 Minutes

Hello {patient_name},

Your appointment is about to begin!
"""
        
        if session_type == 'telehealth' and video_link:
            message += f"""
🎥 Join now:
{video_link}

Your psychologist is ready when you are.
"""
        else:
            message += """
Please make your way to the appointment room.
"""
        
        message += """
Tailored Psychology"""
        
        return message
    
    @staticmethod
    def appointment_confirmation(patient_name: str, appointment_date: str,
                                 psychologist_name: str, session_type: str) -> str:
        """Appointment booking confirmation"""
        
        message = f"""✅ Appointment Confirmed

Hello {patient_name},

Your appointment has been successfully booked:

📅 {appointment_date}
👨‍⚕️ {psychologist_name}
💻 Session Type: {session_type.title()}

You will receive reminders before your appointment.

To reschedule or cancel, please contact us at least 24 hours in advance.

Thank you,
Tailored Psychology"""
        
        return message
    
    @staticmethod
    def appointment_cancelled(patient_name: str, appointment_date: str,
                             cancellation_reason: str = None) -> str:
        """Appointment cancellation notification"""
        
        message = f"""❌ Appointment Cancelled

Hello {patient_name},

Your appointment scheduled for {appointment_date} has been cancelled.
"""
        
        if cancellation_reason:
            message += f"""
Reason: {cancellation_reason}
"""
        
        message += """
Would you like to book a new appointment? Please contact us or visit our booking portal.

Thank you,
Tailored Psychology"""
        
        return message
    
    @staticmethod
    def appointment_rescheduled(patient_name: str, old_date: str, new_date: str,
                               psychologist_name: str) -> str:
        """Appointment rescheduling notification"""
        
        message = f"""📅 Appointment Rescheduled

Hello {patient_name},

Your appointment has been rescheduled:

❌ Previous: {old_date}
✅ New Time: {new_date}
👨‍⚕️ {psychologist_name}

You will receive reminders before your new appointment time.

Thank you,
Tailored Psychology"""
        
        return message
    
    @staticmethod
    def psychologist_session_reminder_24h(psychologist_name: str, appointment_date: str,
                                         patient_name: str, duration: int,
                                         session_type: str, video_link: str = None,
                                         notes: str = None) -> str:
        """24-hour session reminder for psychologist"""
        
        message = f"""🔔 Session Reminder

Hello Dr. {psychologist_name},

You have a session scheduled for tomorrow:

📅 {appointment_date}
👤 Patient: {patient_name}
⏱️ {duration} minutes
💻 Type: {session_type.title()}
"""
        
        if video_link:
            message += f"""
🎥 Video Link: {video_link}
"""
        
        if notes:
            # Truncate notes for privacy
            truncated_notes = notes[:100] + "..." if len(notes) > 100 else notes
            message += f"""
📝 Notes: {truncated_notes}
"""
        
        message += """
Tailored Psychology"""
        
        return message
    
    @staticmethod
    def psychologist_session_reminder_1h(psychologist_name: str, appointment_time: str,
                                        patient_name: str, session_type: str,
                                        video_link: str = None) -> str:
        """1-hour session reminder for psychologist"""
        
        message = f"""⏰ Session in 1 Hour

Hello Dr. {psychologist_name},

Your session starts at {appointment_time}
👤 Patient: {patient_name}
💻 Type: {session_type.title()}
"""
        
        if video_link:
            message += f"""
🎥 Video Link: {video_link}
"""
        
        message += """
Tailored Psychology"""
        
        return message
    
    @staticmethod
    def payment_received(patient_name: str, amount: str, invoice_number: str,
                        payment_method: str) -> str:
        """Payment confirmation"""
        
        message = f"""✅ Payment Received

Hello {patient_name},

Thank you! Your payment has been processed:

💳 Amount: ${amount}
📄 Invoice: #{invoice_number}
💰 Method: {payment_method}

A receipt has been sent to your email.

Thank you,
Tailored Psychology"""
        
        return message
    
    @staticmethod
    def invoice_created(patient_name: str, amount: str, invoice_number: str,
                       due_date: str) -> str:
        """New invoice notification"""
        
        message = f"""📄 New Invoice

Hello {patient_name},

A new invoice has been created:

💵 Amount: ${amount}
📄 Invoice: #{invoice_number}
📅 Due Date: {due_date}

You can view and pay your invoice through your patient portal.

Thank you,
Tailored Psychology"""
        
        return message
    
    @staticmethod
    def emergency_contact_progress_update(emergency_contact_name: str, 
                                         patient_name: str, 
                                         summary: str,
                                         clinic_phone: str = None) -> str:
        """Progress update for emergency contact (privacy-compliant)"""
        
        message = f"""📊 Progress Update

Hello {emergency_contact_name},

This is an update regarding {patient_name}'s therapy progress.

{summary}

This message is sent with the patient's consent. For questions, please contact us.
"""
        
        if clinic_phone:
            message += f"""
📞 Contact: {clinic_phone}
"""
        
        message += """
Tailored Psychology
(Confidential Communication)"""
        
        return message
    
    @staticmethod
    def welcome_message(patient_name: str) -> str:
        """Welcome message for new patients"""
        
        message = f"""👋 Welcome to Tailored Psychology

Hello {patient_name},

Welcome! We're glad you've chosen us for your mental health journey.

What you can do:
📅 Book appointments
💬 Message your psychologist
📄 Access your records
💳 Manage billing

Your privacy and wellbeing are our top priorities.

If you have questions, we're here to help.

Warm regards,
Tailored Psychology Team"""
        
        return message
    
    @staticmethod
    def intake_form_reminder(patient_name: str) -> str:
        """Reminder to complete intake form"""
        
        message = f"""📋 Intake Form Reminder

Hello {patient_name},

We notice your intake form is incomplete. Please complete it before your first appointment to help us provide the best care.

It takes about 10-15 minutes.

Log in to your patient portal to complete the form.

Thank you,
Tailored Psychology"""
        
        return message
    
    @staticmethod
    def test_message() -> str:
        """Test message for configuration verification"""
        
        return """✅ Test Message

This is a test message from Tailored Psychology.

If you receive this, WhatsApp notifications are working correctly!

🎉 All systems operational.

- Tailored Psychology Team"""


class MessageValidator:
    """
    Validates WhatsApp messages for healthcare compliance
    """
    
    MAX_MESSAGE_LENGTH = 1600  # WhatsApp limit
    PROHIBITED_TERMS = [
        'password', 'ssn', 'social security', 
        'credit card', 'cvv', 'pin'
    ]
    
    @classmethod
    def validate_message(cls, message: str) -> Dict[str, Any]:
        """
        Validate message for compliance and safety
        
        Returns:
            dict: {'valid': bool, 'errors': list, 'warnings': list}
        """
        errors = []
        warnings = []
        
        # Check length
        if len(message) > cls.MAX_MESSAGE_LENGTH:
            errors.append(f"Message too long ({len(message)} chars). Max: {cls.MAX_MESSAGE_LENGTH}")
        
        # Check for prohibited terms
        message_lower = message.lower()
        for term in cls.PROHIBITED_TERMS:
            if term in message_lower:
                errors.append(f"Message contains prohibited term: '{term}'")
        
        # Check for empty message
        if not message.strip():
            errors.append("Message is empty")
        
        # Check for excessive special characters (potential spam)
        special_char_count = sum(1 for c in message if not c.isalnum() and not c.isspace())
        if special_char_count > len(message) * 0.3:
            warnings.append("Message contains many special characters")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'length': len(message)
        }
    
    @classmethod
    def sanitize_patient_data(cls, data: str) -> str:
        """
        Sanitize patient data for inclusion in messages
        Remove or mask sensitive information
        """
        # This is a basic implementation
        # In production, you might want more sophisticated sanitization
        
        # Remove potential email addresses
        import re
        data = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL REMOVED]', data)
        
        # Remove potential phone numbers
        data = re.sub(r'\b\d{10,15}\b', '[PHONE REMOVED]', data)
        
        # Remove potential Medicare numbers
        data = re.sub(r'\b\d{10}\s\d\b', '[MEDICARE REMOVED]', data)
        
        return data

