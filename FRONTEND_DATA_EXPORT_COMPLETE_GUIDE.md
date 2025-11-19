# 🎯 Complete Frontend Guide: Data Export (PDF/CSV/JSON)

## ⚠️ CRITICAL CHANGES REQUIRED

Your frontend **MUST** use `export_format` instead of `format` in query parameters.

---

## 🔧 Step 1: Update Your `auth.ts` Service

### Find the `requestDataAccess` function and replace it:

```typescript
/**
 * Request patient's personal data export (APP 12 - Privacy Act 1988)
 * @param exportFormat - Format for data export: 'json', 'pdf', or 'csv'
 * @returns Promise with data or file blob
 */
async requestDataAccess(exportFormat: 'json' | 'pdf' | 'csv' = 'json') {
  try {
    console.log('[AuthService] Requesting data access:', { 
      exportFormat, 
      url: `${API_URL}/auth/data-access-request/`,
      hasToken: !!localStorage.getItem('token')
    });

    // CRITICAL: Use 'export_format' not 'format'
    const response = await axiosInstance.get('data-access-request/', {
      params: { 
        export_format: exportFormat  // ⚠️ This is the key change!
      },
      responseType: exportFormat === 'json' ? 'json' : 'blob',
      timeout: 30000, // 30 second timeout for large exports
    });

    console.log('[AuthService] Data access response:', {
      status: response.status,
      contentType: response.headers['content-type'],
      dataType: typeof response.data,
    });

    // For JSON, return the data directly
    if (exportFormat === 'json') {
      return response.data;
    }

    // For PDF/CSV, create a blob and trigger download
    if (response.data) {
      const blob = new Blob([response.data], {
        type: exportFormat === 'pdf' ? 'application/pdf' : 'text/csv'
      });
      
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Get filename from Content-Disposition header or generate one
      const contentDisposition = response.headers['content-disposition'];
      let filename = `my-data-${new Date().toISOString().split('T')[0]}.${exportFormat}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('[AuthService] File downloaded:', filename);
      return { success: true, filename };
    }

    throw new Error('No data received from server');

  } catch (error: any) {
    console.error('[AuthService] Error requesting data access:', error);
    console.error('[AuthService] Error details:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      headers: error.response?.headers,
    });

    if (error.response?.status === 403) {
      throw new Error('You do not have permission to access this data');
    } else if (error.response?.status === 404) {
      throw new Error('Data access endpoint not found. Please contact support.');
    } else if (error.response?.status === 406) {
      throw new Error('Server cannot generate the requested format. Please try a different format.');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. The export is taking too long.');
    } else if (!error.response) {
      throw new Error('Network error. Please check your connection and try again.');
    }
    
    throw new Error(error.response?.data?.error || 'Failed to request data access');
  }
}
```

---

## 🎨 Step 2: Update Your React Component

### In `PatientAccountPage.tsx` (or wherever you have the download buttons):

```typescript
import { useState } from 'react';
import { AuthService } from '../services/auth';

