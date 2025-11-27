# Frontend Video Call Integration Guide

## 🎥 How Video Calls Work

### Backend → Frontend Flow

1. **Backend creates video room** (when appointment is confirmed)
2. **Frontend requests access token** (when user clicks "Join")
3. **Frontend uses Twilio Video SDK** (to connect to room)
4. **Both users join the same room** (using their own tokens)

---

## 📋 Step-by-Step Frontend Implementation

### Step 1: Check if Appointment Has Video Room

When displaying appointments, check if `video_room_id` exists:

```typescript
// API Response from GET /api/appointments/
{
  "id": 1,
  "patient": {...},
  "psychologist": {...},
  "appointment_date": "2025-11-25T16:53:18Z",
  "status": "confirmed",
  "session_type": "telehealth",
  "video_room_id": "apt-1-1732426800-a1b2c3d4",  // ← If this exists, show "Join" button
  "video_room_sid": "RMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
  "duration_minutes": 60
}
```

**Frontend Logic**:
```typescript
const canJoinVideo = appointment.video_room_id && appointment.session_type === 'telehealth';

if (canJoinVideo) {
  // Show "Join Video Call" button
}
```

---

### Step 2: Request Video Access Token

When user clicks "Join Video Call", request their access token:

**API Endpoint**: `GET /api/appointments/video-token/{appointment_id}/`

**Headers**:
```typescript
Authorization: Bearer <user_jwt_token>
```

**Request Example**:
```typescript
// For patient
const response = await fetch(
  `https://api.tailoredpsychology.com.au/api/appointments/video-token/${appointmentId}/`,
  {
    headers: {
      'Authorization': `Bearer ${userToken}`,
      'Content-Type': 'application/json'
    }
  }
);

const tokenData = await response.json();
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "room_name": "apt-1-1732426800-a1b2c3d4",
  "user_identity": "1-patient@email.com",
  "expires_in": 5400,
  "expires_at": "2025-11-25T17:30:00Z",
  "appointment_id": 1,
  "appointment_duration_minutes": 60,
  "token_valid_until": "90 minutes (1 hours)"
}
```

---

### Step 3: Install Twilio Video SDK

Install the Twilio Video JavaScript SDK in your frontend:

```bash
npm install twilio-video
# or
yarn add twilio-video
```

---

### Step 4: Connect to Video Room

Use the access token to connect to the room:

```typescript
import Video from 'twilio-video';

// Get token from API
const { access_token, room_name, user_identity } = tokenData;

// Connect to room
const room = await Video.connect(access_token, {
  name: room_name,
  audio: true,
  video: { width: 640 }
});

console.log(`Connected to room: ${room.name}`);
```

---

### Step 5: Display Local Video

Show the user's own video:

```typescript
// Get local video track
const localParticipant = room.localParticipant;

localParticipant.videoTracks.forEach(publication => {
  const track = publication.track;
  document.getElementById('local-video').appendChild(track.attach());
});
```

---

### Step 6: Display Remote Video

Show the other participant's video:

```typescript
// Handle participants already in room
room.participants.forEach(participant => {
  participant.videoTracks.forEach(publication => {
    if (publication.track) {
      document.getElementById('remote-video').appendChild(publication.track.attach());
    }
  });
});

// Handle new participants joining
room.on('participantConnected', participant => {
  console.log(`${participant.identity} joined`);
  
  participant.on('trackSubscribed', track => {
    document.getElementById('remote-video').appendChild(track.attach());
  });
});

// Handle participants leaving
room.on('participantDisconnected', participant => {
  console.log(`${participant.identity} left`);
});
```

---

### Step 7: Handle Disconnect

Allow user to leave the call:

```typescript
// Disconnect from room
function leaveCall() {
  room.disconnect();
  console.log('Disconnected from room');
}

// Auto-disconnect when user closes tab
window.addEventListener('beforeunload', () => room.disconnect());
```

---

## 🎨 Complete React Component Example

```typescript
import React, { useState, useEffect, useRef } from 'react';
import Video from 'twilio-video';

interface VideoCallProps {
  appointmentId: number;
  userToken: string;
}

