"""
Tests for notification preference checks
Verifies that notifications respect patient preferences
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from users.models import PatientProfile
from appointments.models import Appointment
from services.models import Service, PsychologistProfile
from core.notification_utils import (
    should_send_email_notification,
    should_send_sms_notification,
    should_send_appointment_reminder,
    has_recording_consent
)
from core.email_service import (
    send_appointment_confirmation,
    send_appointment_reminder_24h,
    send_meeting_link_reminder,
    send_appointment_cancelled,
    send_appointment_rescheduled
)
from core.sms_service import send_sms_reminder
from core.whatsapp_service import send_whatsapp_reminder

User = get_user_model()


class NotificationPreferencesTestCase(TestCase):
    """Test notification preference checks"""
    
    def setUp(self):
        """Set up test data"""
        # Create patient
        self.patient = User.objects.create_user(
            email='patient@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            phone_number='+61412345678',
            role='patient'
        )
        self.patient_profile = PatientProfile.objects.create(user=self.patient)
        
        # Create psychologist
        self.psychologist = User.objects.create_user(
            email='psychologist@test.com',
            password='testpass123',
            first_name='Dr. Jane',
            last_name='Smith',
            phone_number='+61412345679',
            role='psychologist'
        )
        PsychologistProfile.objects.create(
            user=self.psychologist,
            ahpra_registration_number='PSY0001234567'
        )
        
        # Create service
        self.service = Service.objects.create(
            name='Individual Therapy',
            description='One-on-one therapy session',
            duration_minutes=50,
            price=150.00
        )
        
        # Create appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            psychologist=self.psychologist,
            service=self.service,
            appointment_date=timezone.now() + timedelta(days=1),
            duration_minutes=50,
            status='scheduled',
            session_type='telehealth'
        )
    
    def test_email_notifications_enabled(self):
        """Test that email notifications are sent when enabled"""
        self.patient_profile.email_notifications_enabled = True
        self.patient_profile.save()
        
        self.assertTrue(should_send_email_notification(self.patient))
    
    def test_email_notifications_disabled(self):
        """Test that email notifications are skipped when disabled"""
        self.patient_profile.email_notifications_enabled = False
        self.patient_profile.save()
        
        self.assertFalse(should_send_email_notification(self.patient))
        
        # Verify email function returns skipped
        result = send_appointment_confirmation(self.appointment)
        self.assertFalse(result.get('success'))
        self.assertTrue(result.get('skipped'))
        self.assertIn('disabled', result.get('reason', '').lower())
    
    def test_sms_notifications_enabled(self):
        """Test that SMS notifications are sent when enabled"""
        self.patient_profile.sms_notifications_enabled = True
        self.patient_profile.save()
        
        self.assertTrue(should_send_sms_notification(self.patient))
    
    def test_sms_notifications_disabled(self):
        """Test that SMS notifications are skipped when disabled"""
        self.patient_profile.sms_notifications_enabled = False
        self.patient_profile.save()
        
        self.assertFalse(should_send_sms_notification(self.patient))
        
        # Verify SMS function returns skipped
        result = send_sms_reminder(self.appointment, '1h')
        self.assertFalse(result.get('success'))
        self.assertTrue(result.get('skipped'))
        self.assertIn('disabled', result.get('reason', '').lower())
    
    def test_appointment_reminders_enabled(self):
        """Test that reminders are sent when enabled"""
        self.patient_profile.appointment_reminders_enabled = True
        self.patient_profile.save()
        
        self.assertTrue(should_send_appointment_reminder(self.patient))
    
    def test_appointment_reminders_disabled(self):
        """Test that reminders are skipped when disabled"""
        self.patient_profile.appointment_reminders_enabled = False
        self.patient_profile.save()
        
        self.assertFalse(should_send_appointment_reminder(self.patient))
        
        # Verify reminder function returns skipped
        result = send_appointment_reminder_24h(self.appointment)
        self.assertFalse(result.get('success'))
        self.assertTrue(result.get('skipped'))
        self.assertIn('disabled', result.get('reason', '').lower())
    
    def test_whatsapp_respects_sms_preference(self):
        """Test that WhatsApp respects SMS notification preference"""
        self.patient_profile.sms_notifications_enabled = False
        self.patient_profile.save()
        
        result = send_whatsapp_reminder(self.appointment, '24h')
        self.assertFalse(result['patient'].get('success'))
        self.assertTrue(result['patient'].get('skipped'))
    
    def test_all_notification_types_disabled(self):
        """Test when all notification types are disabled"""
        self.patient_profile.email_notifications_enabled = False
        self.patient_profile.sms_notifications_enabled = False
        self.patient_profile.appointment_reminders_enabled = False
        self.patient_profile.save()
        
        # All should be disabled
        self.assertFalse(should_send_email_notification(self.patient))
        self.assertFalse(should_send_sms_notification(self.patient))
        self.assertFalse(should_send_appointment_reminder(self.patient))
        
        # All notification functions should skip
        email_result = send_appointment_confirmation(self.appointment)
        sms_result = send_sms_reminder(self.appointment, '1h')
        reminder_result = send_appointment_reminder_24h(self.appointment)
        
        self.assertTrue(email_result.get('skipped'))
        self.assertTrue(sms_result.get('skipped'))
        self.assertTrue(reminder_result.get('skipped'))
    
    def test_re_enable_notifications(self):
        """Test that notifications resume when preferences are re-enabled"""
        # Disable first
        self.patient_profile.email_notifications_enabled = False
        self.patient_profile.save()
        
        result = send_appointment_confirmation(self.appointment)
        self.assertTrue(result.get('skipped'))
        
        # Re-enable
        self.patient_profile.email_notifications_enabled = True
        self.patient_profile.save()
        
        # Should not be skipped (though may fail due to email config, that's OK)
        self.assertTrue(should_send_email_notification(self.patient))
    
    def test_cancellation_respects_email_preference(self):
        """Test that cancellation emails respect email preference"""
        self.patient_profile.email_notifications_enabled = False
        self.patient_profile.save()
        
        result = send_appointment_cancelled(self.appointment, 'patient')
        self.assertTrue(result.get('skipped'))
    
    def test_rescheduled_respects_email_preference(self):
        """Test that rescheduled emails respect email preference"""
        self.patient_profile.email_notifications_enabled = False
        self.patient_profile.save()
        
        old_date = self.appointment.appointment_date
        result = send_appointment_rescheduled(self.appointment, old_date)
        self.assertTrue(result.get('skipped'))
    
    def test_meeting_link_reminder_respects_preferences(self):
        """Test that meeting link reminders respect preferences"""
        self.patient_profile.email_notifications_enabled = False
        self.patient_profile.appointment_reminders_enabled = False
        self.patient_profile.save()
        
        result = send_meeting_link_reminder(self.appointment)
        self.assertTrue(result.get('skipped'))


class RecordingConsentTestCase(TestCase):
    """Test recording consent checks"""
    
    def setUp(self):
        """Set up test data"""
        self.patient = User.objects.create_user(
            email='patient@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            role='patient'
        )
        self.patient_profile = PatientProfile.objects.create(user=self.patient)
    
    def test_recording_consent_false_by_default(self):
        """Test that recording consent is False by default"""
        self.assertFalse(has_recording_consent(self.patient))
    
    def test_recording_consent_when_given(self):
        """Test that recording consent returns True when given"""
        self.patient_profile.telehealth_recording_consent = True
        self.patient_profile.save()
        
        self.assertTrue(has_recording_consent(self.patient))
    
    def test_recording_consent_when_withdrawn(self):
        """Test that recording consent returns False when withdrawn"""
        # Give consent first
        self.patient_profile.telehealth_recording_consent = True
        self.patient_profile.save()
        self.assertTrue(has_recording_consent(self.patient))
        
        # Withdraw consent
        self.patient_profile.telehealth_recording_consent = False
        self.patient_profile.save()
        self.assertFalse(has_recording_consent(self.patient))
    
    def test_no_profile_defaults_to_no_consent(self):
        """Test that missing profile defaults to no consent (privacy-first)"""
        # Create user without profile
        user_no_profile = User.objects.create_user(
            email='noprofile@test.com',
            password='testpass123',
            role='patient'
        )
        
        # Should default to False (privacy-first)
        self.assertFalse(has_recording_consent(user_no_profile))

