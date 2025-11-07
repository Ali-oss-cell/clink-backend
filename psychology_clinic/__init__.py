# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
# Make Celery import optional - server can run without it
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery is not installed - server can still run
    celery_app = None
    __all__ = ()
