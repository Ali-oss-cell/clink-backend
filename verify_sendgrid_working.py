#!/usr/bin/env python
"""
Verify SendGrid is working and show detailed information
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from django.conf import settings
from core.email_service import send_email_via_sendgrid, test_email_configuration
import time

def verify_sendgrid():
    """Verify SendGrid configuration and send test email"""
    
    print("=" * 60)
    print("SendGrid Verification Test")
    print("=" * 60)
    print()
    
    # Check configuration
    print("📋 Configuration Check:")
    print("-" * 60)
    api_key = getattr(settings, 'SENDGRID_API_KEY', None)
    from_email = getattr(settings, 'SENDGRID_FROM_EMAIL', None)
    from_name = getattr(settings, 'SENDGRID_FROM_NAME', None)
    
    print(f"API Key: {'✅ Configured' if api_key else '❌ NOT FOUND'}")
    if api_key:
        print(f"  First 20 chars: {api_key[:20]}...")
    print(f"From Email: {from_email or '❌ NOT SET'}")
    print(f"From Name: {from_name or '❌ NOT SET'}")
    print()
    
    if not api_key or not from_email:
        print("❌ Configuration incomplete!")
        return False
    
    # Send test email
    print("📧 Sending Test Email:")
    print("-" * 60)
    print(f"To: {from_email}")
    print(f"Subject: SendGrid Verification Test")
    print()
    
    try:
        start_time = time.time()
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        result = send_email_via_sendgrid(
            to_email=from_email,
            subject="SendGrid Verification Test",
            message=f"""This is a verification test email from your Psychology Clinic backend.

If you receive this email, SendGrid is working correctly!

Details:
- Time: {timestamp}
- This confirms SendGrid API integration is working.
"""
        )
        elapsed = time.time() - start_time
        
        print(f"✅ Email sent successfully!")
        print(f"   Method: {result.get('method', 'unknown')}")
        print(f"   Status Code: {result.get('status_code', 'N/A')}")
        print(f"   Time taken: {elapsed:.2f} seconds")
        print()
        
        # Show verification steps
        print("=" * 60)
        print("✅ Verification Steps:")
        print("=" * 60)
        print()
        print("1. Check SendGrid Dashboard:")
        print("   → Go to: https://app.sendgrid.com/")
        print("   → Click 'Activity' in the sidebar")
        print("   → Look for email sent to:", from_email)
        print("   → Status should be: 'Delivered' or 'Processed'")
        print()
        print("2. Check Email Inbox:")
        print(f"   → Check inbox at: {from_email}")
        print("   → Look for: 'SendGrid Verification Test'")
        print("   → Check spam folder if not in inbox")
        print()
        print("3. Verify Method Used:")
        print(f"   → Method: {result.get('method', 'unknown')}")
        if result.get('method') == 'sendgrid_direct_api':
            print("   → Used direct API call (requests library)")
        elif result.get('method') == 'sendgrid':
            print("   → Used SendGrid Python library")
        else:
            print("   → Used fallback method")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error sending email: {type(e).__name__}: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check API key is correct")
        print("2. Check domain is authenticated in SendGrid")
        print("3. Check SendGrid Activity for errors")
        return False

if __name__ == '__main__':
    success = verify_sendgrid()
    sys.exit(0 if success else 1)

