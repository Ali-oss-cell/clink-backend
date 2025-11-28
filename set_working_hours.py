#!/usr/bin/env python
"""
Script to set working hours for psychologists who don't have them
This fixes the "No Available Appointments" issue

Usage:
    python set_working_hours.py                    # Interactive mode
    python set_working_hours.py --all               # Set for all automatically
    python set_working_hours.py --id 5              # Set for specific ID
"""

import os
import sys
import django
import argparse
from datetime import time as dt_time

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from django.contrib.auth import get_user_model
from services.models import PsychologistProfile

User = get_user_model()


def set_working_hours_for_psychologist(user, interactive=True):
    """Set working hours for a psychologist"""
    
    try:
        profile = PsychologistProfile.objects.get(user=user)
    except PsychologistProfile.DoesNotExist:
        print(f"❌ Psychologist {user.id} has no profile. Run fix_psychologists.py first.")
        return False
    
    # Check if already has working hours
    if profile.working_days and profile.start_time and profile.end_time:
        print(f"✅ Psychologist {user.id} ({user.get_full_name()}) already has working hours:")
        print(f"   Days: {profile.working_days}")
        print(f"   Time: {profile.start_time} - {profile.end_time}")
        if interactive:
            response = input("   Update anyway? (y/n): ").strip().lower()
            if response != 'y':
                return False
    
    # Default working hours
    default_working_days = 'Monday,Tuesday,Wednesday,Thursday,Friday'
    default_start_time = dt_time(9, 0)  # 9:00 AM
    default_end_time = dt_time(17, 0)   # 5:00 PM
    default_session_duration = 50
    default_break_duration = 10
    
    if interactive:
        print(f"\n{'='*60}")
        print(f"Setting Working Hours for: {user.get_full_name()}")
        print(f"{'='*60}")
        print(f"Current:")
        print(f"  Working Days: {profile.working_days or 'NOT SET'}")
        print(f"  Start Time: {profile.start_time or 'NOT SET'}")
        print(f"  End Time: {profile.end_time or 'NOT SET'}")
        print(f"  Session Duration: {profile.session_duration_minutes} minutes")
        print(f"  Break Duration: {profile.break_between_sessions_minutes} minutes")
        print(f"\nDefaults:")
        print(f"  Working Days: {default_working_days}")
        print(f"  Start Time: {default_start_time}")
        print(f"  End Time: {default_end_time}")
        print(f"  Session Duration: {default_session_duration} minutes")
        print(f"  Break Duration: {default_break_duration} minutes")
        
        # Ask for custom values
        working_days = input(f"\nEnter working days (comma-separated, or Enter for {default_working_days}): ").strip()
        if not working_days:
            working_days = default_working_days
        
        start_time_str = input(f"Enter start time HH:MM (or Enter for {default_start_time}): ").strip()
        if not start_time_str:
            start_time = default_start_time
        else:
            try:
                hour, minute = map(int, start_time_str.split(':'))
                start_time = dt_time(hour, minute)
            except ValueError:
                print("❌ Invalid time format. Using default.")
                start_time = default_start_time
        
        end_time_str = input(f"Enter end time HH:MM (or Enter for {default_end_time}): ").strip()
        if not end_time_str:
            end_time = default_end_time
        else:
            try:
                hour, minute = map(int, end_time_str.split(':'))
                end_time = dt_time(hour, minute)
            except ValueError:
                print("❌ Invalid time format. Using default.")
                end_time = default_end_time
        
        session_duration_str = input(f"Enter session duration in minutes (or Enter for {default_session_duration}): ").strip()
        session_duration = int(session_duration_str) if session_duration_str else default_session_duration
        
        break_duration_str = input(f"Enter break duration in minutes (or Enter for {default_break_duration}): ").strip()
        break_duration = int(break_duration_str) if break_duration_str else default_break_duration
    else:
        # Non-interactive: use defaults
        working_days = default_working_days
        start_time = default_start_time
        end_time = default_end_time
        session_duration = default_session_duration
        break_duration = default_break_duration
    
    # Update profile
    try:
        profile.working_days = working_days
        profile.start_time = start_time
        profile.end_time = end_time
        profile.session_duration_minutes = session_duration
        profile.break_between_sessions_minutes = break_duration
        profile.save()
        
        print(f"✅ Working hours set successfully!")
        print(f"   Days: {profile.working_days}")
        print(f"   Time: {profile.start_time} - {profile.end_time}")
        print(f"   Session: {profile.session_duration_minutes} minutes")
        print(f"   Break: {profile.break_between_sessions_minutes} minutes")
        print(f"\n💡 Time slots will be generated automatically when patients view availability.")
        return True
        
    except Exception as e:
        print(f"❌ Error setting working hours: {str(e)}")
        return False


