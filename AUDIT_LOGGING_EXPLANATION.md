# 📋 Audit Logging - Explanation & Implementation Guide

## What is Audit Logging?

**Audit logging** is a system that records **who did what, when, and what changed** in your application. It's like a security camera for your database - tracking all important actions for:

- ✅ **Compliance** - Healthcare regulations (AHPRA, Medicare) require audit trails
- ✅ **Security** - Detect unauthorized access or suspicious activity
- ✅ **Accountability** - Know who made changes and when
- ✅ **Debugging** - Track down issues by seeing what happened
- ✅ **Legal Protection** - Evidence of actions taken

---

## 🎯 What Should Be Logged?

### **Critical Actions to Track:**

#### **1. User Management Actions**
- ✅ User creation (who created which user)
- ✅ User updates (what fields changed)
- ✅ User deletion (who deleted which user)
- ✅ Role changes (who changed user roles)
- ✅ Password changes
- ✅ Email verification status changes
- ✅ Account activation/deactivation

#### **2. Appointment Actions**
- ✅ Appointment booking (who booked, when, with whom)
- ✅ Appointment cancellation (who cancelled, reason)
- ✅ Appointment rescheduling (old time → new time)
- ✅ Appointment status changes (scheduled → completed)
- ✅ Progress notes creation/editing (who wrote what)

#### **3. Billing Actions**
- ✅ Invoice creation (who created, for which patient)
- ✅ Invoice updates (amount changes, status changes)
- ✅ Payment processing (who paid, how much, when)
- ✅ Medicare claim creation
- ✅ Refund processing

#### **4. Patient Data Actions**
- ✅ Intake form submissions
- ✅ Patient profile updates (sensitive health data)
- ✅ Progress notes access (who viewed patient notes)
- ✅ Medical record changes

#### **5. System Actions**
- ✅ Login attempts (successful and failed)
- ✅ Logout events
- ✅ Settings changes (who changed system settings)
- ✅ Resource creation/editing/deletion
- ✅ Psychologist profile updates

#### **6. Security Events**
- ✅ Failed login attempts
- ✅ Permission denied errors
- ✅ Unauthorized access attempts
- ✅ Token refresh events

---

## 📍 Where to Put Audit Logs

### **Option 1: Separate Audit Log App** (Recommended)

Create a new Django app called `audit` or `logging`:

```
clink-backend/
├── audit/                    # New app
│   ├── __init__.py
│   ├── models.py            # AuditLog model
│   ├── admin.py             # Admin interface
│   ├── signals.py           # Auto-logging via signals
│   ├── middleware.py        # Request logging
│   └── utils.py             # Helper functions
```

### **Option 2: Add to Core App**

Add audit logging to the existing `core` app:

```
clink-backend/
├── core/
│   ├── models.py            # Add AuditLog model here
│   ├── signals.py           # Add signals here
│   └── middleware.py        # Add middleware here
```

---

## 🏗️ Implementation Structure

### **1. Audit Log Model**

```python
# audit/models.py or core/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import json

User = get_user_model()


class AuditLog(models.Model):
    """
    Audit log for tracking all important system actions
    """
    
    class ActionType(models.TextChoices):
        CREATE = 'create', 'Create'
        UPDATE = 'update', 'Update'
        DELETE = 'delete', 'Delete'
        VIEW = 'view', 'View'
        LOGIN = 'login', 'Login'
        LOGOUT = 'logout', 'Logout'
        DOWNLOAD = 'download', 'Download'
        EXPORT = 'export', 'Export'
    
    # Who did it
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text="User who performed the action"
    )
    user_email = models.EmailField(
        null=True,
        blank=True,
        help_text="User email (stored even if user is deleted)"
    )
    user_role = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text="User role at time of action"
    )
    
    # What action
    action = models.CharField(
        max_length=20,
        choices=ActionType.choices,
        help_text="Type of action performed"
    )
    
    # What model/object
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Model type (User, Appointment, Invoice, etc.)"
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="ID of the object"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Object details
    object_repr = models.CharField(
        max_length=255,
        help_text="String representation of the object"
    )
    
    # What changed
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="What fields changed (before/after values)"
    )
    
    # Additional info
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the user"
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        help_text="Browser/user agent information"
    )
    request_path = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text="API endpoint or URL accessed"
    )
    request_method = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="HTTP method (GET, POST, PUT, DELETE)"
    )
    
    # When
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When the action occurred"
    )
    
    # Additional metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context (error messages, etc.)"
    )
    
    class Meta:
        db_table = 'audit_log'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user_email or 'Anonymous'} - {self.action} - {self.object_repr} - {self.timestamp}"
```

