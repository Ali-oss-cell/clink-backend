# Session Timer Frontend Implementation Guide

## Overview

The appointment API now includes timer fields that help you build a great user experience for session countdowns and duration tracking. This guide explains how to use these fields in your React frontend.

---

## New Timer Fields in API Response

Every appointment object now includes these timer-related fields:

```json
{
  "id": 48,
  "session_start_time": "2025-11-16T08:33:13.400627+00:00",
  "session_end_time": "2025-11-16T09:33:13.400627+00:00",
  "time_until_start_seconds": 85808,
  "time_remaining_seconds": null,
  "session_status": "upcoming",
  "can_join_session": false,
  "duration_minutes": 60
}
```

---

## Field Descriptions

### 1. `session_start_time` (ISO string)
- **Type**: `string` (ISO 8601 format)
- **Description**: Exact start time of the session
- **Use**: Parse with `new Date()` for accurate time calculations

### 2. `session_end_time` (ISO string)
- **Type**: `string` (ISO 8601 format)
- **Description**: Exact end time of the session (start + duration)
- **Use**: Calculate total session duration or show end time

### 3. `time_until_start_seconds` (integer)
- **Type**: `number` or `null`
- **Description**: Seconds until session starts
  - **Positive**: Session hasn't started yet (countdown)
  - **Negative**: Session has already started
  - **Null**: No appointment date set
- **Use**: Display countdown timer before session starts

### 4. `time_remaining_seconds` (integer or null)
- **Type**: `number` or `null`
- **Description**: Seconds remaining in the session
  - **Number**: Session is in progress (countdown)
  - **0**: Session has just ended
  - **Null**: Session hasn't started yet
- **Use**: Display timer during active session

### 5. `session_status` (string)
- **Type**: `string`
- **Values**:
  - `"upcoming"`: Session hasn't started yet
  - `"starting_soon"`: Starts in less than 5 minutes
  - `"in_progress"`: Session is currently happening
  - `"ended"`: Session has ended
  - `"unknown"`: Missing data
- **Use**: Show different UI states based on session status

### 6. `can_join_session` (boolean)
- **Type**: `boolean`
- **Description**: Whether user can join the video session
  - **True**: Can join (5 min before start until session ends)
  - **False**: Cannot join (too early or session ended)
- **Use**: Enable/disable "Join Session" button

---

## React Implementation Example

### Basic Timer Component

```typescript
import React, { useState, useEffect } from 'react';

interface Appointment {
  id: number;
  session_start_time: string;
  session_end_time: string;
  time_until_start_seconds: number | null;
  time_remaining_seconds: number | null;
  session_status: 'upcoming' | 'starting_soon' | 'in_progress' | 'ended' | 'unknown';
  can_join_session: boolean;
  duration_minutes: number;
}

interface SessionTimerProps {
  appointment: Appointment;
}

const SessionTimer: React.FC<SessionTimerProps> = ({ appointment }) => {
  const [currentTime, setCurrentTime] = useState(Date.now());

  // Update timer every second
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(Date.now());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Calculate time values
  const startTime = new Date(appointment.session_start_time).getTime();
  const endTime = new Date(appointment.session_end_time).getTime();
  const timeUntilStart = Math.max(0, Math.floor((startTime - currentTime) / 1000));
  const timeRemaining = appointment.time_remaining_seconds !== null 
    ? Math.max(0, appointment.time_remaining_seconds - Math.floor((currentTime - startTime) / 1000))
    : null;

  // Format time display
  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  // Render based on session status
  const renderTimer = () => {
    switch (appointment.session_status) {
      case 'upcoming':
        return (
          <div className="timer-upcoming">
            <p className="timer-label">Session starts in:</p>
            <p className="timer-value">{formatTime(timeUntilStart)}</p>
            <p className="timer-subtitle">
              {new Date(appointment.session_start_time).toLocaleString()}
            </p>
          </div>
        );

      case 'starting_soon':
        return (
          <div className="timer-starting-soon">
            <p className="timer-label">⚠️ Session starting soon!</p>
            <p className="timer-value">{formatTime(timeUntilStart)}</p>
            {appointment.can_join_session && (
              <button className="btn-join">Join Session Now</button>
            )}
          </div>
        );

      case 'in_progress':
        return (
          <div className="timer-in-progress">
            <p className="timer-label">Session in progress</p>
            <p className="timer-value">{formatTime(timeRemaining || 0)}</p>
            <p className="timer-subtitle">Time remaining</p>
            {appointment.can_join_session && (
              <button className="btn-join">Join Session</button>
            )}
          </div>
        );

      case 'ended':
        return (
          <div className="timer-ended">
            <p className="timer-label">Session ended</p>
            <p className="timer-subtitle">
              Duration: {appointment.duration_minutes} minutes
            </p>
          </div>
        );

      default:
        return <p>Unable to load timer</p>;
    }
  };

  return (
    <div className="session-timer">
      {renderTimer()}
    </div>
  );
};

export default SessionTimer;
```

---

## Advanced Timer with Visual Progress

