# 🛡️ Frontend Guide: Privacy Policy & Third-Party Data Sharing Display

This guide shows how to display the Privacy Policy and third-party data sharing information in your frontend.

---

## 🔑 API Endpoints

| Method | Endpoint | Description | Who |
|--------|----------|-------------|-----|
| `GET` | `/api/auth/privacy-policy/` | Get Privacy Policy status + third-party info | Patient |
| `POST` | `/api/auth/privacy-policy/` | Accept Privacy Policy | Patient |
| `GET` | `/api/auth/third-party-data-sharing/` | Get third-party data sharing disclosure | Authenticated |

---

## 📦 Service Layer

```typescript
// src/services/privacyService.ts
import axiosInstance from './axiosInstance';

export const PrivacyService = {
  async getPrivacyPolicyStatus() {
    const response = await axiosInstance.get('privacy-policy/');
    return response.data;
  },

  async acceptPrivacyPolicy() {
    const response = await axiosInstance.post('privacy-policy/');
    return response.data;
  },

  async getThirdPartyDataSharing() {
    const response = await axiosInstance.get('third-party-data-sharing/');
    return response.data;
  },
};
```

---

## 🎨 React Components

### Privacy Policy Status Component

```tsx
// components/PrivacyPolicyStatus.tsx
import { useEffect, useState } from 'react';
import { PrivacyService } from '../services/privacyService';

interface ThirdPartyService {
  name: string;
  purpose: string;
  data_shared: string[];
  location: string;
  privacy_policy_url: string;
  safeguards: string[];
  active: boolean;
}

export default function PrivacyPolicyStatus() {
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      setLoading(true);
      const data = await PrivacyService.getPrivacyPolicyStatus();
      setStatus(data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load Privacy Policy status');
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async () => {
    try {
      await PrivacyService.acceptPrivacyPolicy();
      await loadStatus();
      alert('Privacy Policy accepted successfully!');
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to accept Privacy Policy');
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="privacy-policy-section">
      <h2>Privacy Policy</h2>
      
      <div className="status-card">
        <h3>Current Status</h3>
        <p>
          Status: {status.accepted ? '✅ Accepted' : '❌ Not Accepted'}
        </p>
        {status.accepted && (
          <p>Accepted on: {new Date(status.accepted_date).toLocaleDateString()}</p>
        )}
        <p>Version: {status.version || 'None'}</p>
        <p>Latest Version: {status.latest_version}</p>
        
        {status.needs_update && (
          <div className="warning">
            ⚠️ Privacy Policy has been updated. Please review and accept the new version.
          </div>
        )}
      </div>

      <div className="actions">
        <a 
          href={status.privacy_policy_url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="btn btn-secondary"
        >
          📄 Read Privacy Policy
        </a>
        
        {(!status.accepted || status.needs_update) && (
          <button onClick={handleAccept} className="btn btn-primary">
            ✅ Accept Privacy Policy
          </button>
        )}
      </div>

      {/* Third-Party Data Sharing */}
      {status.third_party_data_sharing && Object.keys(status.third_party_data_sharing).length > 0 && (
        <div className="third-party-section">
          <h3>Third-Party Data Sharing</h3>
          <p className="info">
            We share your information with the following third-party services to provide our services:
          </p>
          
          {Object.entries(status.third_party_data_sharing).map(([key, service]: [string, ThirdPartyService]) => (
            <div key={key} className="third-party-card">
              <h4>{service.name}</h4>
              <p><strong>Purpose:</strong> {service.purpose}</p>
              <p><strong>Location:</strong> {service.location}</p>
              <p><strong>Data Shared:</strong> {service.data_shared.join(', ')}</p>
              
              <div className="safeguards">
                <strong>Safeguards:</strong>
                <ul>
                  {service.safeguards.map((safeguard, idx) => (
                    <li key={idx}>{safeguard}</li>
                  ))}
                </ul>
              </div>
              
              <a 
                href={service.privacy_policy_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="link"
              >
                View {service.name} Privacy Policy →
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Third-Party Data Sharing Component

```tsx
// components/ThirdPartyDataSharing.tsx
import { useEffect, useState } from 'react';
import { PrivacyService } from '../services/privacyService';

