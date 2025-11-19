# Frontend Guide: Data Access Request Feature

## When Patients Use This Feature

### Common Use Cases

1. **Privacy Rights (APP 12)**
   - Patient wants to see all data you have about them
   - Required by Australian Privacy Act 1988
   - Patients have the right to access their information

2. **Data Portability**
   - Patient wants to switch clinics
   - Patient wants to keep a copy of their records
   - Patient wants to share data with another healthcare provider

3. **Verification**
   - Patient wants to verify what information is stored
   - Patient wants to check if data is accurate
   - Patient wants to review their consent records

4. **Legal/Insurance**
   - Patient needs records for insurance claims
   - Patient needs records for legal purposes
   - Patient needs proof of treatment

5. **Personal Records**
   - Patient wants to keep personal health records
   - Patient wants to track their treatment history
   - Patient wants to review their progress

---

## Where to Add in Frontend

### 1. Patient Dashboard / Settings Page

**Best Location:** Patient Settings or Privacy Settings section

```typescript
// In Patient Settings Page
<div className="privacy-settings">
  <h2>Privacy & Data</h2>
  
  <div className="data-access-card">
    <h3>Request Your Data</h3>
    <p>
      Under Australian Privacy Act 1988 (APP 12), you have the right to 
      access all personal information we hold about you.
    </p>
    <button onClick={handleRequestData}>
      Download My Data
    </button>
  </div>
</div>
```

### 2. Privacy Policy Page

**Add a section about data access rights:**

```typescript
// In Privacy Policy Page
<section className="data-rights">
  <h2>Your Data Rights</h2>
  <p>
    You have the right to access your personal information at any time.
  </p>
  <button onClick={handleRequestData}>
    Request My Data
  </button>
</section>
```

### 3. Account Settings / Profile Page

**Add to account management section:**

```typescript
// In Account Settings
<div className="account-section">
  <h3>Data Management</h3>
  <div className="data-actions">
    <button onClick={handleRequestData}>
      📥 Download My Data
    </button>
    <p className="help-text">
      Get a complete copy of all your information
    </p>
  </div>
</div>
```

### 4. Footer Link (Optional)

**Add to website footer for easy access:**

```typescript
// In Footer
<footer>
  <div className="privacy-links">
    <Link to="/privacy-policy">Privacy Policy</Link>
    <button onClick={handleRequestData}>Request My Data</button>
  </div>
</footer>
```

---

## Implementation Example

### Complete React Component

```typescript
import React, { useState } from 'react';
import axios from 'axios';

const DataAccessRequest = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleRequestData = async () => {
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        '/api/auth/data-access-request/',
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      // Download as JSON file
      const dataStr = JSON.stringify(response.data.data, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `my-data-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      setSuccess(true);
      setTimeout(() => setSuccess(false), 5000);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to download data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="data-access-request">
      <div className="card">
        <h3>📥 Download My Data</h3>
        <p>
          Request a complete copy of all your personal information, including:
        </p>
        <ul>
          <li>Personal information and profile</li>
          <li>All appointments</li>
          <li>Progress notes</li>
          <li>Billing and payment history</li>
          <li>Consent records</li>
        </ul>
        
        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}
        
        {success && (
          <div className="alert alert-success">
            ✅ Data downloaded successfully!
          </div>
        )}
        
        <button
          onClick={handleRequestData}
          disabled={loading}
          className="btn btn-primary"
        >
          {loading ? 'Downloading...' : 'Download My Data'}
        </button>
        
        <p className="help-text">
          This is your right under Australian Privacy Act 1988 (APP 12)
        </p>
      </div>
    </div>
  );
};

export default DataAccessRequest;
```

---

## UI/UX Best Practices

### 1. Make it Easy to Find
- ✅ Add to Settings/Privacy section
- ✅ Use clear button text: "Download My Data" or "Request My Data"
- ✅ Add icon: 📥 or 🔒

### 2. Explain Why
- ✅ Explain it's their legal right (APP 12)
- ✅ List what data is included
- ✅ Show it's secure and private

### 3. Show Status
- ✅ Loading state while downloading
- ✅ Success message when complete
- ✅ Error handling if it fails

### 4. Format Options (Future Enhancement)
```typescript
// Future: Allow format selection
<div className="format-options">
  <label>Download Format:</label>
  <select>
    <option value="json">JSON (Complete Data)</option>
    <option value="pdf">PDF (Readable Format)</option>
  </select>
</div>
```

---

## When to Show This Feature

### Always Available
- ✅ In patient settings (always visible)
- ✅ In privacy policy page
- ✅ In account management

### Contextual Triggers
- ✅ When patient asks about their data
- ✅ When patient wants to switch clinics
- ✅ When patient needs records for insurance
- ✅ When patient is reviewing privacy settings

---

## Example User Flow

1. **Patient goes to Settings**
   ```
   Dashboard → Settings → Privacy & Data
   ```

2. **Patient clicks "Download My Data"**
   ```
   Button click → API call → Download JSON file
   ```

3. **Patient receives file**
   ```
   File: my-data-2025-11-16.json
   Contains: All patient information
   ```

4. **Patient can use the data**
   - Share with other healthcare providers
   - Keep for personal records
   - Review for accuracy
   - Use for insurance/legal purposes

---

## Quick Implementation Checklist

- [ ] Add button to Patient Settings page
- [ ] Add to Privacy Policy page
- [ ] Create DataAccessRequest component
- [ ] Handle loading states
- [ ] Handle success/error messages
- [ ] Test download functionality
- [ ] Add help text explaining APP 12 rights
- [ ] Style the component to match your design

---

## That's It!

This feature is **required by law** (APP 12), so make sure it's:
- ✅ Easy to find
- ✅ Easy to use
- ✅ Clearly explained
- ✅ Working correctly

Your patients have the right to access their data - make it simple for them!

