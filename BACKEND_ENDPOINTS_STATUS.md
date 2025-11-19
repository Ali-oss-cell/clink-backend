# Backend Endpoints Status - Admin & Billing

**Date:** 2025-01-19  
**Status:** Most Endpoints Ready ✅

---

## 📊 Executive Summary

**Reality Check:** The frontend document claiming these endpoints are "missing" is **mostly incorrect**. 3 out of 4 endpoints are **fully implemented and ready to use**.

| Endpoint | Document Claims | Reality | Status |
|----------|----------------|---------|--------|
| `GET /api/auth/admin/settings/` | ❌ Missing | ✅ **EXISTS** | ✅ Ready |
| `PUT /api/auth/admin/settings/` | ❌ Missing | ⚠️ **Placeholder** | 🔧 Needs Implementation |
| `GET /api/auth/admin/analytics/` | ❌ Missing | ✅ **EXISTS** | ✅ Ready (minor format difference) |
| `POST /api/billing/create-invoice/` | ❌ Missing | ✅ **EXISTS** (different URL) | ✅ Ready |

---

## ✅ 1. GET System Settings - **READY**

### Endpoint Details

**URL:** `GET /api/auth/admin/settings/`  
**Location:** `users/views.py` - `SystemSettingsView.get()`  
**Authentication:** Required (Admin role only)  
**Status:** ✅ **Fully Implemented**

### Request

```bash
GET /api/auth/admin/settings/
Authorization: Bearer <admin_token>
```

### Response (200 OK)

```json
{
  "clinic": {
    "name": "Psychology Clinic",
    "address": "",
    "phone": "",
    "email": "",
    "website": "",
    "abn": ""
  },
  "system": {
    "timezone": "Australia/Sydney",
    "language": "en-au",
    "gst_rate": 0.10,
    "medicare_provider_number": "",
    "ahpra_registration_number": ""
  },
  "notifications": {
    "email_enabled": true,
    "sms_enabled": false,
    "whatsapp_enabled": false
  },
  "billing": {
    "default_payment_method": "card",
    "invoice_terms_days": 30,
    "auto_generate_invoices": true
  }
}
```

### Frontend Integration

```typescript
// src/services/api/admin.ts
async getSystemSettings(): Promise<SystemSettings> {
  const response = await axiosInstance.get('/auth/admin/settings/');
  return response.data;
}
```

### Notes

- ✅ Fully functional
- ✅ Returns all settings from Django settings
- ✅ Ready for frontend use
- ⚠️ Settings are read from Django `settings.py` or environment variables

---

## ⚠️ 2. PUT System Settings - **NEEDS IMPLEMENTATION**

### Endpoint Details

**URL:** `PUT /api/auth/admin/settings/`  
**Location:** `users/views.py` - `SystemSettingsView.put()`  
**Authentication:** Required (Admin role only)  
**Status:** ⚠️ **Placeholder - Not Functional**

### Current Behavior

The endpoint exists but **does not save settings**. It returns a message:

```json
{
  "message": "Settings update via API is not fully implemented. Please update settings via environment variables or Django settings file.",
  "note": "For production, consider implementing a Settings model to store these values in the database."
}
```

### Request (What Frontend Sends)

```json
PUT /api/auth/admin/settings/
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "clinic": {
    "name": "MindWell Clinic",
    "address": "123 Health Street, Melbourne VIC 3000",
    "phone": "+61 3 9000 0000",
    "email": "info@mindwellclinic.com.au",
    "website": "https://mindwellclinic.com.au",
    "abn": "12 345 678 901"
  },
  "system": {
    "timezone": "Australia/Melbourne",
    "language": "en-au",
    "gst_rate": 0.10,
    "medicare_provider_number": "1234567A",
    "ahpra_registration_number": "PSY0001234567"
  },
  "notifications": {
    "email_enabled": true,
    "sms_enabled": true,
    "whatsapp_enabled": false
  },
  "billing": {
    "default_payment_method": "card",
    "invoice_terms_days": 30,
    "auto_generate_invoices": true
  }
}
```

### Expected Response (After Implementation)

```json
{
  "message": "Settings updated successfully",
  "settings": {
    "clinic": { ... },
    "system": { ... },
    "notifications": { ... },
    "billing": { ... }
  }
}
```

### Implementation Options

#### Option 1: Settings Model (Recommended for Production)

Create a `SystemSettings` model to store settings in the database:

