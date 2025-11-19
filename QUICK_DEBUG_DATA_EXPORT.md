# 🚨 Quick Debug Guide: Data Export Errors

## Your Current Error

```
[AuthService] Error requesting data access: Error: Failed to request data access
at Object.requestDataAccess (auth.ts:420:17)
```

This means your **frontend code is throwing an error** at line 420 in `auth.ts`.

---

## 🔍 Step-by-Step Debug

### Step 1: Check Your Frontend Code

Open `auth.ts` and find the `requestDataAccess` function (around line 420).

**❌ WRONG CODE (will fail):**
```typescript
params: { format: exportFormat }  // ❌ This doesn't work!
```

**✅ CORRECT CODE (works):**
```typescript
params: { export_format: exportFormat }  // ✅ Use this!
```

**The parameter name MUST be `export_format`, not `format`!**

---

### Step 2: Update Your `auth.ts` File

**Replace the entire `requestDataAccess` function with this:**

```typescript
async requestDataAccess(exportFormat: 'json' | 'pdf' | 'csv' = 'json') {
  try {
    console.log('[AuthService] Starting request:', exportFormat);

    const response = await axiosInstance.get('data-access-request/', {
      params: { 
        export_format: exportFormat  // ⚠️ MUST be export_format!
      },
      responseType: exportFormat === 'json' ? 'json' : 'blob',
    });

    // For JSON, return data
    if (exportFormat === 'json') {
      return response.data;
    }

    // For PDF/CSV, download file
    const blob = new Blob([response.data], {
      type: exportFormat === 'pdf' ? 'application/pdf' : 'text/csv'
    });
    
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `my-data.${exportFormat}`;
    link.click();
    window.URL.revokeObjectURL(url);

    return { success: true };

  } catch (error: any) {
    console.error('[AuthService] Request failed:', {
      status: error.response?.status,
      message: error.message,
      data: error.response?.data
    });
    throw new Error('Failed to request data access');
  }
}
```

---

### Step 3: Restart Django Server

```bash
cd /home/ali/Desktop/projects/clink-backend
source venv/bin/activate
python manage.py runserver
```

---

### Step 4: Test in Browser Console

**Before clicking the button**, test the endpoint directly:

```javascript
// 1. Check if you have a token
console.log('Token:', localStorage.getItem('token'));

// 2. Test JSON format
fetch('http://127.0.0.1:8000/api/auth/data-access-request/?export_format=json', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
})
.then(r => {
  console.log('Status:', r.status);
  return r.json();
})
.then(data => console.log('✅ Success:', data))
.catch(err => console.error('❌ Failed:', err));
```

**Expected result:** You should see `Status: 200` and your data.

---

### Step 5: Test PDF Download

```javascript
fetch('http://127.0.0.1:8000/api/auth/data-access-request/?export_format=pdf', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
})
.then(r => {
  console.log('Status:', r.status, 'Type:', r.headers.get('content-type'));
  return r.blob();
})
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'test.pdf';
  a.click();
  console.log('✅ Download triggered');
})
.catch(err => console.error('❌ Failed:', err));
```

**Expected result:** PDF should download.

---

## 🐛 Common Issues

### Issue 1: "Network Error" or "Failed to fetch"

**Cause:** Django server not running

**Fix:**
```bash
# Check if server is running
ps aux | grep "manage.py runserver"

# If not running, start it
cd /home/ali/Desktop/projects/clink-backend
source venv/bin/activate
python manage.py runserver
```

---

### Issue 2: "401 Unauthorized"

**Cause:** No token or expired token

**Fix:**
```javascript
// Re-login to get fresh token
fetch('http://127.0.0.1:8000/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'testpatient@example.com',
    password: 'testpass123'
  })
})
.then(r => r.json())
.then(data => {
  localStorage.setItem('token', data.access);
  console.log('✅ New token saved');
});
```

---

