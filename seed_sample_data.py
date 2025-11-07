#!/usr/bin/env python
"""
Sample Data Seeding Script for Psychology Clinic
Creates patients, links them to psychologists, adds progress notes, and schedules appointments
"""

import os
import sys
import django
from datetime import datetime, timedelta, time
import pytz
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from users.models import User, PatientProfile, ProgressNote
from services.models import PsychologistProfile, Service, Specialization
from appointments.models import Appointment, TimeSlot, AvailabilitySlot
from django.utils import timezone
from django.contrib.auth.hashers import make_password

def create_sample_patients():
    """Create sample patients with different demographics and conditions"""
    
    patients_data = [
        {
            'email': 'alice.smith@email.com',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'phone_number': '+61400123456',
            'date_of_birth': '1990-05-15',
            'address_line_1': '123 Collins Street',
            'suburb': 'Melbourne',
            'state': 'VIC',
            'postcode': '3000',
            'medicare_number': '1234567890',
            'condition': 'Anxiety',
            'therapy_goals': 'Manage anxiety, improve sleep quality, reduce panic attacks'
        },
        {
            'email': 'john.doe@email.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '+61400123457',
            'date_of_birth': '1985-08-22',
            'address_line_1': '456 Bourke Street',
            'suburb': 'Melbourne',
            'state': 'VIC',
            'postcode': '3000',
            'medicare_number': '1234567891',
            'condition': 'Depression',
            'therapy_goals': 'Overcome depression, build self-esteem, improve relationships'
        },
        {
            'email': 'emma.wilson@email.com',
            'first_name': 'Emma',
            'last_name': 'Wilson',
            'phone_number': '+61400123458',
            'date_of_birth': '1992-12-03',
            'address_line_1': '789 Swanston Street',
            'suburb': 'Melbourne',
            'state': 'VIC',
            'postcode': '3000',
            'medicare_number': '1234567892',
            'condition': 'ADHD',
            'therapy_goals': 'Improve focus, manage impulsivity, develop coping strategies'
        },
        {
            'email': 'michael.brown@email.com',
            'first_name': 'Michael',
            'last_name': 'Brown',
            'phone_number': '+61400123459',
            'date_of_birth': '1988-03-18',
            'address_line_1': '321 Flinders Street',
            'suburb': 'Melbourne',
            'state': 'VIC',
            'postcode': '3000',
            'medicare_number': '1234567893',
            'condition': 'PTSD',
            'therapy_goals': 'Process trauma, reduce flashbacks, improve daily functioning'
        },
        {
            'email': 'sophie.davis@email.com',
            'first_name': 'Sophie',
            'last_name': 'Davis',
            'phone_number': '+61400123460',
            'date_of_birth': '1995-07-25',
            'address_line_1': '654 Elizabeth Street',
            'suburb': 'Melbourne',
            'state': 'VIC',
            'postcode': '3000',
            'medicare_number': '1234567894',
            'condition': 'Eating Disorder',
            'therapy_goals': 'Develop healthy relationship with food, improve body image'
        },
        {
            'email': 'david.miller@email.com',
            'first_name': 'David',
            'last_name': 'Miller',
            'phone_number': '+61400123461',
            'date_of_birth': '1983-11-12',
            'address_line_1': '987 Collins Street',
            'suburb': 'Melbourne',
            'state': 'VIC',
            'postcode': '3000',
            'medicare_number': '1234567895',
            'condition': 'OCD',
            'therapy_goals': 'Reduce compulsive behaviors, manage intrusive thoughts'
        },
        {
            'email': 'lisa.garcia@email.com',
            'first_name': 'Lisa',
            'last_name': 'Garcia',
            'phone_number': '+61400123462',
            'date_of_birth': '1991-09-08',
            'address_line_1': '147 Russell Street',
            'suburb': 'Melbourne',
            'state': 'VIC',
            'postcode': '3000',
            'medicare_number': '1234567896',
            'condition': 'Bipolar Disorder',
            'therapy_goals': 'Stabilize mood, develop routine, manage episodes'
        },
        {
            'email': 'robert.taylor@email.com',
            'first_name': 'Robert',
            'last_name': 'Taylor',
            'phone_number': '+61400123463',
            'date_of_birth': '1987-01-30',
            'address_line_1': '258 Little Collins Street',
            'suburb': 'Melbourne',
            'state': 'VIC',
            'postcode': '3000',
            'medicare_number': '1234567897',
            'condition': 'Social Anxiety',
            'therapy_goals': 'Build social confidence, reduce social avoidance'
        }
    ]
    
    created_patients = []
    
    for patient_data in patients_data:
        # Check if patient already exists
        if User.objects.filter(email=patient_data['email']).exists():
            print(f"Patient {patient_data['email']} already exists, skipping...")
            continue
            
        # Create user
        user = User.objects.create(
            username=patient_data['email'].split('@')[0],
            email=patient_data['email'],
            first_name=patient_data['first_name'],
            last_name=patient_data['last_name'],
            phone_number=patient_data['phone_number'],
            date_of_birth=patient_data['date_of_birth'],
            address_line_1=patient_data['address_line_1'],
            suburb=patient_data['suburb'],
            state=patient_data['state'],
            postcode=patient_data['postcode'],
            medicare_number=patient_data['medicare_number'],
            role=User.UserRole.PATIENT,
            is_verified=True,
            password=make_password('password123')  # Default password
        )
        
        # Create patient profile
        profile = PatientProfile.objects.create(
            user=user,
            preferred_name=patient_data['first_name'],
            gender_identity='Female' if patient_data['first_name'] in ['Alice', 'Emma', 'Sophie', 'Lisa'] else 'Male',
            presenting_concerns=f"Primary concern: {patient_data['condition']}. Seeking professional help for management and treatment.",
            therapy_goals=patient_data['therapy_goals'],
            intake_completed=True,
            consent_to_treatment=True,
            consent_to_telehealth=True,
            client_signature=f"{patient_data['first_name']} {patient_data['last_name']}",
            consent_date=timezone.now().date()
        )
        
        created_patients.append({
            'user': user,
            'profile': profile,
            'condition': patient_data['condition']
        })
        
        print(f"Created patient: {user.get_full_name()} ({user.email})")
    
    return created_patients

