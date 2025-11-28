"""
Test welcome email functionality
Run this to diagnose email sending issues
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from django.conf import settings
from core.email_service import send_welcome_email, send_email_via_sendgrid, send_email_via_django
from users.models import User

def test_email_configuration():
    """Test email configuration"""
    print("=" * 60)
    print("EMAIL CONFIGURATION TEST")
    print("=" * 60)
    
    # Check SendGrid configuration
    print("\n📧 SendGrid Configuration:")
    print(f"   API Key: {'✅ Set' if getattr(settings, 'SENDGRID_API_KEY', None) else '❌ Not Set'}")
    print(f"   From Email: {getattr(settings, 'SENDGRID_FROM_EMAIL', 'NOT SET')}")
    print(f"   From Name: {getattr(settings, 'SENDGRID_FROM_NAME', 'NOT SET')}")
    
    # Check SMTP configuration
    print("\n📮 SMTP Configuration:")
    print(f"   Backend: {settings.EMAIL_BACKEND}")
    print(f"   Host: {settings.EMAIL_HOST}")
    print(f"   Port: {settings.EMAIL_PORT}")
    print(f"   Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"   Host User: {settings.EMAIL_HOST_USER}")
    print(f"   Password: {'✅ Set' if settings.EMAIL_HOST_PASSWORD else '❌ Not Set'}")
    
    # Check if using placeholders
    if settings.EMAIL_HOST_USER == 'your-email@gmail.com':
        print("\n⚠️  WARNING: Using placeholder email configuration!")
        print("   Please update .env with real values")
    
    return {
        'sendgrid_configured': bool(getattr(settings, 'SENDGRID_API_KEY', None)),
        'smtp_configured': settings.EMAIL_HOST_USER != 'your-email@gmail.com'
    }


def test_send_test_email(to_email):
    """Send a test email"""
    print("\n" + "=" * 60)
    print(f"SENDING TEST EMAIL TO: {to_email}")
    print("=" * 60)
    
    subject = "Test Email - Tailored Psychology"
    message = """
This is a test email from Tailored Psychology.

If you receive this email, your email configuration is working correctly!

Test Details:
- Sent from: test_welcome_email.py
- Configuration: Django email service
- Date: Now

Best regards,
Tailored Psychology Team
"""
    
    try:
        # Try SendGrid first
        print("\n📤 Attempting to send via SendGrid...")
        result = send_email_via_sendgrid(to_email, subject, message)
        
        if result.get('success'):
            print(f"✅ Email sent successfully via {result.get('method', 'sendgrid')}")
            print(f"   Status Code: {result.get('status_code', 'N/A')}")
            return True
        else:
            print(f"❌ Email failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return False


def test_welcome_email_for_user(email):
    """Test welcome email for a specific user"""
    print("\n" + "=" * 60)
    print(f"TESTING WELCOME EMAIL FOR USER: {email}")
    print("=" * 60)
    
    try:
        # Find user
        user = User.objects.filter(email=email).first()
        
        if not user:
            print(f"❌ User not found with email: {email}")
            return False
        
        print(f"\n👤 User Found:")
        print(f"   Name: {user.get_full_name()}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.get_role_display()}")
        
        # Send welcome email
        print(f"\n📤 Sending welcome email...")
        result = send_welcome_email(user)
        
        if result.get('success'):
            print(f"✅ Welcome email sent successfully!")
            print(f"   Method: {result.get('method', 'sendgrid')}")
            return True
        else:
            print(f"❌ Welcome email failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("WELCOME EMAIL DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Test configuration
    config = test_email_configuration()
    
    if not config['sendgrid_configured'] and not config['smtp_configured']:
        print("\n" + "=" * 60)
        print("❌ EMAIL NOT CONFIGURED")
        print("=" * 60)
        print("\nTo fix this, you need to configure email in your .env file:")
        print("\nOption 1: Use SendGrid (Recommended)")
        print("-" * 40)
        print("SENDGRID_API_KEY=your-sendgrid-api-key")
        print("SENDGRID_FROM_EMAIL=noreply@tailoredpsychology.com.au")
        print("SENDGRID_FROM_NAME=Tailored Psychology")
        print("\nOption 2: Use Gmail SMTP")
        print("-" * 40)
        print("EMAIL_HOST_USER=your-gmail@gmail.com")
        print("EMAIL_HOST_PASSWORD=your-app-specific-password")
        print("\nNote: For Gmail, you need to:")
        print("1. Enable 2-factor authentication")
        print("2. Generate an 'App Password'")
        print("3. Use that app password (not your regular password)")
        return
    
    # Ask for test email
    print("\n" + "=" * 60)
    print("INTERACTIVE TEST")
    print("=" * 60)
    print("\nWhat would you like to test?")
    print("1. Send a test email to any address")
    print("2. Test welcome email for an existing user")
    print("3. List recent users")
    print("4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        email = input("Enter test email address: ").strip()
        if email:
            test_send_test_email(email)
    
    elif choice == '2':
        email = input("Enter user's email address: ").strip()
        if email:
            test_welcome_email_for_user(email)
    
    elif choice == '3':
        print("\n📋 Recent Users (last 10):")
        print("-" * 60)
        users = User.objects.all().order_by('-date_joined')[:10]
        for user in users:
            print(f"   {user.email} - {user.get_full_name()} ({user.get_role_display()})")
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()

