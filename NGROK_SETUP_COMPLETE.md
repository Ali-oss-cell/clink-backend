# Ngrok Setup for Twilio Webhooks - COMPLETE

## Current Status

✅ **Ngrok URL**: `https://21a946926b5e.ngrok-free.app`
✅ **Callback URL Added**: `.env` file updated
⚠️ **Port Mismatch**: Ngrok forwarding to port 80, Django running on port 8000

---

## Quick Fix

### Option 1: Restart ngrok with correct port (Recommended)

**Stop current ngrok** (Ctrl+C in the ngrok terminal), then restart:

```bash
ngrok http 8000
```

This will give you a new URL. Update `.env` with the new URL:
```bash
TWILIO_STATUS_CALLBACK_URL=https://NEW-URL.ngrok-free.app/api/appointments/twilio-status-callback/
```

### Option 2: Keep current ngrok and run Django on port 80

**Not recommended** - requires sudo and may conflict with other services.

---

## Current Configuration

**Callback URL in `.env`:**
```
TWILIO_STATUS_CALLBACK_URL=https://21a946926b5e.ngrok-free.app/api/appointments/twilio-status-callback/
```

**Django Server:**
- Running on: `http://127.0.0.1:8000`
- Endpoint: `/api/appointments/twilio-status-callback/`
- Status: ✅ Accessible (405 response = endpoint exists, just needs POST)

---

## After Fixing Port

1. **Restart Django server** to load new `.env` value:
   ```bash
   # Stop current server (Ctrl+C)
   # Then restart:
   python manage.py runserver
   ```

2. **Test the webhook endpoint**:
   ```bash
   curl -X POST https://21a946926b5e.ngrok-free.app/api/appointments/twilio-status-callback/ \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "StatusCallbackEvent=room-created" \
     -d "RoomName=apt-48-test-room" \
     -d "RoomSid=RMtest" \
     -d "Timestamp=2025-11-16T10:00:00Z"
   ```

3. **Check Django logs** - you should see:
   ```
   INFO: Twilio Status Callback: room-created | Room: apt-48-test-room | ...
   ```

---

## Verify Setup

Once ngrok is forwarding to port 8000:

1. **Test locally first**:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/appointments/twilio-status-callback/ \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "StatusCallbackEvent=room-created" \
     -d "RoomName=apt-48-test-room"
   ```

2. **Test through ngrok**:
   ```bash
   curl -X POST https://YOUR-NGROK-URL.ngrok-free.app/api/appointments/twilio-status-callback/ \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "StatusCallbackEvent=room-created" \
     -d "RoomName=apt-48-test-room"
   ```

3. **Check ngrok web interface**: `http://127.0.0.1:4040`
   - You'll see all incoming requests
   - Useful for debugging

---

## Next Steps

1. ✅ **Restart ngrok** on port 8000
2. ✅ **Update `.env`** with new ngrok URL (if it changed)
3. ✅ **Restart Django** to load new config
4. ✅ **Test webhook** with curl
5. ✅ **Create a video room** - Twilio will send callbacks!

---

## Important Notes

- **Ngrok free tier**: URL changes each time you restart (unless you have a paid plan)
- **Keep ngrok running**: Webhooks won't work if ngrok is stopped
- **Django must be running**: Server needs to be up to receive callbacks
- **Check logs**: All webhook events are logged in Django console/logs

---

## Troubleshooting

### Webhook not receiving events?

1. Check ngrok is running: `http://127.0.0.1:4040`
2. Check Django is running: `http://127.0.0.1:8000`
3. Check `.env` has correct URL
4. Restart Django after changing `.env`
5. Test with curl first

### 404 errors?

- Make sure URL ends with `/api/appointments/twilio-status-callback/`
- Check Django server is running
- Verify ngrok is forwarding to correct port

### 405 errors?

- This is normal for GET requests (endpoint only accepts POST)
- Test with POST method

---

**Status**: Configuration ready, just need to fix ngrok port! 🚀

