"""
Notification utility functions for checking patient preferences
Ensures notifications respect patient communication preferences
"""


def should_send_email_notification(patient):
    """
    Check if patient wants to receive email notifications
    
    Args:
        patient: User instance (must be a patient)
    
    Returns:
        bool: True if email notifications should be sent, False otherwise
    """
    if not hasattr(patient, 'patient_profile'):
        # Default to sending if no profile exists (backward compatibility)
        return True
    
    profile = patient.patient_profile
    return profile.email_notifications_enabled


def should_send_sms_notification(patient):
    """
    Check if patient wants to receive SMS notifications
    
    Args:
        patient: User instance (must be a patient)
    
    Returns:
        bool: True if SMS notifications should be sent, False otherwise
    """
    if not hasattr(patient, 'patient_profile'):
        # Default to sending if no profile exists (backward compatibility)
        return True
    
    profile = patient.patient_profile
    return profile.sms_notifications_enabled


def should_send_appointment_reminder(patient):
    """
    Check if patient wants to receive appointment reminders
    
    Args:
        patient: User instance (must be a patient)
    
    Returns:
        bool: True if appointment reminders should be sent, False otherwise
    """
    if not hasattr(patient, 'patient_profile'):
        # Default to sending if no profile exists (backward compatibility)
        return True
    
    profile = patient.patient_profile
    return profile.appointment_reminders_enabled


def has_recording_consent(patient):
    """
    Check if patient has consented to session recording
    
    Args:
        patient: User instance (must be a patient)
    
    Returns:
        bool: True if patient has consented to recording, False otherwise
    """
    if not hasattr(patient, 'patient_profile'):
        # Default to False if no profile exists (privacy-first approach)
        return False
    
    profile = patient.patient_profile
    return profile.telehealth_recording_consent