```python
# core/models.py
class SystemSettings(models.Model):
    """System-wide settings stored in database"""
    
    # Clinic Information
    clinic_name = models.CharField(max_length=255, default='Psychology Clinic')
    clinic_address = models.TextField(blank=True)
    clinic_phone = models.CharField(max_length=20, blank=True)
    clinic_email = models.EmailField(blank=True)
    clinic_website = models.URLField(blank=True)
    clinic_abn = models.CharField(max_length=20, blank=True)
    
    # System Configuration
    timezone = models.CharField(max_length=50, default='Australia/Sydney')
    language = models.CharField(max_length=10, default='en-au')
    gst_rate = models.DecimalField(max_digits=5, decimal_places=4, default=0.10)
    medicare_provider_number = models.CharField(max_length=20, blank=True)
    ahpra_registration_number = models.CharField(max_length=13, blank=True)
    
    # Notifications
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    whatsapp_enabled = models.BooleanField(default=False)
    
    # Billing
    default_payment_method = models.CharField(max_length=20, default='card')
    invoice_terms_days = models.IntegerField(default=30)
    auto_generate_invoices = models.BooleanField(default=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'
    
    def __str__(self):
        return 'System Settings'
    
    @classmethod
    def get_settings(cls):
        """Get or create system settings (singleton pattern)"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
```

Then update the view:

```python
# users/views.py - SystemSettingsView.put()
def put(self, request):
    """Update system settings"""
    if not request.user.is_admin_user():
        return Response(
            {'error': 'Only administrators can update system settings'}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    from core.models import SystemSettings
    settings = SystemSettings.get_settings()
    
    data = request.data
    
    # Update clinic settings
    if 'clinic' in data:
        clinic = data['clinic']
        settings.clinic_name = clinic.get('name', settings.clinic_name)
        settings.clinic_address = clinic.get('address', settings.clinic_address)
        settings.clinic_phone = clinic.get('phone', settings.clinic_phone)
        settings.clinic_email = clinic.get('email', settings.clinic_email)
        settings.clinic_website = clinic.get('website', settings.clinic_website)
        settings.clinic_abn = clinic.get('abn', settings.clinic_abn)
    
    # Update system settings
    if 'system' in data:
        system = data['system']
        settings.timezone = system.get('timezone', settings.timezone)
        settings.language = system.get('language', settings.language)
        settings.gst_rate = system.get('gst_rate', settings.gst_rate)
        settings.medicare_provider_number = system.get('medicare_provider_number', settings.medicare_provider_number)
        # Validate AHPRA number
        ahpra = system.get('ahpra_registration_number', '')
        if ahpra:
            from users.views import validate_ahpra_number
            is_valid, result = validate_ahpra_number(ahpra)
            if not is_valid:
                return Response({'error': result}, status=status.HTTP_400_BAD_REQUEST)
            settings.ahpra_registration_number = result
    
    # Update notification settings
    if 'notifications' in data:
        notifications = data['notifications']
        settings.email_enabled = notifications.get('email_enabled', settings.email_enabled)
        settings.sms_enabled = notifications.get('sms_enabled', settings.sms_enabled)
        settings.whatsapp_enabled = notifications.get('whatsapp_enabled', settings.whatsapp_enabled)
    
    # Update billing settings
    if 'billing' in data:
        billing = data['billing']
        settings.default_payment_method = billing.get('default_payment_method', settings.default_payment_method)
        settings.invoice_terms_days = billing.get('invoice_terms_days', settings.invoice_terms_days)
        settings.auto_generate_invoices = billing.get('auto_generate_invoices', settings.auto_generate_invoices)
    
    settings.save()
    
    # Return updated settings
    return Response({
        'message': 'Settings updated successfully',
        'settings': {
            'clinic': {
                'name': settings.clinic_name,
                'address': settings.clinic_address,
                'phone': settings.clinic_phone,
                'email': settings.clinic_email,
                'website': settings.clinic_website,
                'abn': settings.clinic_abn
            },
            'system': {
                'timezone': settings.timezone,
                'language': settings.language,
                'gst_rate': float(settings.gst_rate),
                'medicare_provider_number': settings.medicare_provider_number,
                'ahpra_registration_number': settings.ahpra_registration_number
            },
            'notifications': {
                'email_enabled': settings.email_enabled,
                'sms_enabled': settings.sms_enabled,
                'whatsapp_enabled': settings.whatsapp_enabled
            },
            'billing': {
                'default_payment_method': settings.default_payment_method,
                'invoice_terms_days': settings.invoice_terms_days,
                'auto_generate_invoices': settings.auto_generate_invoices
            }
        }
    })
```

