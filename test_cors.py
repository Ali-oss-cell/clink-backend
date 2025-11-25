#!/usr/bin/env python3
"""
Test CORS configuration for the backend API
Run this on your Droplet to verify CORS is working correctly
"""

import requests
import sys

def test_cors_headers():
    """Test if CORS headers are being sent correctly"""
    
    base_url = "https://api.tailoredpsychology.com.au"
    origin = "https://tailoredpsychology.com.au"
    
    print("=" * 60)
    print("CORS Configuration Test")
    print("=" * 60)
    print(f"API URL: {base_url}")
    print(f"Frontend Origin: {origin}")
    print()
    
    # Test 1: OPTIONS preflight request
    print("Test 1: OPTIONS Preflight Request")
    print("-" * 60)
    try:
        response = requests.options(
            f"{base_url}/api/appointments/video-token/13/",
            headers={
                "Origin": origin,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,content-type"
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        
        cors_headers = {
            "access-control-allow-origin": None,
            "access-control-allow-credentials": None,
            "access-control-allow-methods": None,
            "access-control-allow-headers": None,
            "access-control-max-age": None
        }
        
        for header_name, expected_value in cors_headers.items():
            header_value = response.headers.get(header_name)
            if header_value:
                print(f"  ✅ {header_name}: {header_value}")
                cors_headers[header_name] = header_value
            else:
                print(f"  ❌ {header_name}: MISSING")
        
        # Check if origin matches
        if cors_headers["access-control-allow-origin"] == origin:
            print(f"\n✅ CORS Origin matches: {origin}")
        elif cors_headers["access-control-allow-origin"]:
            print(f"\n⚠️  CORS Origin is: {cors_headers['access-control-allow-origin']} (expected: {origin})")
        else:
            print(f"\n❌ CORS Origin header is missing!")
            
        if cors_headers["access-control-allow-credentials"] == "true":
            print(f"✅ CORS Credentials allowed")
        else:
            print(f"❌ CORS Credentials not allowed")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    
    print()
    
    # Test 2: Actual GET request (without auth - should get 401)
    print("Test 2: GET Request (without auth - should get 401)")
    print("-" * 60)
    try:
        response = requests.get(
            f"{base_url}/api/appointments/video-token/13/",
            headers={
                "Origin": origin
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        
        cors_origin = response.headers.get("access-control-allow-origin")
        if cors_origin:
            print(f"  ✅ access-control-allow-origin: {cors_origin}")
            if cors_origin == origin:
                print(f"  ✅ Origin matches frontend")
            else:
                print(f"  ⚠️  Origin mismatch (got: {cors_origin}, expected: {origin})")
        else:
            print(f"  ❌ access-control-allow-origin: MISSING")
            
        cors_credentials = response.headers.get("access-control-allow-credentials")
        if cors_credentials:
            print(f"  ✅ access-control-allow-credentials: {cors_credentials}")
        else:
            print(f"  ⚠️  access-control-allow-credentials: MISSING")
            
        if response.status_code == 401:
            print(f"\n✅ Got 401 (expected - no auth token provided)")
        else:
            print(f"\n⚠️  Got {response.status_code} (expected 401)")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    
    print()
    
    # Test 3: Check Django CORS settings
    print("Test 3: Django CORS Settings")
    print("-" * 60)
    try:
        import os
        import django
        
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_clinic.settings')
        django.setup()
        
        from django.conf import settings
        
        print(f"CORS_ALLOWED_ORIGINS: {settings.CORS_ALLOWED_ORIGINS}")
        print(f"CORS_ALLOW_CREDENTIALS: {settings.CORS_ALLOW_CREDENTIALS}")
        print(f"CORS_ALLOW_HEADERS: {settings.CORS_ALLOW_HEADERS}")
        
        if origin in settings.CORS_ALLOWED_ORIGINS:
            print(f"\n✅ {origin} is in CORS_ALLOWED_ORIGINS")
        else:
            print(f"\n❌ {origin} is NOT in CORS_ALLOWED_ORIGINS")
            print(f"   Current allowed origins: {settings.CORS_ALLOWED_ORIGINS}")
            
    except Exception as e:
        print(f"⚠️  Could not check Django settings: {e}")
        print("   (This is OK if running from outside Django environment)")
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    if cors_headers["access-control-allow-origin"] == origin:
        print("✅ CORS is configured correctly!")
        print("   The backend is sending the correct CORS headers.")
        print("   If frontend still has issues, check:")
        print("   1. Browser cache (clear and hard refresh)")
        print("   2. Frontend axiosInstance baseURL")
        print("   3. Browser Network tab for actual request/response")
    else:
        print("❌ CORS is NOT configured correctly!")
        print("   The backend is not sending the correct CORS headers.")
        print("   Check:")
        print("   1. Django CORS settings in settings.py")
        print("   2. Nginx configuration (should pass headers through)")
        print("   3. Gunicorn is running and restarted")
    
    return cors_headers["access-control-allow-origin"] == origin

if __name__ == "__main__":
    success = test_cors_headers()
    sys.exit(0 if success else 1)

