# Frontend Data Access Request - Fix Guide

## The Problem

The frontend is getting "API endpoint not found" error. This is likely because:

1. **Django server needs restart** - The endpoint was just added
2. **Response type issue** - PDF/CSV need `responseType: 'blob'`
3. **Error handling** - Frontend might be checking for 404 incorrectly

---

## Frontend Code Fix

### Update `auth.ts` (or your API service file)

```typescript
// Add this function to your authService or API service
export const dataAccessService = {
  requestDataAccess: async (format: 'json' | 'pdf' | 'csv' = 'json') => {
    const token = localStorage.getItem('access_token'); // Make sure it's 'access_token' not 'token'
    const baseURL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
    
    const config: any = {
      headers: {
        Authorization: `Bearer ${token}`
      }
    };
    
    // For PDF and CSV, we need blob response type
    if (format === 'pdf' || format === 'csv') {
      config.responseType = 'blob';
    }
    
    try {
      const response = await axios.get(
        `${baseURL}/api/auth/data-access-request/?format=${format}`,
        config
      );
      
      return response;
    } catch (error: any) {
      // Better error handling
      if (error.response?.status === 404) {
        throw new Error('Data access endpoint not found. Please ensure the Django server is running and restarted.');
      } else if (error.response?.status === 403) {
        throw new Error('You do not have permission to access this data.');
      } else if (error.response?.status === 401) {
        throw new Error('Please log in to access your data.');
      } else {
        throw new Error(error.response?.data?.error || 'Failed to request data access');
      }
    }
  }
};
```

### Update `PatientAccountPage.tsx`

```typescript
import { dataAccessService } from '../services/api/auth'; // or wherever your service is

// Download PDF
const handleDownloadPDF = async () => {
  try {
    const response = await dataAccessService.requestDataAccess('pdf');
    
    // Create blob and download
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `my-data-${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    console.log('PDF downloaded successfully');
  } catch (error: any) {
    console.error('Error downloading PDF:', error);
    alert(error.message || 'Failed to download PDF');
  }
};

// Download CSV
const handleDownloadCSV = async () => {
  try {
    const response = await dataAccessService.requestDataAccess('csv');
    
    // Create blob and download
    const blob = new Blob([response.data], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `my-data-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    console.log('CSV downloaded successfully');
  } catch (error: any) {
    console.error('Error downloading CSV:', error);
    alert(error.message || 'Failed to download CSV');
  }
};

// Download JSON
const handleDownloadJSON = async () => {
  try {
    const response = await dataAccessService.requestDataAccess('json');
    
    // Download as JSON file
    const dataStr = JSON.stringify(response.data.data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `my-data-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    console.log('JSON downloaded successfully');
  } catch (error: any) {
    console.error('Error downloading JSON:', error);
    alert(error.message || 'Failed to download JSON');
  }
};
```

---

## Quick Checklist

1. ✅ **Restart Django Server**
   ```bash
   # Stop server (Ctrl+C)
   python manage.py runserver
   ```

2. ✅ **Check Token Storage**
   - Make sure you're using `access_token` not `token`
   - Check: `localStorage.getItem('access_token')`

3. ✅ **Check Base URL**
   - Make sure `REACT_APP_API_URL` is set correctly
   - Or use: `http://127.0.0.1:8000` or `http://localhost:8000`

4. ✅ **Use Correct Response Type**
   - JSON: `responseType: 'json'` (default)
   - PDF: `responseType: 'blob'`
   - CSV: `responseType: 'blob'`

5. ✅ **Test Endpoint Directly**
   ```bash
   curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/" \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

---

## Common Issues

### Issue 1: 404 Not Found
**Solution:** Restart Django server

### Issue 2: 401 Unauthorized
**Solution:** Check token is valid and in `Authorization: Bearer <token>` header

### Issue 3: 403 Forbidden
**Solution:** Make sure user is a patient (not psychologist/admin)

### Issue 4: PDF/CSV shows as text
**Solution:** Use `responseType: 'blob'` in axios config

---

## Test the Endpoint

```bash
# Test with curl (replace YOUR_TOKEN)
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/?format=json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json"
```

If this works, the backend is fine - the issue is in the frontend code!

