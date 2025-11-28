#!/usr/bin/env python
"""
Script to fix psychologists without profiles
Creates missing PsychologistProfile for psychologists who don't have one

Usage:
    python fix_psychologists.py                    # Interactive mode (asks for each)
    python fix_psychologists.py --all              # Fix all automatically
    python fix_psychologists.py --id 3              # Fix specific ID
    python fix_psychologists.py --id 3 --id 4       # Fix multiple IDs
"""

import os
import sys
import django
import argparse
from datetime import date, timedelta
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from django.contrib.auth import get_user_model
from services.models import PsychologistProfile

User = get_user_model()


def generate_ahpra_number(user_id):
    """Generate a unique AHPRA number for a user"""
    # Format: PSY + 10 digits (using user ID padded with zeros)
    ahpra = f"PSY{str(user_id).zfill(10)}"
    return ahpra


def check_ahpra_exists(ahpra_number):
    """Check if AHPRA number already exists"""
    return PsychologistProfile.objects.filter(ahpra_registration_number=ahpra_number).exists()


def create_profile_for_psychologist(user, ahpra_number=None, ahpra_expiry_date=None, interactive=True):
    """Create a psychologist profile for a user"""
    
    # Generate AHPRA if not provided
    if not ahpra_number:
        ahpra_number = generate_ahpra_number(user.id)
        # Check if generated number exists, if so, try variations
        counter = 0
        original_ahpra = ahpra_number
        while check_ahpra_exists(ahpra_number):
            counter += 1
            # Try adding counter to make it unique
            ahpra_number = f"PSY{str(user.id).zfill(8)}{str(counter).zfill(2)}"
            if counter > 99:
                # Fallback: use timestamp
                import time
                timestamp = str(int(time.time()))[-6:]
                ahpra_number = f"PSY{timestamp}{str(user.id).zfill(4)}"
                break
    
    # Set expiry date (default: 1 year from today)
    if not ahpra_expiry_date:
        ahpra_expiry_date = date.today() + timedelta(days=365)
    
    # Interactive mode: ask for confirmation
    if interactive:
        print(f"\n{'='*60}")
        print(f"Creating Profile for Psychologist ID: {user.id}")
        print(f"{'='*60}")
        print(f"Name: {user.get_full_name()}")
        print(f"Email: {user.email}")
        print(f"\nProposed Profile Details:")
        print(f"  AHPRA Number: {ahpra_number}")
        print(f"  AHPRA Expiry: {ahpra_expiry_date}")
        print(f"  Title: Dr")
        print(f"  Consultation Fee: $180.00")
        print(f"  Medicare Rebate: $87.45")
        print(f"  Accepting New Patients: Yes")
        print(f"  Active Practitioner: Yes")
        
        response = input(f"\nCreate profile with these details? (y/n): ").strip().lower()
        if response != 'y':
            print("❌ Cancelled")
            return False
        
        # Ask for custom AHPRA if needed
        custom_ahpra = input(f"Enter custom AHPRA number (or press Enter to use {ahpra_number}): ").strip()
        if custom_ahpra:
            # Validate format
            cleaned = custom_ahpra.replace(' ', '').replace('-', '').replace('_', '').upper()
            if not cleaned.startswith('PSY') or len(cleaned) != 13:
                print("❌ Invalid AHPRA format. Must be PSY followed by 10 digits.")
                return False
            if check_ahpra_exists(cleaned):
                print(f"❌ AHPRA number {cleaned} already exists!")
                return False
            ahpra_number = cleaned
        
        # Ask for custom expiry date
        custom_expiry = input(f"Enter AHPRA expiry date YYYY-MM-DD (or press Enter for {ahpra_expiry_date}): ").strip()
        if custom_expiry:
            try:
                from datetime import datetime
                ahpra_expiry_date = datetime.strptime(custom_expiry, '%Y-%m-%d').date()
            except ValueError:
                print("❌ Invalid date format. Use YYYY-MM-DD")
                return False
    
    # Create the profile
    try:
        profile = PsychologistProfile.objects.create(
            user=user,
            ahpra_registration_number=ahpra_number,
            ahpra_expiry_date=ahpra_expiry_date,
            title='Dr',
            qualifications='',
            years_experience=0,
            consultation_fee=Decimal('180.00'),
            medicare_rebate_amount=Decimal('87.45'),
            medicare_provider_number='',
            bio='',
            is_accepting_new_patients=True,
            is_active_practitioner=True,
            telehealth_available=True,
            in_person_available=True
        )
        
        print(f"✅ Profile created successfully!")
        print(f"   Profile ID: {profile.id}")
        print(f"   AHPRA: {profile.ahpra_registration_number}")
        print(f"   Expiry: {profile.ahpra_expiry_date}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating profile: {str(e)}")
        return False


