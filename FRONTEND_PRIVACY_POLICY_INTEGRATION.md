# Frontend Integration Guide: Privacy Policy Acceptance

## Overview

This guide shows you how to integrate the Privacy Policy acceptance feature into your React frontend.

---

## 📋 API Endpoints

### 1. Check Privacy Policy Status
```typescript
GET /api/auth/privacy-policy/
Authorization: Bearer <token>

Response:
{
  "accepted": boolean,
  "accepted_date": "2025-11-16T10:30:00Z" | null,
  "version": "1.0" | "",
  "latest_version": "1.0",
  "needs_update": boolean,
  "privacy_policy_url": "https://yourclinic.com.au/privacy-policy"
}
```

### 2. Accept Privacy Policy
```typescript
POST /api/auth/privacy-policy/
Authorization: Bearer <token>

Response:
{
  "message": "Privacy Policy accepted successfully",
  "accepted_date": "2025-11-16T10:30:00Z",
  "version": "1.0",
  "privacy_policy_url": "https://yourclinic.com.au/privacy-policy"
}
```

### 3. Withdraw Consent
```typescript
POST /api/auth/consent/withdraw/
Authorization: Bearer <token>
Content-Type: application/json

Body:
{
  "consent_type": "all" | "treatment" | "data_sharing" | "marketing",
  "reason": "Optional reason for withdrawal"
}

Response:
{
  "message": "Consent withdrawn successfully (marketing)",
  "withdrawn_date": "2025-11-16T10:35:00Z",
  "withdrawal_reason": "No longer wish to receive marketing emails"
}
```

---

## 🔧 Frontend Implementation

### Step 1: Create API Service Functions

Create or update `src/services/api/privacy.ts`:

```typescript
import axiosInstance from './axiosInstance';

export interface PrivacyPolicyStatus {
  accepted: boolean;
  accepted_date: string | null;
  version: string;
  latest_version: string;
  needs_update: boolean;
  privacy_policy_url: string;
}

export interface AcceptPrivacyPolicyResponse {
  message: string;
  accepted_date: string;
  version: string;
  privacy_policy_url: string;
}

export interface WithdrawConsentRequest {
  consent_type: 'all' | 'treatment' | 'data_sharing' | 'marketing';
  reason?: string;
}

export interface WithdrawConsentResponse {
  message: string;
  withdrawn_date: string;
  withdrawal_reason: string;
}

/**
 * Get Privacy Policy acceptance status
 */
export const getPrivacyPolicyStatus = async (): Promise<PrivacyPolicyStatus> => {
  try {
    const response = await axiosInstance.get<PrivacyPolicyStatus>('/api/auth/privacy-policy/');
    return response.data;
  } catch (error: any) {
    console.error('[PrivacyService] Error getting Privacy Policy status:', error);
    
    // Handle specific error cases
    if (error.response) {
      // Server responded with error status
      const status = error.response.status;
      const errorData = error.response.data;
      
      if (status === 401) {
        // Not authenticated - redirect to login
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        throw new Error('Authentication required. Please log in again.');
      } else if (status === 403) {
        // Not a patient
        throw new Error('Only patients can view Privacy Policy status');
      } else if (status === 500) {
        // Server error
        throw new Error(errorData?.error || 'Server error. Please try again later.');
      }
      
      // Return error message from server
      throw new Error(errorData?.error || 'Failed to get Privacy Policy status');
    } else if (error.request) {
      // Request made but no response
      console.error('No response from server:', error.request);
      throw new Error('No response from server. Please check your connection and ensure the backend is running.');
    } else {
      // Something else happened
      console.error('Error setting up request:', error.message);
      throw new Error(`An unexpected error occurred: ${error.message}`);
    }
  }
};

/**
 * Accept Privacy Policy
 */
export const acceptPrivacyPolicy = async (): Promise<AcceptPrivacyPolicyResponse> => {
  try {
    const response = await axiosInstance.post<AcceptPrivacyPolicyResponse>('/api/auth/privacy-policy/');
    return response.data;
  } catch (error: any) {
    console.error('[PrivacyService] Error accepting Privacy Policy:', error);
    
    if (error.response) {
      const status = error.response.status;
      const errorData = error.response.data;
      
      if (status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
        throw new Error('Authentication required. Please log in again.');
      } else if (status === 403) {
        throw new Error('Only patients can accept Privacy Policy');
      } else if (status === 500) {
        throw new Error(errorData?.error || 'Server error. Please try again later.');
      }
      
      throw new Error(errorData?.error || 'Failed to accept Privacy Policy');
    } else if (error.request) {
      throw new Error('No response from server. Please check your connection.');
    } else {
      throw new Error(`An unexpected error occurred: ${error.message}`);
    }
  }
};

/**
 * Withdraw consent
 */
export const withdrawConsent = async (
  consentType: 'all' | 'treatment' | 'data_sharing' | 'marketing',
  reason?: string
): Promise<WithdrawConsentResponse> => {
  const response = await axiosInstance.post<WithdrawConsentResponse>(
    '/api/auth/consent/withdraw/',
    {
      consent_type: consentType,
      reason: reason || '',
    }
  );
  return response.data;
};
```

---

### Step 2: Add Privacy Policy Checkbox to Registration Form

Update your registration form (e.g., `src/pages/auth/Register.tsx`):

```typescript
import React, { useState } from 'react';
import { acceptPrivacyPolicy, getPrivacyPolicyStatus, PrivacyPolicyStatus } from '@/services/api/privacy';

const RegisterPage: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    // ... other fields
  });
  
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [privacyPolicyUrl, setPrivacyPolicyUrl] = useState('');
  const [loading, setLoading] = useState(false);

  // Load Privacy Policy URL on mount
  React.useEffect(() => {
    const loadPrivacyPolicy = async () => {
      try {
        const status = await getPrivacyPolicyStatus();
        setPrivacyPolicyUrl(status.privacy_policy_url);
      } catch (error) {
        console.error('Failed to load Privacy Policy URL:', error);
      }
    };
    loadPrivacyPolicy();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!privacyAccepted) {
      alert('You must accept the Privacy Policy to register');
      return;
    }

    setLoading(true);
    try {
      // 1. Register the user first
      const registerResponse = await registerUser(formData);
      
      // 2. After successful registration, accept Privacy Policy
      if (registerResponse.token) {
        // Set token in axios instance
        axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${registerResponse.token}`;
        
        // Accept Privacy Policy
        await acceptPrivacyPolicy();
      }
      
      // 3. Redirect to dashboard
      navigate('/dashboard');
    } catch (error) {
      console.error('Registration failed:', error);
      alert('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* ... other form fields ... */}
      
      {/* Privacy Policy Acceptance */}
      <div className="mb-4">
        <label className="flex items-start">
          <input
            type="checkbox"
            checked={privacyAccepted}
            onChange={(e) => setPrivacyAccepted(e.target.checked)}
            className="mt-1 mr-2"
            required
          />
          <span className="text-sm">
            I have read and agree to the{' '}
            <a
              href={privacyPolicyUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              Privacy Policy
            </a>
            {' '}(required)
          </span>
        </label>
        {!privacyAccepted && (
          <p className="text-red-500 text-xs mt-1">
            You must accept the Privacy Policy to continue
          </p>
        )}
      </div>

      {/* Data Sharing Consent (Optional) */}
      <div className="mb-4">
        <label className="flex items-start">
          <input
            type="checkbox"
            name="consent_to_data_sharing"
            className="mt-1 mr-2"
          />
          <span className="text-sm">
            I consent to sharing my data with third-party service providers 
            (Twilio for video calls, Stripe for payments) as described in the Privacy Policy
          </span>
        </label>
      </div>

      {/* Marketing Consent (Optional) */}
      <div className="mb-4">
        <label className="flex items-start">
          <input
            type="checkbox"
            name="consent_to_marketing"
            className="mt-1 mr-2"
          />
          <span className="text-sm">
            I would like to receive marketing communications and newsletters
          </span>
        </label>
      </div>

      <button
        type="submit"
        disabled={loading || !privacyAccepted}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:bg-gray-400"
      >
        {loading ? 'Registering...' : 'Register'}
      </button>
    </form>
  );
};

export default RegisterPage;
```

---

### Step 3: Check Privacy Policy Status on Login

Update your login flow to check if Privacy Policy needs to be accepted:

```typescript
// src/pages/auth/Login.tsx or src/hooks/useAuth.ts
import { getPrivacyPolicyStatus } from '@/services/api/privacy';

const useAuth = () => {
  const [privacyPolicyStatus, setPrivacyPolicyStatus] = useState<PrivacyPolicyStatus | null>(null);

  const login = async (email: string, password: string) => {
    try {
      // 1. Login
      const response = await loginUser(email, password);
      
      // 2. Check Privacy Policy status
      const status = await getPrivacyPolicyStatus();
      setPrivacyPolicyStatus(status);
      
      // 3. If not accepted or needs update, redirect to Privacy Policy page
      if (!status.accepted || status.needs_update) {
        return {
          ...response,
          requiresPrivacyPolicy: true,
          privacyPolicyStatus: status,
        };
      }
      
      return response;
    } catch (error) {
      throw error;
    }
  };

  return { login, privacyPolicyStatus };
};
```

---

### Step 4: Create Privacy Policy Acceptance Component

Create `src/components/PrivacyPolicyModal.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import { acceptPrivacyPolicy, getPrivacyPolicyStatus, PrivacyPolicyStatus } from '@/services/api/privacy';

interface PrivacyPolicyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAccept: () => void;
  required?: boolean;
}

const PrivacyPolicyModal: React.FC<PrivacyPolicyModalProps> = ({
  isOpen,
  onClose,
  onAccept,
  required = false,
}) => {
  const [status, setStatus] = useState<PrivacyPolicyStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [accepted, setAccepted] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadStatus();
    }
  }, [isOpen]);

  const loadStatus = async () => {
    try {
      const data = await getPrivacyPolicyStatus();
      setStatus(data);
      setAccepted(data.accepted && !data.needs_update);
    } catch (error) {
      console.error('Failed to load Privacy Policy status:', error);
    }
  };

  const handleAccept = async () => {
    if (!accepted) {
      setLoading(true);
      try {
        await acceptPrivacyPolicy();
        setAccepted(true);
        onAccept();
        onClose();
      } catch (error) {
        console.error('Failed to accept Privacy Policy:', error);
        alert('Failed to accept Privacy Policy. Please try again.');
      } finally {
        setLoading(false);
      }
    } else {
      onClose();
    }
  };

  if (!isOpen || !status) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-2xl max-h-[90vh] overflow-y-auto">
        <h2 className="text-2xl font-bold mb-4">Privacy Policy</h2>
        
        {status.needs_update && (
          <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
            <p className="font-bold">Privacy Policy Updated</p>
            <p className="text-sm">
              The Privacy Policy has been updated. Please review and accept the new version.
            </p>
          </div>
        )}

        <div className="mb-4">
          <p className="text-sm text-gray-600 mb-2">
            Version: {status.latest_version}
            {status.accepted && (
              <span className="ml-2 text-green-600">
                (Previously accepted: {status.version})
              </span>
            )}
          </p>
          
          <iframe
            src={status.privacy_policy_url}
            className="w-full h-96 border border-gray-300 rounded"
            title="Privacy Policy"
          />
        </div>

        <div className="mb-4">
          <label className="flex items-start">
            <input
              type="checkbox"
              checked={accepted}
              onChange={(e) => setAccepted(e.target.checked)}
              className="mt-1 mr-2"
            />
            <span className="text-sm">
              I have read and agree to the Privacy Policy (required)
            </span>
          </label>
        </div>

        <div className="flex justify-end gap-2">
          {!required && (
            <button
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-100"
            >
              Cancel
            </button>
          )}
          <button
            onClick={handleAccept}
            disabled={!accepted || loading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? 'Accepting...' : 'Accept Privacy Policy'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicyModal;
```

---

### Step 5: Add Privacy Policy Check to Protected Routes

Update your route protection (e.g., `src/components/ProtectedRoute.tsx`):

```typescript
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getPrivacyPolicyStatus } from '@/services/api/privacy';
import PrivacyPolicyModal from './PrivacyPolicyModal';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const [showPrivacyModal, setShowPrivacyModal] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token');
      if (!token) {
        navigate('/login');
        return;
      }

      try {
        // Check Privacy Policy status
        const status = await getPrivacyPolicyStatus();
        
        if (!status.accepted || status.needs_update) {
          setShowPrivacyModal(true);
        } else {
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        navigate('/login');
      }
    };

    checkAuth();
  }, [navigate]);

  const handlePrivacyAccept = () => {
    setShowPrivacyModal(false);
    setIsAuthenticated(true);
  };

  if (!isAuthenticated) {
    return (
      <>
        {showPrivacyModal && (
          <PrivacyPolicyModal
            isOpen={showPrivacyModal}
            onClose={() => navigate('/login')}
            onAccept={handlePrivacyAccept}
            required={true}
          />
        )}
      </>
    );
  }

  return <>{children}</>;
};

