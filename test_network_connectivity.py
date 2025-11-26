#!/usr/bin/env python
"""
Test network connectivity to SendGrid API
This will help diagnose where the connection is failing
"""
import socket
import requests
import sys

def test_dns():
    """Test DNS resolution"""
    print("=" * 60)
    print("Test 1: DNS Resolution")
    print("=" * 60)
    try:
        ip = socket.gethostbyname('api.sendgrid.com')
        print(f"✅ DNS Resolution: {ip}")
        return True
    except Exception as e:
        print(f"❌ DNS Error: {e}")
        return False

def test_tcp_connection():
    """Test TCP connection to port 443"""
    print("\n" + "=" * 60)
    print("Test 2: TCP Connection (Port 443)")
    print("=" * 60)
    try:
        sock = socket.create_connection(('api.sendgrid.com', 443), timeout=10)
        sock.close()
        print("✅ TCP Connection: Success")
        return True
    except socket.timeout:
        print("❌ TCP Connection: Timeout (10 seconds)")
        print("   → Firewall may be blocking outbound HTTPS")
        return False
    except Exception as e:
        print(f"❌ TCP Connection Error: {e}")
        return False

def test_https_request():
    """Test HTTPS request"""
    print("\n" + "=" * 60)
    print("Test 3: HTTPS Request")
    print("=" * 60)
    try:
        response = requests.get('https://api.sendgrid.com/v3/', timeout=10)
        print(f"✅ HTTPS Request: Status {response.status_code}")
        return True
    except requests.exceptions.Timeout:
        print("❌ HTTPS Request: Timeout (10 seconds)")
        print("   → Connection is being blocked or very slow")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ HTTPS Request: Connection Error")
        print(f"   → {e}")
        return False
    except Exception as e:
        print(f"❌ HTTPS Request Error: {type(e).__name__}: {e}")
        return False

def test_google():
    """Test if general HTTPS works"""
    print("\n" + "=" * 60)
    print("Test 4: General HTTPS (Google)")
    print("=" * 60)
    try:
        response = requests.get('https://www.google.com', timeout=10)
        print(f"✅ General HTTPS: Status {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ General HTTPS Error: {e}")
        print("   → Outbound HTTPS is completely blocked")
        return False

def main():
    print("\n" + "=" * 60)
    print("SendGrid Network Connectivity Test")
    print("=" * 60 + "\n")
    
    results = {
        'dns': test_dns(),
        'tcp': test_tcp_connection(),
        'https': test_https_request(),
        'general': test_google()
    }
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if all(results.values()):
        print("✅ All tests passed! Network connectivity is fine.")
        print("   → The issue might be with the SendGrid Python library")
        print("   → Try using requests library directly instead")
    elif results['general'] and not results['https']:
        print("⚠️  General HTTPS works, but SendGrid API is blocked")
        print("   → Check if SendGrid IPs are blocked by firewall")
        print("   → Contact your hosting provider")
    elif not results['tcp']:
        print("❌ TCP connection fails - Outbound HTTPS is blocked")
        print("   → Check firewall: sudo ufw status")
        print("   → Allow outbound HTTPS: sudo ufw allow out 443/tcp")
    elif not results['dns']:
        print("❌ DNS resolution fails")
        print("   → Check DNS settings: /etc/resolv.conf")
        print("   → Try: sudo systemctl restart systemd-resolved")
    else:
        print("⚠️  Partial connectivity issues detected")
        print("   → Review individual test results above")
    
    return 0 if all(results.values()) else 1

if __name__ == '__main__':
    sys.exit(main())