def create_progress_notes(patients, psychologists):
    """Create progress notes for patients"""
    
    note_templates = {
        'Anxiety': [
            {
                'subjective': 'Patient reports feeling anxious about upcoming work presentation. Physical symptoms include increased heart rate and sweating. Sleep has been disrupted for the past week.',
                'objective': 'Patient appeared tense during session, fidgeting with hands. Voice was slightly shaky. Maintained good eye contact and engaged well in conversation.',
                'assessment': 'Generalized anxiety disorder with situational triggers. Patient shows good insight into their condition and is motivated to work on coping strategies.',
                'plan': 'Continue CBT techniques. Practice deep breathing exercises daily. Schedule follow-up in 2 weeks to assess progress with presentation anxiety.'
            },
            {
                'subjective': 'Patient reports improvement in sleep quality after implementing relaxation techniques. Still experiences some anxiety in social situations but feels more confident.',
                'objective': 'Patient appeared more relaxed and confident. Good engagement in session. Reported completing homework assignments successfully.',
                'assessment': 'Positive progress noted. Patient is responding well to treatment. Anxiety levels have decreased from 8/10 to 5/10.',
                'plan': 'Introduce exposure therapy for social situations. Continue current treatment plan. Next session in 2 weeks.'
            }
        ],
        'Depression': [
            {
                'subjective': 'Patient reports feeling low mood for past 3 weeks. Loss of interest in previously enjoyable activities. Difficulty concentrating at work.',
                'objective': 'Patient appeared withdrawn and tired. Spoke quietly and slowly. Good rapport maintained despite low mood.',
                'assessment': 'Major depressive episode, moderate severity. Patient shows good insight and is willing to engage in treatment.',
                'plan': 'Begin cognitive behavioral therapy. Monitor mood daily using mood diary. Consider referral to psychiatrist for medication evaluation.'
            },
            {
                'subjective': 'Patient reports slight improvement in mood after starting treatment. More energy in the mornings. Still struggling with motivation but making small steps.',
                'objective': 'Patient appeared more animated and engaged. Smiled during session. Reported completing some activities from previous session.',
                'assessment': 'Early signs of improvement. Patient is responding well to CBT techniques. Depression severity reduced from 7/10 to 5/10.',
                'plan': 'Continue current treatment. Increase activity scheduling. Next session in 1 week.'
            }
        ],
        'ADHD': [
            {
                'subjective': 'Patient reports difficulty focusing at work and home. Frequently loses track of tasks. Feels overwhelmed by daily responsibilities.',
                'objective': 'Patient was fidgety during session but maintained attention when engaged. Good insight into their challenges.',
                'assessment': 'ADHD, predominantly inattentive type. Patient shows good self-awareness and motivation for treatment.',
                'plan': 'Implement organizational strategies and time management techniques. Consider environmental modifications. Follow-up in 2 weeks.'
            },
            {
                'subjective': 'Patient reports improvement in task completion using new strategies. Still struggles with distractions but feels more in control.',
                'objective': 'Patient appeared more focused and organized. Brought completed homework to session.',
                'assessment': 'Good progress with behavioral interventions. Patient is developing better coping strategies.',
                'plan': 'Continue current strategies. Introduce additional focus techniques. Next session in 2 weeks.'
            }
        ],
        'PTSD': [
            {
                'subjective': 'Patient reports frequent nightmares and flashbacks related to traumatic event. Avoids certain situations that trigger memories.',
                'objective': 'Patient appeared tense and hypervigilant. Good engagement in therapy despite emotional difficulty.',
                'assessment': 'Post-traumatic stress disorder. Patient is ready to begin trauma-focused therapy.',
                'plan': 'Begin EMDR therapy. Establish safety and stabilization techniques first. Weekly sessions recommended.'
            },
            {
                'subjective': 'Patient reports some reduction in nightmare frequency. Still experiences triggers but feels more equipped to handle them.',
                'objective': 'Patient appeared more relaxed and confident. Good progress in therapy engagement.',
                'assessment': 'Positive response to treatment. Patient is developing better coping mechanisms for trauma symptoms.',
                'plan': 'Continue EMDR therapy. Focus on processing specific traumatic memories. Next session in 1 week.'
            }
        ],
        'Eating Disorder': [
            {
                'subjective': 'Patient reports restrictive eating patterns and body image concerns. Feels anxious around food and meal times.',
                'objective': 'Patient appeared thin and anxious. Good engagement in therapy despite emotional difficulty.',
                'assessment': 'Eating disorder, restrictive type. Patient shows insight and motivation for recovery.',
                'plan': 'Begin cognitive behavioral therapy for eating disorders. Establish regular eating patterns. Weekly sessions recommended.'
            },
            {
                'subjective': 'Patient reports slight improvement in relationship with food. Still struggles with body image but is working on challenging negative thoughts.',
                'objective': 'Patient appeared more hopeful and engaged. Good progress in therapy.',
                'assessment': 'Early signs of recovery. Patient is responding well to treatment interventions.',
                'plan': 'Continue current treatment. Focus on body image work. Next session in 1 week.'
            }
        ],
        'OCD': [
            {
                'subjective': 'Patient reports intrusive thoughts about contamination and compulsive hand washing. Rituals are interfering with daily life.',
                'objective': 'Patient appeared anxious and engaged in subtle checking behaviors during session.',
                'assessment': 'Obsessive-compulsive disorder, contamination subtype. Patient is motivated for treatment.',
                'plan': 'Begin exposure and response prevention therapy. Start with least anxiety-provoking exposures. Weekly sessions.'
            },
            {
                'subjective': 'Patient reports some reduction in compulsive behaviors. Still experiences intrusive thoughts but feels more able to resist compulsions.',
                'objective': 'Patient appeared more relaxed and confident. Good engagement in therapy.',
                'assessment': 'Good progress with ERP therapy. Patient is developing better coping strategies.',
                'plan': 'Continue exposure therapy. Gradually increase exposure difficulty. Next session in 1 week.'
            }
        ],
        'Bipolar Disorder': [
            {
                'subjective': 'Patient reports recent manic episode followed by depressive episode. Mood instability affecting work and relationships.',
                'objective': 'Patient appeared stable during session. Good insight into their condition.',
                'assessment': 'Bipolar disorder, type I. Patient is currently stable and engaged in treatment.',
                'plan': 'Focus on mood monitoring and early warning signs. Develop crisis plan. Bi-weekly sessions.'
            },
            {
                'subjective': 'Patient reports better mood stability with current treatment. More aware of triggers and early warning signs.',
                'objective': 'Patient appeared stable and engaged. Good progress in therapy.',
                'assessment': 'Good response to treatment. Patient is developing better self-management skills.',
                'plan': 'Continue current treatment. Focus on maintaining stability. Next session in 2 weeks.'
            }
        ],
        'Social Anxiety': [
            {
                'subjective': 'Patient reports intense anxiety in social situations. Avoids social gatherings and feels judged by others.',
                'objective': 'Patient appeared anxious but engaged well in one-on-one therapy session.',
                'assessment': 'Social anxiety disorder. Patient shows good insight and motivation for treatment.',
                'plan': 'Begin cognitive restructuring and gradual exposure therapy. Weekly sessions recommended.'
            },
            {
                'subjective': 'Patient reports slight improvement in social confidence. Attended one small social gathering with reduced anxiety.',
                'objective': 'Patient appeared more confident and hopeful. Good engagement in therapy.',
                'assessment': 'Positive progress with treatment. Patient is developing better social skills and confidence.',
                'plan': 'Continue exposure therapy. Gradually increase social challenges. Next session in 1 week.'
            }
        ]
    }
    
    created_notes = []
    
    for patient_info in patients:
        user = patient_info['user']
        condition = patient_info['condition']
        
        # Assign to random psychologist
        psychologist = random.choice(psychologists)
        
        # Create 2-4 progress notes per patient
        num_notes = random.randint(2, 4)
        templates = note_templates.get(condition, note_templates['Anxiety'])
        
        for i in range(num_notes):
            # Create session date (spread over past 3 months)
            session_date = timezone.now() - timedelta(days=random.randint(7, 90))
            
            # Use template or create generic note
            if i < len(templates):
                note_data = templates[i]
            else:
                note_data = {
                    'subjective': f'Patient reports ongoing work on {condition.lower()} management. Making steady progress with treatment goals.',
                    'objective': 'Patient appeared engaged and motivated during session. Good rapport maintained.',
                    'assessment': f'Continued progress in {condition.lower()} treatment. Patient is responding well to therapeutic interventions.',
                    'plan': 'Continue current treatment approach. Monitor progress and adjust as needed. Next session in 2 weeks.'
                }
            
            note = ProgressNote.objects.create(
                patient=user,
                psychologist=psychologist,
                session_date=session_date,
                session_number=i + 1,
                subjective=note_data['subjective'],
                objective=note_data['objective'],
                assessment=note_data['assessment'],
                plan=note_data['plan'],
                session_duration=50,
                progress_rating=random.randint(4, 9)  # Random rating 4-9
            )
            
            created_notes.append(note)
            print(f"Created progress note for {user.get_full_name()} with {psychologist.get_full_name()}")
    
    return created_notes

