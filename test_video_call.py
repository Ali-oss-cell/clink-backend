#!/usr/bin/env python
"""
Video Call Test Script - Psychology Clinic
Creates test doctor and patient, books an appointment, and generates video tokens
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from django.contrib.auth import get_user_model
from appointments.models import Appointment
from appointments.video_service import get_video_service
from services.models import Service

User = get_user_model()

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def get_or_create_test_users():
    """Get or create test doctor and patient"""
    print_header("Step 1: Setting Up Test Users")
    
    # Check for existing test users
    doctor = User.objects.filter(email='test.doctor@clinic.test').first()
    patient = User.objects.filter(email='test.patient@clinic.test').first()
    
    if doctor and patient:
        print_info("Found existing test users")
        print_success(f"Doctor: {doctor.get_full_name()} ({doctor.email})")
        print_success(f"Patient: {patient.get_full_name()} ({patient.email})")
        return doctor, patient
    
    print_info("Creating new test users...")
    
    # Create test doctor (psychologist)
    if not doctor:
        doctor = User.objects.create_user(
            email='test.doctor@clinic.test',
            password='test123',
            first_name='Dr. Sarah',
            last_name='Thompson',
            role=User.UserRole.PSYCHOLOGIST,
            phone_number='+61412345678',
            is_active=True
        )
        print_success(f"Created doctor user: {doctor.get_full_name()} ({doctor.email})")
    
    # Ensure psychologist profile exists (create if missing)
    from services.models import PsychologistProfile
    from datetime import date, timedelta
    from decimal import Decimal, ROUND_HALF_UP
    try:
        # Generate valid AHPRA number: PSY + 10 digits (e.g., PSY0000000001)
        ahpra_number = f'PSY{doctor.id:010d}'  # Pad to 10 digits
        profile, created = PsychologistProfile.objects.get_or_create(
            user=doctor,
            defaults={
                'ahpra_registration_number': ahpra_number,
                'ahpra_expiry_date': date.today() + timedelta(days=365),  # Expires in 1 year
                'consultation_fee': Decimal('180.00'),
                'medicare_rebate_amount': Decimal('87.45').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                'years_experience': 10,
                'bio': 'Experienced clinical psychologist specializing in anxiety and depression.',
                'qualifications': 'PhD in Clinical Psychology',
                'title': 'Dr',
                'has_professional_indemnity_insurance': True
            }
        )
        if created:
            print_success(f"Created psychologist profile for {doctor.get_full_name()}")
        else:
            print_info(f"Psychologist profile already exists for {doctor.get_full_name()}")
    except Exception as e:
        print_error(f"Error creating psychologist profile: {str(e)}")
        # Try to get existing profile
        try:
            profile = doctor.psychologist_profile
            print_info(f"Using existing psychologist profile")
        except:
            print_error("Could not create or retrieve psychologist profile")
            raise
    
    # Create test patient
    if not patient:
        from datetime import date
        patient = User.objects.create_user(
            email='test.patient@clinic.test',
            password='test123',
            first_name='John',
            last_name='Smith',
            role=User.UserRole.PATIENT,
            phone_number='+61498765432',
            date_of_birth=date(1990, 1, 15),
            gender='male',
            is_active=True
        )
        
        # Create patient profile
        from users.models import PatientProfile
        PatientProfile.objects.get_or_create(
            user=patient,
            defaults={
                'gender_identity': 'male',
                'emergency_contact_name': 'Jane Smith',
                'emergency_contact_phone': '+61412345679',
                'emergency_contact_relationship': 'spouse',
                'preferred_name': 'John'
            }
        )
        print_success(f"Created patient: {patient.get_full_name()} ({patient.email})")
    
    return doctor, patient

def get_or_create_service(doctor):
    """Get or create test service"""
    from services.models import PsychologistProfile
    # Ensure psychologist profile exists
    try:
        profile = doctor.psychologist_profile
    except PsychologistProfile.DoesNotExist:
        from datetime import date, timedelta
        from decimal import Decimal, ROUND_HALF_UP
        # Generate valid AHPRA number: PSY + 10 digits (e.g., PSY0000000001)
        ahpra_number = f'PSY{doctor.id:010d}'  # Pad to 10 digits
        PsychologistProfile.objects.get_or_create(
            user=doctor,
            defaults={
                'ahpra_registration_number': ahpra_number,
                'ahpra_expiry_date': date.today() + timedelta(days=365),
                'consultation_fee': Decimal('180.00'),
                'medicare_rebate_amount': Decimal('87.45').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                'years_experience': 10,
                'bio': 'Experienced clinical psychologist specializing in anxiety and depression.',
                'qualifications': 'PhD in Clinical Psychology',
                'title': 'Dr',
                'has_professional_indemnity_insurance': True
            }
        )
        doctor.refresh_from_db()  # Refresh to get the profile
    
    # Services are clinic-wide, not tied to specific psychologist
    service = Service.objects.filter(
        name__icontains='telehealth'
    ).first()
    
    if not service:
        service = Service.objects.create(
            name='Telehealth Consultation',
            description='Online video consultation',
            duration_minutes=60,
            standard_fee=180.00,
            medicare_rebate=87.45,
            is_telehealth_available=True,
            is_active=True
        )
        print_success("Created test service: Telehealth Consultation")
        
        # Optionally add to psychologist's services_offered
        if hasattr(doctor, 'psychologist_profile'):
            doctor.psychologist_profile.services_offered.add(service)
    else:
        print_info(f"Using existing service: {service.name}")
    
    return service

def create_test_appointment(doctor, patient, service, minutes_from_now=5):
    """Create a test appointment"""
    print_header("Step 2: Creating Test Appointment")
    
    # Calculate appointment time
    appointment_time = timezone.now() + timedelta(minutes=minutes_from_now)
    
    print_info(f"Scheduling appointment for: {appointment_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"(In {minutes_from_now} minutes from now)")
    
    # Create appointment
    appointment = Appointment.objects.create(
        patient=patient,
        psychologist=doctor,
        service=service,
        appointment_date=appointment_time,  # DateTimeField, not separate date/time
        duration_minutes=60,
        session_type='telehealth',  # session_type, not appointment_type
        status='confirmed',
        notes='Test video call appointment'
    )
    
    print_success(f"Created appointment ID: {appointment.id}")
    print_success(f"Appointment date/time: {appointment.appointment_date}")
    print_success(f"Session type: {appointment.session_type}")
    
    return appointment

def create_video_room(appointment):
    """Create Twilio video room for appointment"""
    print_header("Step 3: Creating Video Room")
    
    try:
        video_service = get_video_service()
        
        # Validate credentials first
        print_info("Validating Twilio credentials...")
        validation = video_service.validate_credentials()
        
        if not validation.get('valid'):
            print_error(f"Twilio credentials invalid: {validation.get('error')}")
            return False
        
        if not validation.get('api_key_valid'):
            print_error(f"API Key invalid: {validation.get('api_key_error')}")
            return False
        
        print_success("Twilio credentials valid")
        
        # Create room
        print_info("Creating video room...")
        room_data = video_service.create_room(
            appointment_id=appointment.id,
            appointment_date=appointment.appointment_date,
            enable_recording=False  # Disable recording for test
        )
        
        # Save room details to appointment
        appointment.video_room_id = room_data['room_name']
        appointment.video_room_sid = room_data['room_sid']
        appointment.save()
        
        print_success(f"Video room created: {room_data['room_name']}")
        print_success(f"Room SID: {room_data['room_sid']}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to create video room: {str(e)}")
        return False

def generate_tokens(appointment, doctor, patient):
    """Generate video access tokens for both users"""
    print_header("Step 4: Generating Video Access Tokens")
    
    try:
        video_service = get_video_service()
        
        # Generate doctor token
        doctor_identity = f"{doctor.id}-{doctor.email}"
        doctor_token = video_service.generate_access_token(
            user_identity=doctor_identity,
            room_name=appointment.video_room_id,
            ttl_hours=2
        )
        
        # Generate patient token
        patient_identity = f"{patient.id}-{patient.email}"
        patient_token = video_service.generate_access_token(
            user_identity=patient_identity,
            room_name=appointment.video_room_id,
            ttl_hours=2
        )
        
        print_success("Tokens generated successfully")
        
        return {
            'doctor': {
                'identity': doctor_identity,
                'token': doctor_token
            },
            'patient': {
                'identity': patient_identity,
                'token': patient_token
            }
        }
        
    except Exception as e:
        print_error(f"Failed to generate tokens: {str(e)}")
        return None

def print_results(appointment, doctor, patient, tokens):
    """Print test results and instructions"""
    print_header("✅ Test Setup Complete!")
    
    print(f"\n{Colors.BOLD}Test Users:{Colors.ENDC}")
    print(f"  Doctor:  {doctor.email} / password: test123")
    print(f"  Patient: {patient.email} / password: test123")
    
    print(f"\n{Colors.BOLD}Appointment Details:{Colors.ENDC}")
    print(f"  ID: {appointment.id}")
    print(f"  Date: {appointment.appointment_date}")
    print(f"  Time: {appointment.start_time}")
    print(f"  Room: {appointment.video_room_id}")
    
    print(f"\n{Colors.BOLD}API Endpoints to Test:{Colors.ENDC}")
    print(f"\n  {Colors.OKCYAN}1. Get Doctor Token:{Colors.ENDC}")
    print(f"     GET https://api.tailoredpsychology.com.au/api/appointments/video-token/{appointment.id}/")
    print(f"     Authorization: Bearer <doctor_jwt_token>")
    
    print(f"\n  {Colors.OKCYAN}2. Get Patient Token:{Colors.ENDC}")
    print(f"     GET https://api.tailoredpsychology.com.au/api/appointments/video-token/{appointment.id}/")
    print(f"     Authorization: Bearer <patient_jwt_token>")
    
    print(f"\n{Colors.BOLD}Direct Tokens (for quick testing):{Colors.ENDC}")
    
    print(f"\n  {Colors.OKGREEN}Doctor Token:{Colors.ENDC}")
    print(f"    Identity: {tokens['doctor']['identity']}")
    print(f"    Token: {tokens['doctor']['token'][:50]}...")
    
    print(f"\n  {Colors.OKGREEN}Patient Token:{Colors.ENDC}")
    print(f"    Identity: {tokens['patient']['identity']}")
    print(f"    Token: {tokens['patient']['token'][:50]}...")
    
    print(f"\n{Colors.BOLD}How to Test:{Colors.ENDC}")
    print(f"  1. Login as doctor in your frontend: {doctor.email}")
    print(f"  2. Login as patient in another browser: {patient.email}")
    print(f"  3. Both join the video call for appointment {appointment.id}")
    print(f"  4. Tokens are valid for 2 hours")
    
    print(f"\n{Colors.BOLD}Test Commands:{Colors.ENDC}")
    print(f"  # Login as doctor")
    print(f"  curl -X POST https://api.tailoredpsychology.com.au/api/auth/login/ \\")
    print(f"    -H \"Content-Type: application/json\" \\")
    print(f"    -d '{{\"email\": \"{doctor.email}\", \"password\": \"test123\"}}'")
    
    print(f"\n  # Login as patient")
    print(f"  curl -X POST https://api.tailoredpsychology.com.au/api/auth/login/ \\")
    print(f"    -H \"Content-Type: application/json\" \\")
    print(f"    -d '{{\"email\": \"{patient.email}\", \"password\": \"test123\"}}'")
    
    print(f"\n{Colors.WARNING}Note: Run this script again to create a new test appointment{Colors.ENDC}")
    print(f"{Colors.WARNING}      The same test users will be reused{Colors.ENDC}\n")

def main():
    """Main test function"""
    print_header("🎥 Video Call Test Script")
    
    try:
        # Step 1: Get or create test users
        doctor, patient = get_or_create_test_users()
        
        # Get or create service
        service = get_or_create_service(doctor)
        
        # Step 2: Create test appointment
        print_info("\nHow many minutes from now should the appointment be?")
        try:
            minutes = int(input(f"{Colors.OKCYAN}Enter minutes (default: 5): {Colors.ENDC}") or "5")
        except ValueError:
            minutes = 5
        
        appointment = create_test_appointment(doctor, patient, service, minutes)
        
        # Step 3: Create video room
        if not create_video_room(appointment):
            print_error("\nFailed to create video room. Check your Twilio credentials.")
            print_info("Run this on your Droplet to verify:")
            print_info("  python manage.py shell")
            print_info("  from appointments.video_service import get_video_service")
            print_info("  video_service = get_video_service()")
            print_info("  print(video_service.validate_credentials())")
            sys.exit(1)
        
        # Step 4: Generate tokens
        tokens = generate_tokens(appointment, doctor, patient)
        
        if not tokens:
            print_error("\nFailed to generate tokens. Check your Twilio API Key.")
            sys.exit(1)
        
        # Print results
        print_results(appointment, doctor, patient, tokens)
        
    except Exception as e:
        print_error(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

