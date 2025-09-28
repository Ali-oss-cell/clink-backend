"""
Billing app URLs - Payments, invoices, and Medicare rebates
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'medicare-claims', views.MedicareClaimViewSet, basename='medicare-claim')

urlpatterns = [
    path('', include(router.urls)),
    path('process-payment/', views.ProcessPaymentView.as_view(), name='process-payment'),
    path('stripe-webhook/', views.StripeWebhookView.as_view(), name='stripe-webhook'),
    path('create-payment-intent/', views.CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('medicare-rebate/', views.MedicareRebateView.as_view(), name='medicare-rebate'),
    path('invoices/<int:invoice_id>/download/', views.DownloadInvoiceView.as_view(), name='download-invoice'),
]