#### Option 2: Environment Variables (Current Approach)

Keep using environment variables but update them via a management command or admin interface. This requires server restart.

### Validation Requirements

When implementing, validate:

- **AHPRA registration number**: Must be format `PSY0001234567` (3 letters + 10 digits)
- **GST rate**: Must be between 0 and 1
- **Email**: Must be valid email format
- **Phone**: Must be valid Australian format
- **ABN**: Must be valid ABN format (11 digits)

---

## ✅ 3. GET System Analytics - **READY**

### Endpoint Details

**URL:** `GET /api/auth/admin/analytics/`  
**Location:** `users/views.py` - `SystemAnalyticsView.get()`  
**Authentication:** Required (Admin role only)  
**Status:** ✅ **Fully Implemented**

### Query Parameters

- `period` (optional): `"today"`, `"week"`, `"month"`, `"year"`, `"all"` (default: `"month"`)
- `start_date` (optional): ISO date string (e.g., `"2025-01-01"`)
- `end_date` (optional): ISO date string (e.g., `"2025-01-31"`)

### Request Examples

```bash
# Monthly analytics (default)
GET /api/auth/admin/analytics/

# Weekly analytics
GET /api/auth/admin/analytics/?period=week

# Custom date range
GET /api/auth/admin/analytics/?start_date=2025-01-01&end_date=2025-01-31

# All-time analytics
GET /api/auth/admin/analytics/?period=all
```

### Response (200 OK)

```json
{
  "period": {
    "type": "month",
    "start_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "users": {
    "total": 500,
    "by_role": [
      {"role": "patient", "count": 400},
      {"role": "psychologist", "count": 15},
      {"role": "practice_manager", "count": 3},
      {"role": "admin", "count": 2}
    ],
    "growth": [
      {"date": "2025-01-01", "count": 5},
      {"date": "2025-01-02", "count": 3}
    ],
    "verified_count": 450,
    "verification_rate": 90.0
  },
  "appointments": {
    "total": 2500,
    "by_status": [
      {"status": "completed", "count": 2000},
      {"status": "scheduled", "count": 400},
      {"status": "cancelled", "count": 100}
    ],
    "by_type": [
      {"session_type": "individual", "count": 2000},
      {"session_type": "telehealth", "count": 500}
    ],
    "trends": [
      {"date": "2025-01-01", "count": 50},
      {"date": "2025-01-02", "count": 45}
    ]
  },
  "financial": {
    "total_revenue": 300000.00,
    "total_invoices": 2000,
    "paid_invoices": 1800,
    "pending_invoices": 200,
    "total_medicare_claims": 1500
  },
  "progress_notes": {
    "total": 1800,
    "average_rating": 7.5
  },
  "performance": {
    "active_patients": 120,
    "total_users": 500,
    "verification_rate": 90.0
  }
}
```

### Frontend Integration

```typescript
// src/services/api/admin.ts
async getSystemAnalytics(params?: {
  period?: 'today' | 'week' | 'month' | 'year' | 'all';
  start_date?: string;
  end_date?: string;
}): Promise<SystemAnalytics> {
  const response = await axiosInstance.get('/auth/admin/analytics/', { params });
  return response.data;
}
```

### Format Difference Note

**Frontend Document Expects:**
```json
{
  "users": {
    "by_role": {
      "patient": 1000,
      "psychologist": 20
    }
  }
}
```

**Backend Actually Returns:**
```json
{
  "users": {
    "by_role": [
      {"role": "patient", "count": 400},
      {"role": "psychologist", "count": 15}
    ]
  }
}
```

**Frontend Fix Needed:**
```typescript
// Convert array to object if needed
const byRoleObject = analytics.users.by_role.reduce((acc, item) => {
  acc[item.role] = item.count;
  return acc;
}, {} as Record<string, number>);
```

### Notes

- ✅ Fully functional
- ✅ Comprehensive analytics
- ✅ Date range filtering works
- ⚠️ Minor format difference: `by_role` is array, not object (easy to convert in frontend)

---

## ✅ 4. POST Create Invoice - **READY** (Different URL)

### Endpoint Details

