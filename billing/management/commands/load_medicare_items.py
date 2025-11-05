"""
Django management command to load Medicare item numbers
Loads Australian Medicare Benefits Schedule (MBS) item numbers for psychology services
"""

from django.core.management.base import BaseCommand
from decimal import Decimal
from billing.models import MedicareItemNumber


class Command(BaseCommand):
    help = 'Load Medicare item numbers for psychology services'

    def handle(self, *args, **options):
        """Load Medicare item numbers"""
        
        # Medicare item numbers for psychology services (2024 MBS)
        medicare_items = [
            {
                'item_number': '80110',
                'description': 'Clinical psychology service - individual',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 10,
                'requires_referral': True
            },
            {
                'item_number': '80115',
                'description': 'Clinical psychology service - group (2-8 people)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 10,
                'requires_referral': True
            },
            {
                'item_number': '80120',
                'description': 'Clinical psychology service - individual (additional sessions)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 20,
                'requires_referral': True
            },
            {
                'item_number': '80125',
                'description': 'Clinical psychology service - group (additional sessions)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 20,
                'requires_referral': True
            },
            {
                'item_number': '80130',
                'description': 'Clinical psychology service - individual (chronic disease management)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 5,
                'requires_referral': True
            },
            {
                'item_number': '80135',
                'description': 'Clinical psychology service - group (chronic disease management)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 5,
                'requires_referral': True
            },
            {
                'item_number': '80140',
                'description': 'Clinical psychology service - individual (eating disorders)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 40,
                'requires_referral': True
            },
            {
                'item_number': '80145',
                'description': 'Clinical psychology service - group (eating disorders)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 40,
                'requires_referral': True
            },
            {
                'item_number': '80150',
                'description': 'Clinical psychology service - individual (autism spectrum disorder)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 20,
                'requires_referral': True
            },
            {
                'item_number': '80155',
                'description': 'Clinical psychology service - group (autism spectrum disorder)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 20,
                'requires_referral': True
            },
            {
                'item_number': '80160',
                'description': 'Clinical psychology service - individual (mental health care plan)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 10,
                'requires_referral': True
            },
            {
                'item_number': '80165',
                'description': 'Clinical psychology service - group (mental health care plan)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 10,
                'requires_referral': True
            },
            {
                'item_number': '80170',
                'description': 'Clinical psychology service - individual (suicide prevention)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 12,
                'requires_referral': True
            },
            {
                'item_number': '80175',
                'description': 'Clinical psychology service - group (suicide prevention)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 12,
                'requires_referral': True
            },
            {
                'item_number': '80180',
                'description': 'Clinical psychology service - individual (perinatal mental health)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 12,
                'requires_referral': True
            },
            {
                'item_number': '80185',
                'description': 'Clinical psychology service - group (perinatal mental health)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 12,
                'requires_referral': True
            },
            {
                'item_number': '80190',
                'description': 'Clinical psychology service - individual (trauma)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 16,
                'requires_referral': True
            },
            {
                'item_number': '80195',
                'description': 'Clinical psychology service - group (trauma)',
                'service_type': MedicareItemNumber.ServiceType.CLINICAL_PSYCHOLOGIST,
                'standard_rebate': Decimal('88.25'),
                'safety_net_rebate': Decimal('88.25'),
                'min_session_duration': 50,
                'max_sessions_per_year': 16,
                'requires_referral': True
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for item_data in medicare_items:
            item_number = item_data['item_number']
            
            # Check if item already exists
            if MedicareItemNumber.objects.filter(item_number=item_number).exists():
                # Update existing item
                medicare_item = MedicareItemNumber.objects.get(item_number=item_number)
                for key, value in item_data.items():
                    setattr(medicare_item, key, value)
                medicare_item.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated Medicare item {item_number}')
                )
            else:
                # Create new item
                MedicareItemNumber.objects.create(**item_data)
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created Medicare item {item_number}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded Medicare items: {created_count} created, {updated_count} updated'
            )
        )
