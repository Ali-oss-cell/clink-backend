# ✅ AHPRA Expiry Monitoring - Implementation Complete

## Overview

AHPRA expiry monitoring system that automatically checks psychologist registrations, sends warnings, and suspends expired accounts.

---

## What Was Implemented

### 1. Celery Task: `check_ahpra_expiry()`
**Location:** `appointments/tasks.py`

**What it does:**
- Runs monthly (via Celery Beat)
- Checks all psychologist AHPRA expiry dates
- Sends warning emails 30 days before expiry
- Automatically suspends psychologists with expired registrations
- Cancels all future appointments for expired psychologists
- Notifies practice managers
- Logs all actions for audit trail

**Returns:**
```python
{
    'expiring_soon': 2,        # Psychologists expiring within 30 days
    'expired': 1,              # Psychologists with expired registrations
    'warnings_sent': 2,        # Warning emails sent
    'suspended': 1,            # Psychologists suspended
    'appointments_cancelled': 5,  # Future appointments cancelled
    'errors': 0                # Errors encountered
}
```

### 2. Email Functions
**Location:** `core/email_service.py`

**Functions added:**
- `send_ahpra_expiry_warning_email()` - Sends warning 30 days before expiry
- `send_ahpra_expired_email()` - Sends notification when expired

**Email recipients:**
- Psychologist (warning and expired notifications)
- Practice managers (expired notifications only)

### 3. Celery Beat Schedule
**Location:** `psychology_clinic/celery.py`

**Schedule:**
- Task runs **monthly** (every 30 days)
- Task name: `appointments.tasks.check_ahpra_expiry`

### 4. Automatic Actions

**When AHPRA expires:**
1. ✅ Psychologist account suspended (`is_active_practitioner = False`)
2. ✅ All future appointments cancelled
3. ✅ Patients notified of cancellations
4. ✅ Psychologist notified via email
5. ✅ Practice managers notified via email
6. ✅ All actions logged in audit trail

**30 days before expiry:**
1. ✅ Warning email sent to psychologist
2. ✅ Action logged in audit trail

---

## How to Use

### Manual Check (Testing)

```python
# In Django shell
python manage.py shell

>>> from appointments.tasks import check_ahpra_expiry
>>> result = check_ahpra_expiry()
>>> print(result)
{
    'expiring_soon': 1,
    'expired': 0,
    'warnings_sent': 1,
    'suspended': 0,
    'appointments_cancelled': 0,
    'errors': 0
}
```

### Automatic Monthly Check

The task runs automatically via Celery Beat. Make sure Celery Beat is running:

```bash
# Start Celery Beat (scheduler)
celery -A psychology_clinic beat -l info

# Start Celery Worker (task executor)
celery -A psychology_clinic worker -l info
```

### Check Celery Beat Schedule

```python
# In Django shell
python manage.py shell

>>> from psychology_clinic.celery import app
>>> print(app.conf.beat_schedule)
```

---

## Testing

### Test Warning Email

```python
# Create a psychologist with expiry in 30 days
from services.models import PsychologistProfile
from users.models import User
from datetime import date, timedelta

psychologist = User.objects.filter(role='psychologist').first()
profile = psychologist.psychologist_profile
profile.ahpra_expiry_date = date.today() + timedelta(days=30)
profile.save()

# Run the check
from appointments.tasks import check_ahpra_expiry
result = check_ahpra_expiry()
# Should send warning email
```

### Test Expired Registration

```python
# Set expiry date in the past
profile.ahpra_expiry_date = date.today() - timedelta(days=1)
profile.is_active_practitioner = True
profile.save()

# Run the check
result = check_ahpra_expiry()
# Should suspend psychologist and cancel appointments
```

---

## Configuration

### Celery Beat Schedule

The task is configured to run monthly. To change the frequency, edit `psychology_clinic/celery.py`:

```python
'check-ahpra-expiry': {
    'task': 'appointments.tasks.check_ahpra_expiry',
    'schedule': 2592000.0,  # 30 days in seconds
    # Or use crontab for more control:
    # 'schedule': crontab(day_of_month=1, hour=9, minute=0),  # First of month at 9 AM
},
```

### Warning Period

Currently set to 30 days. To change, edit `appointments/tasks.py`:

```python
warning_date = today + timedelta(days=30)  # Change 30 to desired days
```

---

## Compliance Benefits

✅ **AHPRA Compliance**
- Ensures all psychologists have current registrations
- Prevents practice with expired registrations
- Automatic suspension protects clinic from liability

✅ **Audit Trail**
- All actions logged for compliance
- Track when warnings were sent
- Track when psychologists were suspended

✅ **Patient Protection**
- Automatic cancellation prevents appointments with unregistered psychologists
- Patients notified of cancellations

---

## Next Steps

1. **Start Celery Beat** (if not already running):
   ```bash
   celery -A psychology_clinic beat -l info
   ```

2. **Test the task manually** to ensure it works

3. **Monitor logs** for any errors

4. **Set up email notifications** to ensure emails are being sent

---

## Related Documentation

- [Complete Compliance Guide](AUSTRALIAN_LEGAL_COMPLIANCE_GUIDE.md)
- [Compliance Quick Checklist](COMPLIANCE_QUICK_CHECKLIST.md)
- [Compliance Implementation Progress](COMPLIANCE_IMPLEMENTATION_PROGRESS.md)

---

## Status

✅ **COMPLETE** - AHPRA expiry monitoring is fully implemented and ready to use!

