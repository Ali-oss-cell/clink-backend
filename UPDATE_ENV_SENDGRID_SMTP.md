# Update .env File for SendGrid SMTP

## Current Issue

You have:
- ✅ `SENDGRID_API_KEY` configured
- ❌ Still using Gmail SMTP (`EMAIL_HOST=smtp.gmail.com`)

## Fix: Replace Gmail SMTP with SendGrid SMTP

### In your `.env` file, REPLACE these lines:

**OLD (Gmail):**
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

**NEW (SendGrid SMTP):**
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key-here
```

## Complete Email Section Should Look Like:

```env
# Email Configuration (SendGrid via Twilio)
SENDGRID_API_KEY=your-sendgrid-api-key-here
SENDGRID_FROM_EMAIL=noreply@tailoredpsychology.com.au
SENDGRID_FROM_NAME=Tailored Psychology

# SendGrid SMTP Configuration (using API key as password)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key-here
DEFAULT_FROM_EMAIL=noreply@tailoredpsychology.com.au
```

## Important Notes:

1. **EMAIL_HOST_USER** must be exactly `apikey` (the literal word)
2. **EMAIL_HOST_PASSWORD** is your SendGrid API key
3. **EMAIL_HOST** is `smtp.sendgrid.net` (not gmail.com)
4. **DEFAULT_FROM_EMAIL** should match your authenticated domain

## After Updating:

1. Save the `.env` file
2. Restart your Django application:
   ```bash
   sudo systemctl restart gunicorn
   ```
3. Test email:
   ```bash
   python manage.py shell
   ```
   ```python
   from django.core.mail import send_mail
   from django.conf import settings
   send_mail('Test', 'Test email', settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])
   ```

