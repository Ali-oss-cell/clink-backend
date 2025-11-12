"""
Audit logging models for tracking system actions
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import json

User = get_user_model()


class AuditLog(models.Model):
    """
    Audit log for tracking all important system actions
    
    Records who did what, when, and what changed for compliance and security.
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
            models.Index(fields=['user_email']),
        ]
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
    
    def __str__(self):
        return f"{self.user_email or 'Anonymous'} - {self.get_action_display()} - {self.object_repr} - {self.timestamp}"
