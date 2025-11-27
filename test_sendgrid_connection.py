#!/usr/bin/env python
"""
Test SendGrid connection with timeout handling
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from django.conf import settings
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import socket

def test_sendgrid_connection():
    """Test SendGrid connection with proper timeout"""
    
    api_key = getattr(settings, 'SENDGRID_API_KEY', None)
    from_email = getattr(settings, 'SENDGRID_FROM_EMAIL', 'noreply@tailoredpsychology.com.au')
    from_name = getattr(settings, 'SENDGRID_FROM_NAME', 'Tailored Psychology')
    
    print("=" * 60)
    print("SendGrid Connection Test")
    print("=" * 60)
    print(f"API Key: {'✅ Found' if api_key else '❌ NOT FOUND'}")
    if api_key:
        print(f"API Key (first 20 chars): {api_key[:20]}...")
    print(f"From Email: {from_email}")
    print(f"From Name: {from_name}")
    print()
    
    if not api_key:
        print("❌ ERROR: SENDGRID_API_KEY not found in settings")
        print("   Make sure you've added it to your .env file")
        return False
    
    # Test network connectivity first
    print("Testing network connectivity to SendGrid...")
    try:
        socket.setdefaulttimeout(5)
        sock = socket.create_connection(('api.sendgrid.com', 443), timeout=5)
        sock.close()
        print("✅ Network connection successful")
    except Exception as e:
        print(f"❌ Network connection failed: {e}")
        print("   Check firewall settings or network connectivity")
        return False
    finally:
        socket.setdefaulttimeout(None)
    
    # Test SendGrid API
    print("\nTesting SendGrid API...")
    try:
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        
        # Create a simple test email
        from_email_obj = Email(from_email, from_name)
        to_email_obj = To(from_email)  # Send to self for testing
        subject = "SendGrid Test - Connection Verification"
        content = Content("text/plain", "This is a test email to verify SendGrid connection.")
        
        mail = Mail(from_email_obj, to_email_obj, subject, content)
        
        print("Sending test email (this may take 10-30 seconds)...")
        socket.setdefaulttimeout(30)  # 30 second timeout
        try:
            response = sg.send(mail)
            print(f"✅ Email sent successfully!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response Headers: {dict(response.headers)}")
            print(f"\n📧 Check your inbox at: {from_email}")
            print("   Also check SendGrid Dashboard → Activity")
            return True
        except socket.timeout:
            print("❌ Connection timeout (30 seconds)")
            print("   The server may have network issues or SendGrid is slow")
            return False
        except Exception as e:
            print(f"❌ Error sending email: {type(e).__name__}: {e}")
            return False
        finally:
            socket.setdefaulttimeout(None)
            
    except Exception as e:
        print(f"❌ Error creating SendGrid client: {type(e).__name__}: {e}")
        return False

if __name__ == '__main__':
    success = test_sendgrid_connection()
    sys.exit(0 if success else 1)

