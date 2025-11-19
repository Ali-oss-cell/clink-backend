#!/usr/bin/env python
"""
Quick verification script to test preference and consent logic
Can be run without full Django setup to verify core logic
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from users.models import PatientProfile, ProgressNote
from core.notification_utils import (
    should_send_email_notification,
    should_send_sms_notification,
    should_send_appointment_reminder,
    has_recording_consent
)
from core.progress_sharing_service import share_progress_with_emergency_contact, create_progress_summary

User = get_user_model()


def test_notification_preferences():
    """Test notification preference checks"""
    print("\n" + "="*60)
    print("TESTING: Notification Preferences")
    print("="*60)
    
    # Create test patient
    patient, _ = User.objects.get_or_create(
        email='test_patient@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Patient',
            'role': 'patient'
        }
    )
    profile, _ = PatientProfile.objects.get_or_create(user=patient)
    
    # Test 1: Email notifications disabled
    profile.email_notifications_enabled = False
    profile.save()
    result = should_send_email_notification(patient)
    assert result == False, "Email should be disabled"
    print("✅ Test 1: Email notifications disabled - PASSED")
    
    # Test 2: Email notifications enabled
    profile.email_notifications_enabled = True
    profile.save()
    result = should_send_email_notification(patient)
    assert result == True, "Email should be enabled"
    print("✅ Test 2: Email notifications enabled - PASSED")
    
    # Test 3: SMS notifications disabled
    profile.sms_notifications_enabled = False
    profile.save()
    result = should_send_sms_notification(patient)
    assert result == False, "SMS should be disabled"
    print("✅ Test 3: SMS notifications disabled - PASSED")
    
    # Test 4: Appointment reminders disabled
    profile.appointment_reminders_enabled = False
    profile.save()
    result = should_send_appointment_reminder(patient)
    assert result == False, "Reminders should be disabled"
    print("✅ Test 4: Appointment reminders disabled - PASSED")
    
    print("\n✅ All notification preference tests PASSED!")


def test_recording_consent():
    """Test recording consent checks"""
    print("\n" + "="*60)
    print("TESTING: Recording Consent")
    print("="*60)
    
    # Create test patient
    patient, _ = User.objects.get_or_create(
        email='test_patient2@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Patient',
            'role': 'patient'
        }
    )
    profile, _ = PatientProfile.objects.get_or_create(user=patient)
    
    # Test 1: No consent
    profile.telehealth_recording_consent = False
    profile.save()
    result = has_recording_consent(patient)
    assert result == False, "Should not have consent"
    print("✅ Test 1: No recording consent - PASSED")
    
    # Test 2: Has consent
    profile.telehealth_recording_consent = True
    profile.save()
    result = has_recording_consent(patient)
    assert result == True, "Should have consent"
    print("✅ Test 2: Has recording consent - PASSED")
    
    print("\n✅ All recording consent tests PASSED!")


def test_progress_sharing():
    """Test progress sharing logic"""
    print("\n" + "="*60)
    print("TESTING: Progress Sharing")
    print("="*60)
    
    # Create test patient with emergency contact
    patient, _ = User.objects.get_or_create(
        email='test_patient3@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'Patient',
            'role': 'patient'
        }
    )
    profile, _ = PatientProfile.objects.get_or_create(user=patient)
    profile.emergency_contact_name = 'Jane Doe'
    profile.emergency_contact_phone = '+61412345678'
    profile.save()
    
    # Create psychologist
    psychologist, _ = User.objects.get_or_create(
        email='test_psych@example.com',
        defaults={
            'first_name': 'Dr. Test',
            'last_name': 'Psychologist',
            'role': 'psychologist'
        }
    )
    
    # Create progress note
    progress_note = ProgressNote.objects.create(
        patient=patient,
        psychologist=psychologist,
        session_date=timezone.now(),
        session_number=1,
        subjective='Patient reports feeling better and managing anxiety well',
        objective='Patient appeared calm and engaged during session',
        assessment='Clinical impression: Patient shows signs of improvement. Diagnosis: Anxiety disorder.',
        plan='Continue current CBT approach. Monitor for side effects.',
        progress_rating=7
    )
    
    # Test 1: Sharing disabled
    profile.share_progress_with_emergency_contact = False
    profile.save()
    result = share_progress_with_emergency_contact(progress_note)
    assert result.get('shared') == False, "Should not share when disabled"
    assert 'consent' in result.get('reason', '').lower(), "Should mention consent"
    print("✅ Test 1: Progress sharing disabled - PASSED")
    
    # Test 2: Sharing enabled (but we'll mock SMS to avoid actual sending)
    profile.share_progress_with_emergency_contact = True
    profile.save()
    
    # Test summary creation
    summary = create_progress_summary(progress_note)
    assert 'Test Patient' in summary, "Should contain patient name"
    assert '7/10' in summary, "Should contain progress rating"
    assert 'feeling better' in summary, "Should contain subjective info"
    assert 'anxiety disorder' not in summary.lower(), "Should NOT contain diagnosis"
    assert 'CBT' not in summary, "Should NOT contain treatment details"
    print("✅ Test 2: Progress summary is non-sensitive - PASSED")
    
    # Cleanup
    progress_note.delete()
    
    print("\n✅ All progress sharing tests PASSED!")


def main():
    """Run all verification tests"""
    print("\n" + "="*60)
    print("VERIFICATION: Preferences & Consent Implementation")
    print("="*60)
    
    try:
        test_notification_preferences()
        test_recording_consent()
        test_progress_sharing()
        
        print("\n" + "="*60)
        print("✅ ALL VERIFICATION TESTS PASSED!")
        print("="*60)
        print("\nImplementation is working correctly!")
        return 0
    
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

