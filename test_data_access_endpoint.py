#!/usr/bin/env python
"""
Test script for data access request endpoint
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

print("=" * 60)
print("Testing Data Access Request Endpoint")
print("=" * 60)

# Get a patient user
patient = User.objects.filter(role='patient').first()

if not patient:
    print("❌ No patient users found. Please create a patient first.")
    sys.exit(1)

print(f"✅ Found patient: {patient.email}")

# Test URL reverse
try:
    url = reverse('data-access-request')
    print(f"✅ URL reverse works: {url}")
except Exception as e:
    print(f"❌ URL reverse failed: {e}")
    sys.exit(1)

# Test with authenticated client
client = Client()
client.force_login(patient)

# Test GET request
print("\nTesting GET request...")
response = client.get('/api/auth/data-access-request/')

print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    print("✅ Endpoint works! Status: 200 OK")
    data = response.json()
    print(f"✅ Response has 'data' key: {'data' in data}")
    print(f"✅ Response has 'summary' key: {'summary' in data}")
elif response.status_code == 404:
    print("❌ Endpoint not found (404)")
    print("Response content:", response.content[:200])
elif response.status_code == 403:
    print("⚠️  Forbidden (403) - Check if user is a patient")
elif response.status_code == 401:
    print("⚠️  Unauthorized (401) - Authentication issue")
else:
    print(f"⚠️  Unexpected status: {response.status_code}")
    print("Response content:", response.content[:200])

# Test with format parameter
print("\nTesting with format=pdf...")
response = client.get('/api/auth/data-access-request/?format=pdf')
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print(f"✅ PDF format works! Content-Type: {response.get('Content-Type', 'N/A')}")

print("\nTesting with format=csv...")
response = client.get('/api/auth/data-access-request/?format=csv')
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print(f"✅ CSV format works! Content-Type: {response.get('Content-Type', 'N/A')}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)

