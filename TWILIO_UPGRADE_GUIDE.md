# Twilio Account Upgrade Guide for Production

## ⚠️ Why You Need to Upgrade

Your psychology clinic backend uses Twilio for **critical production features**:
- ✅ **Video calls** (telehealth appointments)
- ✅ **WhatsApp reminders** (appointment notifications)
- ✅ **SMS backup** (when WhatsApp fails)

**Trial accounts have severe limitations** that will break your production system:
- ❌ Only **1 phone number** (you may need multiple)
- ❌ Can only message **verified recipients** (not all patients)
- ❌ **Account deactivates** when trial balance runs out
- ❌ **No production reliability** guarantees

---

## 📋 Upgrade Checklist

### Step 1: Upgrade Your Twilio Account

1. **Go to Twilio Console**: https://console.twilio.com
2. **Click "Upgrade"** (top right) or go to **Admin > Account billing**
3. **Complete upgrade process**:
   - Create profile
   - Add business address
   - Load starting balance (recommended: $50-100)
   - Add payment method (credit card)

**Reference**: [Twilio Upgrade Documentation](https://www.twilio.com/docs/usage/tutorials/how-to-use-your-free-trial-account#upgrade-your-account)

---

### Step 2: Verify Your Phone Number Requirements

#### For WhatsApp:
- ✅ You can use the **Twilio WhatsApp Sandbox** (free) for testing
- ⚠️ For production, you need a **verified WhatsApp Business number**
- 📞 Contact Twilio support to set up WhatsApp Business API

#### For SMS:
- ✅ You can keep your existing trial number
- ✅ Or purchase additional numbers if needed
- 📍 **Australian numbers**: Available for purchase in Console

#### For Video:
- ✅ **No phone number needed** - Video works independently
- ✅ Your current setup is fine

---

### Step 3: Verify Recipients (If Still Needed)

After upgrade, you can:
- ✅ **Remove verification requirement** for SMS/WhatsApp
- ✅ Send to **any phone number** (with proper consent)
- ✅ Use **unverified numbers** in production

**Note**: For Australian healthcare, ensure you have proper consent before sending messages.

---

### Step 4: Configure Production Settings

#### A. Video Room Settings (Already Configured)
- ✅ Media Region: **Australia - au1** ✓
- ✅ Status Callback URL: `https://api.tailoredpsychology.com.au/api/appointments/twilio-status-callback/`
- ✅ Client-side Room Creation: **Enabled** ✓

#### B. WhatsApp Business Setup (If Needed)
1. Go to **Messaging > Try it out > Send a WhatsApp message**
2. Follow prompts to set up WhatsApp Business API
3. Update `TWILIO_WHATSAPP_FROM` in your `.env` file

#### C. SMS Phone Number
1. Go to **Phone Numbers > Manage > Active numbers**
2. Verify your number has **SMS capability**
3. Update `TWILIO_PHONE_NUMBER` in your `.env` file

---

## 💰 Cost Estimates

### Monthly Costs (Australian Clinic - 50-100 patients/month)

| Service | Usage | Cost |
|---------|-------|------|
| **Video Calls** | 50-100 sessions/month | ~$0.004/min = **$2-4/month** |
| **WhatsApp** | 200-400 messages/month | **Free** (via Twilio) |
| **SMS Backup** | 50-100 messages/month | $0.0079/msg = **$0.40-0.80/month** |
| **Phone Number** | 1 number | **$1.00/month** |
| **Total** | | **~$3.50-6/month** |

**Note**: Video is the main cost. WhatsApp is free, SMS is cheap backup.

---

## 🔒 Production Security Checklist

After upgrading:

1. ✅ **Rotate API keys** (create new ones, delete old)
2. ✅ **Enable 2FA** on Twilio account
3. ✅ **Set up billing alerts** (get notified at $10, $50, $100)
4. ✅ **Review usage limits** (set max spending if needed)
5. ✅ **Validate webhook signatures** (already in your code)

---

## 📝 Environment Variables to Update

After upgrade, ensure these are set in your Droplet `.env`:

```bash
# Twilio Configuration (Production)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-production-auth-token
TWILIO_API_KEY=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_SECRET=your-production-api-secret

# WhatsApp (if using Business API)
TWILIO_WHATSAPP_FROM=whatsapp:+61412345678

# SMS (if using SMS)
TWILIO_PHONE_NUMBER=+61412345678

# Video Status Callback (already configured)
TWILIO_STATUS_CALLBACK_URL=https://api.tailoredpsychology.com.au/api/appointments/twilio-status-callback/
```

---

## 🚨 Important Notes

### Trial Account Limitations (Will Break Production)

1. **Verified Recipients Only**:
   - ❌ Trial: Can only message verified numbers
   - ✅ Paid: Can message any number (with consent)

2. **One Phone Number**:
   - ❌ Trial: Only 1 number
   - ✅ Paid: Unlimited numbers

3. **Balance Depletion**:
   - ❌ Trial: Account deactivates when balance = $0
   - ✅ Paid: Auto-recharge available

4. **Production Reliability**:
   - ❌ Trial: Not guaranteed for production
   - ✅ Paid: SLA and support

---

## ✅ Post-Upgrade Testing

After upgrading, test these features:

1. **Video Calls**:
   ```bash
   # Test creating a video room
   curl -X POST https://api.tailoredpsychology.com.au/api/appointments/video-room/1/ \
     -H "Authorization: Bearer YOUR_TOKEN"
   ```

2. **WhatsApp** (if configured):
   - Send test reminder to your phone
   - Verify delivery

3. **SMS Backup**:
   - Trigger SMS fallback
   - Verify delivery

4. **Status Callbacks**:
   - Create video room
   - Check webhook logs: `journalctl -u gunicorn -f`

---

## 📞 Support

If you need help:
- **Twilio Support**: https://support.twilio.com
- **Twilio Console**: https://console.twilio.com
- **Documentation**: https://www.twilio.com/docs

---

## Summary

**Action Required**: ⚠️ **Upgrade your Twilio account before going live**

**Why**: Trial accounts will break in production (verified recipients only, balance limits)

**Cost**: ~$3.50-6/month for typical clinic usage

**Time**: 10-15 minutes to upgrade

**Impact**: Critical - Video calls and notifications won't work reliably on trial account

