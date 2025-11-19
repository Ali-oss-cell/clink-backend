# 🎥 Video Call - Complete User Flow & Frontend Requirements

## 📱 **How Video Calls Work - Complete Flow**

### **Scenario: Appointment at 11:00 AM**

---

## 🔔 **Step 1: Reminders (Before Appointment)**

### **24 Hours Before (10:00 AM Previous Day)**
Both patient and psychologist receive:

**WhatsApp Message:**
```
🔔 Appointment Reminder

Hello [Name],

Your appointment is tomorrow:
📅 Monday, November 15 at 11:00 AM
👨‍⚕️ Dr. Smith
⏱️ 50 minutes

🎥 Video Link:
https://yourwebsite.com/video-session/apt-123-abc

💡 Tip: Join 5 minutes early!

See you tomorrow! 👋
```

**Email:**
- Same information
- Meeting link included
- Calendar invite (optional)

### **1 Hour Before (10:00 AM)**
Both receive:
```
⏰ Starting in 1 Hour

Your appointment starts at 11:00 AM
👨‍⚕️ Dr. Smith

🎥 Join here:
https://yourwebsite.com/video-session/apt-123-abc

Ready when you are! ✨
```

### **15 Minutes Before (10:45 AM)**
Both receive:
```
🚀 Starting in 15 Minutes!

Your session is about to begin!

🎥 Join now:
https://yourwebsite.com/video-session/apt-123-abc

💡 Test your camera & mic!

See you soon! 👋
```

---

## 🎥 **Step 2: Joining the Video Call (At 11:00 AM)**

### **Option A: Click Link from WhatsApp/Email** (Recommended)

1. **Patient clicks link** → Opens website → `/video-session/apt-123-abc`
2. **Psychologist clicks link** → Opens website → `/video-session/apt-123-abc`
3. **Frontend automatically:**
   - Gets access token from your API
   - Connects to Twilio room
   - Shows video call interface

### **Option B: Go to Website Directly**

1. **Patient logs in** → Dashboard → "Join Video Session" button
2. **Psychologist logs in** → Dashboard → "Join Video Session" button
3. **Frontend shows:**
   - List of upcoming appointments
   - "Join" button for each appointment
   - Click → Opens video call

---

## 💻 **What Frontend Needs to Implement**

### **1. Video Call Page/Component**

**Route:** `/video-session/:roomName` or `/appointments/:id/video`

**What it does:**
1. **Get Access Token:**
   ```typescript
   // Call your API
   GET /api/appointments/video-token/{appointment_id}/
   
   // Response:
   {
     "access_token": "eyJhbGciOiJIUzI1NiIs...",
     "room_name": "apt-123-abc",
     "user_identity": "1-patient@example.com",
     "expires_in": 7200
   }
   ```

2. **Connect to Twilio:**
   ```typescript
   import Video from 'twilio-video';
   
   // Connect to room
   const room = await Video.connect(accessToken, {
     name: roomName,
     audio: true,
     video: true
   });
   ```

