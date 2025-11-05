"""
Billing models for Psychology Clinic
Australian Medicare integration and payment processing
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

User = get_user_model()


class MedicareItemNumber(models.Model):
    """
    Medicare item numbers for psychology services
    Based on Australian Medicare Benefits Schedule (MBS)
    """
    
    class ServiceType(models.TextChoices):
        PSYCHOLOGIST = 'psychologist', 'Psychologist'
        CLINICAL_PSYCHOLOGIST = 'clinical_psychologist', 'Clinical Psychologist'
        PSYCHIATRIST = 'psychiatrist', 'Psychiatrist'
        GENERAL_PRACTITIONER = 'gp', 'General Practitioner'
    
    item_number = models.CharField(
        max_length=10,
        unique=True,
        help_text="Medicare item number (e.g., 80110, 80115)"
    )
    
    description = models.CharField(
        max_length=200,
        help_text="Service description"
    )
    
    service_type = models.CharField(
        max_length=25,
        choices=ServiceType.choices,
        help_text="Type of healthcare provider"
    )
    
    # Medicare rebate amounts (in AUD)
    standard_rebate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Standard Medicare rebate amount"
    )
    
    safety_net_rebate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Safety net rebate amount (if applicable)"
    )
    
    # Session requirements
    min_session_duration = models.PositiveIntegerField(
        default=50,
        help_text="Minimum session duration in minutes"
    )
    
    max_sessions_per_year = models.PositiveIntegerField(
        default=10,
        help_text="Maximum sessions per calendar year"
    )
    
    requires_referral = models.BooleanField(
        default=True,
        help_text="Whether a GP referral is required"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this item number is currently active"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['item_number']
        verbose_name = 'Medicare Item Number'
        verbose_name_plural = 'Medicare Item Numbers'
    
    def __str__(self):
        return f"{self.item_number} - {self.description}"


class Invoice(models.Model):
    """
    Invoice model for psychology clinic billing
    Includes Medicare integration and Australian GST compliance
    """
    
    class InvoiceStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SENT = 'sent', 'Sent'
        PAID = 'paid', 'Paid'
        OVERDUE = 'overdue', 'Overdue'
        CANCELLED = 'cancelled', 'Cancelled'
        REFUNDED = 'refunded', 'Refunded'
    
    # Basic invoice information
    invoice_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique invoice number"
    )
    
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='invoices',
        help_text="Patient who received the service"
    )
    
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='invoices',
        help_text="Associated appointment"
    )
    
    # Service details
    service_description = models.CharField(
        max_length=200,
        help_text="Description of the service provided"
    )
    
    service_date = models.DateField(
        help_text="Date the service was provided"
    )
    
    # Financial information (Australian GST = 10%)
    GST_RATE = Decimal('0.10')
    
    subtotal_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Amount before GST"
    )
    
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="GST amount (10% of subtotal)"
    )
    
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Total amount including GST"
    )
    
    # Medicare information
    medicare_item_number = models.ForeignKey(
        MedicareItemNumber,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        help_text="Medicare item number used"
    )
    
    medicare_rebate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Medicare rebate amount"
    )
    
    out_of_pocket = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Amount patient pays after Medicare rebate"
    )
    
    # Invoice status and dates
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        help_text="Current invoice status"
    )
    
    due_date = models.DateField(
        help_text="Payment due date"
    )
    
    paid_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date payment was received"
    )
    
    # Australian business details
    abn = models.CharField(
        max_length=11,
        blank=True,
        help_text="Australian Business Number"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Invoice'
        verbose_name_plural = 'Invoices'
    
    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.patient.get_full_name()}"
    
    def save(self, *args, **kwargs):
        """Auto-generate invoice number and calculate amounts"""
        if not self.invoice_number:
            self.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate GST and total
        self.gst_amount = self.subtotal_amount * self.GST_RATE
        self.total_amount = self.subtotal_amount + self.gst_amount
        
        # Calculate out-of-pocket amount
        self.out_of_pocket = self.total_amount - self.medicare_rebate
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        from django.utils import timezone
        return self.status == self.InvoiceStatus.SENT and timezone.now().date() > self.due_date


class MedicareClaim(models.Model):
    """
    Medicare claim for psychology services
    Handles Australian Medicare rebate processing
    """
    
    class ClaimStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUBMITTED = 'submitted', 'Submitted to Medicare'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        PAID = 'paid', 'Paid'
        CANCELLED = 'cancelled', 'Cancelled'
    
    # Claim identification
    claim_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique Medicare claim number"
    )
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='medicare_claims',
        help_text="Associated invoice"
    )
    
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='medicare_claims',
        help_text="Patient making the claim"
    )
    
    # Medicare details
    medicare_number = models.CharField(
        max_length=10,
        help_text="Patient's Medicare number"
    )
    
    medicare_item_number = models.ForeignKey(
        MedicareItemNumber,
        on_delete=models.PROTECT,
        help_text="Medicare item number for this claim"
    )
    
    # Claim amounts
    service_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total service fee charged"
    )
    
    medicare_rebate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Medicare rebate amount"
    )
    
    patient_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount patient pays"
    )
    
    # Claim status and processing
    status = models.CharField(
        max_length=20,
        choices=ClaimStatus.choices,
        default=ClaimStatus.PENDING,
        help_text="Current claim status"
    )
    
    claim_date = models.DateField(
        help_text="Date claim was submitted"
    )
    
    processed_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date claim was processed by Medicare"
    )
    
    # Medicare response
    medicare_reference = models.CharField(
        max_length=50,
        blank=True,
        help_text="Medicare reference number"
    )
    
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection (if applicable)"
    )
    
    # Australian compliance
    bulk_billing = models.BooleanField(
        default=False,
        help_text="Whether this is a bulk billing claim"
    )
    
    safety_net_applied = models.BooleanField(
        default=False,
        help_text="Whether safety net rebate was applied"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-claim_date']
        verbose_name = 'Medicare Claim'
        verbose_name_plural = 'Medicare Claims'
    
    def __str__(self):
        return f"Claim {self.claim_number} - {self.patient.get_full_name()}"
    
    def save(self, *args, **kwargs):
        """Auto-generate claim number"""
        if not self.claim_number:
            self.claim_number = f"MC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class Payment(models.Model):
    """
    Payment model for psychology clinic
    Handles various payment methods including Medicare
    """
    
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Cash'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        CREDIT_CARD = 'credit_card', 'Credit Card'
        DEBIT_CARD = 'debit_card', 'Debit Card'
        MEDICARE = 'medicare', 'Medicare'
        PRIVATE_HEALTH = 'private_health', 'Private Health Insurance'
        PAYPAL = 'paypal', 'PayPal'
        STRIPE = 'stripe', 'Stripe'
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PROCESSING = 'processing', 'Processing'
        COMPLETED = 'completed', 'Completed'
        FAILED = 'failed', 'Failed'
        REFUNDED = 'refunded', 'Refunded'
        CANCELLED = 'cancelled', 'Cancelled'
    
    # Payment identification
    payment_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique payment identifier"
    )
    
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments',
        help_text="Associated invoice"
    )
    
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payments',
        help_text="Patient making the payment"
    )
    
    # Payment details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Payment amount"
    )
    
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        help_text="Method of payment"
    )
    
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        help_text="Payment status"
    )
    
    # External payment references
    stripe_payment_intent_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Stripe payment intent ID"
    )
    
    stripe_charge_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Stripe charge ID"
    )
    
    bank_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bank transfer reference"
    )
    
    # Medicare claim reference
    medicare_claim = models.ForeignKey(
        MedicareClaim,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
        help_text="Associated Medicare claim"
    )
    
    # Payment processing
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date payment was processed"
    )
    
    failure_reason = models.TextField(
        blank=True,
        help_text="Reason for payment failure"
    )
    
    # Australian compliance
    gst_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="GST amount included in payment"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
    
    def __str__(self):
        return f"Payment {self.payment_id} - ${self.amount}"
    
    def save(self, *args, **kwargs):
        """Auto-generate payment ID"""
        if not self.payment_id:
            self.payment_id = f"PAY-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class MedicareSafetyNet(models.Model):
    """
    Medicare Safety Net tracking for patients
    Tracks annual spending for safety net eligibility
    """
    
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='safety_net',
        help_text="Patient"
    )
    
    calendar_year = models.PositiveIntegerField(
        help_text="Calendar year for safety net tracking"
    )
    
    total_medical_expenses = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total medical expenses for the year"
    )
    
    medicare_rebates_received = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total Medicare rebates received"
    )
    
    safety_net_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('2448.90'),  # 2024 threshold
        help_text="Safety net threshold amount"
    )
    
    is_safety_net_eligible = models.BooleanField(
        default=False,
        help_text="Whether patient is eligible for safety net"
    )
    
    safety_net_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date safety net eligibility was reached"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['patient', 'calendar_year']
        ordering = ['-calendar_year']
        verbose_name = 'Medicare Safety Net'
        verbose_name_plural = 'Medicare Safety Nets'
    
    def __str__(self):
        return f"Safety Net {self.calendar_year} - {self.patient.get_full_name()}"
    
    def save(self, *args, **kwargs):
        """Update safety net eligibility"""
        if self.total_medical_expenses >= self.safety_net_threshold:
            self.is_safety_net_eligible = True
            if not self.safety_net_date:
                from django.utils import timezone
                self.safety_net_date = timezone.now().date()
        else:
            self.is_safety_net_eligible = False
            self.safety_net_date = None
        
        super().save(*args, **kwargs)