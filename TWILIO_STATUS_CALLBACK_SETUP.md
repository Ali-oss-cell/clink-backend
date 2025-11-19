# Twilio Status Callback Setup Guide

## What Are Status Callbacks?

Status callbacks are **optional webhooks** that Twilio sends to your server when video room events occur. They're useful for:
- Tracking when participants join/leave
- Logging room events
- Auto-completing appointments when sessions end
- Monitoring room usage

**IMPORTANT**: Status callbacks are **NOT required** for video calls to work. They're just for tracking and automation.

---

## Current Status

✅ **Webhook endpoint created**: `/api/appointments/twilio-status-callback/`
✅ **Video service updated**: Can use status callback URL if configured
✅ **Event handling**: Logs all events (can be extended to save to database)

---

## Setup Instructions

### Step 1: Get a Public URL (For Production)

Status callbacks require a **publicly accessible URL**. Twilio needs to reach your server.

**For Local Development:**
- Use **ngrok** or similar tunneling service
- Example: `ngrok http 8000`
- You'll get a URL like: `https://abc123.ngrok.io`

**For Production:**
- Use your production domain
- Example: `https://yourdomain.com/api/appointments/twilio-status-callback/`

### Step 2: Configure the Callback URL

Add to your `.env` file:

```bash
# For local development (with ngrok):
TWILIO_STATUS_CALLBACK_URL=https://abc123.ngrok.io/api/appointments/twilio-status-callback/

# For production:
TWILIO_STATUS_CALLBACK_URL=https://yourdomain.com/api/appointments/twilio-status-callback/
```

### Step 3: Configure in Twilio Console (Optional)

You can also set a default callback URL in Twilio Console:
1. Go to [Twilio Console](https://console.twilio.com)
2. Navigate to: **Video** → **Rooms** → **Settings**
3. Under **Webhook Notifications**, set:
   - **Status Callback URL**: Your public URL
   - **HTTP Method**: POST

**Note**: The URL in your `.env` file will override the console setting when creating rooms via API.

---

## Events You'll Receive

The webhook receives these events:

| Event | Description |
|-------|-------------|
| `room-created` | Room was created |
| `room-ended` | Room completed/ended |
| `participant-connected` | Participant joined the room |
| `participant-disconnected` | Participant left the room |
| `track-added` | Participant added audio/video track |
| `track-removed` | Participant removed track |
| `track-enabled` | Participant unpaused track |
| `track-disabled` | Participant paused track |
| `recording-started` | Recording began |
| `recording-completed` | Recording finished |
| `recording-failed` | Recording error occurred |

---

## Testing the Webhook

### Test Locally with ngrok:

1. **Start ngrok:**
   ```bash
   ngrok http 8000
   ```

2. **Copy the HTTPS URL** (e.g., `https://abc123.ngrok.io`)

3. **Update `.env`:**
   ```bash
   TWILIO_STATUS_CALLBACK_URL=https://abc123.ngrok.io/api/appointments/twilio-status-callback/
   ```

4. **Restart Django server**

5. **Create a video room** - Twilio will send callbacks to your endpoint

6. **Check Django logs** - You'll see callback events logged

### Test with curl:

```bash
curl -X POST http://127.0.0.1:8000/api/appointments/twilio-status-callback/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "StatusCallbackEvent=room-created" \
  -d "RoomName=apt-48-test-room" \
  -d "RoomSid=RMxxxxxxxxxxxxxxxxxxxxxxxxxx" \
  -d "RoomStatus=in-progress" \
  -d "Timestamp=2025-11-16T10:00:00Z"
```

---

## Extending the Webhook

The current implementation **logs events**. You can extend it to:

### 1. Save Events to Database

Create a model to store events:

```python
# appointments/models.py
class VideoRoomEvent(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=50)
    room_name = models.CharField(max_length=255)
    room_sid = models.CharField(max_length=255)
    participant_identity = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 2. Auto-Complete Appointments

Uncomment this in `TwilioStatusCallbackView`:

```python
elif event_type == 'room-ended':
    if appointment and appointment.status in ['scheduled', 'confirmed']:
        appointment.status = 'completed'
        appointment.save()
```

### 3. Track Session Duration

Store participant duration when they disconnect:

```python
elif event_type == 'participant-disconnected':
    participant_duration = request.data.get('ParticipantDuration')
    if appointment and participant_duration:
        # Store duration in appointment notes or separate model
        appointment.notes += f"\nSession duration: {participant_duration} seconds"
        appointment.save()
```

---

## Troubleshooting

### Webhook Not Receiving Events

1. **Check URL is public**: Use ngrok for local testing
2. **Check `.env` file**: Make sure `TWILIO_STATUS_CALLBACK_URL` is set
3. **Check Django logs**: Look for callback logs
4. **Test endpoint manually**: Use curl to verify it works
5. **Check Twilio Console**: Verify callback URL in room settings

### Events Not Logged

1. **Check Django logging**: Ensure logger is configured
2. **Check server logs**: Look in `logs/django.log`
3. **Verify endpoint**: Test with curl first

---

## Security Note

The webhook endpoint is **public** (no authentication). Twilio validates requests using request signatures. For production, consider:

1. **Validating Twilio signatures** (recommended)
2. **Rate limiting** the endpoint
3. **IP whitelisting** (Twilio IPs only)

---

## Summary

✅ **Status callbacks are optional** - video calls work without them
✅ **Useful for tracking** - monitor room events and participant activity
✅ **Easy to set up** - just add URL to `.env`
✅ **Extensible** - can save events, auto-complete appointments, etc.

**The token error you're experiencing is NOT related to status callbacks.** It's about frontend caching old tokens. Clear your browser cache to fix it!

