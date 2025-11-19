"""
Celery configuration for psychology_clinic project.

This module configures Celery for handling background tasks like:
- Sending WhatsApp appointment reminders
- Processing payment notifications
- Generating reports
- Email notifications
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')

app = Celery('psychology_clinic')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for recurring tasks
app.conf.beat_schedule = {
    'send-appointment-reminders': {
        'task': 'appointments.tasks.send_appointment_reminders',
        'schedule': 3600.0,  # Run every hour
    },
    'process-payment-notifications': {
        'task': 'billing.tasks.process_pending_payments',
        'schedule': 1800.0,  # Run every 30 minutes
    },
    'cleanup-expired-sessions': {
        'task': 'core.tasks.cleanup_expired_sessions',
        'schedule': 86400.0,  # Run daily
    },
    'check-ahpra-expiry': {
        'task': 'appointments.tasks.check_ahpra_expiry',
        'schedule': 2592000.0,  # Run monthly (30 days = 2,592,000 seconds)
    },
    'check-insurance-expiry': {
        'task': 'appointments.tasks.check_insurance_expiry',
        'schedule': 2592000.0,  # Run monthly (30 days = 2,592,000 seconds)
    },
    'process-approved-deletion-requests': {
        'task': 'users.tasks.process_approved_deletion_requests',
        'schedule': 86400.0,  # Run daily (24 hours = 86,400 seconds)
    },
    'check-deletion-requests-ready': {
        'task': 'users.tasks.check_deletion_requests_ready',
        'schedule': 86400.0,  # Run daily (24 hours = 86,400 seconds)
    },
}

app.conf.timezone = settings.TIME_ZONE

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
