# Test CORS from Browser Console

## Quick Test Script

Open your browser on `https://tailoredpsychology.com.au`, open DevTools (F12), go to **Console** tab, and paste this:

```javascript
// Test CORS Configuration
(async function testCORS() {
  const apiUrl = 'https://api.tailoredpsychology.com.au';
  const frontendOrigin = window.location.origin;
  
  console.log('🧪 Testing CORS Configuration');
  console.log('='.repeat(60));
  console.log(`Frontend Origin: ${frontendOrigin}`);
  console.log(`API URL: ${apiUrl}`);
  console.log();
  
  // Test 1: OPTIONS Preflight
  console.log('Test 1: OPTIONS Preflight Request');
  console.log('-'.repeat(60));
  try {
    const optionsResponse = await fetch(`${apiUrl}/api/appointments/video-token/13/`, {
      method: 'OPTIONS',
      headers: {
        'Origin': frontendOrigin,
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'authorization,content-type'
      }
    });
    
    console.log(`Status: ${optionsResponse.status}`);
    console.log('Response Headers:');
    
    const corsHeaders = {
      'access-control-allow-origin': optionsResponse.headers.get('access-control-allow-origin'),
      'access-control-allow-credentials': optionsResponse.headers.get('access-control-allow-credentials'),
      'access-control-allow-methods': optionsResponse.headers.get('access-control-allow-methods'),
      'access-control-allow-headers': optionsResponse.headers.get('access-control-allow-headers'),
      'access-control-max-age': optionsResponse.headers.get('access-control-max-age')
    };
    
    for (const [name, value] of Object.entries(corsHeaders)) {
      if (value) {
        console.log(`  ✅ ${name}: ${value}`);
      } else {
        console.log(`  ❌ ${name}: MISSING`);
      }
    }
    
    if (corsHeaders['access-control-allow-origin'] === frontendOrigin) {
      console.log(`\n✅ CORS Origin matches: ${frontendOrigin}`);
    } else if (corsHeaders['access-control-allow-origin']) {
      console.log(`\n⚠️  CORS Origin mismatch:`);
      console.log(`   Got: ${corsHeaders['access-control-allow-origin']}`);
      console.log(`   Expected: ${frontendOrigin}`);
    } else {
      console.log(`\n❌ CORS Origin header is MISSING!`);
    }
    
  } catch (error) {
    console.error('❌ OPTIONS request failed:', error);
    console.error('   This usually means CORS is blocking the request');
  }
  
  console.log();
  
  // Test 2: GET Request (without auth - should get 401)
  console.log('Test 2: GET Request (without auth)');
  console.log('-'.repeat(60));
  try {
    const getResponse = await fetch(`${apiUrl}/api/appointments/video-token/13/`, {
      method: 'GET',
      headers: {
        'Origin': frontendOrigin,
        'Content-Type': 'application/json'
      }
    });
    
    console.log(`Status: ${getResponse.status}`);
    
    const corsOrigin = getResponse.headers.get('access-control-allow-origin');
    if (corsOrigin) {
      console.log(`✅ access-control-allow-origin: ${corsOrigin}`);
      if (corsOrigin === frontendOrigin) {
        console.log(`   ✅ Origin matches frontend`);
      } else {
        console.log(`   ⚠️  Origin mismatch`);
      }
    } else {
      console.log(`❌ access-control-allow-origin: MISSING`);
    }
    
    const corsCredentials = getResponse.headers.get('access-control-allow-credentials');
    if (corsCredentials) {
      console.log(`✅ access-control-allow-credentials: ${corsCredentials}`);
    } else {
      console.log(`⚠️  access-control-allow-credentials: MISSING`);
    }
    
    if (getResponse.status === 401) {
      console.log(`\n✅ Got 401 (expected - no auth token)`);
    } else {
      const data = await getResponse.json().catch(() => ({}));
      console.log(`⚠️  Got ${getResponse.status}:`, data);
    }
    
  } catch (error) {
    console.error('❌ GET request failed:', error);
    console.error('   Error type:', error.name);
    console.error('   Error message:', error.message);
    
    if (error.message.includes('CORS') || error.message.includes('Access-Control')) {
      console.error('\n❌ This is a CORS error!');
      console.error('   The backend is not sending CORS headers correctly.');
    } else if (error.message.includes('Failed to fetch') || error.message.includes('network')) {
      console.error('\n❌ This is a network error!');
      console.error('   Check if the backend is accessible.');
    }
  }
  
  console.log();
  
  // Test 3: GET Request with auth token
  console.log('Test 3: GET Request (with auth token)');
  console.log('-'.repeat(60));
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    console.log('⚠️  No auth token found in localStorage');
    console.log('   Skipping authenticated request test');
  } else {
    console.log(`Token found: ${token.substring(0, 20)}...`);
    
    try {
      const authResponse = await fetch(`${apiUrl}/api/appointments/video-token/13/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Origin': frontendOrigin,
          'Content-Type': 'application/json'
        }
      });
      
      console.log(`Status: ${authResponse.status}`);
      
      const corsOrigin = authResponse.headers.get('access-control-allow-origin');
      if (corsOrigin) {
        console.log(`✅ access-control-allow-origin: ${corsOrigin}`);
      } else {
        console.log(`❌ access-control-allow-origin: MISSING`);
      }
      
      if (authResponse.ok) {
        const data = await authResponse.json();
        console.log(`✅ Success! Got video token:`);
        console.log(`   Room: ${data.room_name}`);
        console.log(`   Expires in: ${data.expires_in} seconds`);
      } else {
        const errorData = await authResponse.json().catch(() => ({}));
        console.log(`❌ Error:`, errorData);
      }
      
    } catch (error) {
      console.error('❌ Authenticated request failed:', error);
    }
  }
  
  console.log();
  console.log('='.repeat(60));
  console.log('Summary');
  console.log('='.repeat(60));
  console.log('Check the results above:');
  console.log('✅ = Working correctly');
  console.log('❌ = Problem found');
  console.log('⚠️  = Warning (might be OK)');
})();
```

## What to Look For

### ✅ Good Signs:
- `access-control-allow-origin: https://tailoredpsychology.com.au` is present
- `access-control-allow-credentials: true` is present
- Status 200 or 401 (not CORS errors)
- No "CORS policy" errors in console

### ❌ Bad Signs:
- `access-control-allow-origin: MISSING`
- "CORS policy" error messages
- Status 0 or "blocked" in Network tab
- "Failed to fetch" errors

## If CORS Headers Are Missing

Run this on your **Droplet** to check backend:

```bash
cd /var/www/clink-backend
python3 test_cors.py
```

This will test CORS from the server side and show you exactly what headers are being sent.

## Quick Fix Commands (on Droplet)

If CORS headers are missing:

```bash
# 1. Verify Django settings
cd /var/www/clink-backend
source venv/bin/activate
python manage.py shell
# Then in shell:
# from django.conf import settings
# print(settings.CORS_ALLOWED_ORIGINS)

# 2. Restart Gunicorn
sudo systemctl restart gunicorn

# 3. Reload Nginx
sudo systemctl reload nginx

# 4. Test CORS
python3 test_cors.py
```

