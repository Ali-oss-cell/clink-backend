from django.contrib import admin
from django.utils import timezone
from .models import PatientProfile, ProgressNote, DataDeletionRequest


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_name', 'intake_completed', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'preferred_name']
    list_filter = ['intake_completed', 'created_at']


@admin.register(ProgressNote)
class ProgressNoteAdmin(admin.ModelAdmin):
    list_display = ['patient', 'psychologist', 'session_date', 'session_number', 'created_at']
    search_fields = ['patient__email', 'psychologist__email']
    list_filter = ['session_date', 'created_at']
    date_hierarchy = 'session_date'


@admin.register(DataDeletionRequest)
class DataDeletionRequestAdmin(admin.ModelAdmin):
    """Admin interface for data deletion requests (APP 13)"""
    
    list_display = [
        'id', 'patient', 'request_date', 'status', 
        'earliest_deletion_date', 'scheduled_deletion_date', 
        'reviewed_by', 'reviewed_date'
    ]
    list_filter = [
        'status', 'request_date', 'reviewed_date',
        'rejection_reason', 'retention_period_years'
    ]
    search_fields = [
        'patient__email', 'patient__first_name', 'patient__last_name',
        'reason', 'rejection_notes', 'notes'
    ]
    readonly_fields = [
        'request_date', 'earliest_deletion_date', 'created_at', 'updated_at',
        'deletion_completed_date'
    ]
    date_hierarchy = 'request_date'
    
    fieldsets = (
        ('Patient Information', {
            'fields': ('patient',)
        }),
        ('Request Details', {
            'fields': ('request_date', 'reason', 'status')
        }),
        ('Review Information', {
            'fields': (
                'reviewed_by', 'reviewed_date', 
                'rejection_reason', 'rejection_notes', 'notes'
            )
        }),
        ('Deletion Schedule', {
            'fields': (
                'retention_period_years', 'earliest_deletion_date',
                'scheduled_deletion_date', 'deletion_completed_date'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        """Bulk approve deletion requests"""
        count = 0
        for deletion_request in queryset.filter(status=DataDeletionRequest.RequestStatus.PENDING):
            if deletion_request.can_be_deleted_now():
                deletion_request.status = DataDeletionRequest.RequestStatus.APPROVED
                deletion_request.reviewed_by = request.user
                deletion_request.reviewed_date = timezone.now()
                deletion_request.scheduled_deletion_date = timezone.now()
                deletion_request.save()
                count += 1
        self.message_user(request, f'{count} deletion request(s) approved.')
    approve_requests.short_description = 'Approve selected deletion requests'
    
    def reject_requests(self, request, queryset):
        """Bulk reject deletion requests"""
        count = queryset.filter(status=DataDeletionRequest.RequestStatus.PENDING).update(
            status=DataDeletionRequest.RequestStatus.REJECTED,
            reviewed_by=request.user,
            reviewed_date=timezone.now(),
            rejection_reason=DataDeletionRequest.RejectionReason.OTHER
        )
        self.message_user(request, f'{count} deletion request(s) rejected.')
    reject_requests.short_description = 'Reject selected deletion requests'
