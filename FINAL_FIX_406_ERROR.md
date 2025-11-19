# ✅ FINAL FIX: 406 Not Acceptable Error - SOLVED!

## 🎯 THE ONE CHANGE YOU NEED

**In your frontend `auth.ts` file, change this:**

```typescript
// ❌ OLD (doesn't work)
params: { format: exportFormat }

// ✅ NEW (works!)
params: { export_format: exportFormat }
```

**That's it! Just change `format` to `export_format`!**

---

## Problem History

1. **First Issue:** 404 Not Found with `?format=pdf`
   - **Cause:** DRF's `format` parameter conflict
   - **Fix:** Changed to `?export_format=pdf` ✅

2. **Second Issue:** 406 Not Acceptable with `?export_format=pdf`
   - **Cause:** DRF content negotiation trying to render HttpResponse
   - **Fix:** Override `finalize_response()` to bypass DRF for HttpResponse ✅

---

## Final Solution (WORKING NOW!)

Added `finalize_response()` method to `DataAccessRequestView`:

```python
def finalize_response(self, request, response, *args, **kwargs):
    """Override to bypass DRF rendering for HttpResponse (PDF/CSV files)"""
    # If it's a Django HttpResponse (not DRF Response), return as-is
    from django.http import HttpResponse
    if isinstance(response, HttpResponse) and not isinstance(response, Response):
        return response
    # Otherwise, use default DRF finalization for Response objects (JSON)
    return super().finalize_response(request, response, *args, **kwargs)
```

This tells DRF:
- If it's an `HttpResponse` (PDF/CSV), don't process it - just return it
- If it's a `Response` object (JSON), process it normally

---

## Test Results

All three formats work perfectly:

```bash
# ✅ JSON Format
GET /api/auth/data-access-request/?export_format=json
Status: 200 OK
Content-Type: application/json

# ✅ PDF Format  
GET /api/auth/data-access-request/?export_format=pdf
Status: 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="my-data-Test-Patient-20251118.pdf"

# ✅ CSV Format
GET /api/auth/data-access-request/?export_format=csv
Status: 200 OK
Content-Type: text/csv
Content-Disposition: attachment; filename="my-data-Test-Patient-20251118.csv"
```

---

## Frontend Update

Update your frontend to use `export_format` instead of `format`:

```typescript
// In auth.ts or your data access service
async requestDataAccess(exportFormat: 'json' | 'pdf' | 'csv' = 'json') {
  const response = await axiosInstance.get('data-access-request/', {
    params: { export_format: exportFormat },  // Changed from 'format'
    responseType: exportFormat === 'json' ? 'json' : 'blob',
  });
  
  // Handle file downloads for PDF/CSV
  if (exportFormat !== 'json' && response.data) {
    const blob = new Blob([response.data], {
      type: exportFormat === 'pdf' ? 'application/pdf' : 'text/csv'
    });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `my-data-${new Date().toISOString().split('T')[0]}.${exportFormat}`;
    link.click();
    window.URL.revokeObjectURL(url);
  }
  
  return response;
}
```

---

## Test Account

- **Email:** `testpatient@example.com`
- **Password:** `testpass123`

---

## What Changed in Backend

### File: `users/views.py`

1. **Query Parameter Name:**
   - OLD: `?format=pdf` ❌
   - NEW: `?export_format=pdf` ✅

2. **Added `finalize_response()` Override:**
   ```python
   def finalize_response(self, request, response, *args, **kwargs):
       from django.http import HttpResponse
       if isinstance(response, HttpResponse) and not isinstance(response, Response):
           return response
       return super().finalize_response(request, response, *args, **kwargs)
   ```

---

## Summary

✅ **All formats working:**
- JSON: Works
- PDF: Works (2.2 KB file downloaded)
- CSV: Works (1 KB file downloaded)

✅ **Backend: 100% complete**
✅ **Ready for frontend integration**

**Next Step:** Update your frontend to use `export_format` instead of `format` and test!

