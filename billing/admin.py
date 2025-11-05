"""
Billing admin for Psychology Clinic
Australian Medicare integration and payment management
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal

from .models import (
    MedicareItemNumber,
    Invoice,
    MedicareClaim,
    Payment,
    MedicareSafetyNet
)


@admin.register(MedicareItemNumber)
class MedicareItemNumberAdmin(admin.ModelAdmin):
    """Admin for Medicare item numbers"""
    
    list_display = [
        'item_number',
        'description',
        'service_type',
        'standard_rebate',
        'safety_net_rebate',
        'requires_referral',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'service_type',
        'requires_referral',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'item_number',
        'description'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'item_number',
                'description',
                'service_type',
                'is_active'
            )
        }),
        ('Rebate Information', {
            'fields': (
                'standard_rebate',
                'safety_net_rebate'
            )
        }),
        ('Requirements', {
            'fields': (
                'min_session_duration',
                'max_sessions_per_year',
                'requires_referral'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin for invoices"""
    
    list_display = [
        'invoice_number',
        'patient_name',
        'appointment_link',
        'service_date',
        'total_amount',
        'medicare_rebate',
        'out_of_pocket',
        'status',
        'is_overdue',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'service_date',
        'created_at',
        'appointment__psychologist'
    ]
    
    search_fields = [
        'invoice_number',
        'patient__first_name',
        'patient__last_name',
        'patient__email'
    ]
    
    readonly_fields = [
        'invoice_number',
        'gst_amount',
        'total_amount',
        'out_of_pocket',
        'is_overdue',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': (
                'invoice_number',
                'patient',
                'appointment',
                'service_description',
                'service_date'
            )
        }),
        ('Financial Details', {
            'fields': (
                'subtotal_amount',
                'gst_amount',
                'total_amount',
                'medicare_rebate',
                'out_of_pocket'
            )
        }),
        ('Medicare Information', {
            'fields': (
                'medicare_item_number',
            )
        }),
        ('Status & Dates', {
            'fields': (
                'status',
                'due_date',
                'paid_date',
                'is_overdue'
            )
        }),
        ('Business Details', {
            'fields': (
                'abn',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def patient_name(self, obj):
        """Display patient name"""
        return obj.patient.get_full_name()
    patient_name.short_description = 'Patient'
    
    def appointment_link(self, obj):
        """Link to appointment"""
        if obj.appointment:
            url = reverse('admin:appointments_appointment_change', args=[obj.appointment.id])
            return format_html('<a href="{}">Appointment {}</a>', url, obj.appointment.id)
        return '-'
    appointment_link.short_description = 'Appointment'
    
    def is_overdue(self, obj):
        """Display overdue status"""
        if obj.is_overdue:
            return format_html('<span style="color: red;">Overdue</span>')
        return 'No'
    is_overdue.short_description = 'Overdue'
    is_overdue.boolean = True


@admin.register(MedicareClaim)
class MedicareClaimAdmin(admin.ModelAdmin):
    """Admin for Medicare claims"""
    
    list_display = [
        'claim_number',
        'patient_name',
        'invoice_link',
        'medicare_number',
        'item_number',
        'service_fee',
        'medicare_rebate',
        'patient_payment',
        'status',
        'claim_date',
        'processed_date'
    ]
    
    list_filter = [
        'status',
        'bulk_billing',
        'safety_net_applied',
        'claim_date',
        'processed_date'
    ]
    
    search_fields = [
        'claim_number',
        'patient__first_name',
        'patient__last_name',
        'medicare_number',
        'medicare_reference'
    ]
    
    readonly_fields = [
        'claim_number',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Claim Information', {
            'fields': (
                'claim_number',
                'invoice',
                'patient',
                'medicare_number'
            )
        }),
        ('Medicare Details', {
            'fields': (
                'medicare_item_number',
                'service_fee',
                'medicare_rebate',
                'patient_payment'
            )
        }),
        ('Status & Processing', {
            'fields': (
                'status',
                'claim_date',
                'processed_date',
                'medicare_reference',
                'rejection_reason'
            )
        }),
        ('Australian Compliance', {
            'fields': (
                'bulk_billing',
                'safety_net_applied'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def patient_name(self, obj):
        """Display patient name"""
        return obj.patient.get_full_name()
    patient_name.short_description = 'Patient'
    
    def invoice_link(self, obj):
        """Link to invoice"""
        if obj.invoice:
            url = reverse('admin:billing_invoice_change', args=[obj.invoice.id])
            return format_html('<a href="{}">Invoice {}</a>', url, obj.invoice.invoice_number)
        return '-'
    invoice_link.short_description = 'Invoice'
    
    def item_number(self, obj):
        """Display Medicare item number"""
        return obj.medicare_item_number.item_number
    item_number.short_description = 'Item Number'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin for payments"""
    
    list_display = [
        'payment_id',
        'patient_name',
        'invoice_link',
        'amount',
        'payment_method',
        'status',
        'processed_at',
        'created_at'
    ]
    
    list_filter = [
        'payment_method',
        'status',
        'processed_at',
        'created_at'
    ]
    
    search_fields = [
        'payment_id',
        'patient__first_name',
        'patient__last_name',
        'invoice__invoice_number',
        'stripe_payment_intent_id',
        'bank_reference'
    ]
    
    readonly_fields = [
        'payment_id',
        'processed_at',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'payment_id',
                'invoice',
                'patient',
                'amount',
                'payment_method',
                'status'
            )
        }),
        ('External References', {
            'fields': (
                'stripe_payment_intent_id',
                'stripe_charge_id',
                'bank_reference',
                'medicare_claim'
            )
        }),
        ('Processing', {
            'fields': (
                'processed_at',
                'failure_reason'
            )
        }),
        ('Australian Compliance', {
            'fields': (
                'gst_amount',
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def patient_name(self, obj):
        """Display patient name"""
        return obj.patient.get_full_name()
    patient_name.short_description = 'Patient'
    
    def invoice_link(self, obj):
        """Link to invoice"""
        if obj.invoice:
            url = reverse('admin:billing_invoice_change', args=[obj.invoice.id])
            return format_html('<a href="{}">Invoice {}</a>', url, obj.invoice.invoice_number)
        return '-'
    invoice_link.short_description = 'Invoice'


@admin.register(MedicareSafetyNet)
class MedicareSafetyNetAdmin(admin.ModelAdmin):
    """Admin for Medicare Safety Net tracking"""
    
    list_display = [
        'patient_name',
        'calendar_year',
        'total_medical_expenses',
        'medicare_rebates_received',
        'safety_net_threshold',
        'is_safety_net_eligible',
        'safety_net_date',
        'remaining_to_threshold'
    ]
    
    list_filter = [
        'calendar_year',
        'is_safety_net_eligible',
        'safety_net_date'
    ]
    
    search_fields = [
        'patient__first_name',
        'patient__last_name',
        'patient__email'
    ]
    
    readonly_fields = [
        'is_safety_net_eligible',
        'safety_net_date',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Patient Information', {
            'fields': (
                'patient',
                'calendar_year'
            )
        }),
        ('Expense Tracking', {
            'fields': (
                'total_medical_expenses',
                'medicare_rebates_received',
                'safety_net_threshold'
            )
        }),
        ('Safety Net Status', {
            'fields': (
                'is_safety_net_eligible',
                'safety_net_date'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def patient_name(self, obj):
        """Display patient name"""
        return obj.patient.get_full_name()
    patient_name.short_description = 'Patient'
    
    def remaining_to_threshold(self, obj):
        """Calculate remaining amount to threshold"""
        remaining = obj.safety_net_threshold - obj.total_medical_expenses
        return f"${max(Decimal('0.00'), remaining):.2f}"
    remaining_to_threshold.short_description = 'Remaining to Threshold'


# Custom admin actions
@admin.action(description='Mark selected invoices as paid')
def mark_invoices_paid(modeladmin, request, queryset):
    """Mark selected invoices as paid"""
    updated = queryset.update(
        status=Invoice.InvoiceStatus.PAID,
        paid_date=timezone.now().date()
    )
    modeladmin.message_user(request, f'{updated} invoices marked as paid.')


@admin.action(description='Submit selected claims to Medicare')
def submit_claims_to_medicare(modeladmin, request, queryset):
    """Submit selected claims to Medicare"""
    claims = queryset.filter(status=MedicareClaim.ClaimStatus.PENDING)
    updated = claims.update(
        status=MedicareClaim.ClaimStatus.SUBMITTED,
        claim_date=timezone.now().date()
    )
    modeladmin.message_user(request, f'{updated} claims submitted to Medicare.')


# Add actions to admin classes
InvoiceAdmin.actions = [mark_invoices_paid]
MedicareClaimAdmin.actions = [submit_claims_to_medicare]