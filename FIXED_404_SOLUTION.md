# ✅ FIXED: 404 Error for PDF/CSV Downloads

## Problem Identified

The backend was returning `404 Not Found` for PDF and CSV downloads, but JSON worked fine.

## Root Cause

**Django REST Framework's `format` parameter conflict!**

When you use `?format=pdf` or `?format=csv`, DRF's built-in format negotiation system intercepts the request **before** it reaches your view code. DRF reserves the `format` parameter for its own content negotiation.

## The Fix (COMPLETED ✅)

Changed the query parameter name from `format` to `export_format` in the backend.

### Backend Changes (Done)
- Updated `users/views.py` - `DataAccessRequestView`
- Changed `request.query_params.get('format')` to `request.query_params.get('export_format')`

### Test Results

```bash
# ✅ JSON - Works
GET /api/auth/data-access-request/
Status: 200 OK

# ✅ PDF - Now Works!
GET /api/auth/data-access-request/?export_format=pdf
Status: 200 OK
Content-Type: application/pdf

# ✅ CSV - Now Works!
GET /api/auth/data-access-request/?export_format=csv
Status: 200 OK
Content-Type: text/csv
```

---

## Frontend Update Required

**You MUST update your frontend code to use the new parameter name.**

### Change This:

```typescript
// ❌ OLD - This will return 404
const response = await axios.get('data-access-request/', {
  params: { format: 'pdf' }  // DRF conflict!
});
```

### To This:

```typescript
// ✅ NEW - This works!
const response = await axios.get('data-access-request/', {
  params: { export_format: 'pdf' }  // No conflict!
});
```

---

## Complete Frontend Fix

In your `auth.ts` or wherever you handle data access requests:

```typescript
/**
 * Request access to user's data (Privacy Act 1988 - APP 12)
 * @param exportFormat - 'json', 'pdf', or 'csv'
 */
async requestDataAccess(exportFormat: 'json' | 'pdf' | 'csv' = 'json') {
  try {
    const response = await axiosInstance.get('data-access-request/', {
      params: { export_format: exportFormat },  // Changed from 'format'
      responseType: exportFormat === 'json' ? 'json' : 'blob',
    });
    
    // Handle PDF/CSV downloads
    if (exportFormat !== 'json' && response.data) {
      const blob = new Blob([response.data], { 
        type: exportFormat === 'pdf' ? 'application/pdf' : 'text/csv' 
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `my-data.${exportFormat}`;
      link.click();
      window.URL.revokeObjectURL(url);
    }
    
    return response;
  } catch (error) {
    console.error('[AuthService] Error requesting data access:', error);
    throw error;
  }
}
```

---

## Testing Credentials

Use this test patient account to verify:

- **Email:** `testpatient@example.com`
- **Password:** `testpass123`

### Test Steps:

1. Login with the test account
2. Try downloading PDF - should work now!
3. Try downloading CSV - should work now!
4. Try downloading JSON - should work as before!

---

## Why This Happened

DRF has built-in format suffix support:
- `/api/endpoint.json` 
- `/api/endpoint.pdf`
- `/api/endpoint.xml`

When you use `?format=xxx`, DRF thinks you're using its format negotiation feature and tries to handle it automatically. Since we're not using DRF's PDF/CSV renderers, it returns 404.

By renaming to `export_format`, we completely avoid this conflict.

---

## Summary

- ❌ **Before:** `?format=pdf` → 404 Not Found
- ✅ **After:** `?export_format=pdf` → 200 OK with PDF file

**Action Required:** Update your frontend to use `export_format` instead of `format`.

Once you make this one-line change in your frontend, PDF and CSV downloads will work perfectly!

