# 🚀 Twilio Quick Start - 5 Steps

## What You Need to Do Right Now

### 1️⃣ **Sign Up for Twilio** (5 minutes)
- Go to [twilio.com](https://www.twilio.com) and create account
- You'll get $15.50 free credit

### 2️⃣ **Get Your Credentials** (2 minutes)
After logging in, you'll see on the dashboard:
- ✅ **Account SID** (starts with `AC...`)
- ✅ **Auth Token** (click "View" to see it)

### 3️⃣ **Create API Key** (2 minutes)
- Go to **Account → API Keys & Tokens**
- Click **"Create new API Key"**
- Name it: `Psychology Clinic Video`
- Copy **both** the Key SID (`SK...`) and Secret

### 4️⃣ **Set Up WhatsApp Sandbox** (3 minutes)
- Go to **Messaging → Try it out → Send a WhatsApp message**
- You'll see a sandbox number (e.g., `whatsapp:+14155238886`)
- Send the code shown to that number via WhatsApp
- Copy the sandbox number

### 5️⃣ **Add to Your `.env` File**

Open your `.env` file and add:

```bash
TWILIO_ACCOUNT_SID=AC_your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_API_KEY=SK_your_api_key_here
TWILIO_API_SECRET=your_api_secret_here
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

**Replace with your actual values!**

---

## ✅ Test It Works

```bash
# Activate virtual environment
source venv/bin/activate

# Test in Python shell
python manage.py shell
```

```python
# Test video service
from appointments.video_service import get_video_service
video_service = get_video_service()
result = video_service.validate_credentials()
print(result)  # Should show {'valid': True, ...}

# Test WhatsApp (use your phone number)
from core.whatsapp_service import test_whatsapp_configuration
result = test_whatsapp_configuration('+61412345678')  # Your phone
print(result)  # Check your WhatsApp!
```

---

## 📖 Full Guide

For detailed instructions, see **[TWILIO_SETUP_GUIDE.md](TWILIO_SETUP_GUIDE.md)**

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "Credentials not configured" | Check all 5 variables in `.env` |
| "Invalid Account SID" | Make sure you copied it correctly |
| WhatsApp not working | Make sure you joined the sandbox |
| Video room fails | Check API Key and Secret are correct |

---

**That's it! You're ready to use video calls and WhatsApp messaging! 🎉**

