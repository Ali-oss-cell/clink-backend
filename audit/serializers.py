"""
Serializers for audit logs
"""

from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for audit log entries"""
    
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    content_type_name = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'timestamp', 'user', 'user_email', 'user_role',
            'action', 'action_display', 'content_type', 'content_type_name',
            'object_id', 'object_repr', 'changes', 'ip_address',
            'user_agent', 'request_path', 'request_method', 'metadata'
        ]
        read_only_fields = fields
    
    def get_content_type_name(self, obj):
        """Get content type name"""
        if obj.content_type:
            return obj.content_type.model
        return None

