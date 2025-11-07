"""
Script to create sample psychology services
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from services.models import Service, Specialization

# Create services if they don't exist
services_data = [
    {
        'name': 'Individual Therapy',
        'service_type': 'individual',
        'description': 'One-on-one therapy session with a qualified psychologist',
        'duration_minutes': 50,
        'standard_fee': 180.00,
        'medicare_rebate': 87.45,
        'medicare_item_number': '80000',
        'is_active': True
    },
    {
        'name': 'Couples Therapy',
        'service_type': 'couples',
        'description': 'Therapy session for couples to improve communication and resolve conflicts',
        'duration_minutes': 60,
        'standard_fee': 220.00,
        'medicare_rebate': 0.00,
        'medicare_item_number': '',
        'is_active': True
    },
    {
        'name': 'Family Therapy',
        'service_type': 'family',
        'description': 'Therapy session for families to address relationship issues and improve communication',
        'duration_minutes': 60,
        'standard_fee': 220.00,
        'medicare_rebate': 0.00,
        'medicare_item_number': '',
        'is_active': True
    },
    {
        'name': 'Psychological Assessment',
        'service_type': 'assessment',
        'description': 'Comprehensive psychological assessment and testing',
        'duration_minutes': 90,
        'standard_fee': 350.00,
        'medicare_rebate': 131.55,
        'medicare_item_number': '80110',
        'is_active': True
    },
    {
        'name': 'Group Therapy',
        'service_type': 'group',
        'description': 'Therapy session in a small group setting',
        'duration_minutes': 90,
        'standard_fee': 100.00,
        'medicare_rebate': 43.55,
        'medicare_item_number': '80020',
        'is_active': True
    }
]

print("Creating sample services...")
created_count = 0
for service_data in services_data:
    service, created = Service.objects.get_or_create(
        name=service_data['name'],
        defaults=service_data
    )
    if created:
        created_count += 1
        print(f"✅ Created: {service.name}")
    else:
        print(f"   Already exists: {service.name}")

print(f"\nTotal services in database: {Service.objects.count()}")
print(f"Active services: {Service.objects.filter(is_active=True).count()}")

# Create specializations if they don't exist
specializations_data = [
    {'name': 'Anxiety Disorders', 'description': 'Treatment of anxiety, panic attacks, and phobias', 'is_active': True},
    {'name': 'Depression', 'description': 'Treatment of depression and mood disorders', 'is_active': True},
    {'name': 'ADHD', 'description': 'Assessment and treatment of ADHD', 'is_active': True},
    {'name': 'Trauma & PTSD', 'description': 'Trauma-informed therapy and PTSD treatment', 'is_active': True},
    {'name': 'Couples Counseling', 'description': 'Relationship therapy and marriage counseling', 'is_active': True},
    {'name': 'Child Psychology', 'description': 'Therapy and assessment for children', 'is_active': True},
    {'name': 'Stress Management', 'description': 'Stress reduction and coping strategies', 'is_active': True},
    {'name': 'Eating Disorders', 'description': 'Treatment of anorexia, bulimia, and binge eating', 'is_active': True},
]

print("\nCreating specializations...")
spec_count = 0
for spec_data in specializations_data:
    spec, created = Specialization.objects.get_or_create(
        name=spec_data['name'],
        defaults=spec_data
    )
    if created:
        spec_count += 1
        print(f"✅ Created: {spec.name}")
    else:
        print(f"   Already exists: {spec.name}")

print(f"\nTotal specializations in database: {Specialization.objects.count()}")
print(f"Active specializations: {Specialization.objects.filter(is_active=True).count()}")

print("\n✅ Sample data creation complete!")

