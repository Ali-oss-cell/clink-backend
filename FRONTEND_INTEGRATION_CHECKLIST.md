# Frontend Integration Checklist - Prevent Common Errors

## 🎯 **GOLDEN RULE: Never Hardcode IDs!**

**❌ WRONG:** 
```typescript
const psychologistId = 1; // Hardcoded
const serviceId = 3;      // Hardcoded
```

**✅ CORRECT:**
```typescript
// ALWAYS get IDs from API responses
const psychologists = await fetch('/api/services/psychologists/').then(r => r.json());
const psychologistId = psychologists[0].id; // From API

const services = await fetch('/api/services/services/', { headers: auth }).then(r => r.json());
const serviceId = services.find(s => s.name === "Individual Therapy").id; // From API
```

**Why?** IDs can change in the database. Always fetch from API and use the `id` field from the response.

---

## ⚠️ Common Errors and How to Prevent Them

### 1. **404 Error: Psychologist Not Found**

**Error:**
```
GET /api/appointments/available-slots/?psychologist_id=1
Response: 404 or {"error": "Psychologist not found"}
```

**Problem:** Using invalid psychologist ID

**Solution:** ✅ Only use valid psychologist IDs

```typescript
// ❌ WRONG - Hardcoded ID that doesn't exist
const psychologistId = 1;

// ✅ CORRECT - Get ID from psychologist selection
const psychologistId = selectedPsychologist.id; // From API response
```

**How to Get Valid Psychologist IDs:**
```typescript
// ✅ CORRECT - Get IDs from API response
const response = await fetch('/api/services/psychologists/');
const psychologists = await response.json();

// psychologists is an array like:
// [
//   { id: 3, user_name: "Dr. Sarah Johnson", ... },
//   { id: 4, user_name: "Dr. Sarah Johnson", ... },
//   { id: 5, user_name: "Dr. Michael Chen", ... }
// ]

// When user selects a psychologist from the list:
const selectedPsychologist = psychologists[0]; // User's selection
const psychologistId = selectedPsychologist.id; // Use THIS id (e.g., 3)
```

**❌ NEVER hardcode like this:**
```typescript
const psychologistId = 1; // DON'T DO THIS!
```

---

### 2. **401 Unauthorized: Authentication Required**

**Error:**
```
GET /api/services/services/
Response: 401 {"detail": "Authentication credentials were not provided."}
```

**Problem:** Calling authenticated endpoints without login

**Solution:** ✅ Login first, then use auth token

```typescript
// Step 1: Login
const loginResponse = await fetch('/api/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password123'
  })
});

const { access, refresh } = await loginResponse.json();
localStorage.setItem('access_token', access);

// Step 2: Use token in all subsequent requests
const response = await fetch('/api/services/services/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
});
```

---

### 3. **Service ID Type Error**

**Error:**
```
POST /api/appointments/book-enhanced/
Body: { "service_id": "psychological-assessment", ... }
Response: 400 or 404
```

**Problem:** Sending service slug instead of numeric ID

**Solution:** ✅ Convert slug to numeric ID first

```typescript
// ❌ WRONG - Using slug directly
const serviceId = "psychological-assessment";

// ✅ CORRECT - Fetch services and map slug to ID
const servicesResponse = await fetch('/api/services/services/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const services = await servicesResponse.json();

// Create mapping
const serviceMap = services.reduce((map, service) => {
  const slug = service.name.toLowerCase().replace(/ /g, '-');
  map[slug] = service.id;
  return map;
}, {});

const serviceId = serviceMap['psychological-assessment']; // Returns 3 (numeric)
```

