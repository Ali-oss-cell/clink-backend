# 🔄 Frontend-Backend Field Format Guide

## Problem

Frontend sends some fields as **arrays**, but backend expects **comma-separated strings**.

## Fields That Need Conversion

These fields accept **both formats** (array or string):

### 1. `working_days`
- **Frontend can send:** `["Monday", "Tuesday"]` (array)
- **Backend accepts:** `"Monday,Tuesday"` (string)
- **Auto-converted:** ✅ Yes

### 2. `languages_spoken`
- **Frontend can send:** `["English", "Spanish"]` (array)
- **Backend accepts:** `"English,Spanish"` (string)
- **Auto-converted:** ✅ Yes

### 3. `session_types`
- **Frontend can send:** `["Individual", "Couples"]` (array)
- **Backend accepts:** `"Individual,Couples"` (string)
- **Auto-converted:** ✅ Yes

### 4. `insurance_providers`
- **Frontend can send:** `["Medicare", "Private"]` (array)
- **Backend accepts:** `"Medicare,Private"` (string)
- **Auto-converted:** ✅ Yes

### 5. `billing_methods`
- **Frontend can send:** `["Credit Card", "Bank Transfer"]` (array)
- **Backend accepts:** `"Credit Card,Bank Transfer"` (string)
- **Auto-converted:** ✅ Yes

---

## How It Works

The backend serializer automatically converts arrays to strings:

```python
# Frontend sends:
{
  "working_days": ["Monday", "Tuesday"]
}

# Backend converts to:
{
  "working_days": "Monday,Tuesday"
}
```

---

## Frontend Options

### Option 1: Send Arrays (Recommended)
✅ **Just send arrays** - backend will convert automatically

```javascript
const updateData = {
  working_days: ["Monday", "Tuesday", "Wednesday"],
  languages_spoken: ["English", "Spanish"],
  session_types: ["Individual", "Couples"]
};
```

### Option 2: Send Strings
✅ **Send comma-separated strings** - works as-is

```javascript
const updateData = {
  working_days: "Monday,Tuesday,Wednesday",
  languages_spoken: "English,Spanish",
  session_types: "Individual,Couples"
};
```

**Both formats work!** The backend handles conversion automatically.

---

## Fields That Must Be Arrays

These fields **must** be arrays (many-to-many relationships):

- ✅ `specializations` - Array of IDs: `[1, 2, 3]`
- ✅ `services_offered` - Array of IDs: `[1, 2, 3]`

---

## Fields That Must Be Strings

These fields **must** be strings:

- ✅ `title` - String: `"Dr"`
- ✅ `qualifications` - String: `"PhD in Psychology"`
- ✅ `bio` - String: `"Experienced psychologist..."`
- ✅ `practice_name` - String: `"Tailored Psychology"`
- ✅ All other text fields

---

## Example Request

```json
PUT /api/services/psychologists/2/

{
  "title": "Dr",
  "qualifications": "PhD in Clinical Psychology",
  "working_days": ["Monday", "Tuesday", "Wednesday"],  // ✅ Array works
  "languages_spoken": ["English", "Spanish"],           // ✅ Array works
  "session_types": ["Individual", "Couples"],           // ✅ Array works
  "specializations": [1, 2, 3],                         // ✅ Must be array
  "services_offered": [1, 2],                           // ✅ Must be array
  "is_accepting_new_patients": true,
  "max_patients_per_day": 8
}
```

---

## After Deploying Fix

1. **Pull latest code:**
   ```bash
   git pull origin main
   ```

2. **Restart server:**
   ```bash
   sudo systemctl restart gunicorn
   ```

3. **Test again** - should work now!

---

**The fix is deployed! Just pull and restart on your server.** 🚀


