# 🚀 Psychology Clinic React TypeScript Frontend Guide

## 📋 **Complete Frontend Structure Based on User Journey**

### **🏗️ Enhanced Project Structure**

```
psychology_clinic_frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Header/
│   │   │   ├── Footer/
│   │   │   ├── Layout/
│   │   │   ├── LoadingSpinner/
│   │   │   └── ProtectedRoute/
│   │   ├── auth/
│   │   │   ├── Login/
│   │   │   ├── PatientRegistration/
│   │   │   └── ForgotPassword/
│   │   ├── intake/
│   │   │   ├── IntakeForm/
│   │   │   ├── PersonalDetails/
│   │   │   ├── EmergencyContact/
│   │   │   ├── ReferralInfo/
│   │   │   ├── MedicalHistory/
│   │   │   ├── PresentingConcerns/
│   │   │   └── ConsentAgreement/
│   │   ├── dashboard/
│   │   │   ├── PatientDashboard/
│   │   │   ├── PsychologistDashboard/
│   │   │   └── ManagerDashboard/
│   │   ├── appointments/
│   │   │   ├── BookingForm/
│   │   │   ├── BookingCalendar/
│   │   │   ├── ServiceSelector/
│   │   │   ├── PsychologistSelector/
│   │   │   └── AppointmentHistory/
│   │   ├── video/
│   │   │   ├── TwilioVideoCall/
│   │   │   ├── VideoControls/
│   │   │   └── VideoSession/
│   │   ├── progress/
│   │   │   ├── SOAPNoteForm/
│   │   │   ├── ProgressNotesList/
│   │   │   └── PatientProgress/
│   │   └── payment/
│   │       ├── PaymentForm/
│   │       ├── StripeElements/
│   │       └── InvoiceHistory/
│   ├── pages/
│   │   ├── public/
│   │   │   ├── Homepage.tsx
│   │   │   ├── About.tsx
│   │   │   ├── Services.tsx
│   │   │   ├── Resources.tsx
│   │   │   ├── Contact.tsx
│   │   │   └── FAQs.tsx
│   │   ├── auth/
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   └── ForgotPasswordPage.tsx
│   │   ├── patient/
│   │   │   ├── PatientDashboardPage.tsx
│   │   │   ├── IntakeFormPage.tsx
│   │   │   ├── BookAppointmentPage.tsx
│   │   │   ├── AppointmentHistoryPage.tsx
│   │   │   ├── VideoSessionPage.tsx
│   │   │   └── ProfilePage.tsx
│   │   ├── psychologist/
│   │   │   ├── PsychologistDashboardPage.tsx
│   │   │   ├── SchedulePage.tsx
│   │   │   ├── PatientsPage.tsx
│   │   │   ├── ProgressNotesPage.tsx
│   │   │   └── VideoSessionPage.tsx
│   │   └── manager/
│   │       ├── ManagerDashboardPage.tsx
│   │       ├── UserManagementPage.tsx
│   │       ├── AppointmentOverviewPage.tsx
│   │       └── BillingDashboardPage.tsx
│   ├── services/
│   │   ├── api/
│   │   │   ├── auth.ts
│   │   │   ├── users.ts
│   │   │   ├── appointments.ts
│   │   │   ├── billing.ts
│   │   │   ├── services.ts
│   │   │   └── progressNotes.ts
│   │   ├── twilio/
│   │   │   └── videoService.ts
│   │   ├── stripe/
│   │   │   └── paymentService.ts
│   │   └── whatsapp/
│   │       └── notificationService.ts
│   ├── store/
│   │   ├── slices/
│   │   │   ├── authSlice.ts
│   │   │   ├── userSlice.ts
│   │   │   ├── appointmentSlice.ts
│   │   │   └── intakeSlice.ts
│   │   └── index.ts
│   ├── types/
│   │   ├── auth.ts
│   │   ├── user.ts
│   │   ├── appointment.ts
│   │   ├── intake.ts
│   │   ├── progressNote.ts
│   │   └── api.ts
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   ├── useIntakeForm.ts
│   │   └── useAppointmentBooking.ts
│   ├── utils/
│   │   ├── constants.ts
│   │   ├── validators.ts
│   │   ├── formatters.ts
│   │   └── dateHelpers.ts
│   └── assets/
│       ├── images/
│       ├── icons/
│       └── styles/
└── public/
```

