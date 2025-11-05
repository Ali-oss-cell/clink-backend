"""
Billing serializers for Psychology Clinic
Australian Medicare integration and payment processing
"""

from rest_framework import serializers
from decimal import Decimal
from .models import (
    MedicareItemNumber,
    Invoice,
    MedicareClaim,
    Payment,
    MedicareSafetyNet
)


class MedicareItemNumberSerializer(serializers.ModelSerializer):
    """Serializer for Medicare item numbers"""
    
    class Meta:
        model = MedicareItemNumber
        fields = [
            'id',
            'item_number',
            'description',
            'service_type',
            'standard_rebate',
            'safety_net_rebate',
            'min_session_duration',
            'max_sessions_per_year',
            'requires_referral',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoices with Medicare integration"""
    
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    patient_email = serializers.CharField(source='patient.email', read_only=True)
    patient_medicare_number = serializers.CharField(source='patient.medicare_number', read_only=True)
    appointment_date = serializers.DateTimeField(source='appointment.appointment_date', read_only=True)
    psychologist_name = serializers.CharField(source='appointment.psychologist.get_full_name', read_only=True)
    medicare_item_description = serializers.CharField(source='medicare_item_number.description', read_only=True)
    
    # Calculated fields
    gst_percentage = serializers.SerializerMethodField()
    medicare_coverage_percentage = serializers.SerializerMethodField()
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Invoice
        fields = [
            'id',
            'invoice_number',
            'patient',
            'patient_name',
            'patient_email',
            'patient_medicare_number',
            'appointment',
            'appointment_date',
            'psychologist_name',
            'service_description',
            'service_date',
            'subtotal_amount',
            'gst_amount',
            'gst_percentage',
            'total_amount',
            'medicare_item_number',
            'medicare_item_description',
            'medicare_rebate',
            'medicare_coverage_percentage',
            'out_of_pocket',
            'status',
            'due_date',
            'paid_date',
            'is_overdue',
            'abn',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'invoice_number',
            'gst_amount',
            'total_amount',
            'out_of_pocket',
            'is_overdue',
            'created_at',
            'updated_at'
        ]
    
    def get_gst_percentage(self, obj):
        """Get GST percentage (10% in Australia)"""
        return float(obj.GST_RATE * 100)
    
    def get_medicare_coverage_percentage(self, obj):
        """Calculate Medicare coverage percentage"""
        if obj.total_amount > 0:
            return float((obj.medicare_rebate / obj.total_amount) * 100)
        return 0.0
    
    def validate_subtotal_amount(self, value):
        """Validate subtotal amount"""
        if value < Decimal('0.00'):
            raise serializers.ValidationError("Subtotal amount cannot be negative")
        return value
    
    def validate_medicare_rebate(self, value):
        """Validate Medicare rebate amount"""
        if value < Decimal('0.00'):
            raise serializers.ValidationError("Medicare rebate cannot be negative")
        return value


class MedicareClaimSerializer(serializers.ModelSerializer):
    """Serializer for Medicare claims"""
    
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    patient_medicare_number = serializers.CharField(source='patient.medicare_number', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    service_fee = serializers.DecimalField(source='invoice.total_amount', read_only=True, max_digits=10, decimal_places=2)
    item_description = serializers.CharField(source='medicare_item_number.description', read_only=True)
    
    # Status information
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_approved = serializers.SerializerMethodField()
    is_rejected = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicareClaim
        fields = [
            'id',
            'claim_number',
            'invoice',
            'invoice_number',
            'patient',
            'patient_name',
            'patient_medicare_number',
            'medicare_number',
            'medicare_item_number',
            'item_description',
            'service_fee',
            'medicare_rebate',
            'patient_payment',
            'status',
            'status_display',
            'is_approved',
            'is_rejected',
            'claim_date',
            'processed_date',
            'medicare_reference',
            'rejection_reason',
            'bulk_billing',
            'safety_net_applied',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'claim_number',
            'created_at',
            'updated_at'
        ]
    
    def get_is_approved(self, obj):
        """Check if claim is approved"""
        return obj.status == obj.ClaimStatus.APPROVED
    
    def get_is_rejected(self, obj):
        """Check if claim is rejected"""
        return obj.status == obj.ClaimStatus.REJECTED
    
    def validate_medicare_number(self, value):
        """Validate Medicare number format"""
        if not value:
            raise serializers.ValidationError("Medicare number is required")
        
        # Basic Medicare number validation (10 digits)
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Medicare number must be 10 digits")
        
        return value


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments"""
    
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Payment processing information
    is_completed = serializers.SerializerMethodField()
    is_failed = serializers.SerializerMethodField()
    is_refunded = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = [
            'id',
            'payment_id',
            'invoice',
            'invoice_number',
            'patient',
            'patient_name',
            'amount',
            'payment_method',
            'payment_method_display',
            'status',
            'status_display',
            'is_completed',
            'is_failed',
            'is_refunded',
            'stripe_payment_intent_id',
            'stripe_charge_id',
            'bank_reference',
            'medicare_claim',
            'processed_at',
            'failure_reason',
            'gst_amount',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'payment_id',
            'processed_at',
            'created_at',
            'updated_at'
        ]
    
    def get_is_completed(self, obj):
        """Check if payment is completed"""
        return obj.status == obj.PaymentStatus.COMPLETED
    
    def get_is_failed(self, obj):
        """Check if payment failed"""
        return obj.status == obj.PaymentStatus.FAILED
    
    def get_is_refunded(self, obj):
        """Check if payment was refunded"""
        return obj.status == obj.PaymentStatus.REFUNDED
    
    def validate_amount(self, value):
        """Validate payment amount"""
        if value <= Decimal('0.00'):
            raise serializers.ValidationError("Payment amount must be greater than zero")
        return value


class MedicareSafetyNetSerializer(serializers.ModelSerializer):
    """Serializer for Medicare Safety Net tracking"""
    
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    patient_medicare_number = serializers.CharField(source='patient.medicare_number', read_only=True)
    
    # Safety net calculations
    remaining_to_threshold = serializers.SerializerMethodField()
    safety_net_benefit = serializers.SerializerMethodField()
    
    class Meta:
        model = MedicareSafetyNet
        fields = [
            'id',
            'patient',
            'patient_name',
            'patient_medicare_number',
            'calendar_year',
            'total_medical_expenses',
            'medicare_rebates_received',
            'safety_net_threshold',
            'is_safety_net_eligible',
            'safety_net_date',
            'remaining_to_threshold',
            'safety_net_benefit',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'is_safety_net_eligible',
            'safety_net_date',
            'created_at',
            'updated_at'
        ]
    
    def get_remaining_to_threshold(self, obj):
        """Calculate remaining amount to reach safety net threshold"""
        remaining = obj.safety_net_threshold - obj.total_medical_expenses
        return max(Decimal('0.00'), remaining)
    
    def get_safety_net_benefit(self, obj):
        """Calculate potential safety net benefit"""
        if obj.is_safety_net_eligible:
            # Safety net provides higher rebates
            return obj.medicare_rebates_received * Decimal('0.20')  # 20% additional benefit
        return Decimal('0.00')


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating invoices with Medicare integration"""
    
    medicare_item_number = serializers.PrimaryKeyRelatedField(
        queryset=MedicareItemNumber.objects.filter(is_active=True),
        help_text="Medicare item number for this service"
    )
    
    class Meta:
        model = Invoice
        fields = [
            'patient',
            'appointment',
            'service_description',
            'service_date',
            'subtotal_amount',
            'medicare_item_number',
            'due_date',
            'abn'
        ]
    
    def validate(self, data):
        """Validate invoice data"""
        # Check if appointment exists and belongs to patient
        appointment = data['appointment']
        patient = data['patient']
        
        if appointment.patient != patient:
            raise serializers.ValidationError(
                "Appointment does not belong to the specified patient"
            )
        
        # Check if appointment is completed
        if appointment.status not in ['completed']:
            raise serializers.ValidationError(
                "Invoice can only be created for completed appointments"
            )
        
        # Validate Medicare item number requirements
        item_number = data['medicare_item_number']
        if item_number.requires_referral:
            # Check if patient has a referral (this would need to be implemented)
            pass
        
        return data


class MedicareClaimCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Medicare claims"""
    
    class Meta:
        model = MedicareClaim
        fields = [
            'invoice',
            'medicare_number',
            'medicare_item_number',
            'bulk_billing'
        ]
    
    def validate(self, data):
        """Validate Medicare claim data"""
        invoice = data['invoice']
        
        # Check if invoice is paid or has Medicare rebate
        if invoice.medicare_rebate <= Decimal('0.00'):
            raise serializers.ValidationError(
                "Medicare claim can only be created for invoices with Medicare rebate"
            )
        
        # Check if claim already exists for this invoice
        if MedicareClaim.objects.filter(invoice=invoice).exists():
            raise serializers.ValidationError(
                "Medicare claim already exists for this invoice"
            )
        
        return data


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments"""
    
    class Meta:
        model = Payment
        fields = [
            'invoice',
            'amount',
            'payment_method',
            'stripe_payment_intent_id',
            'bank_reference'
        ]
    
    def validate(self, data):
        """Validate payment data"""
        invoice = data['invoice']
        amount = data['amount']
        
        # Check if payment amount matches invoice
        if amount != invoice.out_of_pocket:
            raise serializers.ValidationError(
                f"Payment amount must match invoice out-of-pocket amount: ${invoice.out_of_pocket}"
            )
        
        # Check if invoice is already paid
        if invoice.status == invoice.InvoiceStatus.PAID:
            raise serializers.ValidationError(
                "Invoice is already paid"
            )
        
        return data
