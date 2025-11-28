#!/usr/bin/env python
"""
Diagnostic script to check psychologist existence and profile
Run: python check_psychologist.py [psychologist_id]
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from django.contrib.auth import get_user_model
from services.models import PsychologistProfile

User = get_user_model()

def check_psychologist(psychologist_id):
    """Check if psychologist exists and has a profile"""
    print(f"\n{'='*60}")
    print(f"Checking Psychologist ID: {psychologist_id}")
    print(f"{'='*60}\n")
    
    try:
        # Check if user exists
        user = User.objects.get(id=psychologist_id)
        print(f"✅ User {psychologist_id} exists")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.get_full_name()}")
        print(f"   Role: {user.role}")
        
        # Check if user is a psychologist
        if user.role != User.UserRole.PSYCHOLOGIST:
            print(f"\n❌ ERROR: User {psychologist_id} is NOT a psychologist!")
            print(f"   Current role: {user.role}")
            print(f"   Required role: {User.UserRole.PSYCHOLOGIST}")
            print(f"\n💡 SOLUTION: Update user role to 'psychologist'")
            return False
        
        print(f"✅ User is a psychologist")
        
        # Check if psychologist profile exists
        try:
            profile = PsychologistProfile.objects.get(user=user)
            print(f"✅ Psychologist profile exists")
            print(f"   AHPRA Number: {profile.ahpra_registration_number}")
            print(f"   Title: {profile.title}")
            print(f"   Is Active: {profile.is_active_practitioner}")
            print(f"   Accepting New Patients: {profile.is_accepting_new_patients}")
            print(f"   Telehealth Available: {profile.telehealth_available}")
            print(f"   In-Person Available: {profile.in_person_available}")
            
            return True
            
        except PsychologistProfile.DoesNotExist:
            print(f"\n❌ ERROR: Psychologist profile does NOT exist!")
            print(f"   User {psychologist_id} is a psychologist but has no profile.")
            print(f"\n💡 SOLUTION: Create a psychologist profile")
            return False
            
    except User.DoesNotExist:
        print(f"\n❌ ERROR: User {psychologist_id} does NOT exist!")
        print(f"\n💡 SOLUTION: Create a psychologist user first")
        return False

def list_all_psychologists():
    """List all psychologists with profiles"""
    print(f"\n{'='*60}")
    print("All Psychologists in Database")
    print(f"{'='*60}\n")
    
    psychologists = User.objects.filter(role=User.UserRole.PSYCHOLOGIST)
    
    if not psychologists.exists():
        print("❌ No psychologists found in database!")
        return
    
    print(f"Found {psychologists.count()} psychologist(s):\n")
    
    for psych in psychologists:
        print(f"ID: {psych.id} | {psych.get_full_name()} | {psych.email}")
        try:
            profile = psych.psychologist_profile
            print(f"   ✅ Has Profile | AHPRA: {profile.ahpra_registration_number}")
            print(f"   Active: {profile.is_active_practitioner} | Accepting: {profile.is_accepting_new_patients}")
        except PsychologistProfile.DoesNotExist:
            print(f"   ❌ NO PROFILE")
        print()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        psychologist_id = int(sys.argv[1])
        check_psychologist(psychologist_id)
    else:
        # List all psychologists
        list_all_psychologists()
        print("\n" + "="*60)
        print("To check a specific psychologist, run:")
        print("  python check_psychologist.py <psychologist_id>")
        print("="*60 + "\n")

