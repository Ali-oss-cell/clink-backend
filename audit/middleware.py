"""
Middleware for audit logging
"""

from .utils import set_request


class AuditLoggingMiddleware:
    """
    Middleware to store request in thread local for audit logging
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Store request in thread local for use in signals/utils
        set_request(request)
        
        response = self.get_response(request)
        
        return response