const VideoCall: React.FC<VideoCallProps> = ({ appointmentId, userToken }) => {
  const [room, setRoom] = useState<Video.Room | null>(null);
  const [connecting, setConnecting] = useState(false);
  const localVideoRef = useRef<HTMLDivElement>(null);
  const remoteVideoRef = useRef<HTMLDivElement>(null);

  // Join video call
  const joinCall = async () => {
    setConnecting(true);
    
    try {
      // 1. Get access token from backend
      const response = await fetch(
        `https://api.tailoredpsychology.com.au/api/appointments/video-token/${appointmentId}/`,
        {
          headers: {
            'Authorization': `Bearer ${userToken}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      const { access_token, room_name } = await response.json();
      
      // 2. Connect to Twilio Video room
      const videoRoom = await Video.connect(access_token, {
        name: room_name,
        audio: true,
        video: { width: 640, height: 480 }
      });
      
      setRoom(videoRoom);
      
      // 3. Attach local video
      videoRoom.localParticipant.videoTracks.forEach(publication => {
        const track = publication.track;
        if (track && localVideoRef.current) {
          localVideoRef.current.appendChild(track.attach());
        }
      });
      
      // 4. Handle remote participants
      videoRoom.participants.forEach(participant => {
        attachParticipantTracks(participant);
      });
      
      videoRoom.on('participantConnected', participant => {
        console.log(`${participant.identity} joined`);
        attachParticipantTracks(participant);
      });
      
      videoRoom.on('participantDisconnected', participant => {
        console.log(`${participant.identity} left`);
        detachParticipantTracks(participant);
      });
      
    } catch (error) {
      console.error('Error joining call:', error);
      alert('Failed to join video call');
    } finally {
      setConnecting(false);
    }
  };
  
  // Attach remote participant's tracks
  const attachParticipantTracks = (participant: Video.RemoteParticipant) => {
    participant.tracks.forEach(publication => {
      if (publication.track && remoteVideoRef.current) {
        remoteVideoRef.current.appendChild(publication.track.attach());
      }
    });
    
    participant.on('trackSubscribed', track => {
      if (remoteVideoRef.current) {
        remoteVideoRef.current.appendChild(track.attach());
      }
    });
  };
  
  // Detach participant's tracks
  const detachParticipantTracks = (participant: Video.RemoteParticipant) => {
    participant.tracks.forEach(publication => {
      if (publication.track) {
        publication.track.detach().forEach(element => element.remove());
      }
    });
  };
  
  // Leave call
  const leaveCall = () => {
    if (room) {
      room.disconnect();
      setRoom(null);
    }
  };
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (room) {
        room.disconnect();
      }
    };
  }, [room]);
  
  return (
    <div className="video-call-container">
      <div className="video-grid">
        {/* Local video (your camera) */}
        <div className="local-video">
          <h3>You</h3>
          <div ref={localVideoRef} className="video-wrapper"></div>
        </div>
        
        {/* Remote video (other participant) */}
        <div className="remote-video">
          <h3>Remote Participant</h3>
          <div ref={remoteVideoRef} className="video-wrapper"></div>
        </div>
      </div>
      
      {/* Controls */}
      <div className="controls">
        {!room ? (
          <button 
            onClick={joinCall} 
            disabled={connecting}
            className="btn-join"
          >
            {connecting ? 'Connecting...' : 'Join Video Call'}
          </button>
        ) : (
          <button onClick={leaveCall} className="btn-leave">
            Leave Call
          </button>
        )}
      </div>
    </div>
  );
};

export default VideoCall;
```

---

## 📝 API Endpoints Summary

### 1. Get Appointments
```
GET /api/appointments/
```
**Response**: List of appointments with `video_room_id`

### 2. Get Video Token
```
GET /api/appointments/video-token/{appointment_id}/
```
**Response**: Access token for joining room

### 3. Refresh Token (if expired)
```
POST /api/appointments/video-token-refresh/{appointment_id}/
```
**Response**: New access token

### 4. Get Room Status
```
GET /api/appointments/video-status/{appointment_id}/
```
**Response**: Room status and participant count

---

## 🎯 Frontend Checklist

- [ ] Install `twilio-video` package
- [ ] Create video call component
- [ ] Request camera/microphone permissions
- [ ] Fetch video token from backend API
- [ ] Connect to Twilio room using token
- [ ] Display local video
- [ ] Display remote video
- [ ] Handle participant join/leave events
- [ ] Add mute/unmute controls
- [ ] Add camera on/off controls
- [ ] Add "Leave Call" button
- [ ] Handle errors gracefully
- [ ] Test with two different users/browsers

---

## 🔐 Security Notes

1. **Tokens are user-specific**: Patient token ≠ Psychologist token
2. **Tokens expire**: Default 1-2 hours (based on appointment duration)
3. **Room name is unique**: Each appointment has its own room
4. **Both users join same room**: Using `room_name` from backend

---

## 🐛 Troubleshooting

### "Join" button doesn't show
- Check if `video_room_id` exists in appointment data
- Check if `session_type === 'telehealth'`

### Can't connect to room
- Check if token is valid (not expired)
- Check browser console for errors
- Verify camera/microphone permissions

### Can't see remote video
- Make sure both users have joined the room
- Check if remote user has camera enabled
- Check browser console for track errors

### Token expired
- Use `/api/appointments/video-token-refresh/{id}/` to get new token
- Implement auto-refresh before expiry

---

## 📚 Additional Resources

- **Twilio Video JavaScript SDK**: https://www.twilio.com/docs/video/javascript
- **React Example**: https://github.com/twilio/twilio-video-app-react
- **API Documentation**: Check your backend's `/api/appointments/` endpoints

---

## 💡 Quick Test

1. Open browser 1 as patient
2. Login and navigate to appointment
3. Click "Join Video Call"
4. Open browser 2 (incognito) as psychologist
5. Login and navigate to same appointment
6. Click "Join Video Call"
7. Both should see each other's video

That's it! 🎉

