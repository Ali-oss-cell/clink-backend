# 🎥 Video Calls & 📧 Notifications Implementation Guide

Based on your project structure analysis, here's the complete implementation plan.

---

## 📊 **Current Infrastructure**

### ✅ **Already Configured:**
1. **Twilio** - For video calls and WhatsApp
2. **Celery** - For background tasks
3. **Celery Beat** - For scheduled tasks
4. **Email** - SMTP configuration ready
5. **Redis** - Task queue (needs to be running)

### 📁 **Existing Components:**
- `psychology_clinic/celery.py` - Celery configured
- `appointments/models.py` - Has `video_room_id` field
- `appointments/views.py` - Has `CreateVideoRoomView`
- Settings configured for Twilio & Email

---

## 🎥 **Video Calls Solution - Twilio Video**

### **Why Twilio Video?**
✅ Already configured in your project  
✅ HIPAA compliant (important for healthcare)  
✅ No external app needed (browser-based)  
✅ Works on mobile and desktop  
✅ Easy to integrate  
✅ Secure and encrypted  

### **Architecture:**

```
┌─────────────────────────────────────────────────────────┐
│                   Video Call Flow                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. Appointment Created                                 │
│     ↓                                                   │
│  2. Backend creates Twilio Room                         │
│     ↓                                                   │
│  3. Generate access tokens for patient & psychologist   │
│     ↓                                                   │
│  4. Send meeting link via email/SMS (24h before)        │
│     ↓                                                   │
│  5. Patient/Psychologist click link                     │
│     ↓                                                   │
│  6. Frontend requests access token                      │
│     ↓                                                   │
│  7. Join Twilio room with token                         │
│     ↓                                                   │
│  8. Video call session active                           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 📧 **Notification System Architecture**

### **Notification Channels:**

1. **Email** (Primary) - Appointment confirmations, reminders
2. **WhatsApp** (Optional) - Quick reminders via Twilio
3. **SMS** (Optional) - Emergency notifications via Twilio
4. **In-App** (Future) - Real-time notifications

### **Notification Schedule:**

```
Appointment Booked
↓
├─ Immediate: Confirmation email
├─ 24 hours before: Reminder email + meeting link
├─ 1 hour before: WhatsApp/SMS reminder
└─ 15 minutes before: Final reminder with meeting link
```

---

## 🛠️ **Implementation Steps**

### **Step 1: Create Appointment Tasks (Celery)**

Create: `appointments/tasks.py`

This will handle:
- Sending appointment reminders
- Creating video rooms automatically
- Sending meeting links
- Cleaning up old video rooms

### **Step 2: Create Video Call Service**

Create: `appointments/video_service.py`

This will handle:
- Creating Twilio rooms
- Generating access tokens
- Managing room lifecycle
- Recording sessions (optional)

### **Step 3: Create Notification Service**

Create: `core/notifications.py`

This will handle:
- Email templates
- WhatsApp messages
- SMS messages
- Notification scheduling

### **Step 4: Update Appointment Creation**

Modify booking flow to:
- Automatically create video room for telehealth
- Send confirmation email
- Schedule reminders

---

## 📝 **What I'll Create for You:**

### **1. Video Call System:**
- ✅ Twilio room creation
- ✅ Access token generation
- ✅ Meeting link endpoints
- ✅ Frontend integration code

### **2. Notification System:**
- ✅ Celery tasks for scheduled reminders
- ✅ Email templates
- ✅ WhatsApp/SMS integration
- ✅ Automatic scheduling

### **3. API Endpoints:**
- `POST /api/appointments/{id}/video-room/` - Create/get video room
- `GET /api/appointments/{id}/video-token/` - Get access token
- `POST /api/appointments/{id}/send-reminder/` - Manual reminder
- `GET /api/appointments/{id}/meeting-details/` - Get meeting info

---

## 🎯 **Recommended Approach**

### **Phase 1: Core Video Functionality** (Priority: HIGH)
1. Create video room on telehealth appointment booking
2. Generate access tokens for patient & psychologist
3. Return meeting link in appointment details
4. Frontend video call component

### **Phase 2: Email Notifications** (Priority: HIGH)
1. Confirmation email on booking
2. 24-hour reminder with meeting link
3. Email templates (professional HTML)
4. Test email delivery

### **Phase 3: Advanced Notifications** (Priority: MEDIUM)
1. WhatsApp reminders
2. SMS fallback
3. Multiple reminder schedule
4. Notification preferences

### **Phase 4: Enhancements** (Priority: LOW)
1. Recording sessions
2. Screen sharing
3. Chat during session
4. Session notes/transcription

---

## 🔧 **Prerequisites**

### **Required Services:**

#### **1. Redis (for Celery)**
```bash
# Install Redis
sudo apt install redis-server  # Ubuntu/Debian
brew install redis  # macOS

# Start Redis
redis-server

# Or with Docker
docker run -d -p 6379:6379 redis:alpine
```

#### **2. Twilio Account**
```bash
# Sign up at twilio.com
# Get credentials from console:
- Account SID
- Auth Token
- API Key
- API Secret
```

#### **3. Email Service**
Options:
- **SendGrid** (recommended for production)
- **Gmail SMTP** (for testing)
- **AWS SES**
- **Mailgun**

---

## ⚙️ **Environment Variables**

Add to `.env`:

```bash
# Twilio Video
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_API_KEY=SKxxxxxxxxxxxxxxxxxxxxx
TWILIO_API_SECRET=your_api_secret

