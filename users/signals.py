"""
Django signals for user-related events
Handles automatic actions when models are created/updated
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProgressNote
from core.progress_sharing_service import share_progress_with_emergency_contact


@receiver(post_save, sender=ProgressNote)
def handle_progress_note_created(sender, instance, created, **kwargs):
    """
    Automatically share progress with emergency contact when progress note is created
    
    This signal is triggered when a ProgressNote is saved.
    If it's a new note (created=True) and the patient has consented,
    it will automatically share a summary with the emergency contact.
    """
    if created:  # Only for new progress notes, not updates
        try:
            # Share progress with emergency contact (if consent given)
            result = share_progress_with_emergency_contact(instance)
            
            # Log the result (you can add logging here if needed)
            if result.get('shared'):
                print(f"✅ Progress shared with emergency contact for {instance.patient.get_full_name()}")
                print(f"   Method: {result.get('method')}")
            else:
                # Don't log if consent not given (this is expected)
                if result.get('reason') != 'Patient has not consented to sharing progress':
                    print(f"⚠️ Progress sharing skipped: {result.get('reason')}")
        
        except Exception as e:
            # Don't fail the progress note creation if sharing fails
            print(f"❌ Error sharing progress with emergency contact: {str(e)}")