---

## 🔧 **TypeScript Type Definitions**

### **src/types/auth.ts**
```typescript
export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: 'patient' | 'psychologist' | 'practice_manager' | 'admin';
  phone_number?: string;
  date_of_birth?: string;
  is_verified: boolean;
  created_at: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  tokens: AuthTokens;
}

export interface PatientRegistrationRequest {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  phone_number?: string;
  date_of_birth?: string;
}
```

### **src/types/intake.ts**
```typescript
export interface IntakeFormData {
  // Personal Details
  first_name: string;
  last_name: string;
  preferred_name?: string;
  date_of_birth: string;
  gender_identity?: string;
  pronouns?: string;
  phone_number: string;
  email: string;
  address_line_1: string;
  suburb: string;
  state: string;
  postcode: string;
  medicare_number?: string;

  // Emergency Contact
  emergency_contact_name?: string;
  emergency_contact_relationship?: string;
  emergency_contact_phone?: string;

  // Referral Information
  referral_source?: string;
  has_gp_referral: boolean;
  gp_name?: string;
  gp_practice_name?: string;

  // Medical History
  previous_therapy: boolean;
  previous_therapy_details?: string;
  current_medications?: string;
  medical_conditions?: string;

  // Presenting Concerns
  presenting_concerns?: string;
  therapy_goals?: string;

  // Consent
  consent_to_treatment: boolean;
  consent_to_telehealth: boolean;
  intake_completed: boolean;
}

export interface IntakeStep {
  id: number;
  title: string;
  completed: boolean;
  fields: string[];
}
```

### **src/types/appointment.ts**
```typescript
export interface Psychologist {
  id: number;
  user: User;
  title: string;
  display_name: string;
  qualifications: string;
  specializations: string[];
  years_experience: number;
  consultation_fee: number;
  is_accepting_new_patients: boolean;
  bio?: string;
  profile_image?: string;
}

export interface Service {
  id: number;
  name: string;
  service_type: 'individual' | 'couples' | 'family' | 'group' | 'assessment';
  description: string;
  duration_minutes: number;
  standard_fee: number;
  medicare_rebate: number;
  out_of_pocket_cost: number;
}

export interface AppointmentBooking {
  service: number;
  psychologist: number;
  appointment_date: string;
  appointment_time: string;
  session_type: 'in_person' | 'telehealth';
  notes?: string;
}

export interface Appointment {
  id: number;
  patient: User;
  psychologist: Psychologist;
  service: Service;
  appointment_datetime: string;
  session_type: 'in_person' | 'telehealth';
  status: 'scheduled' | 'completed' | 'cancelled' | 'no_show';
  video_room_id?: string;
  notes?: string;
}
```

---

## 🌐 **API Service Layer**

### **src/services/api/auth.ts**
```typescript
import axios from 'axios';
import { LoginRequest, LoginResponse, PatientRegistrationRequest } from '../../types/auth';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const authAPI = axios.create({
  baseURL: `${API_BASE_URL}/api/auth`,
});

// Request interceptor to add auth token
authAPI.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle token refresh
authAPI.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Handle token refresh logic
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh/`, {
            refresh: refreshToken,
          });
          localStorage.setItem('access_token', response.data.access);
          return authAPI.request(error.config);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await authAPI.post('/login/', credentials);
    return response.data;
  },

  registerPatient: async (data: PatientRegistrationRequest): Promise<LoginResponse> => {
    const response = await authAPI.post('/register/patient/', data);
    return response.data;
  },

  refreshToken: async (refresh: string): Promise<{ access: string }> => {
    const response = await authAPI.post('/refresh/', { refresh });
    return response.data;
  },

  logout: async (): Promise<void> => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await authAPI.get('/profile/');
    return response.data;
  },
};
```

### **src/services/api/intake.ts**
```typescript
import { authAPI } from './auth';
import { IntakeFormData } from '../../types/intake';