# Twilio Messaging (WhatsApp/SMS)
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_PHONE_NUMBER=+1234567890

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com  # Or SendGrid
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0

# App URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

---

## 📧 **Email Templates Structure**

```
templates/
├── email/
│   ├── base.html                      # Base email template
│   ├── appointment_confirmation.html  # Booking confirmation
│   ├── appointment_reminder_24h.html  # 24-hour reminder
│   ├── appointment_reminder_1h.html   # 1-hour reminder
│   ├── appointment_cancelled.html     # Cancellation notice
│   ├── appointment_rescheduled.html   # Reschedule notice
│   └── video_meeting_link.html        # Meeting link email
```

---

## 🔐 **Security Considerations**

### **Video Calls:**
1. ✅ Access tokens expire after 1 hour
2. ✅ Tokens tied to specific user identity
3. ✅ Room names are unique and unpredictable
4. ✅ Only appointment participants can join
5. ✅ Encrypted end-to-end

### **Notifications:**
1. ✅ Don't include sensitive medical info in SMS/WhatsApp
2. ✅ Use secure email (TLS)
3. ✅ Meeting links expire after appointment time
4. ✅ Rate limiting on reminder sends

---

## 🎨 **Frontend Integration**

### **Video Call Component (React)**

```jsx
import { useEffect, useState } from 'react';
import Video from 'twilio-video';

const VideoCall = ({ appointmentId, token }) => {
  const [room, setRoom] = useState(null);
  
  useEffect(() => {
    // Connect to Twilio room
    Video.connect(token, {
      audio: true,
      video: { width: 640 }
    }).then(room => {
      setRoom(room);
      
      // Attach local video
      const localMediaContainer = document.getElementById('local-media');
      room.localParticipant.tracks.forEach(publication => {
        if (publication.track) {
          localMediaContainer.appendChild(publication.track.attach());
        }
      });
      
      // Attach remote participants
      room.participants.forEach(participant => {
        attachParticipant(participant);
      });
      
      room.on('participantConnected', participant => {
        attachParticipant(participant);
      });
    });
    
    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, [token]);
  
  const attachParticipant = (participant) => {
    const remoteMediaContainer = document.getElementById('remote-media');
    participant.tracks.forEach(publication => {
      if (publication.isSubscribed) {
        remoteMediaContainer.appendChild(publication.track.attach());
      }
    });
    
    participant.on('trackSubscribed', track => {
      remoteMediaContainer.appendChild(track.attach());
    });
  };
  
  return (
    <div className="video-call">
      <div id="remote-media" className="remote-video"></div>
      <div id="local-media" className="local-video"></div>
      <button onClick={() => room.disconnect()}>End Call</button>
    </div>
  );
};
```

---

## 📊 **Database Schema Additions**

### **Optional: Notification Log**

```python
class NotificationLog(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20)  # email, sms, whatsapp
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)  # sent, failed, pending
    recipient = models.EmailField()
    message_id = models.CharField(max_length=255, blank=True)
```

---

## 🚀 **Quick Start Commands**

### **1. Install Dependencies**
```bash
pip install twilio celery redis python-decouple
```

### **2. Start Redis**
```bash
redis-server
```

### **3. Start Celery Worker**
```bash
cd /home/ali/Desktop/projects/clink-backend
source venv/bin/activate
celery -A psychology_clinic worker -l info
```

### **4. Start Celery Beat (Scheduler)**
```bash
celery -A psychology_clinic beat -l info
```

### **5. Test Video Room Creation**
```bash
curl -X POST http://localhost:8000/api/appointments/video-room/1/ \
  -H 'Authorization: Bearer YOUR_TOKEN'
```

---

## ✅ **Testing Checklist**

### **Video Calls:**
- [ ] Create video room for telehealth appointment
- [ ] Generate access token for patient
- [ ] Generate access token for psychologist
- [ ] Patient can join room
- [ ] Psychologist can join room
- [ ] Audio works
- [ ] Video works
- [ ] Room closes after appointment

### **Email Notifications:**
- [ ] Confirmation email sends on booking
- [ ] 24-hour reminder sends
- [ ] 1-hour reminder sends
- [ ] Meeting link included in email
- [ ] Cancellation email sends
- [ ] Reschedule email sends

### **WhatsApp/SMS:**
- [ ] WhatsApp reminder sends
- [ ] SMS reminder sends
- [ ] No sensitive info in messages
- [ ] Meeting link works

---

## 🎯 **What Should We Build First?**

I recommend this order:

### **Priority 1:** Video Room Creation & Access Tokens
- Essential for telehealth appointments
- Users need this immediately
- ~2 hours implementation

### **Priority 2:** Email Notifications
- Confirmation emails
- 24-hour reminder with meeting link
- ~3 hours implementation

### **Priority 3:** Celery Tasks for Auto-Reminders
- Automated scheduling
- Background processing
- ~2 hours implementation

### **Priority 4:** WhatsApp/SMS (Optional)
- Enhanced notification delivery
- ~1 hour implementation

---

## 💡 **My Recommendation**

**Start with:**
1. ✅ Video room creation endpoints
2. ✅ Email notification system
3. ✅ Celery tasks for reminders
4. ✅ Frontend video call component

**Would you like me to implement:**
- [ ] Video call system (Twilio integration)
- [ ] Email notification system
- [ ] Celery tasks for reminders
- [ ] All of the above

Let me know which one to start with, and I'll create the complete implementation!

