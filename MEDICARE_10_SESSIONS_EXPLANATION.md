# Medicare 10 Sessions Per Year - Australian Healthcare Reality

## ✅ Yes, This is Real!

The **10 sessions per calendar year limit** is a real Medicare policy in Australia for psychology services under the **Better Access Initiative**.

---

## How It Works in Australia

### Initial 10 Sessions
- Patients can claim Medicare rebates for **up to 10 psychology sessions per calendar year**
- This applies to services with Medicare item numbers (e.g., 80110, 80115)
- The limit resets on **January 1st** each year

### Additional Sessions
- Patients can get **additional sessions** (up to 10 more) with a **new GP referral**
- This requires a review with their GP
- Total possible: **20 sessions per year** (10 initial + 10 additional)

### What's Covered
- Individual psychology sessions
- Clinical psychology sessions
- Group therapy (different limits)
- Telehealth psychology sessions

### What's NOT Limited
- Private sessions (no Medicare rebate) - unlimited
- Sessions paid fully out-of-pocket - unlimited
- Services without Medicare item numbers - unlimited

---

## Our Implementation

✅ **Enforces 10 sessions per year** for Medicare-eligible services
✅ **Blocks booking** if limit reached
✅ **Shows remaining sessions** to patients
✅ **Resets each calendar year** (January 1st)

---

## Frontend Updates Needed

You should update your frontend to:

1. **Show Medicare session limit** when booking
2. **Display remaining sessions** in patient dashboard
3. **Handle error messages** when limit reached
4. **Show warning** when approaching limit (e.g., 8+ sessions used)

---

## Example Frontend Display

**When Booking:**
```
Medicare Sessions This Year: 7/10 remaining
⚠️ You have 3 Medicare sessions remaining this year
```

**When Limit Reached:**
```
❌ Medicare session limit reached (10/10 used)
You can still book private sessions (no Medicare rebate)
Or wait until next year for Medicare sessions
```

---

## This is Standard Practice

All psychology clinics in Australia must:
- Track Medicare session limits
- Enforce the 10-session limit
- Inform patients of remaining sessions
- Handle limit reached scenarios

**Our implementation is correct and compliant!** ✅