def create_appointments(patients, psychologists, services):
    """Create scheduled appointments for patients"""
    
    # Create availability slots for psychologists (Monday-Friday, 9 AM - 5 PM)
    for psychologist in psychologists:
        for day in range(5):  # Monday to Friday
            for hour in range(9, 17):  # 9 AM to 5 PM
                AvailabilitySlot.objects.get_or_create(
                    psychologist=psychologist,
                    day_of_week=day,
                    start_time=time(hour, 0),
                    end_time=time(hour + 1, 0),
                    is_available=True
                )
    
    created_appointments = []
    
    # Create appointments for next 4 weeks
    for patient_info in patients:
        user = patient_info['user']
        condition = patient_info['condition']
        
        # Assign to random psychologist
        psychologist = random.choice(psychologists)
        
        # Create 2-6 appointments per patient
        num_appointments = random.randint(2, 6)
        
        for i in range(num_appointments):
            # Create appointment date (next 4 weeks)
            appointment_date = timezone.now() + timedelta(days=random.randint(1, 28))
            
            # Random time between 9 AM and 5 PM
            hour = random.randint(9, 16)
            appointment_datetime = appointment_date.replace(hour=hour, minute=0, second=0, microsecond=0)
            
            # Random service
            service = random.choice(services)
            
            # Random status (mostly scheduled/confirmed)
            status_choices = ['scheduled', 'confirmed', 'scheduled', 'confirmed', 'completed']
            status = random.choice(status_choices)
            
            # Create time slot
            time_slot = TimeSlot.objects.create(
                psychologist=psychologist,
                date=appointment_date.date(),
                start_time=appointment_datetime,
                end_time=appointment_datetime + timedelta(hours=1),
                is_available=False  # This slot is now booked
            )
            
            # Create appointment
            appointment = Appointment.objects.create(
                patient=user,
                psychologist=psychologist,
                service=service,
                appointment_date=appointment_datetime,
                duration_minutes=60,
                status=status,
                session_type=random.choice(['telehealth', 'in_person']),
                notes=f"Follow-up session for {condition.lower()} management. Patient is making good progress.",
                video_room_id=f"room_{user.id}_{psychologist.id}_{appointment_datetime.strftime('%Y%m%d%H%M')}"
            )
            
            # Link the time slot to the appointment
            time_slot.appointment = appointment
            time_slot.save()
            
            created_appointments.append(appointment)
            print(f"Created appointment for {user.get_full_name()} with {psychologist.get_full_name()} on {appointment_datetime}")
    
    return created_appointments

