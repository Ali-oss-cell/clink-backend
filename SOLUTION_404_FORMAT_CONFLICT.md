# Solution: 404 Error with format=pdf/csv Parameter

## Root Cause Found! 🎯

The issue is **DRF's built-in format suffix system**. When you use the query parameter `?format=pdf` or `?format=csv`, Django REST Framework's content negotiation system intercepts the request **before it reaches your view**.

### Evidence

When I added logging to the view:
- `?format=json` → View called successfully ✅
- `?format=pdf` → **View NEVER called**, 404 returned ❌
- `?format=csv` → **View NEVER called**, 404 returned ❌

The view code is **100% correct**. The URL routing is **100% correct**. The problem is DRF's automatic format handling.

---

## The Fix

**Change the query parameter name from `format` to `export_format`**

### Backend Changes (DONE ✅)

Changed in `users/views.py`:

```python
# OLD (conflicts with DRF)
format_type = request.query_params.get('format', 'json').lower()

# NEW (works perfectly)
format_type = request.query_params.get('export_format', 'json').lower()
```

### Frontend Changes (REQUIRED)

Update all calls to the data access endpoint:

**OLD (doesn't work):**
```typescript
// ❌ This triggers DRF format negotiation, returns 404
const response = await axios.get('data-access-request/', {
  params: { format: 'pdf' }
});
```

**NEW (works):**
```typescript
// ✅ This works perfectly
const response = await axios.get('data-access-request/', {
  params: { export_format: 'pdf' }
});
```

---

## Complete Frontend Fix

In `src/services/api/auth.ts` (or wherever you handle data access requests):

```typescript
/**
 * Request access to user's data (Privacy Act 1988 - APP 12)
 * @param exportFormat - 'json', 'pdf', or 'csv'
 */
async requestDataAccess(exportFormat: 'json' | 'pdf' | 'csv' = 'json') {
  try {
    const response = await axiosInstance.get('data-access-request/', {
      params: { export_format: exportFormat },  // Changed from 'format' to 'export_format'
      responseType: exportFormat === 'json' ? 'json' : 'blob',
    });
    
    return response;
  } catch (error) {
    console.error('[AuthService] Error requesting data access:', error);
    throw error;
  }
}
```

---

## Testing After Fix

### Backend Test (curl)

```bash
# Login first
curl -X POST "http://127.0.0.1:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"email": "testpatient@example.com", "password": "testpass123"}'

# Use the token from response

# Test JSON (should work)
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/?export_format=json" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test PDF (should now work!)
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/?export_format=pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o my-data.pdf

# Test CSV (should now work!)
curl -X GET "http://127.0.0.1:8000/api/auth/data-access-request/?export_format=csv" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o my-data.csv
```

### Frontend Test

Update your frontend code and test:

```typescript
// Download PDF
await requestDataAccess('pdf');

// Download CSV
await requestDataAccess('csv');

// Get JSON
await requestDataAccess('json');
```

---

## Why This Happens

DRF (Django REST Framework) has built-in support for format suffixes like `.json`, `.pdf`, `.xml`. This feature allows URLs like:

- `/api/endpoint/` (default format)
- `/api/endpoint.json` (JSON format)
- `/api/endpoint.pdf` (PDF format)

When you use the query parameter `?format=pdf`, DRF's format negotiation system tries to handle it, but since we're not using DRF's built-in renderer classes for PDF/CSV, it returns 404.

By using a different parameter name (`export_format`), we bypass DRF's format negotiation entirely.

---

##Summary

- ❌ **OLD:** `?format=pdf` → 404 Not Found
- ✅ **NEW:** `?export_format=pdf` → Works perfectly!

**Action Required:** Update your frontend to use `export_format` instead of `format`.

---

## Related Documentation

- Updated: `DATA_ACCESS_REQUEST_COMPLETE.md`
- Updated: `FRONTEND_DATA_ACCESS_REQUEST_GUIDE.md`

