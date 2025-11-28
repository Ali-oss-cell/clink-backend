#!/usr/bin/env python
"""
Diagnostic script to check available services
Run: python check_services.py
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from services.models import Service

def list_all_services():
    """List all services in the database"""
    print(f"\n{'='*60}")
    print("All Services in Database")
    print(f"{'='*60}\n")
    
    services = Service.objects.all().order_by('id')
    
    if not services.exists():
        print("❌ No services found in database!")
        print("\n💡 SOLUTION: Create services via Django admin or API")
        return
    
    print(f"Found {services.count()} service(s):\n")
    
    for service in services:
        status = "✅ Active" if service.is_active else "❌ Inactive"
        print(f"ID: {service.id} | {service.name}")
        print(f"   Status: {status}")
        print(f"   Type: {service.service_type}")
        print(f"   Duration: {service.duration_minutes} minutes")
        print(f"   Fee: ${service.standard_fee}")
        print(f"   Medicare Rebate: ${service.medicare_rebate}")
        print(f"   Telehealth: {'Yes' if service.is_telehealth_available else 'No'}")
        print()
    
    print(f"{'='*60}")
    print("Active Services (for booking):")
    print(f"{'='*60}\n")
    
    active_services = Service.objects.filter(is_active=True)
    if active_services.exists():
        for service in active_services:
            print(f"  ID: {service.id} - {service.name}")
    else:
        print("  ❌ No active services found!")
        print("  💡 SOLUTION: Activate services or create new ones")
    
    print()

if __name__ == '__main__':
    list_all_services()

