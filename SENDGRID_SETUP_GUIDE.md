# SendGrid Email Setup Guide

**Date**: 2025-11-26  
**Status**: Ready to Configure

---

## 📋 **Prerequisites**

✅ SendGrid account created  
✅ Domain authenticated (`tailoredpsychology.com.au`)  
✅ API Key created (get from SendGrid Dashboard → Settings → API Keys)

---

## 🔧 **Step 1: Add SendGrid Configuration to `.env` File**

### On Your Server

SSH into your server and edit the `.env` file:

```bash
cd /var/www/clink-backend
sudo nano .env
```

### Add These Lines

Find the **Email Configuration** section and update it:

```env
# Email Configuration (SendGrid via Twilio)
SENDGRID_API_KEY=your-sendgrid-api-key-here
SENDGRID_FROM_EMAIL=noreply@tailoredpsychology.com.au
SENDGRID_FROM_NAME=Tailored Psychology
```

**Important**: 
- Replace the API key with your actual key (shown above)
- The `SENDGRID_FROM_EMAIL` must match your authenticated domain
- Save the file (Ctrl+O, Enter, Ctrl+X in nano)

---

## ✅ **Step 2: Verify Configuration**

### Test Email Sending

```bash
cd /var/www/clink-backend
source venv/bin/activate
python manage.py shell
```

Then run:

```python
from core.email_service import test_email_configuration
result = test_email_configuration()
print(result)
```

**Expected Output**:
```python
{
    'success': True,
    'message': 'Test email sent successfully',
    'from_email': 'noreply@tailoredpsychology.com.au'
}
```

### Check Email Delivery

1. Go to SendGrid Dashboard → **Activity**
2. You should see the test email in the activity feed
3. Check the recipient inbox (the `SENDGRID_FROM_EMAIL` address)

---

## 📧 **Step 3: Verify Email Types**

The system will automatically use SendGrid for:

- ✅ Appointment confirmations
- ✅ 24-hour reminders
- ✅ 1-hour reminders
- ✅ 15-minute reminders
- ✅ Cancellation notifications
- ✅ Rescheduling notifications
- ✅ AHPRA expiry warnings
- ✅ Insurance expiry warnings
- ✅ All other system emails

---

## 🔍 **Troubleshooting**

### Issue: "Test email failed"

**Check**:
1. API key is correct (no extra spaces)
2. Domain is authenticated in SendGrid
3. `SENDGRID_FROM_EMAIL` matches authenticated domain
4. SendGrid package is installed: `pip install sendgrid==6.11.0`

### Issue: "Email not received"

**Check**:
1. SendGrid Activity feed (may be in spam)
2. Domain authentication status
3. Email address is valid
4. Check SendGrid logs for errors

### Issue: "Import error: sendgrid"

**Fix**:
```bash
cd /var/www/clink-backend
source venv/bin/activate
pip install sendgrid==6.11.0
```

---

## 🎯 **What Happens Next**

Once configured:

1. **All emails use SendGrid** automatically
2. **No code changes needed** - existing email functions work
3. **Falls back to Django SMTP** if SendGrid fails (if configured)
4. **Professional emails** from your domain

---

## 📊 **Monitoring**

### Check SendGrid Activity

1. Go to [SendGrid Dashboard](https://app.sendgrid.com/)
2. Click **Activity** in the sidebar
3. View all sent emails, bounces, and delivery status

### Check Email Logs

```bash
# Django logs
tail -f /var/log/gunicorn/error.log

# Celery logs (for scheduled emails)
tail -f /var/log/celery/worker.log
```

---

## ✅ **Configuration Complete Checklist**

- [ ] API key added to `.env` file
- [ ] `SENDGRID_FROM_EMAIL` set correctly
- [ ] `SENDGRID_FROM_NAME` set correctly
- [ ] Test email sent successfully
- [ ] Email received in inbox
- [ ] SendGrid Activity shows email
- [ ] Domain authentication verified

---

## 🚀 **Next Steps**

After SendGrid is configured:

1. **Test appointment booking** - Should send confirmation email
2. **Test reminders** - Celery Beat should send scheduled reminders
3. **Create HTML email templates** - Make emails look professional
4. **Monitor delivery rates** - Check SendGrid dashboard regularly

---

**Last Updated**: 2025-11-26  
**Status**: Ready to Configure

