# 📋 Frontend Guide: Using Service ID for Booking

## 🎯 **The Problem**

Frontend fetches services correctly but gets "Service not found" when booking.

**Root Cause:** The `service_id` being sent doesn't match what exists in the database.

---

## ✅ **Current Database Status**

- **Only 1 service exists:** ID: 1 - "Telehealth Consultation"
- Frontend must use `service_id: 1` when booking

---

## 🔧 **Correct Frontend Implementation**

### **Step 1: Fetch Services**

```typescript
const fetchServices = async () => {
  const response = await fetch('/api/services/');
  if (!response.ok) {
    throw new Error('Failed to fetch services');
  }
  return await response.json();
};

// Usage
const services = await fetchServices();
// services = [{id: 1, name: "Telehealth Consultation", ...}]
```

### **Step 2: Store Service ID**

```typescript
// ✅ CORRECT: Store the ID from the service object
const selectedService = services[0]; // or user-selected service
const serviceId = selectedService.id; // This will be 1

// ❌ WRONG: Don't hardcode or use index
const serviceId = 2; // ❌ Service 2 doesn't exist!
const serviceId = services.indexOf(selectedService); // ❌ Wrong!
```

### **Step 3: Use Service ID When Booking**

```typescript
const bookAppointment = async (timeSlotId: number, serviceId: number) => {
  const response = await fetch('/api/appointments/book-enhanced/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      psychologist_id: psychologistId,
      service_id: serviceId,  // ✅ Use the ID from service object
      time_slot_id: timeSlotId,
      session_type: 'telehealth'
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Failed to book appointment');
  }
  
  return await response.json();
};

// Usage
const service = services.find(s => s.name === "Telehealth Consultation");
await bookAppointment(timeSlotId, service.id); // ✅ service.id = 1
```

---

## 🐛 **Common Mistakes**

### **Mistake 1: Using Service Name Instead of ID**
```typescript
// ❌ WRONG
body: JSON.stringify({
  service_id: "Telehealth Consultation", // ❌ Should be number, not string
  ...
})

// ✅ CORRECT
body: JSON.stringify({
  service_id: 1, // ✅ Use the ID
  ...
})
```

### **Mistake 2: Hardcoding Wrong ID**
```typescript
// ❌ WRONG
const serviceId = 2; // Service 2 doesn't exist!

// ✅ CORRECT
const serviceId = services[0].id; // Use ID from fetched services
```

### **Mistake 3: Using Array Index**
```typescript
// ❌ WRONG
const serviceId = services.indexOf(selectedService); // Returns 0, not 1

// ✅ CORRECT
const serviceId = selectedService.id; // Use the actual ID property
```

### **Mistake 4: Not Storing ID**
```typescript
// ❌ WRONG
const serviceName = "Telehealth Consultation";
// Later...
service_id: serviceName // ❌ Sending name instead of ID

// ✅ CORRECT
const service = {id: 1, name: "Telehealth Consultation"};
// Later...
service_id: service.id // ✅ Sending ID
```

---

## 📋 **Complete Example**

```typescript
// 1. Fetch services
const services = await fetch('/api/services/').then(r => r.json());
console.log('Available services:', services);
// Output: [{id: 1, name: "Telehealth Consultation", ...}]

// 2. Select service (or use first one)
const selectedService = services[0]; // or user-selected
console.log('Selected service ID:', selectedService.id); // Should be 1

// 3. Book appointment with correct service_id
const bookingData = {
  psychologist_id: 5,
  service_id: selectedService.id, // ✅ Use ID from service object
  time_slot_id: 123,
  session_type: 'telehealth'
};

const response = await fetch('/api/appointments/book-enhanced/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(bookingData)
});

if (!response.ok) {
  const error = await response.json();
  console.error('Booking error:', error);
  // Error now includes:
  // {
  //   error: "Service with ID X not found or is inactive",
  //   available_services: [{id: 1, name: "Telehealth Consultation"}],
  //   service_id_provided: X
  // }
  throw new Error(error.error);
}

const result = await response.json();
console.log('Booking successful:', result);
```

---

## 🔍 **Debugging**

### **Check What Service ID is Being Sent**

Add logging to see what's being sent:

```typescript
const bookingData = {
  psychologist_id: psychologistId,
  service_id: serviceId, // ← Check this value
  time_slot_id: timeSlotId,
  session_type: 'telehealth'
};

console.log('Booking with service_id:', bookingData.service_id);
console.log('Service ID type:', typeof bookingData.service_id);
// Should be: number 1, not string "1" or number 2

await fetch('/api/appointments/book-enhanced/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(bookingData)
});
```

### **Check Error Response**

The improved error response now shows:

```json
{
  "error": "Service with ID 2 not found or is inactive",
  "available_services": [
    {"id": 1, "name": "Telehealth Consultation"}
  ],
  "service_id_provided": 2
}
```

This tells you:
- What service_id was sent (2)
- What services are available (only ID 1)
- The problem (ID 2 doesn't exist)

---

## ✅ **Quick Fix**

If you just want to get it working quickly:

```typescript
// Quick fix: Use service ID 1 (the only service that exists)
const bookAppointment = async (timeSlotId: number) => {
  const response = await fetch('/api/appointments/book-enhanced/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      psychologist_id: psychologistId,
      service_id: 1, // ✅ Hardcode ID 1 for now
      time_slot_id: timeSlotId,
      session_type: 'telehealth'
    })
  });
  
  return await response.json();
};
```

**Then fix properly later** by fetching services and using the ID from the response.

---

## 📝 **Summary**

1. ✅ **Fetch services** from `/api/services/`
2. ✅ **Use `service.id`** (not name, not index, not hardcoded)
3. ✅ **Send as number** (not string)
4. ✅ **Check error response** for available services if booking fails

---

## 🚀 **Test**

```bash
# Test services endpoint
curl https://api.tailoredpsychology.com.au/api/services/

# Should return:
# [{"id": 1, "name": "Telehealth Consultation", ...}]

# Test booking with correct service_id
curl -X POST https://api.tailoredpsychology.com.au/api/appointments/book-enhanced/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "psychologist_id": 5,
    "service_id": 1,  # ← Use ID 1
    "time_slot_id": 123,
    "session_type": "telehealth"
  }'
```