---

## 🔧 How to Use Audit Logging

### **Method 1: Manual Logging in Views**

```python
# users/views.py

from audit.models import AuditLog
from audit.utils import log_action

class UserViewSet(viewsets.ModelViewSet):
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        # Log the action
        log_action(
            user=request.user,
            action='create',
            obj=response.data,
            changes={'created': response.data},
            request=request
        )
        
        return response
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {
            'email': instance.email,
            'role': instance.role,
            'is_active': instance.is_active,
        }
        
        response = super().update(request, *args, **kwargs)
        
        instance.refresh_from_db()
        new_data = {
            'email': instance.email,
            'role': instance.role,
            'is_active': instance.is_active,
        }
        
        # Calculate changes
        changes = {}
        for key in old_data:
            if old_data[key] != new_data[key]:
                changes[key] = {
                    'old': old_data[key],
                    'new': new_data[key]
                }
        
        # Log the action
        if changes:
            log_action(
                user=request.user,
                action='update',
                obj=instance,
                changes=changes,
                request=request
            )
        
        return response
```

### **Method 2: Django Signals (Automatic)**

```python
# audit/signals.py

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from audit.models import AuditLog
from audit.utils import log_action

@receiver(post_save, sender='users.User')
def log_user_changes(sender, instance, created, **kwargs):
    """Automatically log user changes"""
    action = 'create' if created else 'update'
    
    # Get request from thread local (if available)
    from audit.middleware import get_request
    request = get_request()
    
    log_action(
        user=request.user if request and request.user.is_authenticated else None,
        action=action,
        obj=instance,
        request=request
    )

@receiver(post_delete, sender='users.User')
def log_user_deletion(sender, instance, **kwargs):
    """Log user deletion"""
    from audit.middleware import get_request
    request = get_request()
    
    log_action(
        user=request.user if request and request.user.is_authenticated else None,
        action='delete',
        obj=instance,
        request=request
    )
```

### **Method 3: Middleware (Request Logging)**

```python
# audit/middleware.py

from audit.models import AuditLog
from audit.utils import log_action
import threading

_thread_locals = threading.local()

def get_request():
    """Get current request from thread local"""
    return getattr(_thread_locals, 'request', None)

class AuditLoggingMiddleware:
    """Middleware to log all requests"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Store request in thread local
        _thread_locals.request = request
        
        # Log login attempts
        if request.path == '/api/auth/login/' and request.method == 'POST':
            # Will be logged after successful login in view
            pass
        
        response = self.get_response(request)
        
        # Log important actions
        if request.user.is_authenticated:
            # Log view actions for sensitive data
            if 'appointments' in request.path and request.method == 'GET':
                # Log appointment views
                pass
        
        return response
```

### **Helper Function**

```python
# audit/utils.py

from .models import AuditLog
from django.contrib.contenttypes.models import ContentType

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
    # Get content type
    content_type = None
    object_id = None
    object_repr = str(obj) if obj else None
    
    if obj:
        content_type = ContentType.objects.get_for_model(obj)
        object_id = obj.pk
    
    # Get user info
    user_email = user.email if user else None
    user_role = user.role if user and hasattr(user, 'role') else None
    
    # Get request info
    ip_address = None
    user_agent = None
    request_path = None
    request_method = None
    
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        request_path = request.path
        request_method = request.method
    
    # Create audit log
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

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

---

## 📊 Where to Track Specific Actions

### **1. User Management** (`users/views.py`)

```python
# Log in UserViewSet methods:
- create() → log_action(action='create', obj=user)
- update() → log_action(action='update', obj=user, changes={...})
- destroy() → log_action(action='delete', obj=user)
```

### **2. Appointments** (`appointments/views.py`)

```python
# Log in booking_views.py:
- BookAppointmentEnhancedView → log_action(action='create', obj=appointment)
- CancelAppointmentView → log_action(action='update', obj=appointment, changes={'status': 'cancelled'})
- CompleteSessionView → log_action(action='update', obj=appointment, changes={'status': 'completed'})
```

### **3. Billing** (`billing/views.py`)

```python
# Log in InvoiceViewSet:
- create() → log_action(action='create', obj=invoice)
- update() → log_action(action='update', obj=invoice, changes={...})
- create_medicare_claim() → log_action(action='create', obj=claim)
```

### **4. Login/Logout** (`users/views.py`)

```python
# Log in login view:
- LoginView → log_action(action='login', user=user)
- LogoutView → log_action(action='logout', user=user)
```

### **5. Progress Notes** (`users/patient_models.py`)

```python
# Log via signals:
- post_save → log_action(action='create' or 'update', obj=progress_note)
- post_delete → log_action(action='delete', obj=progress_note)
```

---

## 🔍 Querying Audit Logs

### **1. Django Admin Interface** ✅ (Admins can check here)

```python
# audit/admin.py

