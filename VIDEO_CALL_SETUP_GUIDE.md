# Video Call Setup Guide - Twilio Video Configuration

## 📋 Required Environment Variables (.env)

### Essential Twilio Credentials (Required for Video Calls)

Add these to your `.env` file on your Droplet:

```bash
# ============================================
# TWILIO VIDEO CONFIGURATION (REQUIRED)
# ============================================

# Twilio Account Credentials
# Get these from: https://console.twilio.com → Account → API Keys & Tokens
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-twilio-auth-token-here

# Twilio API Key & Secret (REQUIRED for Video Tokens)
# Create API Key at: https://console.twilio.com → Account → API Keys & Tokens → Create API Key
TWILIO_API_KEY=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_SECRET=your-api-secret-here

# Optional: Status Callback URL (for webhook events)
# Set this to receive room events (participant join/leave, room ended, etc.)
TWILIO_STATUS_CALLBACK_URL=https://api.tailoredpsychology.com.au/api/appointments/twilio-status-callback/
```

---

## 🔑 How to Get Your Twilio Credentials

### Step 1: Get Account SID and Auth Token

1. Go to: https://console.twilio.com
2. Navigate to: **Account** → **API Keys & Tokens**
3. You'll see:
   - **Account SID**: `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
   - **Auth Token**: Click "View" to reveal (copy this)

### Step 2: Create API Key (Required for Video)

1. In **API Keys & Tokens** page, click **Create API Key**
2. Give it a name: `Video API Key - Production`
3. Click **Create**
4. **IMPORTANT**: Copy the **API Key SID** (`SKxxxxxxxx...`) and **API Secret** immediately
   - ⚠️ The secret is shown **only once** - save it now!
   - If you lose it, you'll need to create a new API key

### Step 3: Add to .env File

On your Droplet:

```bash
cd /var/www/clink-backend
sudo nano .env
```

Add the credentials:

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-actual-auth-token
TWILIO_API_KEY=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_SECRET=your-actual-api-secret
TWILIO_STATUS_CALLBACK_URL=https://api.tailoredpsychology.com.au/api/appointments/twilio-status-callback/
```

Save and restart:

```bash
sudo systemctl restart gunicorn
```

---

## ✅ Video Call Setup Checklist

### 1. Twilio Console Settings

Go to: **Video** → **Rooms** → **Settings**

- ✅ **Media Region**: `Australia - au1` (already set correctly)
- ✅ **Status Callback URL**: `https://api.tailoredpsychology.com.au/api/appointments/twilio-status-callback/`
- ✅ **HTTP Method**: `POST`
- ✅ **Client-side Room Creation**: `Enabled` (already set)
- ⚠️ **Recording**: `Disabled` by default (enabled per-room with consent)

### 2. Environment Variables

Verify all 4 required variables are set:

```bash
# Check if variables are set
cd /var/www/clink-backend
source venv/bin/activate
python manage.py shell
```

```python
from django.conf import settings
print("Account SID:", bool(settings.TWILIO_ACCOUNT_SID))
print("Auth Token:", bool(settings.TWILIO_AUTH_TOKEN))
print("API Key:", bool(settings.TWILIO_API_KEY))
print("API Secret:", bool(settings.TWILIO_API_SECRET))
```

All should print `True`. If any print `False`, add the missing variable to `.env`.

### 3. Test Video Service

Test the video service configuration:

```bash
cd /var/www/clink-backend
source venv/bin/activate
python manage.py shell
```

```python
from appointments.video_service import get_video_service

# Test credentials
video_service = get_video_service()
result = video_service.validate_credentials()
print(result)
```

Expected output:
```python
{
    'valid': True,
    'account_sid': 'ACxxxxxxxx...',
    'account_status': 'active',
    'api_key_valid': True,
    'credentials_match': True
}
```

If `api_key_valid` is `False`, check that your API Key and Secret match your Account SID.

---

## 🔐 Important Security Question: Token Sharing

### ❌ **NO - Do NOT share the same token between patient and doctor!**

**Each user gets their own unique token** with their own identity. This is the correct and secure approach.

### How It Works:

1. **Patient requests token**:
   - Endpoint: `GET /api/appointments/video-token/{appointment_id}/`
   - User: Patient (authenticated)
   - Returns: Token with identity `"{patient_id}-{patient_email}"`

2. **Psychologist requests token**:
   - Endpoint: `GET /api/appointments/video-token/{appointment_id}/`
   - User: Psychologist (authenticated)
   - Returns: Token with identity `"{psychologist_id}-{psychologist_email}"`

