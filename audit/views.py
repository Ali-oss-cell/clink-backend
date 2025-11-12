"""
Views for audit logs API
"""

from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View audit logs - Admin only
    Endpoint: GET /api/audit/logs/
    """
    queryset = AuditLog.objects.select_related('user', 'content_type').all()
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
        # Last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_logs = self.queryset.filter(timestamp__gte=thirty_days_ago)
        
        # Actions by type
        actions_by_type = {}
        for action_type, count in recent_logs.values('action').annotate(
            count=Count('id')
        ).values_list('action', 'count'):
            actions_by_type[action_type] = count
        
        # Actions by role
        actions_by_role = {}
        for role, count in recent_logs.exclude(user_role__isnull=True).values('user_role').annotate(
            count=Count('id')
        ).values_list('user_role', 'count'):
            actions_by_role[role] = count
        
        stats = {
            'total_logs': self.queryset.count(),
            'recent_logs_30_days': recent_logs.count(),
            'actions_by_type': actions_by_type,
            'actions_by_role': actions_by_role,
        }
        
        return Response(stats)
