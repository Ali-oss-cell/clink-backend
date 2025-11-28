"""
Debug script to test welcome email during registration
Run this to see what happens when a user registers
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from users.models import User
from core.email_service import send_welcome_email
import logging

# Setup logging to see errors
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_welcome_email_for_existing_user(email):
    """Test welcome email for an existing user"""
    print("=" * 60)
    print(f"TESTING WELCOME EMAIL FOR: {email}")
    print("=" * 60)
    
    try:
        # Find user
        user = User.objects.filter(email=email).first()
        
        if not user:
            print(f"❌ User not found: {email}")
            return False
        
        print(f"\n👤 User Found:")
        print(f"   ID: {user.id}")
        print(f"   Name: {user.get_full_name()}")
        print(f"   Email: {user.email}")
        print(f"   Role: {user.get_role_display()}")
        print(f"   Has Patient Profile: {hasattr(user, 'patient_profile')}")
        
        if hasattr(user, 'patient_profile'):
            profile = user.patient_profile
            print(f"   Email Notifications Enabled: {profile.email_notifications_enabled}")
        
        # Send welcome email
        print(f"\n📤 Sending welcome email...")
        print("-" * 60)
        
        result = send_welcome_email(user)
        
        print("-" * 60)
        print(f"\n📊 Result:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   Method: {result.get('method', 'unknown')}")
        print(f"   Status Code: {result.get('status_code', 'N/A')}")
        
        if result.get('success'):
            print(f"\n✅ Welcome email sent successfully!")
            print(f"   Check inbox: {user.email}")
            print(f"   Check spam folder too!")
            return True
        else:
            print(f"\n❌ Welcome email failed!")
            print(f"   Error: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"\n❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def simulate_registration(email):
    """Simulate what happens during registration"""
    print("=" * 60)
    print("SIMULATING USER REGISTRATION")
    print("=" * 60)
    
    try:
        # Find or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': 'Test',
                'last_name': 'User',
                'role': User.UserRole.PATIENT
            }
        )
        
        if created:
            print(f"✅ Created new user: {user.email}")
        else:
            print(f"ℹ️  User already exists: {user.email}")
        
        # This is what happens in PatientRegistrationSerializer.create()
        print(f"\n📧 Calling send_welcome_email()...")
        
        try:
            result = send_welcome_email(user)
            
            if result.get('success'):
                print(f"✅ Email sent! Status: {result.get('status_code')}")
            else:
                print(f"❌ Email failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Exception in send_welcome_email: {str(e)}")
            import traceback
            traceback.print_exc()
            # This is what happens in the serializer - it just passes
            print(f"\n⚠️  In actual registration, this error would be silently ignored!")
            pass
        
        return result.get('success', False) if 'result' in locals() else False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python debug_welcome_email.py <email>")
        print("\nExample:")
        print("  python debug_welcome_email.py user@example.com")
        sys.exit(1)
    
    email = sys.argv[1]
    
    print("\n" + "=" * 60)
    print("WELCOME EMAIL DEBUG TOOL")
    print("=" * 60)
    
    # Test 1: Test for existing user
    print("\n" + "=" * 60)
    print("TEST 1: Send welcome email to existing user")
    print("=" * 60)
    test_welcome_email_for_existing_user(email)
    
    # Test 2: Simulate registration
    print("\n" + "=" * 60)
    print("TEST 2: Simulate registration process")
    print("=" * 60)
    simulate_registration(email)
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE")
    print("=" * 60)
    print("\n💡 Tips:")
    print("   - Check SendGrid dashboard for delivery status")
    print("   - Check server logs for errors")
    print("   - Check spam folder")
    print("   - Verify email address is correct")


if __name__ == '__main__':
    main()