from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for viewing audit logs - Admin only"""
    
    list_display = ['timestamp', 'user_email', 'user_role', 'action', 'object_repr', 'ip_address']
    list_filter = ['action', 'timestamp', 'user_role', 'content_type']
    search_fields = ['user_email', 'object_repr', 'request_path', 'ip_address']
    readonly_fields = [
        'timestamp', 'user', 'user_email', 'user_role', 'action', 
        'content_type', 'object_id', 'object_repr', 'changes', 
        'ip_address', 'user_agent', 'request_path', 'request_method', 'metadata'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    # Only admins can view
    def has_add_permission(self, request):
        return False  # Prevent manual creation
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing (logs are read-only)
    
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete logs (for compliance)
        return request.user.is_superuser
```

**How Admins Access:**
1. Go to Django Admin: `http://localhost:8000/admin/`
2. Login as admin
3. Click on **"Audit Logs"** in the sidebar
4. View, search, and filter all audit logs

**Features:**
- ✅ View all actions (create, update, delete, login, etc.)
- ✅ Filter by action type, user role, date
- ✅ Search by user email, object name, IP address
- ✅ See what changed (before/after values)
- ✅ View IP addresses and browser info
- ✅ Export logs (via admin actions)

### **2. API Endpoint** ✅ (Admins can check via API/Frontend)

```python
# audit/views.py

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View audit logs - Admin only
    Endpoint: GET /api/audit/logs/
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser]  # Only admins can access
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'user_role', 'content_type']
    search_fields = ['user_email', 'object_repr', 'request_path', 'ip_address']
    ordering_fields = ['timestamp', 'user_email', 'action']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        queryset = AuditLog.objects.select_related('user', 'content_type').all()
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by action
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get audit log statistics"""
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        # Last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_logs = self.queryset.filter(timestamp__gte=thirty_days_ago)
        
        stats = {
            'total_logs': self.queryset.count(),
            'recent_logs_30_days': recent_logs.count(),
            'actions_by_type': dict(
                recent_logs.values('action').annotate(count=Count('id')).values_list('action', 'count')
            ),
            'actions_by_role': dict(
                recent_logs.values('user_role').annotate(count=Count('id')).values_list('user_role', 'count')
            ),
        }
        
        return Response(stats)
```

**API Endpoints:**
- `GET /api/audit/logs/` - List all audit logs (Admin only)
- `GET /api/audit/logs/{id}/` - Get single audit log (Admin only)
- `GET /api/audit/logs/stats/` - Get statistics (Admin only)

**Query Parameters:**
- `?user_id=1` - Filter by user
- `?action=update` - Filter by action type
- `?start_date=2024-01-01` - Filter by date range
- `?end_date=2024-01-31`
- `?search=john@example.com` - Search by email, object name, IP
- `?ordering=-timestamp` - Sort by timestamp

**Frontend Usage:**
```typescript
// Admin dashboard can show audit logs
const response = await fetch('/api/audit/logs/?action=update&start_date=2024-01-01', {
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});

const logs = await response.json();
// Display in admin audit log page
```

---

## ✅ Summary

### **What to Log:**
- ✅ User management (create, update, delete)
- ✅ Appointment actions (book, cancel, complete)
- ✅ Billing actions (invoice, payment, claims)
- ✅ Patient data access (view, edit)
- ✅ Login/logout events
- ✅ System settings changes

### **Where to Put It:**
- ✅ **New app**: `audit/` (recommended)
- ✅ **Or**: Add to `core/` app

### **How to Implement:**
- ✅ **Manual**: Call `log_action()` in views
- ✅ **Automatic**: Use Django signals
- ✅ **Middleware**: Log all requests

### **Priority:**
- ⚠️ **Medium Priority** - Important for compliance but not blocking production

---

**This provides a complete audit trail for compliance and security!** 🔒

