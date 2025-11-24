# Privacy Policy Setup Guide

## ✅ Backend (Already Done)

The backend has complete privacy policy functionality:
- ✅ Database models for tracking acceptance
- ✅ API endpoints for GET/POST privacy policy
- ✅ Third-party data sharing disclosure
- ✅ Consent withdrawal system
- ✅ GDPR-compliant data export

## 🔧 What You Need to Do

### 1. Update Backend Environment Variables

SSH into your droplet and edit the `.env` file:

```bash
sudo nano /var/www/clink-backend/.env
```

Add these lines:

```bash
# Privacy Policy & Compliance
PRIVACY_POLICY_VERSION=1.0
PRIVACY_POLICY_URL=https://tailoredpsychology.com.au/privacy-policy
CONSENT_FORM_VERSION=1.0
TELEHEALTH_CONSENT_VERSION=1.0
```

Restart Gunicorn:

```bash
sudo systemctl restart gunicorn
```

### 2. Create Privacy Policy Document

Use the template at `PRIVACY_POLICY_TEMPLATE.md` and fill in:

- `[Your Clinic Name]` → Tailored Psychology
- `[privacy@yourclinic.com.au]` → Your actual email
- `[Address]` → Your clinic address
- `[Phone Number]` → Your phone number
- `[DATE]` → Today's date

**IMPORTANT:** Have a legal professional review this before publishing!

### 3. Create Frontend Privacy Policy Page

Create a static page in your React frontend at:

```
/src/pages/PrivacyPolicy.tsx
```

Display the privacy policy text with proper formatting.

**Route:** `https://tailoredpsychology.com.au/privacy-policy`

### 4. Implement Privacy Policy Acceptance in Frontend

When users register, show them the privacy policy and require acceptance.

**API Endpoints (already working):**

#### Check Privacy Policy Status
```bash
GET https://api.tailoredpsychology.com.au/api/auth/privacy-policy/
Authorization: Bearer <token>

Response:
{
  "accepted": false,
  "accepted_date": null,
  "version": "",
  "latest_version": "1.0",
  "needs_update": true,
  "privacy_policy_url": "https://tailoredpsychology.com.au/privacy-policy",
  "third_party_data_sharing": {
    "twilio": {
      "name": "Twilio",
      "purpose": "Video calls and SMS/WhatsApp notifications",
      "data_shared": ["name", "phone", "email"],
      "location": "United States",
      "privacy_policy_url": "https://www.twilio.com/legal/privacy",
      "safeguards": [
        "Encrypted transmission",
        "GDPR compliant",
        "SOC 2 certified"
      ],
      "active": true
    },
    "stripe": {
      "name": "Stripe",
      "purpose": "Payment processing",
      "data_shared": ["name", "email", "payment information"],
      "location": "United States",
      "privacy_policy_url": "https://stripe.com/au/privacy",
      "safeguards": [
        "PCI DSS Level 1 compliant",
        "Encrypted transmission"
      ],
      "active": true
    }
  }
}
```

#### Accept Privacy Policy
```bash
POST https://api.tailoredpsychology.com.au/api/auth/privacy-policy/
Authorization: Bearer <token>

Response:
{
  "message": "Privacy Policy accepted successfully",
  "accepted_date": "2025-11-24T12:00:00Z",
  "version": "1.0",
  "privacy_policy_url": "https://tailoredpsychology.com.au/privacy-policy"
}
```

### 5. Frontend Implementation Example

```typescript
// src/services/privacyService.ts
import axiosInstance from './axiosInstance';

export const privacyService = {
  async getPrivacyPolicyStatus() {
    const response = await axiosInstance.get('/auth/privacy-policy/');
    return response.data;
  },

  async acceptPrivacyPolicy() {
    const response = await axiosInstance.post('/auth/privacy-policy/');
    return response.data;
  },
};
```

```tsx
// src/components/PrivacyPolicyModal.tsx
import { useState } from 'react';
import { privacyService } from '../services/privacyService';

export default function PrivacyPolicyModal({ onAccept }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAccept = async () => {
    setLoading(true);
    setError('');
    try {
      await privacyService.acceptPrivacyPolicy();
      onAccept();
    } catch (err) {
      setError('Failed to accept privacy policy. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal">
      <h2>Privacy Policy</h2>
      <div className="privacy-content">
        {/* Display privacy policy text */}
        <p>Read the full policy at: 
          <a href="https://tailoredpsychology.com.au/privacy-policy" target="_blank">
            Privacy Policy
          </a>
        </p>
      </div>
      
      {error && <div className="error">{error}</div>}
      
      <button onClick={handleAccept} disabled={loading}>
        {loading ? 'Accepting...' : 'I Accept'}
      </button>
    </div>
  );
}
```

### 6. Test the System

#### Test Privacy Policy Status
```bash
# Get a JWT token first (login)
TOKEN="your_jwt_token_here"

# Check privacy policy status
curl -H "Authorization: Bearer $TOKEN" \
  https://api.tailoredpsychology.com.au/api/auth/privacy-policy/
```

#### Test Privacy Policy Acceptance
```bash
# Accept privacy policy
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  https://api.tailoredpsychology.com.au/api/auth/privacy-policy/
```

## 📋 Checklist

- [ ] Update `.env` file on droplet with privacy policy URL
- [ ] Restart Gunicorn service
- [ ] Create privacy policy document (use template)
- [ ] Have legal professional review privacy policy
- [ ] Create privacy policy page on frontend (`/privacy-policy`)
- [ ] Add privacy policy acceptance during registration
- [ ] Add link to privacy policy in footer
- [ ] Test API endpoints work correctly
- [ ] Test frontend shows privacy policy correctly
- [ ] Test acceptance tracking works

## 🔗 Related Documentation

- `PRIVACY_POLICY_TEMPLATE.md` - Privacy policy template
- `FRONTEND_PRIVACY_POLICY_INTEGRATION.md` - Frontend integration guide
- `COMPLIANCE_IMPLEMENTATION_PROGRESS.md` - Compliance features overview
- `THIRD_PARTY_DATA_SHARING_COMPLETE.md` - Third-party data sharing details

## 📞 Support

If you have questions about privacy compliance, consult with:
- A privacy lawyer familiar with Australian Privacy Act 1988
- Office of the Australian Information Commissioner (OAIC): https://www.oaic.gov.au

