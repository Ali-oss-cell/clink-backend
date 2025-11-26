# SendGrid SMTP Setup (Alternative to Web API)

If the Web API is timing out, use SendGrid's SMTP Relay instead.

## Why Use SMTP?

- ✅ More reliable connection (uses standard SMTP port 587)
- ✅ Works through most firewalls
- ✅ Same email delivery, different method
- ✅ No API timeout issues

## Setup Steps

### 1. Get SMTP Credentials from SendGrid

1. Go to SendGrid Dashboard → **Settings** → **Sender Authentication**
2. Click on your authenticated domain
3. Go to **SMTP Relay** tab
4. Create an **SMTP Username** and **SMTP Password**
5. Note the **SMTP Server**: `smtp.sendgrid.net`
6. Note the **Port**: `587` (TLS) or `465` (SSL)

### 2. Add to `.env` File

```env
# SendGrid SMTP Configuration (Alternative to Web API)
SENDGRID_SMTP_USERNAME=apikey
SENDGRID_SMTP_PASSWORD=your-sendgrid-api-key-here
SENDGRID_SMTP_HOST=smtp.sendgrid.net
SENDGRID_SMTP_PORT=587
SENDGRID_SMTP_USE_TLS=True

# Or use your API key as SMTP password
# SMTP Username: apikey
# SMTP Password: your-sendgrid-api-key-here
```

**Important**: For SendGrid SMTP:
- **Username**: Always `apikey` (literal word)
- **Password**: Your SendGrid API Key (the same one you have)

### 3. Update Django Settings

The system will automatically use SMTP if configured. Update `psychology_clinic/settings.py`:

```python
# SendGrid SMTP (if Web API doesn't work)
SENDGRID_SMTP_USERNAME = config('SENDGRID_SMTP_USERNAME', default='apikey')
SENDGRID_SMTP_PASSWORD = config('SENDGRID_SMTP_PASSWORD', default='')
SENDGRID_SMTP_HOST = config('SENDGRID_SMTP_HOST', default='smtp.sendgrid.net')
SENDGRID_SMTP_PORT = config('SENDGRID_SMTP_PORT', default=587, cast=int)
SENDGRID_SMTP_USE_TLS = config('SENDGRID_SMTP_USE_TLS', default=True, cast=bool)

# Use SMTP if configured
if SENDGRID_SMTP_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = SENDGRID_SMTP_HOST
    EMAIL_PORT = SENDGRID_SMTP_PORT
    EMAIL_USE_TLS = SENDGRID_SMTP_USE_TLS
    EMAIL_HOST_USER = SENDGRID_SMTP_USERNAME
    EMAIL_HOST_PASSWORD = SENDGRID_SMTP_PASSWORD
    DEFAULT_FROM_EMAIL = SENDGRID_FROM_EMAIL
```

### 4. Test SMTP Connection

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    subject='SendGrid SMTP Test',
    message='This is a test email via SendGrid SMTP',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=[settings.DEFAULT_FROM_EMAIL],
    fail_silently=False,
)
```

---

## Quick Setup (Using API Key as SMTP Password)

SendGrid allows using your API key directly as the SMTP password:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key-here
DEFAULT_FROM_EMAIL=noreply@tailoredpsychology.com.au
```

This is the **easiest** method - just use your existing API key!

---

## Which Method to Use?

- **Web API**: Faster, more features, but may timeout
- **SMTP Relay**: More reliable, works through firewalls, standard email protocol

**Recommendation**: Try SMTP if Web API times out.