def find_psychologists_without_profiles():
    """Find all psychologists without profiles"""
    psychologists = User.objects.filter(role=User.UserRole.PSYCHOLOGIST)
    without_profiles = []
    
    for psych in psychologists:
        try:
            psych.psychologist_profile
        except PsychologistProfile.DoesNotExist:
            without_profiles.append(psych)
    
    return without_profiles


def main():
    parser = argparse.ArgumentParser(description='Fix psychologists without profiles')
    parser.add_argument('--all', action='store_true', help='Fix all psychologists without profiles automatically')
    parser.add_argument('--id', type=int, action='append', dest='ids', help='Fix specific psychologist ID(s)')
    parser.add_argument('--non-interactive', action='store_true', help='Non-interactive mode (use defaults)')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print("Fix Psychologists Without Profiles")
    print(f"{'='*60}\n")
    
    # Find psychologists without profiles
    psychologists_without_profiles = find_psychologists_without_profiles()
    
    if not psychologists_without_profiles:
        print("✅ All psychologists have profiles! Nothing to fix.")
        return
    
    print(f"Found {len(psychologists_without_profiles)} psychologist(s) without profiles:\n")
    for psych in psychologists_without_profiles:
        print(f"  ID: {psych.id} | {psych.get_full_name()} | {psych.email}")
    
    # Handle specific IDs
    if args.ids:
        fixed_count = 0
        for psych_id in args.ids:
            try:
                user = User.objects.get(id=psych_id, role=User.UserRole.PSYCHOLOGIST)
                try:
                    user.psychologist_profile
                    print(f"\n✅ Psychologist {psych_id} already has a profile. Skipping.")
                except PsychologistProfile.DoesNotExist:
                    if create_profile_for_psychologist(user, interactive=not args.non_interactive):
                        fixed_count += 1
            except User.DoesNotExist:
                print(f"\n❌ Psychologist {psych_id} not found or not a psychologist!")
        
        print(f"\n{'='*60}")
        print(f"✅ Fixed {fixed_count} psychologist(s)")
        print(f"{'='*60}\n")
        return
    
    # Handle --all flag
    if args.all:
        print(f"\nFixing all {len(psychologists_without_profiles)} psychologist(s)...\n")
        fixed_count = 0
        for psych in psychologists_without_profiles:
            if create_profile_for_psychologist(psych, interactive=not args.non_interactive):
                fixed_count += 1
        
        print(f"\n{'='*60}")
        print(f"✅ Fixed {fixed_count} out of {len(psychologists_without_profiles)} psychologist(s)")
        print(f"{'='*60}\n")
        return
    
    # Interactive mode: ask for each
    print(f"\n{'='*60}")
    print("Interactive Mode")
    print(f"{'='*60}\n")
    print("Options:")
    print("  1. Fix all automatically")
    print("  2. Fix one by one (interactive)")
    print("  3. Exit")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == '1':
        fixed_count = 0
        for psych in psychologists_without_profiles:
            if create_profile_for_psychologist(psych, interactive=False):
                fixed_count += 1
        print(f"\n✅ Fixed {fixed_count} psychologist(s)")
    elif choice == '2':
        fixed_count = 0
        for psych in psychologists_without_profiles:
            if create_profile_for_psychologist(psych, interactive=True):
                fixed_count += 1
        print(f"\n✅ Fixed {fixed_count} psychologist(s)")
    else:
        print("Exiting...")


if __name__ == '__main__':
    main()

