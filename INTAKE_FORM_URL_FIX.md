# 🔧 Intake Form URL Issue - Fix

## Problem

Frontend is calling: `POST /api/users/intake-form/`  
But getting: **405 Method Not Allowed**

## Root Cause

The intake form endpoint is registered in `users/urls.py` which is included at `/api/auth/`, not `/api/users/`.

**Current URL structure:**
- `users/urls.py` → included at `/api/auth/` (line 52 in main urls.py)
- So intake form is at: `/api/auth/intake-form/` ✅
- But frontend calls: `/api/users/intake-form/` ❌

## Solution Options

### Option 1: Fix Frontend (Recommended)
Change frontend to use correct URL:
```javascript
// Change from:
POST /api/users/intake-form/

// To:
POST /api/auth/intake-form/
```

### Option 2: Add Duplicate Route (Quick Fix)
Add intake form route to `/api/users/` as well:

```python
# In users/urls.py, add to users_urlpatterns:
users_urlpatterns = [
    path('', include(users_router.urls)),
    path('intake-form/', views.IntakeFormView.as_view(), name='intake-form-users'),  # ADD THIS
]
```

### Option 3: Move Route (Better Organization)
Move intake form to `/api/users/` since it's user-specific data.

---

## Current URL Structure

```
/api/auth/intake-form/          ✅ EXISTS (GET, POST, PUT)
/api/users/intake-form/          ❌ DOESN'T EXIST
```

---

## Quick Fix (Add Route)

Add this to `users/urls.py`:

```python
# Separate URL patterns for /api/users/ endpoint
users_urlpatterns = [
    # User ViewSet at root
    path('', include(users_router.urls)),
    # Add intake form here too
    path('intake-form/', views.IntakeFormView.as_view(), name='intake-form-users'),
]
```

This will make it available at both:
- `/api/auth/intake-form/` (existing)
- `/api/users/intake-form/` (new, matches frontend)

---

**Which option do you prefer?** I recommend Option 2 (add duplicate route) for quick fix.