**How to Get Valid Service IDs:**
```typescript
// ✅ CORRECT - Get IDs from API response
const response = await fetch('/api/services/services/', {
  headers: { 'Authorization': `Bearer ${token}` }
});
const services = await response.json();

// services is an array like:
// [
//   { id: 1, name: "Individual Therapy Session", ... },
//   { id: 2, name: "Couples Therapy Session", ... },
//   { id: 3, name: "Psychological Assessment", ... }
// ]

// When user selects a service from the list or URL slug:
const selectedService = services.find(s => 
  s.name.toLowerCase().replace(/ /g, '-') === 'individual-therapy-session'
);
const serviceId = selectedService.id; // Use THIS id (e.g., 1)
```

**❌ NEVER hardcode like this:**
```typescript
const serviceId = 1; // DON'T DO THIS!
```

---

### 4. **Missing Required Fields in Booking**

**Error:**
```
POST /api/appointments/book-enhanced/
Response: 400 {"error": "psychologist_id, service_id, and time_slot_id are required"}
```

**Problem:** Missing required fields in booking request

**Solution:** ✅ Always include all required fields

```typescript
// ✅ CORRECT - All required fields
const bookingData = {
  psychologist_id: 3,              // Required: numeric ID
  service_id: 1,                   // Required: numeric ID
  time_slot_id: 99,                // Required: numeric ID from slots list
  session_type: 'telehealth',      // Required: 'telehealth' or 'in_person'
  notes: 'First session'           // Optional: any text
};

await fetch('/api/appointments/book-enhanced/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(bookingData)
});
```

---

### 5. **Invalid Session Type**

**Error:**
```
POST /api/appointments/book-enhanced/
Body: { "session_type": "online", ... }
Response: 400 {"error": "session_type must be either 'telehealth' or 'in_person'"}
```

**Problem:** Using invalid session type value

**Solution:** ✅ Only use valid session types

```typescript
// ❌ WRONG
const sessionType = 'online';
const sessionType = 'video';
const sessionType = 'virtual';

// ✅ CORRECT - Only these two values
const sessionType = 'telehealth';  // For video sessions
const sessionType = 'in_person';   // For physical office visits
```

---

## 📋 Complete Booking Flow Checklist

### Frontend Implementation Checklist:

- [ ] **Step 1: User Authentication**
  - [ ] Implement login form
  - [ ] Store access token in localStorage
  - [ ] Add token to all API requests

- [ ] **Step 2: Browse Psychologists**
  - [ ] Fetch from `/api/services/psychologists/` ( auth)
  - [ ] Display psychologist cards with profile info
  - [ ] Store selected psychologist's numeric ID

- [ ] **Step 3: Fetch Services**
  - [ ] Call `/api/services/services/` with auth token
  - [ ] Create slug-to-ID mapping
  - [ ] Store selected service's numeric ID

- [ ] **Step 4: View Available Slots**
  - [ ] Call `/api/appointments/available-slots/`
  - [ ] Pass psychologist_id as number (not string)
  - [ ] Pass start_date in YYYY-MM-DD format
  - [ ] Display slots grouped by date

- [ ] **Step 5: Select Session Type**
  - [ ] Show toggle: Telehealth vs In-Person
  - [ ] Store selection as 'telehealth' or 'in_person'
  - [ ] Validate psychologist offers selected type

- [ ] **Step 6: Book Appointment**
  - [ ] Call `/api/appointments/book-enhanced/`
  - [ ] Include auth token in header
  - [ ] Send all numeric IDs (not slugs)
  - [ ] Use correct session_type value

- [ ] **Step 7: Handle Response**
  - [ ] Show success message with appointment details
  - [ ] Navigate to payment/confirmation page
  - [ ] Handle errors gracefully

---

## 🔍 Debugging Tips

### Check Your Data Before Sending:

```typescript
// Before booking, validate your data
const bookingData = {
  psychologist_id: selectedPsychologist.id,
  service_id: selectedService.id,
  time_slot_id: selectedSlot.id,
  session_type: sessionType
};

console.log('Booking data:', bookingData);

// Validate types
console.log('Types check:', {
  psychologist_id: typeof bookingData.psychologist_id, // Should be 'number'
  service_id: typeof bookingData.service_id,           // Should be 'number'
  time_slot_id: typeof bookingData.time_slot_id,       // Should be 'number'
  session_type: bookingData.session_type               // Should be 'telehealth' or 'in_person'
});

// Validate values
if (typeof bookingData.psychologist_id !== 'number') {
  console.error('❌ psychologist_id must be a number, got:', bookingData.psychologist_id);
}
if (!['telehealth', 'in_person'].includes(bookingData.session_type)) {
  console.error('❌ Invalid session_type:', bookingData.session_type);
}
```

---

## 📝 Quick Reference: Valid Values

### Psychologist IDs (Always from API)
```typescript
// Step 1: Fetch psychologists
const psychologists = await fetch('/api/services/psychologists/').then(r => r.json());

// Step 2: User selects from list (or from URL parameter)
const selected = psychologists.find(p => p.user_name === "Dr. Sarah Johnson");

// Step 3: Use the ID from the response
const psychologistId = selected.id; // ✅ From API (e.g., 3)
```

### Service IDs (Always from API)
```typescript
// Step 1: Fetch services (with auth)
const services = await fetch('/api/services/services/', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// Step 2: Match URL slug to service
const slug = 'individual-therapy-session'; // From URL
const selected = services.find(s => 
  s.name.toLowerCase().replace(/ /g, '-') === slug
);

// Step 3: Use the ID from the response
const serviceId = selected.id; // ✅ From API (e.g., 1)
```

### Time Slot IDs (Always from API)
```typescript
// Step 1: Fetch available slots
const response = await fetch(
  `/api/appointments/available-slots/?psychologist_id=${psychologistId}&start_date=2025-10-08`
).then(r => r.json());

// Step 2: User selects a date and time
const selectedDate = response.available_dates[0]; // User picks a date
const selectedSlot = selectedDate.slots[0]; // User picks a time

// Step 3: Use the ID from the response
const timeSlotId = selectedSlot.id; // ✅ From API (e.g., 99)
```

### Session Types (Hardcoded Values)
```typescript
'telehealth'  // ✅ For video sessions
'in_person'   // ✅ For office visits
```

---

## ✅ Error Prevention Summary

1. **Never hardcode IDs** - Always get from API responses
2. **Always authenticate** - Store and use JWT tokens
3. **Use numeric IDs** - Convert slugs to numbers before booking
4. **Validate session type** - Only 'telehealth' or 'in_person'
5. **Check psychologist exists** - Use IDs from psychologist list
6. **Include all required fields** - psychologist_id, service_id, time_slot_id, session_type
7. **Handle errors gracefully** - Show user-friendly error messages

---

## 🚀 Example: Complete Working Flow

```typescript
// 1. Login
const { access } = await login(email, password);
localStorage.setItem('token', access);

// 2. Get psychologists (public endpoint)
const psychologists = await fetch('/api/services/psychologists/').then(r => r.json());
const selectedPsych = psychologists.find(p => p.id === 3);

// 3. Get services (authenticated)
const services = await fetch('/api/services/services/', {
  headers: { 'Authorization': `Bearer ${access}` }
}).then(r => r.json());
const selectedService = services.find(s => s.id === 1);

// 4. Get available slots
const slots = await fetch(
  `/api/appointments/available-slots/?psychologist_id=${selectedPsych.id}&start_date=2025-10-08`
).then(r => r.json());
const selectedSlot = slots.available_dates[0].slots[0];

// 5. Book appointment
const booking = await fetch('/api/appointments/book-enhanced/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    psychologist_id: selectedPsych.id,     // ✅ Number from API
    service_id: selectedService.id,         // ✅ Number from API
    time_slot_id: selectedSlot.id,          // ✅ Number from API
    session_type: 'telehealth',             // ✅ Valid string
    notes: 'Looking forward to the session'
  })
}).then(r => r.json());

console.log('✅ Booking successful:', booking);
```

---

**Follow this checklist and you'll avoid 99% of common booking errors!** 🎯