def main():
    """Main function to seed all sample data"""
    
    print("🌱 Starting sample data seeding...")
    
    # Get existing psychologists
    psychologists = User.objects.filter(role='psychologist')
    if not psychologists.exists():
        print("❌ No psychologists found. Please create psychologists first.")
        return
    
    # Get existing services
    services = Service.objects.all()
    if not services.exists():
        print("❌ No services found. Please create services first.")
        return
    
    print(f"📋 Found {psychologists.count()} psychologists and {services.count()} services")
    
    # Create patients
    print("\n👥 Creating patients...")
    patients = create_sample_patients()
    print(f"✅ Created {len(patients)} patients")
    
    # Create progress notes
    print("\n📝 Creating progress notes...")
    notes = create_progress_notes(patients, psychologists)
    print(f"✅ Created {len(notes)} progress notes")
    
    # Create appointments
    print("\n📅 Creating appointments...")
    appointments = create_appointments(patients, psychologists, services)
    print(f"✅ Created {len(appointments)} appointments")
    
    print(f"\n🎉 Sample data seeding completed!")
    print(f"   - Patients: {len(patients)}")
    print(f"   - Progress Notes: {len(notes)}")
    print(f"   - Appointments: {len(appointments)}")
    
    # Show summary
    print(f"\n📊 Database Summary:")
    print(f"   - Total Patients: {User.objects.filter(role='patient').count()}")
    print(f"   - Total Psychologists: {User.objects.filter(role='psychologist').count()}")
    print(f"   - Total Progress Notes: {ProgressNote.objects.count()}")
    print(f"   - Total Appointments: {Appointment.objects.count()}")

if __name__ == '__main__':
    main()
