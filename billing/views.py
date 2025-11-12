"""
Billing app views - Payments, invoices, and Medicare rebates
Australian healthcare compliance with Medicare integration
"""

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.db.models import Q, Sum, Count
from django.utils import timezone
from decimal import Decimal
import stripe
from django.conf import settings

from .models import (
    MedicareItemNumber,
    Invoice,
    MedicareClaim,
    Payment,
    MedicareSafetyNet
)
from .serializers import (
    MedicareItemNumberSerializer,
    InvoiceSerializer,
    InvoiceCreateSerializer,
    MedicareClaimSerializer,
    MedicareClaimCreateSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,
    MedicareSafetyNetSerializer
)
from audit.utils import log_action


class MedicareItemNumberViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Medicare item numbers"""
    
    queryset = MedicareItemNumber.objects.filter(is_active=True)
    serializer_class = MedicareItemNumberSerializer
    permission_classes = [AllowAny]  # Public information
    
    def get_queryset(self):
        """Filter Medicare item numbers"""
        queryset = super().get_queryset()
        
        # Filter by service type
        service_type = self.request.query_params.get('service_type')
        if service_type:
            queryset = queryset.filter(service_type=service_type)
        
        # Filter by requires referral
        requires_referral = self.request.query_params.get('requires_referral')
        if requires_referral is not None:
            queryset = queryset.filter(requires_referral=requires_referral.lower() == 'true')
        
        return queryset


class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for invoices with Medicare integration"""
    
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter invoices based on user role"""
        user = self.request.user
        
        if user.is_admin_user() or user.is_practice_manager():
            # Admins and practice managers can see all invoices
            return Invoice.objects.all()
        elif user.is_psychologist():
            # Psychologists can see invoices for their appointments
            return Invoice.objects.filter(
                appointment__psychologist=user
            )
        else:
            # Patients can only see their own invoices
            return Invoice.objects.filter(patient=user)
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return InvoiceCreateSerializer
        return InvoiceSerializer
    
    def perform_create(self, serializer):
        """Create invoice with Medicare calculations"""
        invoice = serializer.save()
        
        # Calculate Medicare rebate if item number is provided
        if invoice.medicare_item_number:
            invoice.medicare_rebate = invoice.medicare_item_number.standard_rebate
            invoice.save()
        
        # Log invoice creation
        log_action(
            user=self.request.user,
            action='create',
            obj=invoice,
            request=self.request,
            metadata={
                'invoice_number': invoice.invoice_number,
                'total_amount': str(invoice.total_amount)
            }
        )
    
    @action(detail=True, methods=['post'])
    def create_medicare_claim(self, request, pk=None):
        """Create Medicare claim for invoice"""
        invoice = self.get_object()
        
        # Check if claim already exists
        if MedicareClaim.objects.filter(invoice=invoice).exists():
            return Response(
                {'error': 'Medicare claim already exists for this invoice'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create Medicare claim
        claim_data = {
            'invoice': invoice.id,
            'medicare_number': request.data.get('medicare_number'),
            'medicare_item_number': invoice.medicare_item_number.id,
            'bulk_billing': request.data.get('bulk_billing', False)
        }
        
        claim_serializer = MedicareClaimCreateSerializer(data=claim_data)
        if claim_serializer.is_valid():
            claim = claim_serializer.save()
            return Response(
                MedicareClaimSerializer(claim).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(claim_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def medicare_claim(self, request, pk=None):
        """Get Medicare claim for invoice"""
        invoice = self.get_object()
        
        try:
            claim = invoice.medicare_claims.first()
            if claim:
                return Response(MedicareClaimSerializer(claim).data)
            else:
                return Response(
                    {'message': 'No Medicare claim found for this invoice'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except MedicareClaim.DoesNotExist:
            return Response(
                {'message': 'No Medicare claim found for this invoice'},
                status=status.HTTP_404_NOT_FOUND
            )


class MedicareClaimViewSet(viewsets.ModelViewSet):
    """ViewSet for Medicare claims"""
    
    serializer_class = MedicareClaimSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter Medicare claims based on user role"""
        user = self.request.user
        
        if user.is_admin_user() or user.is_practice_manager():
            # Admins and practice managers can see all claims
            return MedicareClaim.objects.all()
        elif user.is_psychologist():
            # Psychologists can see claims for their appointments
            return MedicareClaim.objects.filter(
                invoice__appointment__psychologist=user
            )
        else:
            # Patients can only see their own claims
            return MedicareClaim.objects.filter(patient=user)
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return MedicareClaimCreateSerializer
        return MedicareClaimSerializer
    
    @action(detail=True, methods=['post'])
    def submit_to_medicare(self, request, pk=None):
        """Submit claim to Medicare (simulated)"""
        claim = self.get_object()
        
        if claim.status != claim.ClaimStatus.PENDING:
            return Response(
                {'error': 'Claim can only be submitted if status is pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simulate Medicare submission
        claim.status = claim.ClaimStatus.SUBMITTED
        claim.claim_date = timezone.now().date()
        claim.save()
        
        return Response({
            'message': 'Claim submitted to Medicare successfully',
            'claim_number': claim.claim_number,
            'status': claim.get_status_display()
        })
    
    @action(detail=True, methods=['post'])
    def approve_claim(self, request, pk=None):
        """Approve Medicare claim (admin only)"""
        if not request.user.is_admin_user():
            return Response(
                {'error': 'Only admins can approve claims'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        claim = self.get_object()
        
        if claim.status != claim.ClaimStatus.SUBMITTED:
            return Response(
                {'error': 'Claim can only be approved if status is submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Approve claim
        claim.status = claim.ClaimStatus.APPROVED
        claim.processed_date = timezone.now().date()
        claim.medicare_reference = f"MED-{claim.claim_number}"
        claim.save()
        
        return Response({
            'message': 'Claim approved successfully',
            'medicare_reference': claim.medicare_reference,
            'status': claim.get_status_display()
        })


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for payments"""
    
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter payments based on user role"""
        user = self.request.user
        
        if user.is_admin_user() or user.is_practice_manager():
            # Admins and practice managers can see all payments
            return Payment.objects.all()
        elif user.is_psychologist():
            # Psychologists can see payments for their appointments
            return Payment.objects.filter(
                invoice__appointment__psychologist=user
            )
        else:
            # Patients can only see their own payments
            return Payment.objects.filter(patient=user)
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    def perform_create(self, serializer):
        """Create payment and update invoice status"""
        payment = serializer.save()
        
        # Update invoice status if payment is completed
        if payment.status == payment.PaymentStatus.COMPLETED:
            payment.invoice.status = payment.invoice.InvoiceStatus.PAID
            payment.invoice.paid_date = timezone.now().date()
            payment.invoice.save()
    
    @action(detail=True, methods=['post'])
    def process_stripe_payment(self, request, pk=None):
        """Process Stripe payment"""
        payment = self.get_object()
        
        if payment.payment_method != payment.PaymentMethod.STRIPE:
            return Response(
                {'error': 'Payment method is not Stripe'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Configure Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),  # Convert to cents
                currency='aud',
                metadata={
                    'payment_id': payment.payment_id,
                    'invoice_id': payment.invoice.invoice_number,
                    'patient_id': str(payment.patient.id)
                }
            )
            
            # Update payment with Stripe details
            payment.stripe_payment_intent_id = intent.id
            payment.status = payment.PaymentStatus.PROCESSING
            payment.save()
            
            return Response({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            })
            
        except stripe.error.StripeError as e:
            payment.status = payment.PaymentStatus.FAILED
            payment.failure_reason = str(e)
            payment.save()
            
            return Response(
                {'error': f'Stripe error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class MedicareSafetyNetViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for Medicare Safety Net tracking"""
    
    serializer_class = MedicareSafetyNetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter safety net records based on user role"""
        user = self.request.user
        
        if user.is_admin_user() or user.is_practice_manager():
            # Admins and practice managers can see all safety net records
            return MedicareSafetyNet.objects.all()
        else:
            # Patients can only see their own safety net records
            return MedicareSafetyNet.objects.filter(patient=user)


class ProcessPaymentView(APIView):
    """Process payment with Stripe"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Process Stripe payment"""
        try:
            # Configure Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Get payment intent ID from request
            payment_intent_id = request.data.get('payment_intent_id')
            if not payment_intent_id:
                return Response(
                    {'error': 'Payment intent ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Retrieve payment intent
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status == 'succeeded':
                # Find and update payment
                try:
                    payment = Payment.objects.get(
                        stripe_payment_intent_id=payment_intent_id
                    )
                    payment.status = payment.PaymentStatus.COMPLETED
                    payment.processed_at = timezone.now()
                    payment.save()
                    
                    # Update invoice status
                    payment.invoice.status = payment.invoice.InvoiceStatus.PAID
                    payment.invoice.paid_date = timezone.now().date()
                    payment.invoice.save()
                    
                    return Response({
                        'message': 'Payment processed successfully',
                        'payment_id': payment.payment_id,
                        'status': payment.get_status_display()
                    })
                    
                except Payment.DoesNotExist:
                    return Response(
                        {'error': 'Payment not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                return Response(
                    {'error': f'Payment failed: {intent.status}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except stripe.error.StripeError as e:
            return Response(
                {'error': f'Stripe error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class StripeWebhookView(APIView):
    """Stripe webhook handler"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Handle Stripe webhooks"""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response({'error': 'Invalid payload'}, status=400)
        except stripe.error.SignatureVerificationError:
            return Response({'error': 'Invalid signature'}, status=400)
        
        # Handle payment intent succeeded
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            
            try:
                payment = Payment.objects.get(
                    stripe_payment_intent_id=payment_intent['id']
                )
                payment.status = payment.PaymentStatus.COMPLETED
                payment.processed_at = timezone.now()
                payment.save()
                
                # Update invoice status
                payment.invoice.status = payment.invoice.InvoiceStatus.PAID
                payment.invoice.paid_date = timezone.now().date()
                payment.invoice.save()
                
            except Payment.DoesNotExist:
                pass
        
        return Response({'status': 'success'})


class CreatePaymentIntentView(APIView):
    """Create Stripe payment intent"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create payment intent for Stripe"""
        try:
            # Configure Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            
            # Get invoice ID and amount
            invoice_id = request.data.get('invoice_id')
            amount = request.data.get('amount')
            
            if not invoice_id or not amount:
                return Response(
                    {'error': 'Invoice ID and amount are required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(float(amount) * 100),  # Convert to cents
                currency='aud',
                metadata={
                    'invoice_id': invoice_id,
                    'patient_id': str(request.user.id)
                }
            )
            
            return Response({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            })
            
        except stripe.error.StripeError as e:
            return Response(
                {'error': f'Stripe error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class MedicareRebateView(APIView):
    """Medicare rebate processing and calculations"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get Medicare rebate information for a service"""
        item_number = request.query_params.get('item_number')
        
        if not item_number:
            return Response(
                {'error': 'Item number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            medicare_item = MedicareItemNumber.objects.get(
                item_number=item_number,
                is_active=True
            )
            
            return Response({
                'item_number': medicare_item.item_number,
                'description': medicare_item.description,
                'standard_rebate': float(medicare_item.standard_rebate),
                'safety_net_rebate': float(medicare_item.safety_net_rebate) if medicare_item.safety_net_rebate else None,
                'requires_referral': medicare_item.requires_referral,
                'max_sessions_per_year': medicare_item.max_sessions_per_year
            })
            
        except MedicareItemNumber.DoesNotExist:
            return Response(
                {'error': 'Medicare item number not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def post(self, request):
        """Calculate Medicare rebate for a service"""
        item_number = request.data.get('item_number')
        service_fee = request.data.get('service_fee')
        patient_id = request.data.get('patient_id')
        
        if not all([item_number, service_fee, patient_id]):
            return Response(
                {'error': 'Item number, service fee, and patient ID are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get Medicare item number
            medicare_item = MedicareItemNumber.objects.get(
                item_number=item_number,
                is_active=True
            )
            
            # Get patient
            from django.contrib.auth import get_user_model
            User = get_user_model()
            patient = User.objects.get(id=patient_id)
            
            # Calculate rebate
            rebate_amount = medicare_item.standard_rebate
            
            # Check for safety net eligibility
            current_year = timezone.now().year
            safety_net, created = MedicareSafetyNet.objects.get_or_create(
                patient=patient,
                calendar_year=current_year,
                defaults={'total_medical_expenses': Decimal('0.00')}
            )
            
            if safety_net.is_safety_net_eligible and medicare_item.safety_net_rebate:
                rebate_amount = medicare_item.safety_net_rebate
            
            # Calculate out-of-pocket amount
            out_of_pocket = Decimal(str(service_fee)) - rebate_amount
            
            return Response({
                'service_fee': float(service_fee),
                'medicare_rebate': float(rebate_amount),
                'out_of_pocket': float(out_of_pocket),
                'safety_net_applied': safety_net.is_safety_net_eligible,
                'rebate_percentage': float((rebate_amount / Decimal(str(service_fee))) * 100)
            })
            
        except MedicareItemNumber.DoesNotExist:
            return Response(
                {'error': 'Medicare item number not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Calculation error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class DownloadInvoiceView(APIView):
    """Download invoice as PDF"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, invoice_id):
        """Download invoice PDF"""
        try:
            invoice = Invoice.objects.select_related(
                'patient',
                'appointment',
                'appointment__psychologist',
                'medicare_item_number'
            ).get(id=invoice_id)
            
            # Check permissions
            user = request.user
            if not (user.is_admin_user() or user.is_practice_manager() or invoice.patient == user):
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Generate PDF
            from .pdf_service import InvoicePDFService
            
            pdf_service = InvoicePDFService()
            pdf_buffer = pdf_service.generate_invoice_pdf(invoice)
            
            # Create HTTP response with PDF
            from django.http import HttpResponse
            
            response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Invoice_{invoice.invoice_number}.pdf"'
            
            return response
            
        except Invoice.DoesNotExist:
            return Response(
                {'error': 'Invoice not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error generating PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )