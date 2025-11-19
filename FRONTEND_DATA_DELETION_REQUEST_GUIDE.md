# 🛡️ Frontend Guide: Data Deletion Request (APP 13)

This guide shows how to integrate the new backend endpoints that let patients request deletion of their personal information and lets admins review those requests.

---

## 🔑 API Endpoints

| Method | Endpoint | Description | Who |
|--------|----------|-------------|-----|
| `POST` | `/api/auth/data-deletion-request/` | Create a deletion request | Patient |
| `GET` | `/api/auth/data-deletion-request/` | Fetch current request (if any) | Patient |
| `DELETE` | `/api/auth/data-deletion-request/{id}/cancel/` | Cancel a request | Patient |
| `GET` | `/api/auth/data-deletion-requests/?status=` | List requests | Admin / Practice Manager |
| `POST` | `/api/auth/data-deletion-requests/{id}/review/` | Approve or reject | Admin / Practice Manager |

> All endpoints require `Authorization: Bearer <token>` and live under your existing axios instance (`/api/auth/`).

---

## 📦 Service Layer (auth.ts)

```ts
// src/services/auth.ts
import axiosInstance from './axiosInstance';

export const DataDeletionService = {
  async requestDeletion(reason?: string) {
    const res = await axiosInstance.post('data-deletion-request/', { reason });
    return res.data;
  },

  async getDeletionStatus() {
    const res = await axiosInstance.get('data-deletion-request/');
    return res.data;
  },

  async cancelDeletion(requestId: number) {
    const res = await axiosInstance.delete(`data-deletion-request/${requestId}/cancel/`);
    return res.data;
  },

  async listDeletionRequests(status?: string) {
    const res = await axiosInstance.get('data-deletion-requests/', {
      params: status ? { status } : undefined,
    });
    return res.data;
  },

  async reviewDeletionRequest(requestId: number, payload: {
    action: 'approve' | 'reject';
    rejection_reason?: string;
    rejection_notes?: string;
    notes?: string;
  }) {
    const res = await axiosInstance.post(`data-deletion-requests/${requestId}/review/`, payload);
    return res.data;
  },
};
```

---

## 🧑‍⚕️ Patient UI Example

```tsx
// components/PatientDeletionRequestCard.tsx
import { useEffect, useState } from 'react';
import { DataDeletionService } from '../services/auth';

export default function PatientDeletionRequestCard() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [reason, setReason] = useState('');
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const data = await DataDeletionService.getDeletionStatus();
      setStatus(data);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  const handleRequest = async () => {
    setLoading(true);
    try {
      await DataDeletionService.requestDeletion(reason);
      setReason('');
      await fetchStatus();
    } catch (err: any) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = async () => {
    if (!status?.request?.id) return;
    setLoading(true);
    try {
      await DataDeletionService.cancelDeletion(status.request.id);
      await fetchStatus();
    } catch (err: any) {
      setError(err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <h3>Request Data Deletion</h3>
      {error && <p className="error">{error}</p>}

      {!status?.has_request && (
        <div>
          <textarea
            value={reason}
            onChange={e => setReason(e.target.value)}
            placeholder="Optional reason"
          />
          <button onClick={handleRequest} disabled={loading}>
            {loading ? 'Submitting…' : 'Submit Request'}
          </button>
        </div>
      )}

      {status?.has_request && (
        <div className="request-status">
          <p>Status: {status.request.status}</p>
          <p>Scheduled deletion: {status.request.scheduled_deletion_date || 'TBD'}</p>
          {['pending', 'approved'].includes(status.request.status) && (
            <button onClick={handleCancel} disabled={loading}>
              Cancel Request
            </button>
          )}
        </div>
      )}
    </section>
  );
}
```

---

## 🧑‍💼 Admin/Practice Manager UI

```tsx
// components/AdminDeletionRequestsTable.tsx
import { useEffect, useState } from 'react';
import { DataDeletionService } from '../services/auth';

export default function AdminDeletionRequestsTable() {
  const [requests, setRequests] = useState<any[]>([]);
  const [filter, setFilter] = useState<string>('pending');

  const load = async () => {
    const data = await DataDeletionService.listDeletionRequests(filter || undefined);
    setRequests(data.requests || []);
  };

  useEffect(() => {
    load();
  }, [filter]);

  const review = async (id: number, action: 'approve' | 'reject') => {
    const payload: any = { action };
    if (action === 'reject') {
      payload.rejection_reason = 'legal_retention';
      payload.rejection_notes = 'Retention period not met';
    }
    await DataDeletionService.reviewDeletionRequest(id, payload);
    await load();
  };

  return (
    <section>
      <h3>Data Deletion Requests</h3>
      <select value={filter} onChange={e => setFilter(e.target.value)}>
        <option value="">All</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="rejected">Rejected</option>
        <option value="completed">Completed</option>
      </select>

      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Patient</th>
            <th>Status</th>
            <th>Earliest Deletion</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {requests.map(req => (
            <tr key={req.id}>
              <td>{req.id}</td>
              <td>{req.patient_email}</td>
              <td>{req.status}</td>
              <td>{req.earliest_deletion_date?.slice(0, 10) || 'N/A'}</td>
              <td>
                {req.status === 'pending' && (
                  <>
                    <button onClick={() => review(req.id, 'approve')}>Approve</button>
                    <button onClick={() => review(req.id, 'reject')}>Reject</button>
                  </>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
```

---

## 🧪 Testing Flow

1. Login as a patient → call `requestDeletion()`
2. Login as admin → call `listDeletionRequests()` → `reviewDeletionRequest()`
3. Wait for Celery to mark approved requests as `completed`

For local testing without Celery, manually set `status = approved` and `scheduled_deletion_date = now` in Django admin, then run:
```bash
python manage.py shell
>>> from users.tasks import process_approved_deletion_requests
>>> process_approved_deletion_requests()
```

---

## ✅ UX Suggestions

- Show clear warnings (“Deletion is permanent after legal retention period”)
- Disable submit button when a pending request exists
- Surface `earliest_deletion_date`, `scheduled_deletion_date`, and status
- Send toast notifications on success/errors

---

## 📎 Notes

- Only patients can create/cancel requests
- Only admins/practice managers can review
- Backend enforces retention policy & legal blockers (unpaid invoices, active appointments)
- All actions are audit-logged

Need design assets or copy suggestions? Let me know!
