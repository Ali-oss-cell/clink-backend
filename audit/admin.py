"""
Admin configuration for audit logs
"""

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
    
    fieldsets = (
        ('Action Information', {
            'fields': ('timestamp', 'action', 'user', 'user_email', 'user_role')
        }),
        ('Object Information', {
            'fields': ('content_type', 'object_id', 'object_repr')
        }),
        ('Changes', {
            'fields': ('changes',),
            'classes': ('collapse',)
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent', 'request_path', 'request_method'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent manual creation of audit logs"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing of audit logs (they are read-only)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete logs (for compliance)"""
        return request.user.is_superuser
