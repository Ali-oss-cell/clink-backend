#!/usr/bin/env python
"""
Test SendGrid by sending to a real email address
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from django.conf import settings
from core.email_service import send_email_via_sendgrid

def test_to_real_email():
    """Test SendGrid by sending to a real email address"""
    
    print("=" * 60)
    print("SendGrid Test - Send to Real Email")
    print("=" * 60)
    print()
    
    # Get email from user or use default
    if len(sys.argv) > 1:
        test_email = sys.argv[1]
    else:
        # Default test email
        test_email = "alassaada100@gmail.com"
    
    if not test_email:
        print("❌ No email address provided")
        return False
    
    print(f"Sending test email to: {test_email}")
    print()
    
    try:
        result = send_email_via_sendgrid(
            to_email=test_email,
            subject='SendGrid Test - Psychology Clinic',
            message=f"""Hello!

This is a test email from your Psychology Clinic backend.

If you receive this email, SendGrid is working correctly!

Details:
- From: {settings.SENDGRID_FROM_EMAIL}
- Status: Success

The email was sent via SendGrid API and should arrive in your inbox shortly.

Thank you!
Psychology Clinic System
"""
        )
        
        print("✅ Email sent successfully!")
        print(f"   Method: {result.get('method', 'unknown')}")
        print(f"   Status Code: {result.get('status_code', 'N/A')}")
        print()
        print("📧 Check your inbox at:", test_email)
        print("   Also check spam folder if not in inbox")
        print()
        print("📊 Check SendGrid Dashboard:")
        print("   → https://app.sendgrid.com/ → Activity")
        print("   → Look for email to:", test_email)
        print("   → Status should be: 'Delivered'")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False

if __name__ == '__main__':
    success = test_to_real_email()
    sys.exit(0 if success else 1)