3. **Both tokens**:
   - ✅ Join the **same room** (same `room_name`)
   - ✅ Have **different identities** (different `user_identity`)
   - ✅ Are **unique to each user** (cannot be shared)

### Code Reference:

```python
# appointments/views.py - GetVideoAccessTokenView
user_identity = f"{request.user.id}-{request.user.email}"

access_token = video_service.generate_access_token(
    user_identity=user_identity,  # Unique per user
    room_name=appointment.video_room_id,  # Same room for both
    ttl_hours=ttl_hours
)
```

### Why This Is Secure:

1. **Identity Tracking**: Each participant has a unique identity in the room
2. **Access Control**: Only patient or psychologist can get a token for their appointment
3. **Token Expiration**: Tokens expire after the session (prevents reuse)
4. **Audit Trail**: Twilio logs show which identity joined/left

---

## 🎥 Video Call Flow

### Step-by-Step Process:

1. **Appointment Created** → Backend creates video room (if needed)
2. **Patient Opens Video Page** → Frontend calls `/api/appointments/video-token/{id}/`
   - Backend generates token with identity: `"123-patient@email.com"`
   - Returns token to frontend
3. **Psychologist Opens Video Page** → Frontend calls `/api/appointments/video-token/{id}/`
   - Backend generates token with identity: `"456-psychologist@email.com"`
   - Returns token to frontend
4. **Both Join Room** → Twilio Video connects them in the same room
5. **Session Ends** → Room can be completed via API or auto-closes

---

## 🧪 Testing Video Calls

### Test Token Generation:

   ```bash
# Get appointment ID first
curl -X GET https://api.tailoredpsychology.com.au/api/appointments/ \
  -H "Authorization: Bearer YOUR_PATIENT_TOKEN" \
  | jq '.[0].id'

# Get video token (as patient)
curl -X GET https://api.tailoredpsychology.com.au/api/appointments/video-token/1/ \
  -H "Authorization: Bearer YOUR_PATIENT_TOKEN"

# Get video token (as psychologist)
curl -X GET https://api.tailoredpsychology.com.au/api/appointments/video-token/1/ \
  -H "Authorization: Bearer YOUR_PSYCHOLOGIST_TOKEN"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "room_name": "apt-1-1234567890-abc12345",
  "user_identity": "123-patient@email.com",
  "expires_in": 5400,
  "expires_at": "2025-01-24T15:30:00Z",
  "appointment_id": 1,
  "token_valid_until": "90 minutes (1 hours)"
}
```

**Notice**: `user_identity` is different for patient vs psychologist!

---

## 📝 Summary

### Required .env Variables:

```bash
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_API_KEY=SKxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_SECRET=your-api-secret
TWILIO_STATUS_CALLBACK_URL=https://api.tailoredpsychology.com.au/api/appointments/twilio-status-callback/
```

### Token Security:

- ✅ **Each user gets their own unique token**
- ✅ **Same room, different identities**
- ✅ **Tokens are user-specific and cannot be shared**
- ✅ **Secure and compliant with Twilio best practices**

### Setup Steps:

1. ✅ Get Twilio credentials from Console
2. ✅ Create API Key (for video tokens)
3. ✅ Add to `.env` file
4. ✅ Restart Gunicorn
5. ✅ Test token generation
6. ✅ Configure status callback URL (optional)

---

## 🆘 Troubleshooting

### Error: "Twilio credentials not configured"

**Solution**: Check that all 4 variables are in `.env`:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_API_KEY`
- `TWILIO_API_SECRET`

### Error: "Invalid API Key"

**Solution**: 
1. Verify API Key SID starts with `SK`
2. Verify API Secret matches the key
3. Create a new API Key if secret was lost

### Error: "Token generation failed"

**Solution**:
1. Check API Key belongs to the same Account SID
2. Verify API Secret is correct
3. Test with `validate_credentials()` method

### Tokens Not Working in Frontend

**Solution**:
1. Verify token is being generated (check API response)
2. Check token expiration (tokens expire after session)
3. Verify room name matches between patient and psychologist
4. Check browser console for Twilio Video SDK errors

---

## 📚 Additional Resources

- **Twilio Video Docs**: https://www.twilio.com/docs/video
- **Twilio Console**: https://console.twilio.com
- **API Keys Guide**: https://www.twilio.com/docs/iam/keys/api-key
- **Video Token Guide**: https://www.twilio.com/docs/video/tutorials/user-identity-access-tokens
