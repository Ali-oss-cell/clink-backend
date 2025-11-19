# Frontend Integration Guide - Session Recordings

## Overview

This guide explains how to integrate the session recording functionality into your React TypeScript frontend. The backend provides three endpoints for accessing recordings with proper access controls.

---

## 📋 Table of Contents

1. [API Service Layer](#1-api-service-layer)
2. [TypeScript Interfaces](#2-typescript-interfaces)
3. [React Hooks](#3-react-hooks)
4. [UI Components](#4-ui-components)
5. [Integration Points](#5-integration-points)
6. [Example Usage](#6-example-usage)

---

## 1. API Service Layer

### Create/Update: `src/services/api/recordings.ts`

```typescript
import axiosInstance from './axiosInstance';

/**
 * Session Recording API Service
 * Handles all recording-related API calls
 */

export interface SessionRecording {
  id: number;
  appointment_id: number;
  recording_sid: string;
  media_uri: string;
  media_external_location?: string;
  duration: number;
  duration_formatted: string;
  size: number;
  size_formatted: string;
  status: 'started' | 'completed' | 'failed';
  status_display: string;
  participant_identity?: string;
  created_at: string;
  completed_at?: string;
  patient_name: string;
  psychologist_name: string;
}

export interface SessionRecordingListItem {
  id: number;
  recording_sid: string;
  appointment_date: string;
  patient_name: string;
  psychologist_name: string;
  duration: number;
  duration_formatted: string;
  size: number;
  size_formatted: string;
  status: 'started' | 'completed' | 'failed';
  created_at: string;
  completed_at?: string;
}

export interface RecordingDownloadResponse {
  recording_id: number;
  appointment_id: number;
  download_url: string;
  external_location?: string;
  duration: number;
  size: number;
  size_formatted: string;
  duration_formatted: string;
  created_at: string;
  completed_at?: string;
  note: string;
}

export interface RecordingsListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: SessionRecordingListItem[];
}

class RecordingService {
  /**
   * Get recording for a specific appointment
   * @param appointmentId - Appointment ID
   * @returns Recording details
   */
  async getRecordingByAppointment(appointmentId: number): Promise<SessionRecording> {
    const response = await axiosInstance.get<SessionRecording>(
      `/appointments/${appointmentId}/recording/`
    );
    return response.data;
  }

  /**
   * List all recordings accessible to current user
   * @param page - Page number (default: 1)
   * @param pageSize - Items per page (default: 20)
   * @returns Paginated list of recordings
   */
  async listRecordings(
    page: number = 1,
    pageSize: number = 20
  ): Promise<RecordingsListResponse> {
    const response = await axiosInstance.get<RecordingsListResponse>(
      '/appointments/recordings/',
      {
        params: {
          page,
          page_size: pageSize,
        },
      }
    );
    return response.data;
  }

  /**
   * Get download URL for a recording
   * @param recordingId - Recording ID
   * @returns Download URL and metadata
   */
  async getDownloadUrl(recordingId: number): Promise<RecordingDownloadResponse> {
    const response = await axiosInstance.get<RecordingDownloadResponse>(
      `/appointments/recordings/${recordingId}/download/`
    );
    return response.data;
  }

  /**
   * Download recording file
   * Note: This opens the download URL in a new window
   * For direct download, you may need to proxy through backend
   * @param recordingId - Recording ID
   */
  async downloadRecording(recordingId: number): Promise<void> {
    const downloadData = await this.getDownloadUrl(recordingId);
    window.open(downloadData.download_url, '_blank');
  }
}

export const recordingService = new RecordingService();
```

---

## 2. TypeScript Interfaces

### Add to: `src/types/recordings.ts`

```typescript
export type RecordingStatus = 'started' | 'completed' | 'failed';

export interface SessionRecording {
  id: number;
  appointment_id: number;
  recording_sid: string;
  media_uri: string;
  media_external_location?: string;
  duration: number;
  duration_formatted: string;
  size: number;
  size_formatted: string;
  status: RecordingStatus;
  status_display: string;
  participant_identity?: string;
  created_at: string;
  completed_at?: string;
  patient_name: string;
  psychologist_name: string;
}

export interface SessionRecordingListItem {
  id: number;
  recording_sid: string;
  appointment_date: string;
  patient_name: string;
  psychologist_name: string;
  duration: number;
  duration_formatted: string;
  size: number;
  size_formatted: string;
  status: RecordingStatus;
  created_at: string;
  completed_at?: string;
}

export interface RecordingDownloadResponse {
  recording_id: number;
  appointment_id: number;
  download_url: string;
  external_location?: string;
  duration: number;
  size: number;
  size_formatted: string;
  duration_formatted: string;
  created_at: string;
  completed_at?: string;
  note: string;
}

export interface RecordingsListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: SessionRecordingListItem[];
}
```

---

## 3. React Hooks

### Create: `src/hooks/useRecordings.ts`

```typescript
import { useState, useEffect } from 'react';
import { recordingService, SessionRecording, SessionRecordingListItem, RecordingsListResponse } from '../services/api/recordings';

/**
 * Hook to fetch recording for a specific appointment
 */
export function useAppointmentRecording(appointmentId: number | null) {
  const [recording, setRecording] = useState<SessionRecording | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!appointmentId) {
      setRecording(null);
      return;
    }

    const fetchRecording = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await recordingService.getRecordingByAppointment(appointmentId);
        setRecording(data);
      } catch (err: any) {
        if (err.response?.status === 404) {
          setError('No recording found for this appointment');
        } else {
          setError(err.response?.data?.error || 'Failed to load recording');
        }
        setRecording(null);
      } finally {
        setLoading(false);
      }
    };

    fetchRecording();
  }, [appointmentId]);

  return { recording, loading, error, refetch: () => fetchRecording() };
}

/**
 * Hook to list all recordings with pagination
 */
export function useRecordingsList(page: number = 1, pageSize: number = 20) {
  const [data, setData] = useState<RecordingsListResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecordings = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await recordingService.listRecordings(page, pageSize);
        setData(response);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to load recordings');
        setData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchRecordings();
  }, [page, pageSize]);

  const refetch = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await recordingService.listRecordings(page, pageSize);
      setData(response);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load recordings');
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, refetch };
}

/**
 * Hook to download a recording
 */
export function useRecordingDownload() {
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const download = async (recordingId: number) => {
    setDownloading(true);
    setError(null);
    try {
      await recordingService.downloadRecording(recordingId);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to download recording');
      throw err;
    } finally {
      setDownloading(false);
    }
  };

  return { download, downloading, error };
}
```

---

## 4. UI Components

### Component 1: Recording Card (for list view)

### Create: `src/components/recordings/RecordingCard.tsx`

```typescript
import React from 'react';
import { SessionRecordingListItem } from '../../types/recordings';
import { format } from 'date-fns';

interface RecordingCardProps {
  recording: SessionRecordingListItem;
  onView?: (recordingId: number) => void;
  onDownload?: (recordingId: number) => void;
}

export const RecordingCard: React.FC<RecordingCardProps> = ({
  recording,
  onView,
  onDownload,
}) => {
  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'MMM dd, yyyy h:mm a');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'started':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Session Recording
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            {formatDate(recording.appointment_date)}
          </p>
        </div>
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(
            recording.status
          )}`}
        >
          {recording.status_display || recording.status}
        </span>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex items-center text-sm text-gray-600">
          <span className="font-medium mr-2">Patient:</span>
          <span>{recording.patient_name}</span>
        </div>
        <div className="flex items-center text-sm text-gray-600">
          <span className="font-medium mr-2">Psychologist:</span>
          <span>{recording.psychologist_name}</span>
        </div>
        <div className="flex items-center text-sm text-gray-600">
          <span className="font-medium mr-2">Duration:</span>
          <span>{recording.duration_formatted}</span>
        </div>
        <div className="flex items-center text-sm text-gray-600">
          <span className="font-medium mr-2">Size:</span>
          <span>{recording.size_formatted}</span>
        </div>
      </div>

      <div className="flex gap-2">
        {onView && (
          <button
            onClick={() => onView(recording.id)}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            View Details
          </button>
        )}
        {onDownload && recording.status === 'completed' && (
          <button
            onClick={() => onDownload(recording.id)}
            className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
          >
            Download
          </button>
        )}
      </div>
    </div>
  );
};
```

### Component 2: Recording List Page

### Create: `src/pages/RecordingsPage.tsx` (or add to existing page)

```typescript
import React, { useState } from 'react';
import { useRecordingsList, useRecordingDownload } from '../hooks/useRecordings';
import { RecordingCard } from '../components/recordings/RecordingCard';
import { SessionRecordingListItem } from '../types/recordings';

export const RecordingsPage: React.FC = () => {
  const [page, setPage] = useState(1);
  const pageSize = 20;
  const { data, loading, error, refetch } = useRecordingsList(page, pageSize);
  const { download, downloading } = useRecordingDownload();

  const handleView = (recordingId: number) => {
    // Navigate to recording detail page or open modal
    console.log('View recording:', recordingId);
  };

  const handleDownload = async (recordingId: number) => {
    try {
      await download(recordingId);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  if (loading && !data) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-500">Loading recordings...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
        <button
          onClick={() => refetch()}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Session Recordings</h1>

      {data && data.results.length === 0 ? (
        <div className="bg-gray-50 rounded-lg p-8 text-center">
          <p className="text-gray-500">No recordings found.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            {data?.results.map((recording) => (
              <RecordingCard
                key={recording.id}
                recording={recording}
                onView={handleView}
                onDownload={handleDownload}
              />
            ))}
          </div>

          {/* Pagination */}
          {data && data.count > pageSize && (
            <div className="flex justify-between items-center mt-6">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={!data.previous}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300"
              >
                Previous
              </button>
              <span className="text-gray-600">
                Page {page} of {Math.ceil(data.count / pageSize)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={!data.next}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};
```

### Component 3: Recording Detail Modal/Page

### Create: `src/components/recordings/RecordingDetailModal.tsx`

```typescript
import React from 'react';
import { SessionRecording } from '../types/recordings';
import { format } from 'date-fns';
import { useRecordingDownload } from '../../hooks/useRecordings';

interface RecordingDetailModalProps {
  recording: SessionRecording;
  onClose: () => void;
}

export const RecordingDetailModal: React.FC<RecordingDetailModalProps> = ({
  recording,
  onClose,
}) => {
  const { download, downloading } = useRecordingDownload();

  const handleDownload = async () => {
    try {
      await download(recording.id);
    } catch (error) {
      console.error('Download failed:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Recording Details</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-500">Appointment Date</label>
              <p className="text-gray-900">
                {format(new Date(recording.created_at), 'MMM dd, yyyy h:mm a')}
              </p>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Patient</label>
              <p className="text-gray-900">{recording.patient_name}</p>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Psychologist</label>
              <p className="text-gray-900">{recording.psychologist_name}</p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Duration</label>
                <p className="text-gray-900">{recording.duration_formatted}</p>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">File Size</label>
                <p className="text-gray-900">{recording.size_formatted}</p>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Status</label>
              <p className="text-gray-900">{recording.status_display}</p>
            </div>

            {recording.completed_at && (
              <div>
                <label className="text-sm font-medium text-gray-500">Completed At</label>
                <p className="text-gray-900">
                  {format(new Date(recording.completed_at), 'MMM dd, yyyy h:mm a')}
                </p>
              </div>
            )}
          </div>

          <div className="mt-6 flex gap-3">
            {recording.status === 'completed' && (
              <button
                onClick={handleDownload}
                disabled={downloading}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {downloading ? 'Downloading...' : 'Download Recording'}
              </button>
            )}
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
```

### Component 4: Add Recording Link to Appointment Detail

### Update: `src/pages/patient/PatientAppointmentDetailPage.tsx` (or similar)

```typescript
import { useAppointmentRecording } from '../../hooks/useRecordings';
import { RecordingDetailModal } from '../../components/recordings/RecordingDetailModal';

// Inside your component:
const { recording, loading: recordingLoading, error: recordingError } = 
  useAppointmentRecording(appointmentId);

// In your JSX, add a section to show recording:
{recording && (
  <div className="mt-6 p-4 bg-blue-50 rounded-lg">
    <h3 className="text-lg font-semibold mb-2">Session Recording</h3>
    <p className="text-sm text-gray-600 mb-3">
      A recording of this session is available.
    </p>
    <button
      onClick={() => setShowRecordingModal(true)}
      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
    >
      View Recording
    </button>
  </div>
)}

{recordingError && recordingError !== 'No recording found for this appointment' && (
  <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded">
    <p className="text-sm text-red-800">{recordingError}</p>
  </div>
)}

{showRecordingModal && recording && (
  <RecordingDetailModal
    recording={recording}
    onClose={() => setShowRecordingModal(false)}
  />
)}
```

---

## 5. Integration Points

### A. Add to Navigation Menu

Add a "Recordings" link to your navigation:

```typescript
// In your navigation component
<NavLink to="/recordings">Session Recordings</NavLink>
```

### B. Add Route

```typescript
// In your router configuration
<Route path="/recordings" element={<RecordingsPage />} />
```

### C. Show Recording Status in Appointment List

Update your appointment list/card component to show if a recording exists:

```typescript
const { recording } = useAppointmentRecording(appointment.id);

{recording && (
  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
    📹 Recording Available
  </span>
)}
```

---

## 6. Example Usage

### Complete Example: Patient Viewing Their Recording

```typescript
import React, { useState } from 'react';
import { useAppointmentRecording } from '../hooks/useRecordings';
import { RecordingDetailModal } from '../components/recordings/RecordingDetailModal';

export const AppointmentDetailWithRecording: React.FC<{ appointmentId: number }> = ({
  appointmentId,
}) => {
  const [showModal, setShowModal] = useState(false);
  const { recording, loading, error } = useAppointmentRecording(appointmentId);

  return (
    <div>
      {/* Your appointment details here */}
      
      {/* Recording Section */}
      {loading && <p>Checking for recording...</p>}
      
      {error && error !== 'No recording found for this appointment' && (
        <div className="text-red-600">{error}</div>
      )}
      
      {recording && (
        <div className="mt-4 p-4 border rounded-lg">
          <h3>Session Recording Available</h3>
          <button onClick={() => setShowModal(true)}>
            View Recording Details
          </button>
        </div>
      )}
      
      {showModal && recording && (
        <RecordingDetailModal
          recording={recording}
          onClose={() => setShowModal(false)}
        />
      )}
    </div>
  );
};
```

---

## 7. Important Notes

### Access Control
- The backend automatically filters recordings based on user role
- Patients only see their own recordings
- Psychologists only see recordings of their sessions
- Practice Managers/Admins see all recordings

### Error Handling
- Handle 404 errors gracefully (no recording exists)
- Handle 403 errors (permission denied)
- Show appropriate messages to users

### Download URLs
- Twilio URLs may require authentication
- Consider implementing a proxy endpoint if direct access fails
- Test download functionality thoroughly

### Recording Status
- Only show download button for `completed` recordings
- Show appropriate status indicators
- Handle `started` and `failed` states

---

## 8. Testing Checklist

- [ ] List recordings page loads correctly
- [ ] Pagination works
- [ ] Recording card displays all information
- [ ] View details modal opens and displays correctly
- [ ] Download button works (opens Twilio URL)
- [ ] Error states are handled gracefully
- [ ] Loading states are shown
- [ ] Access control works (patients see only their recordings)
- [ ] Recording appears in appointment detail page
- [ ] Status indicators show correctly

---

## 9. Optional Enhancements

1. **Video Player Integration**: If you want to play recordings directly in the app, you'll need to:
   - Use a video player library (e.g., Video.js, React Player)
   - Handle Twilio authentication for video URLs
   - Consider proxying through backend for security

2. **Recording Search/Filter**: Add filters for:
   - Date range
   - Patient name
   - Psychologist name
   - Status

3. **Bulk Download**: Allow downloading multiple recordings at once

4. **Recording Analytics**: Show statistics:
   - Total recordings
   - Total duration
   - Storage used

---

**Last Updated**: January 19, 2025
**Status**: Ready for Frontend Implementation