export const intakeService = {
  getIntakeForm: async (): Promise<IntakeFormData> => {
    const response = await authAPI.get('/intake-form/');
    return response.data;
  },

  updateIntakeForm: async (data: Partial<IntakeFormData>): Promise<IntakeFormData> => {
    const response = await authAPI.put('/intake-form/', data);
    return response.data;
  },

  submitIntakeForm: async (data: IntakeFormData): Promise<{ message: string }> => {
    const response = await authAPI.put('/intake-form/', {
      ...data,
      intake_completed: true,
    });
    return response.data;
  },
};
```

---

## 🏗️ **Key React Components**

### **src/components/auth/PatientRegistration/PatientRegistration.tsx**
```typescript
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch } from '../../../hooks/useAppDispatch';
import { authService } from '../../../services/api/auth';
import { setAuth } from '../../../store/slices/authSlice';
import { PatientRegistrationRequest } from '../../../types/auth';
import styles from './PatientRegistration.module.scss';

export const PatientRegistration: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState<PatientRegistrationRequest>({
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    phone_number: '',
    date_of_birth: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrors({});

    try {
      const response = await authService.registerPatient(formData);
      
      // Store tokens and user data
      localStorage.setItem('access_token', response.tokens.access);
      localStorage.setItem('refresh_token', response.tokens.refresh);
      localStorage.setItem('user', JSON.stringify(response.user));
      
      // Update Redux store
      dispatch(setAuth({
        user: response.user,
        tokens: response.tokens,
        isAuthenticated: true,
      }));

      // Redirect to intake form
      navigate('/patient/intake-form');
    } catch (error: any) {
      setErrors(error.response?.data || { general: 'Registration failed' });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className={styles.registrationContainer}>
      <div className={styles.registrationCard}>
        <h1>Create Your Patient Account</h1>
        <p>Start your journey to better mental health</p>

        <form onSubmit={handleSubmit} className={styles.form}>
          <div className={styles.formGroup}>
            <label htmlFor="first_name">First Name *</label>
            <input
              type="text"
              id="first_name"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              required
              className={errors.first_name ? styles.error : ''}
            />
            {errors.first_name && <span className={styles.errorText}>{errors.first_name}</span>}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="last_name">Last Name *</label>
            <input
              type="text"
              id="last_name"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              required
              className={errors.last_name ? styles.error : ''}
            />
            {errors.last_name && <span className={styles.errorText}>{errors.last_name}</span>}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="email">Email Address *</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className={errors.email ? styles.error : ''}
            />
            {errors.email && <span className={styles.errorText}>{errors.email}</span>}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="phone_number">Phone Number (Australian format)</label>
            <input
              type="tel"
              id="phone_number"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleChange}
              placeholder="+61412345678 or 0412345678"
              className={errors.phone_number ? styles.error : ''}
            />
            {errors.phone_number && <span className={styles.errorText}>{errors.phone_number}</span>}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="date_of_birth">Date of Birth</label>
            <input
              type="date"
              id="date_of_birth"
              name="date_of_birth"
              value={formData.date_of_birth}
              onChange={handleChange}
              className={errors.date_of_birth ? styles.error : ''}
            />
            {errors.date_of_birth && <span className={styles.errorText}>{errors.date_of_birth}</span>}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="password">Password *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              minLength={8}
              className={errors.password ? styles.error : ''}
            />
            {errors.password && <span className={styles.errorText}>{errors.password}</span>}
          </div>

          <div className={styles.formGroup}>
            <label htmlFor="password_confirm">Confirm Password *</label>
            <input
              type="password"
              id="password_confirm"
              name="password_confirm"
              value={formData.password_confirm}
              onChange={handleChange}
              required
              className={errors.password_confirm ? styles.error : ''}
            />
            {errors.password_confirm && <span className={styles.errorText}>{errors.password_confirm}</span>}
          </div>

          {errors.general && <div className={styles.generalError}>{errors.general}</div>}

          <button
            type="submit"
            disabled={loading}
            className={styles.submitButton}
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <p className={styles.loginLink}>
          Already have an account? <a href="/login">Sign in here</a>
        </p>
      </div>
    </div>
  );
};
```

### **src/components/intake/IntakeForm/IntakeForm.tsx**
```typescript
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { intakeService } from '../../../services/api/intake';
import { IntakeFormData, IntakeStep } from '../../../types/intake';
import { PersonalDetails } from '../PersonalDetails/PersonalDetails';
import { EmergencyContact } from '../EmergencyContact/EmergencyContact';
import { ReferralInfo } from '../ReferralInfo/ReferralInfo';
import { MedicalHistory } from '../MedicalHistory/MedicalHistory';
import { PresentingConcerns } from '../PresentingConcerns/PresentingConcerns';
import { ConsentAgreement } from '../ConsentAgreement/ConsentAgreement';
import styles from './IntakeForm.module.scss';

const INTAKE_STEPS: IntakeStep[] = [
  { id: 1, title: 'Personal Details', completed: false, fields: ['first_name', 'last_name', 'email'] },
  { id: 2, title: 'Emergency Contact', completed: false, fields: ['emergency_contact_name'] },
  { id: 3, title: 'Referral Information', completed: false, fields: ['referral_source'] },
  { id: 4, title: 'Medical History', completed: false, fields: ['previous_therapy'] },
  { id: 5, title: 'Presenting Concerns', completed: false, fields: ['presenting_concerns'] },
  { id: 6, title: 'Consent & Agreement', completed: false, fields: ['consent_to_treatment'] },
];

export const IntakeForm: React.FC = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState<IntakeFormData>({} as IntakeFormData);
  const [steps, setSteps] = useState(INTAKE_STEPS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadExistingData();
  }, []);

  const loadExistingData = async () => {
    try {
      const existingData = await intakeService.getIntakeForm();
      setFormData(existingData);
      
      // Update step completion status
      const updatedSteps = steps.map(step => ({
        ...step,
        completed: step.fields.every(field => 
          existingData[field as keyof IntakeFormData] !== undefined &&
          existingData[field as keyof IntakeFormData] !== ''
        ),
      }));
      setSteps(updatedSteps);
    } catch (error) {
      console.error('Failed to load intake form data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStepData = async (stepData: Partial<IntakeFormData>) => {
    const updatedData = { ...formData, ...stepData };
    setFormData(updatedData);

    try {
      await intakeService.updateIntakeForm(stepData);
    } catch (error) {
      console.error('Failed to save step data:', error);
    }
  };

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    try {
      await intakeService.submitIntakeForm(formData);
      navigate('/patient/dashboard');
    } catch (error) {
      console.error('Failed to submit intake form:', error);
    }
  };

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return <PersonalDetails data={formData} onUpdate={handleStepData} />;
      case 2:
        return <EmergencyContact data={formData} onUpdate={handleStepData} />;
      case 3:
        return <ReferralInfo data={formData} onUpdate={handleStepData} />;
      case 4:
        return <MedicalHistory data={formData} onUpdate={handleStepData} />;
      case 5:
        return <PresentingConcerns data={formData} onUpdate={handleStepData} />;
      case 6:
        return <ConsentAgreement data={formData} onUpdate={handleStepData} />;
      default:
        return null;
    }
  };

  if (loading) {
    return <div className={styles.loading}>Loading intake form...</div>;
  }

  return (
    <div className={styles.intakeContainer}>
      <div className={styles.progressBar}>
        {steps.map((step, index) => (
          <div
            key={step.id}
            className={`${styles.step} ${
              currentStep === step.id ? styles.active : ''
            } ${step.completed ? styles.completed : ''}`}
          >
            <div className={styles.stepNumber}>{step.id}</div>
            <div className={styles.stepTitle}>{step.title}</div>
          </div>
        ))}
      </div>

      <div className={styles.formContainer}>
        <div className={styles.stepContent}>
          {renderCurrentStep()}
        </div>

        <div className={styles.navigation}>
          {currentStep > 1 && (
            <button
              type="button"
              onClick={handlePrevious}
              className={styles.previousButton}
            >
              Previous
            </button>
          )}

          {currentStep < steps.length ? (
            <button
              type="button"
              onClick={handleNext}
              className={styles.nextButton}
            >
              Next
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSubmit}
              className={styles.submitButton}
            >
              Complete Intake Form
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
```

---

## 🎯 **State Management (Redux Toolkit)**

### **src/store/slices/authSlice.ts**
```typescript
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { User, AuthTokens } from '../../types/auth';

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  loading: boolean;
}

const initialState: AuthState = {
  user: null,
  tokens: null,
  isAuthenticated: false,
  loading: true,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setAuth: (state, action: PayloadAction<{
      user: User;
      tokens: AuthTokens;
      isAuthenticated: boolean;
    }>) => {
      state.user = action.payload.user;
      state.tokens = action.payload.tokens;
      state.isAuthenticated = action.payload.isAuthenticated;
      state.loading = false;
    },
    clearAuth: (state) => {
      state.user = null;
      state.tokens = null;
      state.isAuthenticated = false;
      state.loading = false;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
  },
});

