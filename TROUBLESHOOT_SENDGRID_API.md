# Troubleshooting SendGrid Web API Connection Timeout

## The Problem

The Web API connection is timing out. This is usually a **network/firewall issue**, not a code issue.

## Step 1: Test Network Connectivity

On your server, run these commands:

```bash
# Test if you can reach SendGrid API
curl -v --connect-timeout 10 https://api.sendgrid.com/v3/ 2>&1 | head -20

# Test DNS resolution
nslookup api.sendgrid.com

# Test basic HTTPS connectivity
curl -I https://www.google.com
```

## Step 2: Check Firewall

```bash
# Check if firewall is blocking outbound HTTPS
sudo ufw status
sudo iptables -L -n | grep 443

# If firewall is active, allow outbound HTTPS
sudo ufw allow out 443/tcp
```

## Step 3: Check if Proxy is Needed

Some servers require a proxy. Check:

```bash
echo $http_proxy
echo $https_proxy
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

If you need a proxy, configure it in your environment.

## Step 4: Test with Different Timeout

The SendGrid library might need a longer timeout. Let's update the code:

```python
# In core/email_service.py, we already added timeout handling
# But we can increase it or use a different approach
```

## Step 5: Use Requests Library Directly (Bypass SendGrid Library)

If the SendGrid library has issues, we can use `requests` directly:

```python
import requests
import json

def send_email_via_sendgrid_direct(to_email, subject, message):
    api_key = settings.SENDGRID_API_KEY
    from_email = settings.SENDGRID_FROM_EMAIL
    
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email},
        "subject": subject,
        "content": [{"type": "text/plain", "value": message}]
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=60)
    return response
```

## Step 6: Check SendGrid Status

Sometimes SendGrid has regional issues. Check:
- https://status.sendgrid.com/
- Try from a different location/network

## Most Likely Causes:

1. **Firewall blocking outbound HTTPS** - Check UFW/iptables
2. **Network routing issue** - Contact your hosting provider
3. **Proxy required** - Configure proxy settings
4. **DNS issue** - Check DNS resolution

## Quick Test Script

Create a file `test_network.py`:

```python
import requests
import socket

# Test 1: DNS Resolution
try:
    ip = socket.gethostbyname('api.sendgrid.com')
    print(f"✅ DNS Resolution: {ip}")
except Exception as e:
    print(f"❌ DNS Error: {e}")

# Test 2: TCP Connection
try:
    sock = socket.create_connection(('api.sendgrid.com', 443), timeout=10)
    sock.close()
    print("✅ TCP Connection: Success")
except Exception as e:
    print(f"❌ TCP Connection Error: {e}")

# Test 3: HTTPS Request
try:
    response = requests.get('https://api.sendgrid.com/v3/', timeout=10)
    print(f"✅ HTTPS Request: Status {response.status_code}")
except Exception as e:
    print(f"❌ HTTPS Request Error: {e}")
```

Run it:
```bash
python test_network.py
```

This will tell you exactly where the connection is failing.