**URL:** `POST /api/billing/invoices/` (NOT `/api/billing/create-invoice/`)  
**Location:** `billing/views.py` - `InvoiceViewSet.create()`  
**Authentication:** Required  
**Status:** ✅ **Fully Implemented**

### Request

```json
POST /api/billing/invoices/
Authorization: Bearer <token>
Content-Type: application/json

{
  "patient": 45,
  "appointment": 123,
  "service_description": "Individual therapy session",
  "service_date": "2025-01-19",
  "subtotal_amount": "180.00",
  "medicare_item_number": 1,
  "due_date": "2025-02-19",
  "abn": "12 345 678 901"
}
```

### Response (201 Created)

```json
{
  "id": 456,
  "invoice_number": "INV-2025-001",
  "patient": 45,
  "patient_name": "John Doe",
  "appointment": 123,
  "service_description": "Individual therapy session",
  "service_date": "2025-01-19",
  "subtotal_amount": "180.00",
  "gst_amount": "18.00",
  "total_amount": "198.00",
  "medicare_rebate": "89.65",
  "out_of_pocket": "108.35",
  "status": "draft",
  "due_date": "2025-02-19",
  "created_at": "2025-01-19T10:00:00Z"
}
```

### Frontend Integration

**Option 1: Use Existing Endpoint**

```typescript
// src/services/api/billing.ts
async createInvoice(data: CreateInvoiceRequest): Promise<Invoice> {
  const response = await axiosInstance.post('/billing/invoices/', data);
  return response.data;
}
```

**Option 2: Add Alias Endpoint (If Frontend Requires Exact URL)**

Add to `billing/urls.py`:

```python
from .views import InvoiceViewSet

urlpatterns = [
    # ... existing patterns ...
    path('create-invoice/', InvoiceViewSet.as_view({'post': 'create'}), name='create-invoice'),
]
```

### Validation

The endpoint validates:

- ✅ Appointment belongs to patient
- ✅ Appointment is completed (status = 'completed')
- ✅ Medicare item number is valid (if provided)
- ✅ Auto-calculates GST (10%)
- ✅ Auto-calculates Medicare rebate (if item number provided)

### Notes

- ✅ Fully functional
- ✅ Auto-calculates GST and Medicare rebates
- ✅ Validates appointment completion
- ⚠️ URL is `/invoices/` not `/create-invoice/` (can add alias if needed)

---

## 📋 Implementation Checklist

### ✅ Already Complete

- [x] `GET /api/auth/admin/settings/` - Fully implemented
- [x] `GET /api/auth/admin/analytics/` - Fully implemented
- [x] `POST /api/billing/invoices/` - Fully implemented (create invoice)

### 🔧 Needs Implementation

- [ ] `PUT /api/auth/admin/settings/` - Create Settings model and implement save logic

### 📝 Frontend Updates Needed

- [ ] Update analytics `by_role` handling (array vs object)
- [ ] Use `/api/billing/invoices/` instead of `/create-invoice/` OR add alias endpoint
- [ ] Handle PUT settings endpoint (currently returns placeholder message)

---

## 🎯 Priority Actions

### High Priority

1. **Implement Settings Model** for `PUT /api/auth/admin/settings/`
   - Create `SystemSettings` model
   - Update `SystemSettingsView.put()` method
   - Add validation (AHPRA, email, phone, etc.)
   - Create migration

### Medium Priority

2. **Frontend Format Adjustment**
   - Update analytics `by_role` handling
   - Convert array to object if needed

3. **Invoice Endpoint Alias** (Optional)
   - Add `/create-invoice/` alias if frontend requires exact URL

---

## 📚 Related Documentation

- **Admin Endpoints Summary:** `ADMIN_ENDPOINTS_SUMMARY.md`
- **Admin API Reference:** `ADMIN_API_JSON_REFERENCE.md`
- **Billing API:** `billing/views.py` and `billing/urls.py`
- **AHPRA Validation:** `FRONTEND_AHPRA_VALIDATION_GUIDE.md`

---

## ✅ Summary

**Status:** 3 out of 4 endpoints are **ready to use**. Only the PUT settings endpoint needs implementation.

**Frontend Impact:** Minimal - mostly ready, just needs:
1. Settings model implementation for PUT endpoint
2. Minor analytics format adjustment
3. Use correct invoice endpoint URL

**Recommendation:** Implement the Settings model to complete the admin settings functionality.

---

**Last Updated:** 2025-01-19  
**Status:** ✅ Mostly Complete - 1 Endpoint Needs Implementation

