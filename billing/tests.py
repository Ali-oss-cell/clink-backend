"""
Tests for billing app
Australian Medicare integration and payment processing
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta

from .models import (
    MedicareItemNumber,
    Invoice,
    MedicareClaim,
    Payment,
    MedicareSafetyNet
)

User = get_user_model()


class MedicareItemNumberModelTest(TestCase):
    """Test Medicare item number model"""
    
    def setUp(self):
        """Set up test data"""
        self.medicare_item = MedicareItemNumber.objects.create(
            item_number='80110',
            description='Clinical psychology service - individual',
            service_type=MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
            standard_rebate=Decimal('88.25'),
            safety_net_rebate=Decimal('88.25'),
            min_session_duration=50,
            max_sessions_per_year=10,
            requires_referral=True,
            is_active=True
        )
    
    def test_medicare_item_creation(self):
        """Test Medicare item number creation"""
        self.assertEqual(self.medicare_item.item_number, '80110')
        self.assertEqual(self.medicare_item.description, 'Clinical psychology service - individual')
        self.assertEqual(self.medicare_item.standard_rebate, Decimal('88.25'))
        self.assertTrue(self.medicare_item.requires_referral)
        self.assertTrue(self.medicare_item.is_active)
    
    def test_medicare_item_str(self):
        """Test Medicare item number string representation"""
        expected = "80110 - Clinical psychology service - individual"
        self.assertEqual(str(self.medicare_item), expected)


class InvoiceModelTest(TestCase):
    """Test Invoice model"""
    
    def setUp(self):
        """Set up test data"""
        # Create users
        self.patient = User.objects.create_user(
            email='patient@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            role=User.UserRole.PATIENT
        )
        
        self.psychologist = User.objects.create_user(
            email='psychologist@test.com',
            password='testpass123',
            first_name='Dr. Jane',
            last_name='Smith',
            role=User.UserRole.PSYCHOLOGIST
        )
        
        # Create Medicare item
        self.medicare_item = MedicareItemNumber.objects.create(
            item_number='80110',
            description='Clinical psychology service - individual',
            service_type=MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
            standard_rebate=Decimal('88.25'),
            min_session_duration=50,
            max_sessions_per_year=10,
            requires_referral=True,
            is_active=True
        )
        
        # Create appointment (mock)
        from appointments.models import Appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            psychologist=self.psychologist,
            appointment_date=timezone.now() + timedelta(days=1),
            duration_minutes=50,
            status='completed'
        )
    
    def test_invoice_creation(self):
        """Test invoice creation"""
        invoice = Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment,
            service_description='Psychology consultation',
            service_date=date.today(),
            subtotal_amount=Decimal('100.00'),
            medicare_item_number=self.medicare_item,
            medicare_rebate=Decimal('88.25'),
            due_date=date.today() + timedelta(days=30),
            abn='12345678901'
        )
        
        self.assertEqual(invoice.patient, self.patient)
        self.assertEqual(invoice.appointment, self.appointment)
        self.assertEqual(invoice.subtotal_amount, Decimal('100.00'))
        self.assertEqual(invoice.gst_amount, Decimal('10.00'))  # 10% GST
        self.assertEqual(invoice.total_amount, Decimal('110.00'))
        self.assertEqual(invoice.out_of_pocket, Decimal('21.75'))  # 110 - 88.25
    
    def test_invoice_auto_calculation(self):
        """Test automatic GST and total calculation"""
        invoice = Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment,
            service_description='Psychology consultation',
            service_date=date.today(),
            subtotal_amount=Decimal('100.00'),
            medicare_item_number=self.medicare_item,
            medicare_rebate=Decimal('88.25'),
            due_date=date.today() + timedelta(days=30)
        )
        
        # Check automatic calculations
        self.assertEqual(invoice.gst_amount, Decimal('10.00'))
        self.assertEqual(invoice.total_amount, Decimal('110.00'))
        self.assertEqual(invoice.out_of_pocket, Decimal('21.75'))
    
    def test_invoice_overdue_property(self):
        """Test invoice overdue property"""
        # Create overdue invoice
        overdue_invoice = Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment,
            service_description='Psychology consultation',
            service_date=date.today(),
            subtotal_amount=Decimal('100.00'),
            medicare_item_number=self.medicare_item,
            medicare_rebate=Decimal('88.25'),
            due_date=date.today() - timedelta(days=1),
            status=Invoice.InvoiceStatus.SENT
        )
        
        self.assertTrue(overdue_invoice.is_overdue)
        
        # Create non-overdue invoice
        current_invoice = Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment,
            service_description='Psychology consultation',
            service_date=date.today(),
            subtotal_amount=Decimal('100.00'),
            medicare_item_number=self.medicare_item,
            medicare_rebate=Decimal('88.25'),
            due_date=date.today() + timedelta(days=1),
            status=Invoice.InvoiceStatus.SENT
        )
        
        self.assertFalse(current_invoice.is_overdue)


class MedicareClaimModelTest(TestCase):
    """Test Medicare claim model"""
    
    def setUp(self):
        """Set up test data"""
        # Create users
        self.patient = User.objects.create_user(
            email='patient@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            role=User.UserRole.PATIENT,
            medicare_number='1234567890'
        )
        
        self.psychologist = User.objects.create_user(
            email='psychologist@test.com',
            password='testpass123',
            first_name='Dr. Jane',
            last_name='Smith',
            role=User.UserRole.PSYCHOLOGIST
        )
        
        # Create Medicare item
        self.medicare_item = MedicareItemNumber.objects.create(
            item_number='80110',
            description='Clinical psychology service - individual',
            service_type=MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
            standard_rebate=Decimal('88.25'),
            min_session_duration=50,
            max_sessions_per_year=10,
            requires_referral=True,
            is_active=True
        )
        
        # Create appointment and invoice
        from appointments.models import Appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            psychologist=self.psychologist,
            appointment_date=timezone.now() + timedelta(days=1),
            duration_minutes=50,
            status='completed'
        )
        
        self.invoice = Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment,
            service_description='Psychology consultation',
            service_date=date.today(),
            subtotal_amount=Decimal('100.00'),
            medicare_item_number=self.medicare_item,
            medicare_rebate=Decimal('88.25'),
            due_date=date.today() + timedelta(days=30)
        )
    
    def test_medicare_claim_creation(self):
        """Test Medicare claim creation"""
        claim = MedicareClaim.objects.create(
            invoice=self.invoice,
            patient=self.patient,
            medicare_number='1234567890',
            medicare_item_number=self.medicare_item,
            service_fee=Decimal('110.00'),
            medicare_rebate=Decimal('88.25'),
            patient_payment=Decimal('21.75'),
            claim_date=date.today(),
            bulk_billing=False
        )
        
        self.assertEqual(claim.invoice, self.invoice)
        self.assertEqual(claim.patient, self.patient)
        self.assertEqual(claim.medicare_number, '1234567890')
        self.assertEqual(claim.service_fee, Decimal('110.00'))
        self.assertEqual(claim.medicare_rebate, Decimal('88.25'))
        self.assertEqual(claim.patient_payment, Decimal('21.75'))
        self.assertFalse(claim.bulk_billing)
    
    def test_medicare_claim_auto_generation(self):
        """Test automatic claim number generation"""
        claim = MedicareClaim.objects.create(
            invoice=self.invoice,
            patient=self.patient,
            medicare_number='1234567890',
            medicare_item_number=self.medicare_item,
            service_fee=Decimal('110.00'),
            medicare_rebate=Decimal('88.25'),
            patient_payment=Decimal('21.75'),
            claim_date=date.today()
        )
        
        # Check that claim number was auto-generated
        self.assertTrue(claim.claim_number.startswith('MC-'))
        self.assertEqual(len(claim.claim_number), 11)  # MC- + 8 chars


class PaymentModelTest(TestCase):
    """Test Payment model"""
    
    def setUp(self):
        """Set up test data"""
        # Create users
        self.patient = User.objects.create_user(
            email='patient@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            role=User.UserRole.PATIENT
        )
        
        self.psychologist = User.objects.create_user(
            email='psychologist@test.com',
            password='testpass123',
            first_name='Dr. Jane',
            last_name='Smith',
            role=User.UserRole.PSYCHOLOGIST
        )
        
        # Create appointment and invoice
        from appointments.models import Appointment
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            psychologist=self.psychologist,
            appointment_date=timezone.now() + timedelta(days=1),
            duration_minutes=50,
            status='completed'
        )
        
        self.invoice = Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment,
            service_description='Psychology consultation',
            service_date=date.today(),
            subtotal_amount=Decimal('100.00'),
            medicare_rebate=Decimal('88.25'),
            due_date=date.today() + timedelta(days=30)
        )
    
    def test_payment_creation(self):
        """Test payment creation"""
        payment = Payment.objects.create(
            invoice=self.invoice,
            patient=self.patient,
            amount=Decimal('21.75'),
            payment_method=Payment.PaymentMethod.CREDIT_CARD,
            status=Payment.PaymentStatus.COMPLETED
        )
        
        self.assertEqual(payment.invoice, self.invoice)
        self.assertEqual(payment.patient, self.patient)
        self.assertEqual(payment.amount, Decimal('21.75'))
        self.assertEqual(payment.payment_method, Payment.PaymentMethod.CREDIT_CARD)
        self.assertEqual(payment.status, Payment.PaymentStatus.COMPLETED)
    
    def test_payment_auto_generation(self):
        """Test automatic payment ID generation"""
        payment = Payment.objects.create(
            invoice=self.invoice,
            patient=self.patient,
            amount=Decimal('21.75'),
            payment_method=Payment.PaymentMethod.CREDIT_CARD
        )
        
        # Check that payment ID was auto-generated
        self.assertTrue(payment.payment_id.startswith('PAY-'))
        self.assertEqual(len(payment.payment_id), 12)  # PAY- + 8 chars


class MedicareSafetyNetModelTest(TestCase):
    """Test Medicare Safety Net model"""
    
    def setUp(self):
        """Set up test data"""
        self.patient = User.objects.create_user(
            email='patient@test.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            role=User.UserRole.PATIENT
        )
    
    def test_safety_net_creation(self):
        """Test safety net creation"""
        safety_net = MedicareSafetyNet.objects.create(
            patient=self.patient,
            calendar_year=2024,
            total_medical_expenses=Decimal('2000.00'),
            medicare_rebates_received=Decimal('500.00'),
            safety_net_threshold=Decimal('2448.90')
        )
        
        self.assertEqual(safety_net.patient, self.patient)
        self.assertEqual(safety_net.calendar_year, 2024)
        self.assertEqual(safety_net.total_medical_expenses, Decimal('2000.00'))
        self.assertEqual(safety_net.medicare_rebates_received, Decimal('500.00'))
        self.assertFalse(safety_net.is_safety_net_eligible)
    
    def test_safety_net_eligibility_calculation(self):
        """Test safety net eligibility calculation"""
        # Create safety net below threshold
        safety_net = MedicareSafetyNet.objects.create(
            patient=self.patient,
            calendar_year=2024,
            total_medical_expenses=Decimal('2000.00'),
            medicare_rebates_received=Decimal('500.00'),
            safety_net_threshold=Decimal('2448.90')
        )
        
        self.assertFalse(safety_net.is_safety_net_eligible)
        self.assertIsNone(safety_net.safety_net_date)
        
        # Update to above threshold
        safety_net.total_medical_expenses = Decimal('2500.00')
        safety_net.save()
        
        self.assertTrue(safety_net.is_safety_net_eligible)
        self.assertIsNotNone(safety_net.safety_net_date)