3. **Display Video:**
   - Show local video (patient/doctor's own camera)
   - Show remote video (other person's camera)
   - Show controls (mute, camera on/off, leave)

4. **Handle Events:**
   - When other person joins
   - When other person leaves
   - Connection errors
   - End call

---

### **2. Dashboard Integration**

**Patient Dashboard:**
```typescript
// Show upcoming appointments
{
  id: 123,
  date: "2025-11-15T11:00:00",
  psychologist: "Dr. Smith",
  status: "scheduled",
  video_room_id: "apt-123-abc",
  // Show "Join Video Session" button if:
  // - Appointment is within 15 minutes
  // - OR appointment time has passed
  canJoin: true
}
```

**Psychologist Dashboard:**
```typescript
// Same structure
// Show "Join Video Session" button
```

---

### **3. Appointment List Component**

**Show in both dashboards:**
- Upcoming appointments
- "Join Video" button (if telehealth and time is right)
- Meeting link (copy to share)

---

## 🎯 **Complete User Journey**

### **Patient Journey:**

```
1. Books appointment (telehealth)
   ↓
2. Receives confirmation email/WhatsApp
   ↓
3. 24h before: Gets reminder with video link
   ↓
4. 1h before: Gets reminder with video link
   ↓
5. 15min before: Gets reminder with video link
   ↓
6. At 11:00 AM:
   Option A: Clicks link from WhatsApp → Video page opens
   Option B: Logs in → Dashboard → "Join Video Session" button
   ↓
7. Video page:
   - Requests camera/mic permission
   - Gets access token from API
   - Connects to Twilio room
   - Shows video call interface
   ↓
8. Sees psychologist when they join
   ↓
9. Has video call
   ↓
10. Clicks "End Call" → Returns to dashboard
```

### **Psychologist Journey:**

```
(Same as patient, but from their perspective)
```

---

## 🛠️ **Frontend Implementation Checklist**

### **Required Components:**

#### **1. Video Call Page** (`/video-session/:roomName`)
- [ ] Install `twilio-video` package
- [ ] Create video component
- [ ] Get access token from API
- [ ] Connect to Twilio room
- [ ] Display local video
- [ ] Display remote video
- [ ] Camera on/off button
- [ ] Microphone mute/unmute button
- [ ] Leave call button
- [ ] Loading state (connecting...)
- [ ] Error handling (connection failed, etc.)
- [ ] Waiting state (waiting for other person)

#### **2. Dashboard Integration**
- [ ] Show upcoming appointments
- [ ] "Join Video Session" button (if telehealth)
- [ ] Check if appointment time is right (within 15 min or started)
- [ ] Link to video page

#### **3. Appointment List**
- [ ] Show video room ID
- [ ] "Join" button for active appointments
- [ ] Copy meeting link button

#### **4. Notifications (Optional)**
- [ ] Show browser notification when appointment is starting
- [ ] "Join Now" button in notification

---

## 📋 **API Endpoints You'll Use**

### **1. Get Access Token**
```http
GET /api/appointments/video-token/{appointment_id}/
Authorization: Bearer <user_token>

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "room_name": "apt-123-abc",
  "user_identity": "1-patient@example.com",
  "expires_in": 7200
}
```

### **2. Get Appointment Details**
```http
GET /api/appointments/{appointment_id}/
Authorization: Bearer <user_token>

Response:
{
  "id": 123,
  "appointment_date": "2025-11-15T11:00:00Z",
  "session_type": "telehealth",
  "video_room_id": "apt-123-abc",
  "psychologist": {...},
  "patient": {...}
}
```

### **3. Create Video Room (if needed)**
```http
POST /api/appointments/video-room/{appointment_id}/
Authorization: Bearer <user_token>

Response:
{
  "message": "Video room created successfully",
  "room_name": "apt-123-abc",
  "room_sid": "RM...",
  "meeting_url": "https://yourwebsite.com/video-session/apt-123-abc"
}
```

---

## 🎨 **Frontend Video Component Example Structure**

```typescript
// VideoCallPage.tsx
import { useEffect, useState } from 'react';
import Video from 'twilio-video';
import { useParams } from 'react-router-dom';

function VideoCallPage() {
  const { roomName } = useParams();
  const [room, setRoom] = useState(null);
  const [localVideoTrack, setLocalVideoTrack] = useState(null);
  const [remoteVideoTrack, setRemoteVideoTrack] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function connectToRoom() {
      try {
        // 1. Get access token from your API
        const response = await fetch(
          `/api/appointments/video-token/${appointmentId}/`,
          {
            headers: {
              'Authorization': `Bearer ${userToken}`
            }
          }
        );
        const { access_token, room_name } = await response.json();

        // 2. Connect to Twilio room
        const room = await Video.connect(access_token, {
          name: room_name,
          audio: true,
          video: true
        });

        setRoom(room);
        setIsConnected(true);
        setIsLoading(false);

        // 3. Get local video track
        const localTracks = await Video.createLocalTracks({
          audio: true,
          video: true
        });
        
        localTracks.forEach(track => {
          if (track.kind === 'video') {
            setLocalVideoTrack(track);
            track.attach('#local-video');
          }
        });

        // 4. Listen for remote participants
        room.on('participantConnected', participant => {
          participant.tracks.forEach(publication => {
            if (publication.track) {
              setRemoteVideoTrack(publication.track);
              publication.track.attach('#remote-video');
            }
          });
        });

        // 5. Handle participant leaving
        room.on('participantDisconnected', () => {
          setRemoteVideoTrack(null);
        });

      } catch (error) {
        console.error('Failed to connect:', error);
        setIsLoading(false);
      }
    }

    connectToRoom();

    // Cleanup on unmount
    return () => {
      if (room) {
        room.disconnect();
      }
      if (localVideoTrack) {
        localVideoTrack.stop();
      }
    };
  }, []);

  const toggleMute = () => {
    // Toggle microphone
  };

  const toggleCamera = () => {
    // Toggle camera
  };

  const leaveCall = () => {
    room?.disconnect();
    // Navigate back to dashboard
  };

  if (isLoading) {
    return <div>Connecting to video call...</div>;
  }

  return (
    <div className="video-call-container">
      <div className="video-grid">
        {/* Remote video (other person) */}
        <div id="remote-video"></div>
        
        {/* Local video (yourself) */}
        <div id="local-video"></div>
      </div>

      <div className="controls">
        <button onClick={toggleMute}>Mute</button>
        <button onClick={toggleCamera}>Camera</button>
        <button onClick={leaveCall}>Leave Call</button>
      </div>
    </div>
  );
}
```

---

## ✅ **Summary: What You Need to Build**

### **1. Video Call Page** (Required)
- Route: `/video-session/:roomName` or `/appointments/:id/video`
- Gets access token from API
- Connects to Twilio
- Shows video streams
- Has controls (mute, camera, leave)

### **2. Dashboard Integration** (Required)
- Show upcoming appointments
- "Join Video Session" button
- Link to video page

### **3. WhatsApp/Email Links** (Already Working!)
- Links point to: `https://yourwebsite.com/video-session/{room_name}`
- Frontend handles the route
- Automatically connects to video

---

## 🎯 **Answer to Your Questions**

### **Q: Will they receive WhatsApp messages?**
**A: Yes!** Both patient and psychologist receive:
- 24h before: Reminder with video link
- 1h before: Reminder with video link
- 15min before: Reminder with video link

### **Q: How will they join?**
**A: Two ways:**
1. **Click link from WhatsApp/Email** → Opens video page → Auto-connects
2. **Go to website** → Dashboard → "Join Video Session" button → Opens video page

### **Q: Do I need to implement a place in frontend?**
**A: Yes!** You need:
1. **Video Call Page** - Where the actual video happens
2. **Dashboard Integration** - "Join Video Session" button
3. **Route handling** - `/video-session/:roomName` route

---

## 🚀 **Next Steps**

1. **Backend:** ✅ Already done!
2. **Frontend:** Build video call component
3. **Testing:** Test with real video calls
4. **Polish:** Add UI/UX improvements

**The backend is ready - you just need to build the frontend video component!** 🎉