function PatientAccountPage() {
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDownloadPDF = async () => {
    try {
      setIsDownloading(true);
      setError(null);
      console.log('[PatientAccount] Starting PDF download...');
      
      await AuthService.requestDataAccess('pdf');
      
      console.log('[PatientAccount] PDF download successful');
    } catch (error: any) {
      console.error('[PatientAccount] Error downloading PDF:', error);
      setError(error.message || 'Failed to download PDF');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleDownloadCSV = async () => {
    try {
      setIsDownloading(true);
      setError(null);
      console.log('[PatientAccount] Starting CSV download...');
      
      await AuthService.requestDataAccess('csv');
      
      console.log('[PatientAccount] CSV download successful');
    } catch (error: any) {
      console.error('[PatientAccount] Error downloading CSV:', error);
      setError(error.message || 'Failed to download CSV');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleViewData = async () => {
    try {
      setIsDownloading(true);
      setError(null);
      console.log('[PatientAccount] Fetching data as JSON...');
      
      const data = await AuthService.requestDataAccess('json');
      console.log('[PatientAccount] Data received:', data);
      
      // You can display this data in a modal or navigate to a details page
      alert('Data retrieved successfully! Check console for details.');
    } catch (error: any) {
      console.error('[PatientAccount] Error fetching data:', error);
      setError(error.message || 'Failed to fetch data');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="account-page">
      <h1>My Account</h1>
      
      {/* Error Display */}
      {error && (
        <div className="alert alert-error">
          <p>{error}</p>
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      {/* Data Export Section */}
      <div className="data-export-section">
        <h2>Download My Data</h2>
        <p>Download a copy of all your personal information stored in our system.</p>
        
        <div className="button-group">
          <button
            onClick={handleDownloadPDF}
            disabled={isDownloading}
            className="btn btn-primary"
          >
            {isDownloading ? '⏳ Downloading...' : '📄 Download PDF'}
          </button>

          <button
            onClick={handleDownloadCSV}
            disabled={isDownloading}
            className="btn btn-primary"
          >
            {isDownloading ? '⏳ Downloading...' : '📊 Download CSV'}
          </button>

          <button
            onClick={handleViewData}
            disabled={isDownloading}
            className="btn btn-secondary"
          >
            {isDownloading ? '⏳ Loading...' : '👁️ View Data'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default PatientAccountPage;
```

---

## 🧪 Step 3: Test the Integration

### 1. **Start Django Server**

```bash
cd /home/ali/Desktop/projects/clink-backend
source venv/bin/activate
python manage.py runserver
```

### 2. **Test from Browser Console**

Open your browser's Developer Console and run:

```javascript
// Test if the endpoint is reachable
fetch('http://127.0.0.1:8000/api/auth/data-access-request/?export_format=json', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
})
.then(r => r.json())
.then(data => console.log('✅ JSON works:', data))
.catch(err => console.error('❌ Error:', err));
```

### 3. **Test PDF Download**

```javascript
fetch('http://127.0.0.1:8000/api/auth/data-access-request/?export_format=pdf', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('token')}`
  }
})
.then(r => r.blob())
.then(blob => {
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'my-data.pdf';
  a.click();
  console.log('✅ PDF downloaded');
})
.catch(err => console.error('❌ Error:', err));
```

---

## 🔍 Debugging Checklist

If you still get errors, check these:

### ✅ Backend Checklist

```bash
# 1. Is Django server running?
ps aux | grep "manage.py runserver"

# 2. Test the endpoint directly with curl
TOKEN="your-token-here"
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/?export_format=pdf" \
  -H "Authorization: Bearer $TOKEN" \
  -I

# Expected: HTTP/1.1 200 OK
# Expected: Content-Type: application/pdf
```

### ✅ Frontend Checklist

1. **Check axios instance configuration:**
   ```typescript
   // In your axios setup file
   const axiosInstance = axios.create({
     baseURL: 'http://127.0.0.1:8000/api/auth/',
     headers: {
       'Content-Type': 'application/json',
     },
   });
   
   // Add token interceptor
   axiosInstance.interceptors.request.use((config) => {
     const token = localStorage.getItem('token');
     if (token) {
       config.headers.Authorization = `Bearer ${token}`;
     }
     return config;
   });
   ```

2. **Check CORS settings in Django:**
   ```python
   # In settings.py
   CORS_ALLOWED_ORIGINS = [
       'http://localhost:5173',
       'http://localhost:3000',
       'http://127.0.0.1:5173',
       'http://127.0.0.1:3000',
   ]
   CORS_ALLOW_CREDENTIALS = True
   ```

3. **Check Network Tab:**
   - Open Developer Tools → Network Tab
   - Click the download button
   - Look for the request to `data-access-request/`
   - Check the **Request Headers** (should have `Authorization: Bearer ...`)
   - Check the **Query Parameters** (should have `export_format=pdf`)
   - Check the **Response Status** (should be `200 OK`)

---

## 🎯 Common Errors & Solutions

### Error: "Failed to request data access"

**Cause:** Generic error, need to check console logs

**Solution:**
1. Check browser console for detailed error
2. Check Django logs: `tail -f logs/django.log`
3. Verify token is valid: Check `localStorage.getItem('token')`

---

### Error: "404 Not Found"

**Cause:** URL is incorrect or Django server not running

**Solution:**
1. Verify Django server is running on port 8000
2. Check the full URL in Network tab
3. Ensure baseURL in axios is correct

---

### Error: "406 Not Acceptable"

**Cause:** Using old `format` parameter instead of `export_format`

**Solution:**
1. Update frontend code to use `export_format` (see Step 1)
2. Restart Django server if needed

---

### Error: "403 Forbidden"

**Cause:** Not logged in as a patient, or token expired

**Solution:**
1. Re-login to get fresh token
2. Ensure logged-in user has `is_patient=True`
3. Check token in localStorage

---

### Error: No file downloads, but status is 200

**Cause:** Blob handling issue in frontend

**Solution:**
1. Ensure `responseType: 'blob'` is set for PDF/CSV
2. Check if popup blocker is preventing download
3. Try the browser console test above

---

## 📝 Full Working Example

Here's a complete, copy-paste ready example:

```typescript
// services/dataExport.ts
import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api/auth';

export const downloadPatientData = async (
  format: 'pdf' | 'csv' | 'json',
  token: string
) => {
  try {
    const response = await axios.get(`${API_URL}/data-access-request/`, {
      params: { export_format: format },
      responseType: format === 'json' ? 'json' : 'blob',
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (format === 'json') {
      return response.data;
    }

    // Create blob and download
    const blob = new Blob([response.data], {
      type: format === 'pdf' ? 'application/pdf' : 'text/csv',
    });
    
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `my-data-${Date.now()}.${format}`;
    link.click();
    window.URL.revokeObjectURL(url);

    return { success: true };
  } catch (error: any) {
    console.error('Download error:', error.response?.data || error.message);
    throw error;
  }
};

// Usage in component:
// await downloadPatientData('pdf', localStorage.getItem('token')!);
```

---

## 🚀 Quick Start Commands

```bash
# Backend
cd /home/ali/Desktop/projects/clink-backend
source venv/bin/activate
python manage.py runserver

# Frontend (in another terminal)
cd /path/to/your/frontend
npm run dev

# Test with curl
curl -X POST "http://127.0.0.1:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email": "testpatient@example.com", "password": "testpass123"}' \
  | jq -r '.access'

# Use the token from above
TOKEN="paste-token-here"
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/?export_format=pdf" \
  -H "Authorization: Bearer $TOKEN" \
  -o test.pdf
```

---

## 📚 API Documentation

### Endpoint: `GET /api/auth/data-access-request/`

**Query Parameters:**
- `export_format` (optional): `json` | `pdf` | `csv` (default: `json`)

**Headers:**
- `Authorization: Bearer <token>` (required)

**Response (JSON):**
```json
{
  "message": "Data access request successful",
  "request_date": "2025-11-19T10:00:00Z",
  "format": "json",
  "data": {
    "personal_information": {...},
    "patient_profile": {...},
    "appointments": [...],
    "progress_notes": [...],
    "billing": {...},
    "consent_records": {...},
    "audit_logs": [...]
  }
}
```

**Response (PDF/CSV):**
- Content-Type: `application/pdf` or `text/csv`
- Content-Disposition: `attachment; filename="my-data-..."`

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ No errors in browser console
2. ✅ Status code is `200 OK` in Network tab
3. ✅ File download starts automatically
4. ✅ Downloaded file opens correctly (PDF viewer / Excel / Text editor)

---

## 🆘 Still Having Issues?

If you're still getting errors after following this guide:

1. **Share the exact error** from browser console
2. **Share the Network request/response** from Developer Tools
3. **Check Django logs:** `tail -50 logs/django.log`
4. **Verify test account works:**
   - Email: `testpatient@example.com`
   - Password: `testpass123`

---

**Last Updated:** November 19, 2025
**Status:** ✅ Backend fully tested and working
**Next:** Frontend integration

