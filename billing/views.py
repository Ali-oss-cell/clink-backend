"""
Billing app views - Payments, invoices, and Medicare rebates
"""

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

# Placeholder views - will be implemented with proper models later

class InvoiceViewSet(viewsets.ModelViewSet):
    """Invoices viewset"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response({
            'message': 'Invoices list - to be implemented'
        })

class PaymentViewSet(viewsets.ModelViewSet):
    """Payments viewset"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response({
            'message': 'Payments list - to be implemented'
        })

class MedicareClaimViewSet(viewsets.ModelViewSet):
    """Medicare claims viewset"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        return Response({
            'message': 'Medicare claims - to be implemented'
        })

class ProcessPaymentView(APIView):
    """Process payment with Stripe"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({
            'message': 'Process payment - to be implemented'
        })

class StripeWebhookView(APIView):
    """Stripe webhook handler"""
    permission_classes = []  # No authentication for webhooks
    
    def post(self, request):
        return Response({
            'message': 'Stripe webhook - to be implemented'
        })

class CreatePaymentIntentView(APIView):
    """Create Stripe payment intent"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({
            'message': 'Create payment intent - to be implemented'
        })

class MedicareRebateView(APIView):
    """Medicare rebate processing"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({
            'message': 'Medicare rebate - to be implemented'
        })

class DownloadInvoiceView(APIView):
    """Download invoice PDF"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, invoice_id):
        return Response({
            'message': f'Download invoice {invoice_id} - to be implemented'
        })