export default function ThirdPartyDataSharing() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const response = await PrivacyService.getThirdPartyDataSharing();
      setData(response);
    } catch (err) {
      console.error('Failed to load third-party data sharing info:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!data) return null;

  return (
    <div className="third-party-disclosure">
      <h2>Third-Party Data Sharing Disclosure</h2>
      <p className="note">{data.note}</p>
      <p>Total Active Services: {data.total_active_services}</p>
      
      <div className="services-list">
        {Object.entries(data.third_parties).map(([key, service]: [string, any]) => (
          <div key={key} className="service-card">
            <h3>{service.name}</h3>
            <div className="service-details">
              <p><strong>Purpose:</strong> {service.purpose}</p>
              <p><strong>Location:</strong> {service.location}</p>
              <p><strong>Data Shared:</strong></p>
              <ul>
                {service.data_shared.map((field: string, idx: number) => (
                  <li key={idx}>{field}</li>
                ))}
              </ul>
              
              <p><strong>Security Safeguards:</strong></p>
              <ul>
                {service.safeguards.map((safeguard: string, idx: number) => (
                  <li key={idx}>{safeguard}</li>
                ))}
              </ul>
              
              <a 
                href={service.privacy_policy_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="btn btn-link"
              >
                View Privacy Policy →
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🎯 Usage Examples

### In Registration Flow

```tsx
// components/RegistrationForm.tsx
function RegistrationForm() {
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [thirdPartyInfo, setThirdPartyInfo] = useState<any>(null);

  useEffect(() => {
    // Load third-party info before showing consent
    PrivacyService.getThirdPartyDataSharing()
      .then(data => setThirdPartyInfo(data));
  }, []);

  return (
    <form>
      {/* Registration fields */}
      
      <div className="privacy-consent">
        <label>
          <input 
            type="checkbox" 
            checked={privacyAccepted}
            onChange={e => setPrivacyAccepted(e.target.checked)}
            required
          />
          I have read and accept the{' '}
          <a href="/privacy-policy" target="_blank">Privacy Policy</a>
        </label>
        
        {thirdPartyInfo && (
          <details className="third-party-info">
            <summary>View Third-Party Data Sharing</summary>
            <ThirdPartyDataSharing data={thirdPartyInfo} />
          </details>
        )}
      </div>
      
      <button 
        type="submit" 
        disabled={!privacyAccepted}
      >
        Register
      </button>
    </form>
  );
}
```

### In Account Settings

```tsx
// pages/AccountSettings.tsx
function AccountSettings() {
  return (
    <div>
      <h1>Account Settings</h1>
      
      <section>
        <PrivacyPolicyStatus />
      </section>
      
      <section>
        <ThirdPartyDataSharing />
      </section>
    </div>
  );
}
```

---

## 📋 Response Format

### Privacy Policy Status

```typescript
interface PrivacyPolicyStatus {
  accepted: boolean;
  accepted_date: string | null;
  version: string;
  latest_version: string;
  needs_update: boolean;
  privacy_policy_url: string;
  third_party_data_sharing: {
    [key: string]: ThirdPartyService;
  };
}
```

### Third-Party Service

```typescript
interface ThirdPartyService {
  name: string;
  purpose: string;
  data_shared: string[];
  location: string;
  privacy_policy_url: string;
  safeguards: string[];
  active: boolean;
}
```

---

## ✅ Best Practices

1. **Show Before Registration:**
   - Display Privacy Policy and third-party info before user registers
   - Require explicit acceptance

2. **Easy Access:**
   - Link to Privacy Policy in footer
   - Show in account settings
   - Include in registration/login flows

3. **Clear Disclosure:**
   - Use simple language
   - Highlight third-party services
   - Show safeguards clearly

4. **Version Management:**
   - Notify users when policy updates
   - Require re-acceptance for major changes
   - Show version history

---

## 🎨 UI Suggestions

### Privacy Policy Modal

```tsx
function PrivacyPolicyModal({ isOpen, onClose, onAccept }) {
  const [status, setStatus] = useState(null);
  
  return (
    <Modal isOpen={isOpen} onClose={onClose}>
      <h2>Privacy Policy</h2>
      
      <iframe 
        src={status?.privacy_policy_url} 
        style={{ width: '100%', height: '400px' }}
      />
      
      <div className="third-party-summary">
        <h3>Third-Party Services</h3>
        <p>We use {status?.third_party_data_sharing?.length || 0} third-party services:</p>
        <ul>
          {Object.values(status?.third_party_data_sharing || {}).map((service: any) => (
            <li key={service.name}>
              {service.name} - {service.purpose}
            </li>
          ))}
        </ul>
      </div>
      
      <div className="actions">
        <button onClick={onClose}>Cancel</button>
        <button onClick={onAccept} className="primary">
          I Accept
        </button>
      </div>
    </Modal>
  );
}
```

---

## 📚 Related Documentation

- [Privacy Policy Template](PRIVACY_POLICY_TEMPLATE.md)
- [Third-Party Data Sharing Complete](THIRD_PARTY_DATA_SHARING_COMPLETE.md)
- [Privacy Policy Acceptance API](FRONTEND_PRIVACY_POLICY_INTEGRATION.md)

---

**Last Updated:** November 19, 2025

