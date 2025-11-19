# Frontend Guide: AHPRA Registration Number Validation

## Overview

The backend now has **enhanced AHPRA registration number validation** with stricter format requirements. This guide explains what changed and how to update your frontend.

---

## What Changed

### Before
- Basic validation (just checked if it exists)
- Accepted various formats
- No normalization

### After
- **Strict format validation**: Must be exactly `3 letters + 10 digits`
- **Format**: `PSY0001234567` (for psychologists)
- **Automatic normalization**: Backend removes spaces/dashes and converts to uppercase
- **Better error messages**: Clear, specific error messages

---

## Validation Rules

### Format Requirements
- **3 uppercase letters** (profession code)
  - Psychologists: Must start with `PSY`
  - Other professions: MED, NUR, PHY, etc.
- **10 digits** (registration number)
- **Total length**: 13 characters

### Valid Examples
```
PSY0001234567
PSY 0001 234 567    (spaces will be removed)
PSY-0001-234-567    (dashes will be removed)
psy0001234567       (will be converted to uppercase)
```

### Invalid Examples
```
PSY123              ❌ Too short
PSY00012345678      ❌ Too long
MED0001234567       ❌ Wrong profession code for psychologist
PSY00012345AB       ❌ Contains letters in number part
1234567890          ❌ Missing profession code
```

---

## Backend Error Messages

The backend now returns specific error messages:

### Format Error
```json
{
  "error": "Invalid AHPRA registration number format. Expected format: 3 letters (e.g., PSY) followed by 10 digits (e.g., PSY0001234567)"
}
```

### Profession Code Error
```json
{
  "error": "Psychologists must have an AHPRA number starting with 'PSY'"
}
```

### Missing Field Error
```json
{
  "error": "AHPRA registration number is required for psychologists"
}
```

---

## Frontend Implementation

### 1. Input Validation (Client-Side)

Add client-side validation to provide immediate feedback:

```typescript
// Validation function
function validateAHPRA(ahpraNumber: string, role: string = 'psychologist'): {
  isValid: boolean;
  error?: string;
  normalized?: string;
} {
  if (!ahpraNumber) {
    return { isValid: false, error: 'AHPRA registration number is required' };
  }

  // Remove spaces, dashes, underscores and convert to uppercase
  const cleaned = ahpraNumber.replace(/[\s\-_]/g, '').toUpperCase();

  // Check format: 3 letters + 10 digits
  const pattern = /^[A-Z]{3}[0-9]{10}$/;
  if (!pattern.test(cleaned)) {
    return {
      isValid: false,
      error: 'Invalid format. Expected: 3 letters (e.g., PSY) followed by 10 digits (e.g., PSY0001234567)'
    };
  }

  // Check profession code for psychologists
  if (role === 'psychologist' && !cleaned.startsWith('PSY')) {
    return {
      isValid: false,
      error: 'Psychologists must have an AHPRA number starting with PSY'
    };
  }

  return { isValid: true, normalized: cleaned };
}
```

### 2. Input Formatting (Optional but Recommended)

Add input masking to help users enter the correct format:

```typescript
// React component with input formatting
import React, { useState } from 'react';

function AHPRAInput({ value, onChange, role = 'psychologist' }) {
  const [displayValue, setDisplayValue] = useState(value || '');

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    let input = e.target.value;
    
    // Remove all non-alphanumeric characters
    input = input.replace(/[^A-Za-z0-9]/g, '');
    
    // Convert to uppercase
    input = input.toUpperCase();
    
    // Limit to 13 characters (3 letters + 10 digits)
    if (input.length > 13) {
      input = input.substring(0, 13);
    }
    
    // Auto-format: Add space after 3 letters if user is typing
    let formatted = input;
    if (input.length > 3) {
      formatted = input.substring(0, 3) + ' ' + input.substring(3);
    }
    
    setDisplayValue(formatted);
    onChange(input); // Send cleaned value to parent
  };

  const handleBlur = () => {
    // Validate on blur
    const validation = validateAHPRA(displayValue.replace(/\s/g, ''), role);
    if (!validation.isValid) {
      // Show error message
      console.error(validation.error);
    }
  };

  return (
    <div>
      <input
        type="text"
        value={displayValue}
        onChange={handleChange}
        onBlur={handleBlur}
        placeholder="PSY 0001234567"
        maxLength={14} // 3 letters + space + 10 digits
        style={{
          textTransform: 'uppercase',
          letterSpacing: '0.1em'
        }}
      />
      <small>Format: PSY followed by 10 digits (e.g., PSY0001234567)</small>
    </div>
  );
}
```

### 3. Error Handling

Update your error handling to display the new error messages:

```typescript
// Error handling example
async function createPsychologist(userData: {
  email: string;
  password: string;
  full_name: string;
  ahpra_registration_number: string;
  ahpra_expiry_date: string;
}) {
  try {
    // Client-side validation first
    const validation = validateAHPRA(userData.ahpra_registration_number, 'psychologist');
    if (!validation.isValid) {
      throw new Error(validation.error);
    }

    // Send to backend
    const response = await fetch('/api/auth/admin/create-user/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        ...userData,
        role: 'psychologist',
        // Backend will normalize, but you can send cleaned value
        ahpra_registration_number: validation.normalized
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to create psychologist');
    }

    return await response.json();
  } catch (error) {
    // Display error to user
    console.error('Error creating psychologist:', error.message);
    // Show error in UI
    setError(error.message);
  }
}
```

