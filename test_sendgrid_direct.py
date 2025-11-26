#!/usr/bin/env python
"""
Direct SendGrid API test using requests library (bypasses sendgrid library timeout issues)
"""
import os
import sys
import django
import requests
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from django.conf import settings

def test_sendgrid_direct():
    """Test SendGrid using direct API call with requests"""
    
    api_key = getattr(settings, 'SENDGRID_API_KEY', None)
    from_email = getattr(settings, 'SENDGRID_FROM_EMAIL', 'noreply@tailoredpsychology.com.au')
    from_name = getattr(settings, 'SENDGRID_FROM_NAME', 'Tailored Psychology')
    
    print("=" * 60)
    print("SendGrid Direct API Test")
    print("=" * 60)
    print(f"API Key: {'✅ Found' if api_key else '❌ NOT FOUND'}")
    if api_key:
        print(f"API Key (first 20 chars): {api_key[:20]}...")
    print(f"From Email: {from_email}")
    print(f"From Name: {from_name}")
    print()
    
    if not api_key:
        print("❌ ERROR: SENDGRID_API_KEY not found in settings")
        return False
    
    # Prepare email data
    email_data = {
        "personalizations": [
            {
                "to": [{"email": from_email}]
            }
        ],
        "from": {
            "email": from_email,
            "name": from_name
        },
        "subject": "SendGrid Test - Connection Verification",
        "content": [
            {
                "type": "text/plain",
                "value": "This is a test email to verify SendGrid connection is working."
            }
        ]
    }
    
    # Send via SendGrid API
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("Sending test email via SendGrid API...")
    print(f"URL: {url}")
    print(f"To: {from_email}")
    print()
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=email_data,
            timeout=30  # 30 second timeout
        )
        
        print(f"✅ Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code in [200, 202]:
            print("\n✅ Email sent successfully!")
            print(f"📧 Check your inbox at: {from_email}")
            print("   Also check SendGrid Dashboard → Activity")
            return True
        else:
            print(f"\n❌ Error: Status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Connection timeout (30 seconds)")
        print("   The server may have network issues")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        print("   Check network connectivity or firewall settings")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

if __name__ == '__main__':
    success = test_sendgrid_direct()
    sys.exit(0 if success else 1)

