"""
Rate limiting middleware and utilities for API protection
Protects against abuse and ensures system stability
"""

from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
from audit.utils import log_action
import time
import logging

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass


class RateLimiter:
    """
    Rate limiter with configurable limits for different actions
    Uses Django cache backend (Redis recommended for production)
    """
    
    # Default rate limits (requests per time period)
    LIMITS = {
        # Authentication endpoints
        'login': {'limit': 5, 'period': 300},  # 5 attempts per 5 minutes
        'register': {'limit': 3, 'period': 3600},  # 3 registrations per hour
        'password_reset': {'limit': 3, 'period': 3600},  # 3 resets per hour
        
        # API endpoints
        'api_general': {'limit': 100, 'period': 60},  # 100 requests per minute
        'api_heavy': {'limit': 20, 'period': 60},  # 20 heavy requests per minute
        
        # Messaging endpoints
        'send_message': {'limit': 10, 'period': 3600},  # 10 messages per hour
        'whatsapp_send': {'limit': 10, 'period': 3600},  # 10 WhatsApp per hour
        
        # Booking endpoints
        'book_appointment': {'limit': 5, 'period': 300},  # 5 bookings per 5 minutes
        
        # Payment endpoints
        'payment_process': {'limit': 5, 'period': 300},  # 5 payments per 5 minutes
    }
    
    @classmethod
    def get_cache_key(cls, identifier: str, action: str) -> str:
        """Generate cache key for rate limiting"""
        return f"rate_limit:{action}:{identifier}"
    
    @classmethod
    def check_rate_limit(cls, identifier: str, action: str = 'api_general') -> dict:
        """
        Check if action is within rate limit
        
        Args:
            identifier: Unique identifier (IP address, user ID, etc.)
            action: Action type (maps to LIMITS)
        
        Returns:
            dict: {'allowed': bool, 'remaining': int, 'reset_in': int}
        
        Raises:
            RateLimitExceeded: If limit is exceeded
        """
        # Get limit configuration
        limit_config = cls.LIMITS.get(action, cls.LIMITS['api_general'])
        max_requests = limit_config['limit']
        time_period = limit_config['period']
        
        # Get cache key
        cache_key = cls.get_cache_key(identifier, action)
        
        # Get current count
        current_count = cache.get(cache_key, 0)
        
        # Check limit
        if current_count >= max_requests:
            # Get TTL for reset time
            ttl = cache.ttl(cache_key)
            if ttl is None or ttl < 0:
                # Key expired or doesn't exist, reset
                current_count = 0
                cache.set(cache_key, 1, time_period)
                return {
                    'allowed': True,
                    'remaining': max_requests - 1,
                    'reset_in': time_period
                }
            
            logger.warning(f"Rate limit exceeded for {identifier} on {action}")
            
            return {
                'allowed': False,
                'remaining': 0,
                'reset_in': ttl,
                'limit': max_requests,
                'period': time_period
            }
        
        # Increment counter
        new_count = current_count + 1
        if current_count == 0:
            # First request, set with expiry
            cache.set(cache_key, new_count, time_period)
            reset_in = time_period
        else:
            # Increment existing counter
            cache.incr(cache_key)
            # Get TTL
            ttl = cache.ttl(cache_key)
            reset_in = ttl if ttl and ttl > 0 else time_period
        
        return {
            'allowed': True,
            'remaining': max_requests - new_count,
            'reset_in': reset_in,
            'limit': max_requests,
            'period': time_period
        }
    
    @classmethod
    def reset_limit(cls, identifier: str, action: str):
        """Reset rate limit for identifier and action"""
        cache_key = cls.get_cache_key(identifier, action)
        cache.delete(cache_key)


class RateLimitMiddleware:
    """
    Middleware for global API rate limiting
    Applies rate limits to all API endpoints
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Paths to exclude from rate limiting
        self.exclude_paths = [
            '/admin/',
            '/static/',
            '/media/',
            '/api/auth/token/refresh/',  # Allow token refresh
        ]
    
    def __call__(self, request):
        # Check if path should be rate limited
        if any(request.path.startswith(path) for path in self.exclude_paths):
            return self.get_response(request)
        
        # Only rate limit API endpoints
        if not request.path.startswith('/api/'):
            return self.get_response(request)
        
        # Get identifier (user ID or IP)
        if hasattr(request, 'user') and request.user.is_authenticated:
            identifier = f"user:{request.user.id}"
            # Staff users get higher limits
            if request.user.role in ['admin', 'practice_manager', 'psychologist']:
                action = 'api_heavy'  # Higher limit for staff
            else:
                action = 'api_general'
        else:
            # Anonymous user, use IP
            identifier = self._get_client_ip(request)
            action = 'api_general'
        
        # Check rate limit
        try:
            rate_check = RateLimiter.check_rate_limit(identifier, action)
            
            if not rate_check['allowed']:
                # Log rate limit violation
                log_action(
                    user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                    action='rate_limit_exceeded',
                    request=request,
                    metadata={
                        'identifier': identifier,
                        'action': action,
                        'reset_in': rate_check['reset_in']
                    }
                )
                
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'detail': f"Too many requests. Please try again in {rate_check['reset_in']} seconds.",
                    'retry_after': rate_check['reset_in']
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Add rate limit headers to response
            response = self.get_response(request)
            response['X-RateLimit-Limit'] = rate_check['limit']
            response['X-RateLimit-Remaining'] = rate_check['remaining']
            response['X-RateLimit-Reset'] = rate_check['reset_in']
            
            return response
            
        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            # Don't block request if rate limiting fails
            return self.get_response(request)
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


def rate_limit_decorator(action: str = 'api_general'):
    """
    Decorator for rate limiting specific views
    
    Usage:
        @rate_limit_decorator('login')
        def login_view(request):
            ...
    """
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            # Get identifier
            if hasattr(request, 'user') and request.user.is_authenticated:
                identifier = f"user:{request.user.id}"
            else:
                # Use IP
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    identifier = x_forwarded_for.split(',')[0].strip()
                else:
                    identifier = request.META.get('REMOTE_ADDR')
            
            # Check rate limit
            rate_check = RateLimiter.check_rate_limit(identifier, action)
            
            if not rate_check['allowed']:
                # Log violation
                log_action(
                    user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                    action='rate_limit_exceeded',
                    request=request,
                    metadata={
                        'identifier': identifier,
                        'action': action,
                        'reset_in': rate_check['reset_in']
                    }
                )
                
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'detail': f"Too many {action} attempts. Please try again in {rate_check['reset_in']} seconds.",
                    'retry_after': rate_check['reset_in']
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Call original function
            response = func(request, *args, **kwargs)
            
            # Add rate limit headers if it's a JsonResponse or Response
            if hasattr(response, '__setitem__'):
                response['X-RateLimit-Limit'] = rate_check['limit']
                response['X-RateLimit-Remaining'] = rate_check['remaining']
                response['X-RateLimit-Reset'] = rate_check['reset_in']
            
            return response
        
        return wrapper
    return decorator

