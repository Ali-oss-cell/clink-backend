# 📧 Email Setup Guide - Fix "No Welcome Email" Issue

## Problem
You created a new account but didn't receive a welcome email.

## Root Cause
Your `.env` file has placeholder email configuration values that need to be replaced with real credentials.

---

## Solution: Choose One Email Method

### ⭐ Option 1: SendGrid (Recommended - Already Configured)

SendGrid is **already set up** in your code and is the **professional** choice for production.

#### Why SendGrid?
- ✅ Professional service (via Twilio)
- ✅ High deliverability rates
- ✅ Already coded in your system
- ✅ Scales to production
- ✅ From: noreply@tailoredpsychology.com.au (looks professional)

#### Setup Steps:

1. **Get Your SendGrid API Key** (you may already have this)
   - Log in to Twilio SendGrid: https://sendgrid.com/
   - Go to Settings → API Keys
   - Click "Create API Key"
   - Name: "Tailored Psychology Backend"
   - Permissions: "Full Access" or "Mail Send"
   - Copy the API key (shown once only!)

2. **Update `.env` File**
   ```bash
   # Add or update these lines:
   SENDGRID_API_KEY=SG.your-actual-api-key-here
   SENDGRID_FROM_EMAIL=noreply@tailoredpsychology.com.au
   SENDGRID_FROM_NAME=Tailored Psychology
   ```

3. **Verify Domain** (Important!)
   - In SendGrid → Settings → Sender Authentication
   - Click "Verify a Single Sender" (quick option)
   - OR "Authenticate Your Domain" (professional option)
   - Add DNS records to GoDaddy/Cloudflare
   - Wait for verification (can take 24-48 hours)

4. **Test It**
   ```bash
   python test_welcome_email.py
   ```

---

### Option 2: Gmail SMTP (Quick Test Only)

**⚠️ NOT recommended for production** - Gmail limits you to 500 emails/day

#### Setup Steps:

1. **Enable 2-Factor Authentication on Gmail**
   - Go to Google Account → Security
   - Enable 2-Step Verification

2. **Generate App Password**
   - Google Account → Security → 2-Step Verification
   - At bottom: "App passwords"
   - Select app: "Mail"
   - Select device: "Other" → "Tailored Psychology"
   - Click "Generate"
   - **Copy the 16-character password**

3. **Update `.env` File**
   ```bash
   EMAIL_HOST_USER=your-gmail@gmail.com
   EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx  # 16-char app password
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   ```

4. **Update `settings.py` DEFAULT_FROM_EMAIL**
   ```python
   # In psychology_clinic/settings.py
   DEFAULT_FROM_EMAIL = 'your-gmail@gmail.com'
   ```

---

## Test Your Configuration

### Method 1: Use the Diagnostic Tool

```bash
cd /home/ali/Desktop/projects/clink-backend
python test_welcome_email.py
```

This will:
- ✅ Check your configuration
- ✅ Tell you what's wrong
- ✅ Let you send test emails
- ✅ Let you resend welcome emails to users

### Method 2: Manual Test in Django Shell

```bash
python manage.py shell
```

```python
from core.email_service import send_email_via_sendgrid

# Send a test email
result = send_email_via_sendgrid(
    to_email='your-email@example.com',
    subject='Test Email',
    message='This is a test from Tailored Psychology!'
)

print(result)
# If success=True, email is working!
```

### Method 3: Resend Welcome Email to Yourself

```bash
python manage.py shell
```

```python
from users.models import User
from core.email_service import send_welcome_email

# Find your user (replace with your email)
user = User.objects.get(email='your-email@example.com')

# Resend welcome email
result = send_welcome_email(user)

print(result)
```

---

## Troubleshooting

### Issue: "SENDGRID_API_KEY not set"
**Fix:** Add `SENDGRID_API_KEY=SG.xxxxx` to your `.env` file

### Issue: "Authentication failed" (Gmail)
**Fix:** 
1. Make sure you're using an **App Password**, not your regular Gmail password
2. App passwords are 16 characters: `xxxx xxxx xxxx xxxx`

### Issue: "Domain not verified" (SendGrid)
**Fix:**
1. Go to SendGrid → Sender Authentication
2. Verify your domain or single sender
3. Add DNS records to your domain registrar
4. Wait 24-48 hours for verification

### Issue: Email goes to spam
**Fix:**
1. Verify your domain in SendGrid (adds DKIM/SPF)
2. Use a professional from email (noreply@yourdomain.com)
3. Don't use Gmail SMTP (looks suspicious)

### Issue: "Connection timeout"
**Fix:**
1. Check your internet connection
2. Try the backup email method in settings.py
3. Check if your firewall blocks SMTP ports

---

## Current Status

Based on your `.env` file, you currently have:
```bash
❌ EMAIL_HOST_USER=your-email@gmail.com  # PLACEHOLDER
❌ EMAIL_HOST_PASSWORD=your-app-password  # PLACEHOLDER
❌ SENDGRID_API_KEY not set
```

**You need to replace these placeholders with real values.**

---

## Recommended Setup for Production

1. **Use SendGrid** (via Twilio)
   - Professional appearance
   - High deliverability
   - Scalable
   - You're already paying for Twilio

2. **Verify Your Domain**
   - `noreply@tailoredpsychology.com.au`
   - Adds DKIM/SPF/DMARC
   - Emails won't go to spam

3. **Add to `.env`**
   ```bash
   SENDGRID_API_KEY=SG.your-key-here
   SENDGRID_FROM_EMAIL=noreply@tailoredpsychology.com.au
   SENDGRID_FROM_NAME=Tailored Psychology
   ```

4. **Restart Your Server**
   ```bash
   # If using systemd:
   sudo systemctl restart gunicorn

   # If running locally:
   # Just stop and start python manage.py runserver
   ```

---

## Quick Fix Right Now

### If you just want to test ASAP:

1. **Use Gmail SMTP** (not for production!)
   
   Update `.env`:
   ```bash
   EMAIL_HOST_USER=your-real-gmail@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password-here
   ```

2. **Restart server**

3. **Test it**
   ```bash
   python test_welcome_email.py
   ```

4. **Create a new test account** or run:
   ```bash
   python manage.py shell
   ```
   ```python
   from users.models import User
   from core.email_service import send_welcome_email
   
   user = User.objects.get(email='your-email@example.com')
   send_welcome_email(user)
   ```

---

## After Email Works

Once emails are working:

1. ✅ Test welcome emails
2. ✅ Test appointment confirmation emails
3. ✅ Test appointment reminder emails
4. ✅ Test password reset emails
5. ✅ Check spam folder
6. ✅ Verify domain for production

---

## Next Steps

1. **Run the diagnostic tool**
   ```bash
   python test_welcome_email.py
   ```

2. **Fix the configuration** (choose SendGrid or Gmail)

3. **Test again**

4. **Create a new user** and verify welcome email arrives

---

**Need Help?**

Run the diagnostic tool - it will tell you exactly what's wrong:
```bash
python test_welcome_email.py
```


