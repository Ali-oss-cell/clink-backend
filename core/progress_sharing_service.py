"""
Progress sharing service for sharing patient progress with emergency contacts
Handles automatic sharing of progress note summaries when patient has consented
"""

from django.conf import settings
from django.utils import timezone
from core.email_service import send_email_via_sendgrid
from core.sms_service import send_sms


def create_progress_summary(progress_note):
    """
    Create a non-sensitive summary of progress note for sharing
    
    Args:
        progress_note: ProgressNote instance
    
    Returns:
        str: Formatted summary text
    """
    patient = progress_note.patient
    session_date = progress_note.session_date.strftime('%B %d, %Y')
    
    # Build summary (non-sensitive information only)
    summary_lines = [
        f"Progress Update for {patient.get_full_name()}",
        "",
        f"Session Date: {session_date}",
    ]
    
    # Add progress rating if available
    if progress_note.progress_rating:
        summary_lines.append(f"Progress Rating: {progress_note.progress_rating}/10")
    
    summary_lines.append("")
    summary_lines.append("General Update:")
    
    # Include limited subjective information (first 200 chars)
    if progress_note.subjective:
        subjective_summary = progress_note.subjective[:200]
        if len(progress_note.subjective) > 200:
            subjective_summary += "..."
        summary_lines.append(subjective_summary)
    
    summary_lines.append("")
    summary_lines.append("Next Steps:")
    
    # Include limited plan information (first 200 chars)
    if progress_note.plan:
        plan_summary = progress_note.plan[:200]
        if len(progress_note.plan) > 200:
            plan_summary += "..."
        summary_lines.append(plan_summary)
    
    summary_lines.append("")
    summary_lines.append("---")
    summary_lines.append("This is an automated update. If you have concerns, please contact the clinic directly.")
    
    return "\n".join(summary_lines)


def share_progress_with_emergency_contact(progress_note):
    """
    Share progress note summary with emergency contact if patient has consented
    
    Args:
        progress_note: ProgressNote instance
    
    Returns:
        dict: Sharing result with status and details
    """
    patient = progress_note.patient
    
    try:
        patient_profile = patient.patient_profile
    except AttributeError:
        return {
            'shared': False,
            'reason': 'Patient profile not found',
            'error': 'PatientProfile does not exist'
        }
    
    # Check if patient has consented to sharing
    if not patient_profile.share_progress_with_emergency_contact:
        return {
            'shared': False,
            'reason': 'Patient has not consented to sharing progress',
            'consent_status': False
        }
    
    # Check if emergency contact information exists
    if not patient_profile.emergency_contact_name:
        return {
            'shared': False,
            'reason': 'Emergency contact name not provided',
            'error': 'Missing emergency contact information'
        }
    
    if not patient_profile.emergency_contact_phone:
        return {
            'shared': False,
            'reason': 'Emergency contact phone not provided',
            'error': 'Missing emergency contact phone number'
        }
    
    # Create summary
    summary = create_progress_summary(progress_note)
    
    # Prepare contact information
    emergency_contact_name = patient_profile.emergency_contact_name
    emergency_contact_phone = patient_profile.emergency_contact_phone
    patient_name = patient.get_full_name()
    
    # Send via SMS (primary method for emergency contacts)
    # Note: Email would require emergency_contact_email field which doesn't exist yet
    results = {
        'shared': False,
        'method': None,
        'contact_name': emergency_contact_name,
        'contact_phone': emergency_contact_phone,
        'patient_name': patient_name,
        'session_date': progress_note.session_date.isoformat()
    }
    
    try:
        sms_result = send_sms(
            to_phone=emergency_contact_phone,
            message=summary[:1600]  # SMS limit
        )
        
        if sms_result.get('success'):
            results['shared'] = True
            results['method'] = 'sms'
            results['sms_result'] = sms_result
            return results
        else:
            results['sms_error'] = sms_result.get('error', 'Unknown SMS error')
    except Exception as e:
        results['sms_error'] = str(e)
    
    # If both methods failed
    results['error'] = 'Failed to send via both email and SMS'
    return results


def send_progress_update_email(emergency_contact_email, patient_name, summary):
    """
    Send progress update via email
    
    Args:
        emergency_contact_email: Emergency contact email address
        patient_name: Patient's full name
        summary: Progress summary text
    
    Returns:
        dict: Email send result
    """
    subject = f"Progress Update for {patient_name}"
    
    return send_email_via_sendgrid(
        to_email=emergency_contact_email,
        subject=subject,
        message=summary
    )


def send_progress_update_sms(emergency_contact_phone, summary):
    """
    Send progress update via SMS
    
    Args:
        emergency_contact_phone: Emergency contact phone number
        summary: Progress summary text (will be truncated to 1600 chars)
    
    Returns:
        dict: SMS send result
    """
    # Truncate to SMS limit
    sms_message = summary[:1600] if len(summary) > 1600 else summary
    
    return send_sms(
        to_phone=emergency_contact_phone,
        message=sms_message
    )

