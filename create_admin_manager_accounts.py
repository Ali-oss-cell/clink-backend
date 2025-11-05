#!/usr/bin/env python
"""
Script to create Admin and Practice Manager accounts
Run this with: python manage.py shell < create_admin_manager_accounts.py
Or: python create_admin_manager_accounts.py (after setting up Django)
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

def create_admin_account():
    """Create admin account"""
    email = 'admin@clinic.com'
    password = 'admin123'
    
    if User.objects.filter(email=email).exists():
        print(f"⚠️  Admin account with email '{email}' already exists!")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.role = User.UserRole.ADMIN
        user.is_verified = True
        user.is_staff = True
        user.is_superuser = True
        # Generate unique username if needed
        if not user.username or User.objects.filter(username=user.username).exclude(pk=user.pk).exists():
            user.username = email.split('@')[0] + '_admin'
        user.save()
        print(f"✅ Updated existing admin account: {email}")
        print(f"   Password: {password}")
    else:
        # Generate unique username
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        user = User.objects.create(
            username=username,
            email=email,
            first_name='System',
            last_name='Administrator',
            role=User.UserRole.ADMIN,
            is_verified=True,
            is_staff=True,
            is_superuser=True,
            password=make_password(password)
        )
        print(f"✅ Created admin account: {email}")
        print(f"   Password: {password}")
    
    return user

def create_practice_manager_account():
    """Create practice manager account"""
    email = 'manager@clinic.com'
    password = 'manager123'
    
    if User.objects.filter(email=email).exists():
        print(f"⚠️  Practice Manager account with email '{email}' already exists!")
        user = User.objects.get(email=email)
        user.set_password(password)
        user.role = User.UserRole.PRACTICE_MANAGER
        user.is_verified = True
        # Generate unique username if needed
        if not user.username or User.objects.filter(username=user.username).exclude(pk=user.pk).exists():
            user.username = email.split('@')[0] + '_manager'
        user.save()
        print(f"✅ Updated existing practice manager account: {email}")
        print(f"   Password: {password}")
    else:
        # Generate unique username
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        user = User.objects.create(
            username=username,
            email=email,
            first_name='Practice',
            last_name='Manager',
            phone_number='0412345678',
            role=User.UserRole.PRACTICE_MANAGER,
            is_verified=True,
            password=make_password(password)
        )
        print(f"✅ Created practice manager account: {email}")
        print(f"   Password: {password}")
    
    return user

def main():
    """Main function"""
    print("=" * 60)
    print("Creating Admin and Practice Manager Accounts")
    print("=" * 60)
    print()
    
    # Create admin account
    print("1️⃣  Creating Admin Account...")
    admin = create_admin_account()
    print()
    
    # Create practice manager account
    print("2️⃣  Creating Practice Manager Account...")
    manager = create_practice_manager_account()
    print()
    
    # Summary
    print("=" * 60)
    print("✅ Account Creation Complete!")
    print("=" * 60)
    print()
    print("📋 Account Credentials:")
    print()
    print("👤 ADMIN ACCOUNT:")
    print(f"   Email: {admin.email}")
    print(f"   Password: admin123")
    print(f"   Role: {admin.get_role_display()}")
    print()
    print("👤 PRACTICE MANAGER ACCOUNT:")
    print(f"   Email: {manager.email}")
    print(f"   Password: manager123")
    print(f"   Role: {manager.get_role_display()}")
    print()
    print("=" * 60)
    print("🔐 Login Endpoint: POST /api/auth/login/")
    print("   Body: { 'email': 'admin@clinic.com', 'password': 'admin123' }")
    print("=" * 60)
    print()

if __name__ == '__main__':
    main()