export const { setAuth, clearAuth, setLoading } = authSlice.actions;
export default authSlice.reducer;
```

---

## 🛡️ **Route Protection**

### **src/components/common/ProtectedRoute/ProtectedRoute.tsx**
```typescript
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAppSelector } from '../../../hooks/useAppSelector';
import { User } from '../../../types/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: User['role'][];
  requireAuth?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles = [],
  requireAuth = true,
}) => {
  const location = useLocation();
  const { user, isAuthenticated, loading } = useAppSelector((state) => state.auth);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (requireAuth && !isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles.length > 0 && user && !allowedRoles.includes(user.role)) {
    // Redirect based on user role
    switch (user.role) {
      case 'patient':
        return <Navigate to="/patient/dashboard" replace />;
      case 'psychologist':
        return <Navigate to="/psychologist/dashboard" replace />;
      case 'practice_manager':
        return <Navigate to="/manager/dashboard" replace />;
      default:
        return <Navigate to="/" replace />;
    }
  }

  return <>{children}</>;
};
```

---

## 🎨 **Styling System (SCSS Modules)**

### **src/assets/styles/_variables.scss**
```scss
// Design Tokens
$primary-color: #2c5aa0;
$primary-dark: #1e3a8a;
$secondary-color: #64748b;
$background-light: #f8fafc;
$background-gray: #e2e8f0;
$text-dark: #1e293b;
$text-light: #64748b;
$border-radius: 8px;
$border-radius-large: 12px;

// Australian Healthcare Colors
$medicare-green: #00a651;
$ahpra-blue: #0052cc;
$error-red: #dc2626;
$success-green: #16a34a;
$warning-orange: #ea580c;

// Breakpoints
$mobile: 480px;
$tablet: 768px;
$desktop: 1200px;

// Spacing
$spacing-xs: 0.25rem;
$spacing-sm: 0.5rem;
$spacing-md: 1rem;
$spacing-lg: 1.5rem;
$spacing-xl: 2rem;
$spacing-2xl: 3rem;