### Issue 3: "404 Not Found"

**Cause:** Wrong URL or endpoint

**Fix:** Check your axios baseURL:
```typescript
// Should be:
const axiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/auth/',
});
```

---

### Issue 4: "403 Forbidden"

**Cause:** Logged in as non-patient user

**Fix:** Use the test patient account:
- Email: `testpatient@example.com`
- Password: `testpass123`

---

### Issue 5: "406 Not Acceptable"

**Cause:** Using `format` instead of `export_format`

**Fix:** Change your code:
```typescript
// ❌ WRONG
params: { format: 'pdf' }

// ✅ CORRECT
params: { export_format: 'pdf' }
```

---

## 📋 Quick Checklist

Before clicking the download button, verify:

- [ ] Django server is running (`python manage.py runserver`)
- [ ] You're logged in (check `localStorage.getItem('token')`)
- [ ] You're using a patient account (not admin/psychologist)
- [ ] Your `auth.ts` uses `export_format` parameter
- [ ] Your axios baseURL is correct
- [ ] Browser console shows no CORS errors

---

## 🧪 Full Test Script

Run this in your browser console to test everything:

```javascript
// Complete test script
(async () => {
  console.log('🧪 Starting tests...\n');

  // 1. Check token
  const token = localStorage.getItem('token');
  if (!token) {
    console.error('❌ No token found. Please login first.');
    return;
  }
  console.log('✅ Token found');

  // 2. Test JSON
  try {
    const r1 = await fetch('http://127.0.0.1:8000/api/auth/data-access-request/?export_format=json', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    console.log('JSON:', r1.status === 200 ? '✅ OK' : `❌ ${r1.status}`);
  } catch (e) {
    console.error('❌ JSON failed:', e.message);
  }

  // 3. Test PDF
  try {
    const r2 = await fetch('http://127.0.0.1:8000/api/auth/data-access-request/?export_format=pdf', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    console.log('PDF:', r2.status === 200 ? '✅ OK' : `❌ ${r2.status}`);
  } catch (e) {
    console.error('❌ PDF failed:', e.message);
  }

  // 4. Test CSV
  try {
    const r3 = await fetch('http://127.0.0.1:8000/api/auth/data-access-request/?export_format=csv', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    console.log('CSV:', r3.status === 200 ? '✅ OK' : `❌ ${r3.status}`);
  } catch (e) {
    console.error('❌ CSV failed:', e.message);
  }

  console.log('\n✅ All tests complete!');
})();
```

**Expected output:**
```
🧪 Starting tests...
✅ Token found
JSON: ✅ OK
PDF: ✅ OK
CSV: ✅ OK
✅ All tests complete!
```

---

## 🆘 Still Not Working?

If tests pass but your button doesn't work:

1. **Check your component code:**
   ```typescript
   // Make sure you're calling it correctly
   await AuthService.requestDataAccess('pdf');  // not 'format'
   ```

2. **Check for try-catch blocks:**
   ```typescript
   try {
     await AuthService.requestDataAccess('pdf');
   } catch (error) {
     console.error('Button error:', error);  // Look here!
   }
   ```

3. **Check axios interceptors:**
   - Make sure your axios instance has the auth interceptor
   - Verify baseURL is set correctly

---

## ✅ Success Looks Like This

When it works, you'll see:

**Browser Console:**
```
[AuthService] Starting request: pdf
✅ File downloaded
```

**Network Tab:**
```
GET /api/auth/data-access-request/?export_format=pdf
Status: 200 OK
Type: application/pdf
```

**And:** A PDF file will download automatically!

---

## 🔧 Need Backend Restart?

```bash
# Kill any running Django servers
pkill -f "manage.py runserver"

# Start fresh
cd /home/ali/Desktop/projects/clink-backend
source venv/bin/activate
python manage.py runserver
```

---

**The #1 fix:** Change `format` to `export_format` in your frontend code! 🎯

