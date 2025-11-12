"""
Utility functions for audit logging
"""

from .models import AuditLog
from django.contrib.contenttypes.models import ContentType
import threading

_thread_locals = threading.local()


def get_request():
    """Get current request from thread local"""
    return getattr(_thread_locals, 'request', None)


def set_request(request):
    """Set current request in thread local"""
    _thread_locals.request = request


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_action(user=None, action='view', obj=None, changes=None, request=None, metadata=None):
    """
    Helper function to create audit log entries
    
    Args:
        user: User who performed the action
        action: Type of action (create, update, delete, view, etc.)
        obj: The object being acted upon
        changes: Dictionary of changes (for updates)
        request: HTTP request object (for IP, user agent, etc.)
        metadata: Additional metadata
    """
    # Get request from thread local if not provided
    if request is None:
        request = get_request()
    
    # Get content type
    content_type = None
    object_id = None
    object_repr = 'Unknown'
    
    if obj:
        try:
            content_type = ContentType.objects.get_for_model(obj)
            object_id = obj.pk
            object_repr = str(obj)
        except Exception:
            # If object is deleted or invalid, use provided representation
            object_repr = str(obj) if obj else 'Unknown'
    
    # Get user info
    user_email = None
    user_role = None
    
    if user:
        user_email = getattr(user, 'email', None)
        user_role = getattr(user, 'role', None)
    elif request and hasattr(request, 'user') and request.user.is_authenticated:
        user = request.user
        user_email = getattr(user, 'email', None)
        user_role = getattr(user, 'role', None)
    
    # Get request info
    ip_address = None
    user_agent = None
    request_path = None
    request_method = None
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limit length
        request_path = request.path[:500]  # Limit length
        request_method = request.method
    
    # Create audit log
    try:
        AuditLog.objects.create(
            user=user,
            user_email=user_email,
            user_role=user_role,
            action=action,
            content_type=content_type,
            object_id=object_id,
            object_repr=object_repr,
            changes=changes or {},
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            request_method=request_method,
            metadata=metadata or {}
        )
    except Exception as e:
        # Don't break the application if logging fails
        # In production, you might want to log this to a separate error log
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create audit log: {str(e)}")

