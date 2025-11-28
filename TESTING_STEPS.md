# 🧪 Testing Steps - Email Configuration & Welcome Emails

## ✅ What's Already Done

- ✅ Code is pushed to GitHub
- ✅ Welcome email function exists
- ✅ Diagnostic tools created
- ✅ Documentation complete

## 📋 What You Need to Do Now

### Step 1: Configure Email (Local Only - Don't Push .env)

**Option A: SendGrid (Recommended)**

1. Get your SendGrid API key:
   - Go to: https://sendgrid.com/
   - Settings → API Keys → Create API Key
   - Copy the key (starts with `SG.`)

2. Edit your `.env` file (local file, not in git):
   ```bash
   # Add or update these lines:
   SENDGRID_API_KEY=SG.paste-your-key-here
   SENDGRID_FROM_EMAIL=noreply@tailoredpsychology.com.au
   SENDGRID_FROM_NAME=Tailored Psychology
   ```

**Option B: Gmail (Quick Test)**

1. Enable 2FA on Gmail
2. Generate App Password
3. Edit your `.env` file:
   ```bash
   EMAIL_HOST_USER=your-gmail@gmail.com
   EMAIL_HOST_PASSWORD=your-16-char-app-password
   ```

---

### Step 2: Verify Configuration

Run the checker:
```bash
python check_email_config.py
```

**Expected Output:**
```
✅ SendGrid is configured - emails should work!
```
OR
```
✅ SMTP is configured - emails should work!
```

If you see ❌, go back to Step 1.

---

### Step 3: Restart Your Server

**If running locally:**
```bash
# Stop your server (Ctrl+C)
# Start it again:
python manage.py runserver
```

**If running on production server:**
```bash
sudo systemctl restart gunicorn
sudo systemctl restart celery
```

---

### Step 4: Test Email Configuration

**Test 1: Check Configuration**
```bash
python check_email_config.py
```
Should show ✅ for email configuration.

**Test 2: Create a New User Account**

1. Go to your registration endpoint (frontend or API)
2. Create a new user account with your real email
3. Check your email inbox
4. Check spam folder too

**Test 3: Check SendGrid Dashboard (if using SendGrid)**

1. Go to: https://app.sendgrid.com/
2. Activity → Email Activity
3. You should see the email sent

---

### Step 5: Verify Welcome Email Arrives

✅ **Success:** You receive welcome email  
❌ **Failed:** Check:
- Spam folder
- SendGrid dashboard for errors
- Server logs for errors
- Run `python check_email_config.py` again

---

## 🔍 Troubleshooting

### If email still doesn't work:

1. **Check .env file:**
   ```bash
   cat .env | grep -E "SENDGRID|EMAIL"
   ```
   Make sure values are real, not placeholders.

2. **Check server logs:**
   - Look for email errors
   - Check if SendGrid API key is valid

3. **Test SendGrid API key:**
   - Go to SendGrid dashboard
   - Check API key permissions
   - Make sure it has "Mail Send" permission

4. **Verify domain (SendGrid):**
   - Settings → Sender Authentication
   - Authenticate your domain
   - Add DNS records
   - Wait 24-48 hours

---

## 📝 Quick Checklist

- [ ] Configure email in `.env` (SendGrid or Gmail)
- [ ] Run `python check_email_config.py` - shows ✅
- [ ] Restart server
- [ ] Create a new test user account
- [ ] Check email inbox (and spam)
- [ ] Verify welcome email received

---

## 🎯 Expected Result

After completing these steps:
- ✅ New users receive welcome emails
- ✅ Email configuration is working
- ✅ All email notifications will work

---

## ⚠️ Important Notes

1. **Don't commit `.env` file** - it contains secrets
2. **`.env` is local only** - each environment needs its own
3. **SendGrid domain verification** takes 24-48 hours
4. **Gmail has 500 emails/day limit** - not for production

---

## 🚀 Ready to Test?

1. Configure email in `.env`
2. Run: `python check_email_config.py`
3. Restart server
4. Create a new user
5. Check your email!

Good luck! 🎉