def find_psychologists_without_working_hours():
    """Find all psychologists without working hours"""
    psychologists = User.objects.filter(role=User.UserRole.PSYCHOLOGIST)
    without_hours = []
    
    for psych in psychologists:
        try:
            profile = psych.psychologist_profile
            if not profile.working_days or not profile.start_time or not profile.end_time:
                without_hours.append(psych)
        except PsychologistProfile.DoesNotExist:
            # Skip - no profile
            pass
    
    return without_hours


def main():
    parser = argparse.ArgumentParser(description='Set working hours for psychologists')
    parser.add_argument('--all', action='store_true', help='Set working hours for all psychologists automatically')
    parser.add_argument('--id', type=int, action='append', dest='ids', help='Set working hours for specific psychologist ID(s)')
    parser.add_argument('--non-interactive', action='store_true', help='Non-interactive mode (use defaults)')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print("Set Working Hours for Psychologists")
    print(f"{'='*60}\n")
    
    # Find psychologists without working hours
    psychologists_without_hours = find_psychologists_without_working_hours()
    
    if not psychologists_without_hours:
        print("✅ All psychologists have working hours set! Nothing to fix.")
        return
    
    print(f"Found {len(psychologists_without_hours)} psychologist(s) without working hours:\n")
    for psych in psychologists_without_hours:
        try:
            profile = psych.psychologist_profile
            print(f"  ID: {psych.id} | {psych.get_full_name()} | {psych.email}")
            print(f"      Days: {profile.working_days or 'NOT SET'}")
            print(f"      Time: {profile.start_time or 'NOT SET'} - {profile.end_time or 'NOT SET'}")
        except PsychologistProfile.DoesNotExist:
            print(f"  ID: {psych.id} | {psych.get_full_name()} | {psych.email} (NO PROFILE)")
        print()
    
    # Handle specific IDs
    if args.ids:
        fixed_count = 0
        for psych_id in args.ids:
            try:
                user = User.objects.get(id=psych_id, role=User.UserRole.PSYCHOLOGIST)
                if set_working_hours_for_psychologist(user, interactive=not args.non_interactive):
                    fixed_count += 1
            except User.DoesNotExist:
                print(f"\n❌ Psychologist {psych_id} not found or not a psychologist!")
        
        print(f"\n{'='*60}")
        print(f"✅ Set working hours for {fixed_count} psychologist(s)")
        print(f"{'='*60}\n")
        return
    
    # Handle --all flag
    if args.all:
        print(f"\nSetting working hours for all {len(psychologists_without_hours)} psychologist(s)...\n")
        fixed_count = 0
        for psych in psychologists_without_hours:
            if set_working_hours_for_psychologist(psych, interactive=not args.non_interactive):
                fixed_count += 1
        
        print(f"\n{'='*60}")
        print(f"✅ Set working hours for {fixed_count} out of {len(psychologists_without_hours)} psychologist(s)")
        print(f"{'='*60}\n")
        return
    
    # Interactive mode: ask for each
    print(f"\n{'='*60}")
    print("Interactive Mode")
    print(f"{'='*60}\n")
    print("Options:")
    print("  1. Set for all automatically")
    print("  2. Set one by one (interactive)")
    print("  3. Exit")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == '1':
        fixed_count = 0
        for psych in psychologists_without_hours:
            if set_working_hours_for_psychologist(psych, interactive=False):
                fixed_count += 1
        print(f"\n✅ Set working hours for {fixed_count} psychologist(s)")
    elif choice == '2':
        fixed_count = 0
        for psych in psychologists_without_hours:
            if set_working_hours_for_psychologist(psych, interactive=True):
                fixed_count += 1
        print(f"\n✅ Set working hours for {fixed_count} psychologist(s)")
    else:
        print("Exiting...")


if __name__ == '__main__':
    main()

