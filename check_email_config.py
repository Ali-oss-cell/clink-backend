"""
Simple email configuration checker
No Django import required - just checks your .env file
"""

import os
from pathlib import Path

def check_env_file():
    """Check .env file for email configuration"""
    env_path = Path(__file__).parent / '.env'
    
    print("=" * 60)
    print("EMAIL CONFIGURATION CHECKER")
    print("=" * 60)
    
    if not env_path.exists():
        print("\n❌ .env file not found!")
        print(f"   Expected location: {env_path}")
        return False
    
    print(f"\n✅ .env file found: {env_path}")
    
    # Read .env file
    config = {}
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    print("\n" + "=" * 60)
    print("CURRENT EMAIL CONFIGURATION")
    print("=" * 60)
    
    # Check SendGrid
    print("\n📧 SendGrid Configuration:")
    sendgrid_key = config.get('SENDGRID_API_KEY', '')
    sendgrid_email = config.get('SENDGRID_FROM_EMAIL', 'NOT SET')
    sendgrid_name = config.get('SENDGRID_FROM_NAME', 'NOT SET')
    
    if sendgrid_key and sendgrid_key != 'your-sendgrid-api-key':
        print(f"   ✅ API Key: Set (starts with: {sendgrid_key[:10]}...)")
        print(f"   ✅ From Email: {sendgrid_email}")
        print(f"   ✅ From Name: {sendgrid_name}")
        sendgrid_ok = True
    else:
        print(f"   ❌ API Key: Not set or using placeholder")
        print(f"   ⚠️  From Email: {sendgrid_email}")
        print(f"   ⚠️  From Name: {sendgrid_name}")
        sendgrid_ok = False
    
    # Check SMTP
    print("\n📮 SMTP Configuration (Gmail):")
    email_user = config.get('EMAIL_HOST_USER', 'NOT SET')
    email_pass = config.get('EMAIL_HOST_PASSWORD', 'NOT SET')
    email_host = config.get('EMAIL_HOST', 'smtp.gmail.com')
    
    if email_user != 'your-email@gmail.com' and email_pass != 'your-app-password':
        print(f"   ✅ Host User: {email_user}")
        print(f"   ✅ Password: Set ({'*' * len(email_pass[:8])}...)")
        print(f"   ✅ Host: {email_host}")
        smtp_ok = True
    else:
        print(f"   ❌ Host User: {email_user} (PLACEHOLDER)")
        print(f"   ❌ Password: {email_pass} (PLACEHOLDER)")
        print(f"   ⚠️  Host: {email_host}")
        smtp_ok = False
    
    # Summary
    print("\n" + "=" * 60)
    print("DIAGNOSIS")
    print("=" * 60)
    
    if sendgrid_ok:
        print("\n✅ SendGrid is configured - emails should work!")
        print("   Method: SendGrid API")
        return True
    elif smtp_ok:
        print("\n✅ SMTP is configured - emails should work!")
        print("   Method: SMTP (Gmail)")
        print("   ⚠️  Warning: Gmail has 500 emails/day limit")
        return True
    else:
        print("\n❌ EMAIL IS NOT CONFIGURED")
        print("\n   This is why you're not receiving welcome emails!")
        print("\n   You need to configure either SendGrid OR Gmail SMTP.")
        print("\n" + "-" * 60)
        print("QUICK FIX OPTIONS:")
        print("-" * 60)
        
        print("\nOption 1: SendGrid (Recommended for Production)")
        print("   1. Get your SendGrid API key from: https://sendgrid.com/")
        print("   2. Add to .env:")
        print("      SENDGRID_API_KEY=SG.your-actual-key-here")
        print("      SENDGRID_FROM_EMAIL=noreply@tailoredpsychology.com.au")
        print("      SENDGRID_FROM_NAME=Tailored Psychology")
        
        print("\nOption 2: Gmail SMTP (Quick Test Only)")
        print("   1. Enable 2FA on Gmail")
        print("   2. Generate App Password")
        print("   3. Add to .env:")
        print("      EMAIL_HOST_USER=your-gmail@gmail.com")
        print("      EMAIL_HOST_PASSWORD=your-16-char-app-password")
        
        print("\n📖 For detailed instructions, see: EMAIL_SETUP_GUIDE.md")
        return False


def show_next_steps(is_configured):
    """Show next steps"""
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    
    if is_configured:
        print("\n1. ✅ Your email is configured!")
        print("2. 📧 Create a new user account to test")
        print("3. 📬 Check your email inbox (and spam folder)")
        print("4. 🔄 If no email arrives, check SendGrid dashboard for errors")
    else:
        print("\n1. 📝 Update your .env file with real email credentials")
        print("2. 📖 Read EMAIL_SETUP_GUIDE.md for detailed instructions")
        print("3. 🔄 Restart your server after updating .env")
        print("4. ✅ Run this script again to verify")
        print("5. 📧 Create a new user account to test")


def main():
    is_configured = check_env_file()
    show_next_steps(is_configured)
    
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    print()


if __name__ == '__main__':
    main()

