# How to Get Your Twilio API Secret

## ⚠️ Critical: API Secret Required for Video Calls

Your video tokens **will not work** without the API Secret. The secret is only shown **once** when you create the API Key.

---

## Option 1: Check if You Saved It

1. Check your notes/password manager for your API Key secret
2. Look for any saved Twilio credentials from November 14, 2025

---

## Option 2: Create a New API Key (Recommended)

If you don't have the secret, create a new API Key:

### Steps:

1. **Go to Twilio Console**: https://console.twilio.com
2. **Navigate to**: Account → API Keys & Tokens → API Keys
3. **Click**: "Create API key"
4. **Fill in**:
   - **Friendly name**: `clink-video-production`
   - **Region**: `Australia (AU1)` (recommended)
5. **Click**: "Create API key"
6. **IMPORTANT**: Copy BOTH values immediately:
   - **API Key SID**: `SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **API Secret**: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` ← **Save this now!**

### Update Your .env File:

After creating the new key, update your `.env`:

```bash
TWILIO_API_KEY=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # New key SID
TWILIO_API_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx   # New secret (save this!)
```

---

## Option 3: View Existing Key (If Secret Was Saved)

If Twilio shows a "View" or "Reveal" button next to your key:
1. Click it to reveal the secret
2. Copy it immediately
3. Add to `.env` file

**Note**: Most Twilio accounts don't allow viewing secrets after creation for security reasons.

---

## ✅ After Getting the Secret

1. **Update `.env` file** on your Droplet:
   ```bash
   cd /var/www/clink-backend
   sudo nano .env
   ```

2. **Add the secret**:
   ```bash
   TWILIO_API_SECRET=your-actual-secret-here
   ```

3. **Restart Gunicorn**:
   ```bash
   sudo systemctl restart gunicorn
   ```

4. **Test**:
   ```bash
   cd /var/www/clink-backend
   source venv/bin/activate
   python manage.py shell
   ```
   ```python
   from appointments.video_service import get_video_service
   video_service = get_video_service()
   result = video_service.validate_credentials()
   print(result)
   ```

   Expected: `'api_key_valid': True`

---

## 🔒 Security Note

- **Never commit** the API Secret to git
- **Store securely** (password manager, secure notes)
- **Rotate periodically** (create new keys every 6-12 months)
- **Use different keys** for development and production

---

## Current Status

✅ **Account SID**: Get from Twilio Console  
✅ **Auth Token**: Get from Twilio Console  
✅ **API Key SID**: Get from Twilio Console  
❌ **API Secret**: **MISSING** - Need to get this!

