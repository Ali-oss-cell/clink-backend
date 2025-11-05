"""
Django management command to calculate Medicare Safety Net
Calculates safety net eligibility for all patients
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from billing.models import MedicareSafetyNet, Invoice, MedicareClaim

User = get_user_model()


class Command(BaseCommand):
    help = 'Calculate Medicare Safety Net eligibility for all patients'

    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            default=timezone.now().year,
            help='Calendar year to calculate safety net for'
        )
        parser.add_argument(
            '--patient-id',
            type=int,
            help='Calculate safety net for specific patient only'
        )

    def handle(self, *args, **options):
        """Calculate Medicare Safety Net eligibility"""
        
        year = options['year']
        patient_id = options.get('patient_id')
        
        if patient_id:
            # Calculate for specific patient
            try:
                patient = User.objects.get(id=patient_id, role=User.UserRole.PATIENT)
                self.calculate_patient_safety_net(patient, year)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Patient with ID {patient_id} not found')
                )
        else:
            # Calculate for all patients
            patients = User.objects.filter(role=User.UserRole.PATIENT)
            
            for patient in patients:
                self.calculate_patient_safety_net(patient, year)
        
        self.stdout.write(
            self.style.SUCCESS(f'Safety net calculation completed for year {year}')
        )

    def calculate_patient_safety_net(self, patient, year):
        """Calculate safety net for a specific patient"""
        
        # Get or create safety net record
        safety_net, created = MedicareSafetyNet.objects.get_or_create(
            patient=patient,
            calendar_year=year,
            defaults={
                'total_medical_expenses': Decimal('0.00'),
                'medicare_rebates_received': Decimal('0.00'),
                'safety_net_threshold': Decimal('2448.90')  # 2024 threshold
            }
        )
        
        # Calculate total medical expenses from invoices
        total_expenses = Invoice.objects.filter(
            patient=patient,
            service_date__year=year,
            status__in=['paid', 'overdue']
        ).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Calculate Medicare rebates received
        total_rebates = MedicareClaim.objects.filter(
            patient=patient,
            claim_date__year=year,
            status__in=['approved', 'paid']
        ).aggregate(
            total=Sum('medicare_rebate')
        )['total'] or Decimal('0.00')
        
        # Update safety net record
        safety_net.total_medical_expenses = total_expenses
        safety_net.medicare_rebates_received = total_rebates
        
        # Check if patient has reached safety net threshold
        if total_expenses >= safety_net.safety_net_threshold:
            safety_net.is_safety_net_eligible = True
            if not safety_net.safety_net_date:
                safety_net.safety_net_date = timezone.now().date()
        else:
            safety_net.is_safety_net_eligible = False
            safety_net.safety_net_date = None
        
        safety_net.save()
        
        # Display results
        remaining = safety_net.safety_net_threshold - total_expenses
        status = "ELIGIBLE" if safety_net.is_safety_net_eligible else "NOT ELIGIBLE"
        
        self.stdout.write(
            f'Patient: {patient.get_full_name()} ({patient.email})'
        )
        self.stdout.write(
            f'  Total Expenses: ${total_expenses:.2f}'
        )
        self.stdout.write(
            f'  Medicare Rebates: ${total_rebates:.2f}'
        )
        self.stdout.write(
            f'  Safety Net Status: {status}'
        )
        if not safety_net.is_safety_net_eligible:
            self.stdout.write(
                f'  Remaining to Threshold: ${max(Decimal("0.00"), remaining):.2f}'
            )
        self.stdout.write('')
