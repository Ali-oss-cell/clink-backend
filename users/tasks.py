"""
Celery tasks for user management and compliance
Handles data deletion requests (APP 13)
"""

from celery import shared_task
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import DataDeletionRequest, User
from audit.utils import log_action
import logging

logger = logging.getLogger(__name__)


@shared_task(name='users.process_approved_deletion_requests')
def process_approved_deletion_requests():
    """
    Process approved data deletion requests that are ready for deletion
    
    Runs daily to:
    - Find approved deletion requests where scheduled_deletion_date has passed
    - Soft delete (archive) patient data
    - Mark deletion requests as completed
    
    Returns:
        dict: Statistics on deletions processed
    """
    now = timezone.now()
    
    # Find approved deletion requests ready for processing
    ready_requests = DataDeletionRequest.objects.filter(
        status=DataDeletionRequest.RequestStatus.APPROVED,
        scheduled_deletion_date__lte=now
    ).select_related('patient')
    
    stats = {
        'processed': 0,
        'errors': 0,
        'skipped': 0
    }
    
    for deletion_request in ready_requests:
        try:
            patient = deletion_request.patient
            
            # Double-check retention policy
            if not deletion_request.can_be_deleted_now():
                logger.warning(
                    f'Deletion request {deletion_request.id} cannot be deleted yet. '
                    f'Earliest deletion date: {deletion_request.earliest_deletion_date}'
                )
                stats['skipped'] += 1
                continue
            
            # Perform soft delete (archive)
            patient.is_deleted = True
            patient.deleted_at = now
            patient.deletion_request = deletion_request
            patient.is_active = False  # Disable login
            patient.save()
            
            # Soft delete patient profile if it exists
            if hasattr(patient, 'patient_profile'):
                # We could add is_deleted to PatientProfile too, but for now just mark user
                pass
            
            # Mark deletion request as completed
            deletion_request.status = DataDeletionRequest.RequestStatus.COMPLETED
            deletion_request.deletion_completed_date = now
            deletion_request.save()
            
            # Log the deletion
            try:
                log_action(
                    user=patient,
                    action='data_deleted',
                    obj=deletion_request,
                    request=None,  # No HTTP request in Celery task
                    metadata={
                        'request_id': deletion_request.id,
                        'deletion_date': now.isoformat(),
                        'retention_period_years': deletion_request.retention_period_years
                    }
                )
            except Exception as log_error:
                logger.warning(f'Failed to log data deletion: {str(log_error)}')
            
            logger.info(f'Successfully processed deletion request {deletion_request.id} for patient {patient.id}')
            stats['processed'] += 1
            
        except Exception as e:
            logger.error(
                f'Error processing deletion request {deletion_request.id}: {str(e)}',
                exc_info=True
            )
            stats['errors'] += 1
    
    logger.info(f'Deletion processing complete: {stats}')
    return stats


@shared_task(name='users.check_deletion_requests_ready')
def check_deletion_requests_ready():
    """
    Check for deletion requests that are now eligible for deletion
    
    Runs daily to:
    - Recalculate earliest_deletion_date for pending requests
    - Notify admins if requests are ready for approval
    
    Returns:
        dict: Statistics on requests checked
    """
    now = timezone.now()
    
    # Find pending requests that might be ready
    pending_requests = DataDeletionRequest.objects.filter(
        status=DataDeletionRequest.RequestStatus.PENDING
    ).select_related('patient')
    
    stats = {
        'checked': 0,
        'ready': 0,
        'not_ready': 0
    }
    
    for deletion_request in pending_requests:
        try:
            # Recalculate earliest deletion date
            deletion_request.calculate_earliest_deletion_date()
            deletion_request.save()
            
            if deletion_request.can_be_deleted_now():
                stats['ready'] += 1
                logger.info(
                    f'Deletion request {deletion_request.id} is now ready for approval. '
                    f'Patient: {deletion_request.patient.email}'
                )
            else:
                stats['not_ready'] += 1
            
            stats['checked'] += 1
            
        except Exception as e:
            logger.error(
                f'Error checking deletion request {deletion_request.id}: {str(e)}',
                exc_info=True
            )
    
    logger.info(f'Deletion request check complete: {stats}')
    return stats