// Typography
$font-family-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
$font-size-sm: 0.875rem;
$font-size-base: 1rem;
$font-size-lg: 1.125rem;
$font-size-xl: 1.25rem;
$font-size-2xl: 1.5rem;
$font-size-3xl: 1.875rem;
```

### **src/components/auth/PatientRegistration/PatientRegistration.module.scss**
```scss
@import '../../../assets/styles/variables';

.registrationContainer {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, $background-light 0%, $background-gray 100%);
  padding: $spacing-md;
}

.registrationCard {
  background: white;
  border-radius: $border-radius-large;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  padding: $spacing-2xl;
  width: 100%;
  max-width: 500px;

  h1 {
    color: $primary-color;
    font-size: $font-size-2xl;
    font-weight: 600;
    margin-bottom: $spacing-sm;
    text-align: center;
  }

  p {
    color: $text-light;
    text-align: center;
    margin-bottom: $spacing-xl;
  }
}

.form {
  .formGroup {
    margin-bottom: $spacing-lg;

    label {
      display: block;
      color: $text-dark;
      font-weight: 500;
      margin-bottom: $spacing-sm;
    }

    input {
      width: 100%;
      padding: $spacing-md;
      border: 2px solid #e5e7eb;
      border-radius: $border-radius;
      font-size: $font-size-base;
      transition: border-color 0.2s ease;

      &:focus {
        outline: none;
        border-color: $primary-color;
        box-shadow: 0 0 0 3px rgba(44, 90, 160, 0.1);
      }

      &.error {
        border-color: $error-red;
      }
    }
  }

  .errorText {
    color: $error-red;
    font-size: $font-size-sm;
    margin-top: $spacing-xs;
    display: block;
  }

  .generalError {
    background: #fef2f2;
    color: $error-red;
    padding: $spacing-md;
    border-radius: $border-radius;
    margin-bottom: $spacing-lg;
    text-align: center;
  }

  .submitButton {
    width: 100%;
    background: $primary-color;
    color: white;
    border: none;
    padding: $spacing-md $spacing-lg;
    border-radius: $border-radius;
    font-size: $font-size-base;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s ease;

    &:hover:not(:disabled) {
      background: $primary-dark;
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  }
}

.loginLink {
  text-align: center;
  margin-top: $spacing-lg;
  color: $text-light;

  a {
    color: $primary-color;
    text-decoration: none;
    font-weight: 500;

    &:hover {
      text-decoration: underline;
    }
  }
}

// Responsive Design
@media (max-width: $mobile) {
  .registrationContainer {
    padding: $spacing-sm;
  }

  .registrationCard {
    padding: $spacing-lg;
  }
}
```

---

## 🚀 **Getting Started Commands**

### **Package.json Setup**
```json
{
  "name": "psychology_clinic_frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "@reduxjs/toolkit": "^1.9.0",
    "react-redux": "^8.0.5",
    "axios": "^1.3.0",
    "@stripe/stripe-js": "^1.46.0",
    "@stripe/react-stripe-js": "^2.1.0",
    "twilio-video": "^2.27.0",
    "date-fns": "^2.29.0",
    "react-hook-form": "^7.43.0",
    "react-query": "^3.39.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "@vitejs/plugin-react": "^3.1.0",
    "typescript": "^4.9.0",
    "vite": "^4.1.0",
    "sass": "^1.58.0"
  }
}
```

---

## 🎯 **Next Steps**

1. **Set up the project structure** as outlined above
2. **Install dependencies** with `npm install`
3. **Configure environment variables** in `.env`
4. **Implement authentication flow** first
5. **Build intake form components** step by step
6. **Add appointment booking system**
7. **Integrate Twilio Video** for sessions
8. **Add Stripe payment processing**
9. **Implement role-based dashboards**
10. **Add WhatsApp notifications**

**Your Django backend is perfectly aligned with this React TypeScript frontend structure!** 🎉

The complete user journey from landing page to ongoing therapy sessions is now mapped out with proper TypeScript types, API integration, and Australian healthcare compliance built in.