### 4. Form Component Example

Complete form example with validation:

```typescript
import React, { useState } from 'react';

function PsychologistRegistrationForm() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    ahpra_registration_number: '',
    ahpra_expiry_date: ''
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const handleAHPRAChange = (value: string) => {
    // Clean input
    const cleaned = value.replace(/[\s\-_]/g, '').toUpperCase();
    
    setFormData(prev => ({
      ...prev,
      ahpra_registration_number: cleaned
    }));

    // Validate
    const validation = validateAHPRA(cleaned, 'psychologist');
    if (validation.isValid) {
      setErrors(prev => ({ ...prev, ahpra_registration_number: '' }));
    } else {
      setErrors(prev => ({ ...prev, ahpra_registration_number: validation.error }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    try {
      // Final validation
      const validation = validateAHPRA(formData.ahpra_registration_number, 'psychologist');
      if (!validation.isValid) {
        setErrors({ ahpra_registration_number: validation.error });
        setLoading(false);
        return;
      }

      await createPsychologist({
        ...formData,
        ahpra_registration_number: validation.normalized || formData.ahpra_registration_number
      });

      // Success - redirect or show success message
      alert('Psychologist created successfully!');
    } catch (error: any) {
      // Handle backend errors
      if (error.message.includes('AHPRA')) {
        setErrors({ ahpra_registration_number: error.message });
      } else {
        setErrors({ general: error.message });
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>AHPRA Registration Number *</label>
        <input
          type="text"
          value={formData.ahpra_registration_number}
          onChange={(e) => handleAHPRAChange(e.target.value)}
          placeholder="PSY0001234567"
          maxLength={13}
          style={{ textTransform: 'uppercase' }}
        />
        {errors.ahpra_registration_number && (
          <div className="error">{errors.ahpra_registration_number}</div>
        )}
        <small>Format: PSY followed by 10 digits (e.g., PSY0001234567)</small>
      </div>

      {/* Other form fields... */}

      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create Psychologist'}
      </button>

      {errors.general && (
        <div className="error">{errors.general}</div>
      )}
    </form>
  );
}
```

---

## Where to Update

### 1. Admin User Creation Form
- **Location**: Admin panel where admins create psychologists
- **Update**: Add AHPRA validation and formatting
- **File**: Likely `AdminCreateUserForm.tsx` or similar

### 2. Psychologist Profile Update Form
- **Location**: Where psychologists update their profile
- **Update**: Add validation when updating AHPRA number
- **File**: Likely `PsychologistProfileForm.tsx` or similar

### 3. Psychologist Registration Form (if applicable)
- **Location**: If psychologists can self-register
- **Update**: Add validation during registration
- **File**: Likely `PsychologistRegistrationForm.tsx` or similar

---

## Testing Checklist

- [ ] Valid format: `PSY0001234567` - Should accept
- [ ] Valid with spaces: `PSY 0001 234 567` - Should accept (backend normalizes)
- [ ] Valid with dashes: `PSY-0001-234-567` - Should accept (backend normalizes)
- [ ] Invalid: Too short `PSY123` - Should show error
- [ ] Invalid: Too long `PSY00012345678` - Should show error
- [ ] Invalid: Wrong code `MED0001234567` - Should show error for psychologists
- [ ] Invalid: Contains letters `PSY00012345AB` - Should show error
- [ ] Empty field - Should show "required" error
- [ ] Backend error messages display correctly

---

## Backward Compatibility

### Good News
- **Backend normalizes input automatically** - You can send any format (with spaces/dashes), and the backend will clean it
- **Existing data**: If you have existing AHPRA numbers in the database, they will be validated on the next update
- **No breaking changes**: The API endpoints remain the same, just better validation

### What You Should Do
1. **Add client-side validation** (optional but recommended for better UX)
2. **Update error handling** to show the new error messages
3. **Consider adding input formatting** to help users enter correct format

---

## Summary

### Required Updates
- ✅ **Error handling**: Update to display new error messages
- ✅ **Validation**: Add client-side validation (optional but recommended)

### Optional Updates
- ⭐ **Input formatting**: Add input masking/formatting for better UX
- ⭐ **Real-time validation**: Show validation errors as user types

### No Changes Needed
- ✅ API endpoints (same URLs, same request format)
- ✅ Request/response structure (same JSON format)
- ✅ Authentication (no changes)

---

## Questions?

If you encounter any issues:
1. Check the error message from the backend (it's now more specific)
2. Ensure AHPRA number is exactly 13 characters (3 letters + 10 digits)
3. For psychologists, ensure it starts with `PSY`
4. Backend will normalize spaces/dashes automatically, but client-side validation improves UX

---

**Last Updated**: 2025-11-19  
**Status**: ✅ Ready for Frontend Integration

