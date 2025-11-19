# SendGrid Email Setup (via Twilio)

## Quick Setup

### 1. Get SendGrid API Key

1. Go to [SendGrid Dashboard](https://app.sendgrid.com/)
2. Go to **Settings** → **API Keys**
3. Click **Create API Key**
4. Name it (e.g., "Psychology Clinic")
5. Give it **Full Access** or **Mail Send** permissions
6. Copy the API key (you'll only see it once!)

### 2. Add to `.env` File

```env
# SendGrid Configuration (via Twilio)
SENDGRID_API_KEY=SG.your_api_key_here
SENDGRID_FROM_EMAIL=noreply@yourclinic.com.au
SENDGRID_FROM_NAME=Psychology Clinic
```

### 3. Verify Sender Email

1. Go to **Settings** → **Sender Authentication**
2. Verify your sender email address (`noreply@yourclinic.com.au`)
3. Or verify your domain

### 4. Test

```python
# In Django shell
python manage.py shell

>>> from core.email_service import test_email_configuration
>>> result = test_email_configuration()
>>> print(result)
```

---

## How It Works

1. **All emails use SendGrid** - The system automatically uses SendGrid API
2. **Falls back to Django SMTP** - If SendGrid not configured, uses Django's email backend
3. **No code changes needed** - All email functions automatically use SendGrid

---

## What Emails Use SendGrid

- ✅ Appointment confirmations
- ✅ Appointment reminders (24h, 1h, 15min)
- ✅ Appointment cancellations
- ✅ Appointment rescheduling
- ✅ AHPRA expiry warnings
- ✅ AHPRA expired notifications
- ✅ All other system emails

---

## That's It!

Once you add the `SENDGRID_API_KEY` to your `.env` file, all emails will automatically use SendGrid!