```typescript
import React, { useState, useEffect } from 'react';

const AdvancedSessionTimer: React.FC<SessionTimerProps> = ({ appointment }) => {
  const [currentTime, setCurrentTime] = useState(Date.now());

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTime(Date.now());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const startTime = new Date(appointment.session_start_time).getTime();
  const endTime = new Date(appointment.session_end_time).getTime();
  const totalDuration = endTime - startTime;
  const elapsed = Math.max(0, currentTime - startTime);
  const progress = appointment.session_status === 'in_progress'
    ? Math.min(100, (elapsed / totalDuration) * 100)
    : 0;

  const formatTime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  return (
    <div className="advanced-timer">
      {/* Progress Bar */}
      {appointment.session_status === 'in_progress' && (
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {/* Timer Display */}
      <div className="timer-display">
        {appointment.session_status === 'in_progress' && appointment.time_remaining_seconds !== null && (
          <>
            <div className="timer-circle">
              <svg viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="#e0e0e0"
                  strokeWidth="8"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="#4CAF50"
                  strokeWidth="8"
                  strokeDasharray={`${2 * Math.PI * 45}`}
                  strokeDashoffset={`${2 * Math.PI * 45 * (1 - progress / 100)}`}
                  transform="rotate(-90 50 50)"
                />
              </svg>
              <div className="timer-text">
                {formatTime(appointment.time_remaining_seconds)}
              </div>
            </div>
            <p className="timer-label">Time Remaining</p>
          </>
        )}

        {appointment.session_status === 'upcoming' && appointment.time_until_start_seconds !== null && (
          <>
            <div className="countdown-display">
              {formatTime(appointment.time_until_start_seconds)}
            </div>
            <p className="timer-label">Until Session Starts</p>
          </>
        )}
      </div>

      {/* Join Button */}
      {appointment.can_join_session && (
        <button 
          className="btn-join-primary"
          onClick={() => {
            // Navigate to video session
            window.location.href = `/video-session/${appointment.id}`;
          }}
        >
          {appointment.session_status === 'starting_soon' ? 'Join Early' : 'Join Session'}
        </button>
      )}
    </div>
  );
};
```

---

## UX Best Practices

### 1. **Update Timer Every Second**
```typescript
useEffect(() => {
  const interval = setInterval(() => {
    // Refresh appointment data or update local timer
    setCurrentTime(Date.now());
  }, 1000);
  return () => clearInterval(interval);
}, []);
```

### 2. **Show Different States Clearly**

- **Upcoming**: Show countdown with calm colors (blue/gray)
- **Starting Soon**: Show warning with yellow/orange colors
- **In Progress**: Show active timer with green colors
- **Ended**: Show completed state with muted colors

### 3. **Enable Join Button at Right Time**

```typescript
{appointment.can_join_session && (
  <button 
    onClick={handleJoinSession}
    disabled={!appointment.can_join_session}
  >
    Join Video Session
  </button>
)}
```

### 4. **Handle Edge Cases**

```typescript
// Check if timer data is valid
if (!appointment.session_start_time || !appointment.session_end_time) {
  return <div>Unable to load session timer</div>;
}

// Handle null values gracefully
const timeRemaining = appointment.time_remaining_seconds ?? 0;
```

### 5. **Refresh Data Periodically**

```typescript
// Refresh appointment data every 30 seconds to get updated timer values
useEffect(() => {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/appointments/${appointment.id}/`);
    const updatedAppointment = await response.json();
    setAppointment(updatedAppointment);
  }, 30000); // 30 seconds

  return () => clearInterval(interval);
}, [appointment.id]);
```

---

## Mobile-Friendly Timer Display

```typescript
const MobileTimer: React.FC<SessionTimerProps> = ({ appointment }) => {
  const formatCompact = (seconds: number): string => {
    if (seconds >= 3600) {
      return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
    } else if (seconds >= 60) {
      return `${Math.floor(seconds / 60)}m`;
    } else {
      return `${seconds}s`;
    }
  };

  return (
    <div className="mobile-timer">
      {appointment.session_status === 'in_progress' && (
        <div className="mobile-timer-active">
          <span className="timer-icon">⏱️</span>
          <span className="timer-text">
            {formatCompact(appointment.time_remaining_seconds || 0)}
          </span>
        </div>
      )}
      
      {appointment.session_status === 'starting_soon' && (
        <div className="mobile-timer-warning">
          <span className="timer-icon">⚠️</span>
          <span className="timer-text">
            Starts in {formatCompact(appointment.time_until_start_seconds || 0)}
          </span>
        </div>
      )}
    </div>
  );
};
```

---

## CSS Styling Example

```css
.session-timer {
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.timer-upcoming {
  background: #e3f2fd;
  color: #1976d2;
}

.timer-starting-soon {
  background: #fff3e0;
  color: #f57c00;
  animation: pulse 2s infinite;
}

.timer-in-progress {
  background: #e8f5e9;
  color: #388e3c;
}

.timer-ended {
  background: #f5f5f5;
  color: #757575;
}

.timer-value {
  font-size: 2rem;
  font-weight: bold;
  margin: 10px 0;
}

.timer-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

.btn-join {
  margin-top: 15px;
  padding: 12px 24px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.btn-join:hover {
  background: #45a049;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}
```

---

## Summary

The timer fields provide everything you need for a great user experience:

1. **Countdown before session** - `time_until_start_seconds`
2. **Timer during session** - `time_remaining_seconds`
3. **Session status** - `session_status` for UI state
4. **Join button control** - `can_join_session` for enabling/disabling
5. **Exact times** - `session_start_time` and `session_end_time` for calculations

**Remember**: Update the timer every second on the frontend for smooth countdown, and refresh appointment data every 30 seconds to sync with server time.

