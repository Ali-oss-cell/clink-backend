# 🔧 Fix: "Service not found" Error

## 🐛 **Problem**

Frontend is getting `{error: 'Service not found'}` when trying to book an appointment.

## ✅ **Solution**

### **Current Status:**
- ✅ Only **1 service exists** in database: **ID: 1** - "Telehealth Consultation"
- ❌ Frontend is probably sending `service_id: 2` (or another ID that doesn't exist)

---

## 🔍 **Diagnosis**

### **Check Available Services:**
```bash
cd /var/www/clink-backend
source venv/bin/activate
python check_services.py
```

**Output shows:**
```
ID: 1 - Telehealth Consultation (Active)
```

---

## ✅ **Fix Options**

### **Option 1: Frontend Should Use Service ID 1**

The frontend should:
1. Fetch services from `/api/services/` endpoint
2. Use the `id` from the response
3. Send `service_id: 1` when booking

**Example:**
```typescript
// Fetch services
const services = await fetch('/api/services/').then(r => r.json());
// services = [{id: 1, name: "Telehealth Consultation", ...}]

// Use service ID when booking
await bookAppointment({
  service_id: 1,  // ← Use ID from services list
  time_slot_id: 123,
  psychologist_id: 5
});
```

### **Option 2: Create More Services**

If you need more services, create them via:
- Django Admin: `/admin/services/service/`
- API: `POST /api/services/` (requires authentication)

---

## 📋 **Services Endpoint**

### **Get All Services:**
```http
GET /api/services/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Telehealth Consultation",
    "description": "...",
    "standard_fee": "180.00",
    "medicare_rebate": "87.45",
    "duration_minutes": 60,
    "is_active": true
  }
]
```

---

## 🔧 **Frontend Code Fix**

### **Before (Wrong):**
```typescript
// Hardcoded service_id that doesn't exist
const serviceId = 2;  // ❌ Service 2 doesn't exist!
```

### **After (Correct):**
```typescript
// Fetch services first
const fetchServices = async () => {
  const response = await fetch('/api/services/');
  const services = await response.json();
  return services;
};

// Use first available service
const services = await fetchServices();
const serviceId = services[0]?.id;  // ✅ Use ID 1

// Or let user select
const selectedService = services.find(s => s.name === "Telehealth Consultation");
const serviceId = selectedService?.id;  // ✅ Use ID 1
```

---

## 🎯 **Quick Test**

### **Test Services Endpoint:**
```bash
curl https://api.tailoredpsychology.com.au/api/services/
```

**Should return:**
```json
[
  {
    "id": 1,
    "name": "Telehealth Consultation",
    ...
  }
]
```

### **Test Booking with Correct Service ID:**
```bash
curl -X POST https://api.tailoredpsychology.com.au/api/appointments/book-enhanced/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "psychologist_id": 5,
    "service_id": 1,  # ← Use ID 1 (the only service that exists)
    "time_slot_id": 123,
    "session_type": "telehealth"
  }'
```

---

## 📝 **Summary**

**Problem:** Frontend sending `service_id` that doesn't exist  
**Solution:** Use `service_id: 1` (the only active service)  
**Prevention:** Always fetch services from `/api/services/` and use IDs from response

---

## 🚀 **Next Steps**

1. ✅ Check what `service_id` frontend is sending (check browser console/network tab)
2. ✅ Update frontend to use `service_id: 1` or fetch from `/api/services/`
3. ✅ Test booking again
4. ✅ (Optional) Create more services if needed

