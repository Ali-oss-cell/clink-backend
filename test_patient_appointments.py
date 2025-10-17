#!/usr/bin/env python
"""
Quick test script for Patient Appointments Endpoint
Run this to test the endpoint with your existing database
"""

import requests
import json
from getpass import getpass

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/users/login/"
APPOINTMENTS_URL = f"{BASE_URL}/api/appointments/patient/appointments/"

def print_separator():
    print("\n" + "="*70 + "\n")

def login(email, password):
    """Login and get JWT token"""
    print(f"🔐 Logging in as {email}...")
    
    response = requests.post(
        LOGIN_URL,
        json={"email": email, "password": password},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        return data.get('access')
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_endpoint(token, status='all', page=1, page_size=10):
    """Test the patient appointments endpoint"""
    print(f"📋 Fetching appointments (status={status}, page={page}, page_size={page_size})...")
    
    params = {
        'status': status,
        'page': page,
        'page_size': page_size
    }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.get(APPOINTMENTS_URL, params=params, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Request successful!\n")
        
        # Display summary
        print(f"📊 SUMMARY:")
        print(f"   Total appointments: {data['count']}")
        print(f"   Current page results: {len(data['results'])}")
        print(f"   Has next page: {'Yes' if data['next'] else 'No'}")
        print(f"   Has previous page: {'Yes' if data['previous'] else 'No'}")
        
        print_separator()
        
        # Display appointments
        if data['results']:
            print(f"📅 APPOINTMENTS:\n")
            for i, apt in enumerate(data['results'], 1):
                print(f"   {i}. Appointment ID: {apt['id']}")
                print(f"      Date: {apt['formatted_date']} at {apt['formatted_time']}")
                print(f"      Duration: {apt['duration_minutes']} minutes")
                print(f"      Type: {apt['session_type']}")
                print(f"      Status: {apt['status']}")
                print(f"      Psychologist: {apt['psychologist']['name']}")
                print(f"      Title: {apt['psychologist']['title']}")
                
                if apt.get('location'):
                    print(f"      Location: {apt['location']}")
                if apt.get('meeting_link'):
                    print(f"      Meeting Link: {apt['meeting_link']}")
                
                print(f"      Can Reschedule: {'✅ Yes' if apt['can_reschedule'] else '❌ No'}")
                print(f"      Can Cancel: {'✅ Yes' if apt['can_cancel'] else '❌ No'}")
                
                if apt.get('notes'):
                    print(f"      Notes: {apt['notes']}")
                
                print()
        else:
            print("   No appointments found.")
        
        print_separator()
        
        # Display full JSON
        print("📄 FULL JSON RESPONSE:")
        print(json.dumps(data, indent=2))
        
        return data
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return None

def main():
    """Main test function"""
    print_separator()
    print("🧪 PATIENT APPOINTMENTS ENDPOINT TEST")
    print_separator()
    
    # Get credentials
    print("Please enter patient credentials:")
    email = input("Email: ")
    password = getpass("Password: ")
    
    print_separator()
    
    # Login
    token = login(email, password)
    
    if not token:
        print("\n❌ Cannot continue without valid token")
        return
    
    print_separator()
    
    # Test different scenarios
    while True:
        print("\n🎯 TEST OPTIONS:")
        print("   1. Get all appointments")
        print("   2. Get upcoming appointments")
        print("   3. Get completed appointments")
        print("   4. Get cancelled appointments")
        print("   5. Get past appointments")
        print("   6. Custom query")
        print("   0. Exit")
        
        choice = input("\nSelect option: ")
        
        print_separator()
        
        if choice == '1':
            test_endpoint(token, status='all')
        elif choice == '2':
            test_endpoint(token, status='upcoming')
        elif choice == '3':
            test_endpoint(token, status='completed')
        elif choice == '4':
            test_endpoint(token, status='cancelled')
        elif choice == '5':
            test_endpoint(token, status='past')
        elif choice == '6':
            status = input("Status (all/upcoming/completed/cancelled/past): ")
            page = int(input("Page (default 1): ") or 1)
            page_size = int(input("Page size (default 10): ") or 10)
            test_endpoint(token, status=status, page=page, page_size=page_size)
        elif choice == '0':
            print("👋 Goodbye!")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