export default ProtectedRoute;
```

---

### Step 6: Add Consent Management to Settings

Create `src/pages/settings/ConsentSettings.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import { withdrawConsent } from '@/services/api/privacy';

const ConsentSettings: React.FC = () => {
  const [withdrawing, setWithdrawing] = useState(false);
  const [withdrawType, setWithdrawType] = useState<'all' | 'treatment' | 'data_sharing' | 'marketing'>('marketing');
  const [reason, setReason] = useState('');

  const handleWithdraw = async () => {
    if (!confirm('Are you sure you want to withdraw consent? This may affect your ability to use certain services.')) {
      return;
    }

    setWithdrawing(true);
    try {
      await withdrawConsent(withdrawType, reason);
      alert('Consent withdrawn successfully');
      // Refresh user data or redirect
    } catch (error) {
      console.error('Failed to withdraw consent:', error);
      alert('Failed to withdraw consent. Please try again.');
    } finally {
      setWithdrawing(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4">Consent Management</h2>
      
      <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
        <p className="font-bold">Important</p>
        <p className="text-sm">
          Withdrawing consent may affect your ability to use certain services. 
          Please contact us if you have questions.
        </p>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">
          Select consent to withdraw:
        </label>
        <select
          value={withdrawType}
          onChange={(e) => setWithdrawType(e.target.value as any)}
          className="w-full border border-gray-300 rounded px-3 py-2"
        >
          <option value="marketing">Marketing Communications</option>
          <option value="data_sharing">Data Sharing with Third Parties</option>
          <option value="treatment">Treatment Consent</option>
          <option value="all">All Consents</option>
        </select>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">
          Reason (optional):
        </label>
        <textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          className="w-full border border-gray-300 rounded px-3 py-2"
          rows={3}
          placeholder="Please let us know why you're withdrawing consent..."
        />
      </div>

      <button
        onClick={handleWithdraw}
        disabled={withdrawing}
        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:bg-gray-400"
      >
        {withdrawing ? 'Processing...' : 'Withdraw Consent'}
      </button>
    </div>
  );
};

export default ConsentSettings;
```

---

## 📝 Summary of Frontend Changes

### Required Changes:

1. ✅ **Registration Form**
   - Add Privacy Policy checkbox (required)
   - Add data sharing consent checkbox (optional)
   - Add marketing consent checkbox (optional)
   - Accept Privacy Policy after successful registration

2. ✅ **Login Flow**
   - Check Privacy Policy status after login
   - Redirect to Privacy Policy acceptance if needed

3. ✅ **Protected Routes**
   - Check Privacy Policy status before allowing access
   - Show Privacy Policy modal if not accepted

4. ✅ **Settings Page**
   - Add consent management section
   - Allow users to withdraw consent

### Optional Enhancements:

- Privacy Policy status indicator in header
- Notification when Privacy Policy is updated
- Consent history/log in user profile
- Privacy Policy version comparison view

---

## 🧪 Testing Checklist

- [ ] User can accept Privacy Policy during registration
- [ ] User cannot register without accepting Privacy Policy
- [ ] User is prompted to accept Privacy Policy on login if not accepted
- [ ] User is notified when Privacy Policy is updated
- [ ] User can view Privacy Policy status in settings
- [ ] User can withdraw consent
- [ ] Withdrawn consent prevents access to related services

---

## 📚 API Integration Summary

```typescript
// 1. Check status
GET /api/auth/privacy-policy/

// 2. Accept Privacy Policy
POST /api/auth/privacy-policy/

// 3. Withdraw consent
POST /api/auth/consent/withdraw/
Body: { consent_type: string, reason?: string }
```

All endpoints require authentication (Bearer token).

---

## 🚀 Quick Start

1. Copy the API service functions to your `src/services/api/privacy.ts`
2. Add Privacy Policy checkbox to registration form
3. Add Privacy Policy check to protected routes
4. Test the flow end-to-end

That's it! Your frontend is now integrated with the Privacy Policy compliance system.

