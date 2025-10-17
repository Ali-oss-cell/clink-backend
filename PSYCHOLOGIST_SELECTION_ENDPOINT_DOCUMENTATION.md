# Psychologist Selection Page - API Documentation

## Overview
This document provides comprehensive information about the API endpoint used for the psychologist selection page, including all available fields, filtering capabilities, and implementation examples.

---

## 📋 Main Endpoint

### **GET /api/services/psychologists/**

Returns a list of all psychologist profiles with comprehensive information for display and filtering.

#### **Authentication**
- **Required**: No (public endpoint)
- **Recommended**: Yes (for personalized features and next_available_slot calculation)

#### **Query Parameters**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `service` | integer | Filter by service ID | `?service=1` |
| `specialization` | integer | Filter by specialization ID | `?specialization=2` |
| `is_accepting_new_patients` | boolean | Only show psychologists accepting new patients | `?is_accepting_new_patients=true` |
| `telehealth_available` | boolean | Filter by telehealth availability | `?telehealth_available=true` |
| `in_person_available` | boolean | Filter by in-person availability | `?in_person_available=true` |

---

## 📦 Response Structure

### **Success Response (200 OK)**

```json
[
  {
    // ============ BASIC INFORMATION ============
    "id": 1,
    "user_name": "Dr. Sarah Johnson",
    "user_gender": "female",
    "display_name": "Dr Sarah Johnson",
    "title": "Dr",
    
    // ============ PROFILE IMAGE ============
    "profile_image": "/media/psychologist_profiles/dr_sarah_johnson.jpg",
    "profile_image_url": "http://localhost:8000/media/psychologist_profiles/dr_sarah_johnson.jpg",
    "has_profile_image": true,
    
    // ============ PROFESSIONAL CREDENTIALS ============
    "ahpra_registration_number": "PSY0001234567",
    "is_ahpra_current": true,
    "qualifications": "M.Psych (Clinical), B.Psych (Hons), MAPS",
    "years_experience": 12,
    "experience_level": "Senior",
    
    // ============ PRICING INFORMATION ============
    "consultation_fee": "180.00",
    "medicare_rebate_amount": "87.45",
    "patient_cost_after_rebate": "92.55",
    
    // ============ AVAILABILITY ============
    "is_accepting_new_patients": true,
    "telehealth_available": true,
    "in_person_available": true,
    "working_days": "Monday,Tuesday,Wednesday,Thursday,Friday",
    "working_days_list": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    "start_time": "09:00:00",
    "end_time": "17:00:00",
    "session_types": "Individual Therapy, Couples Therapy",
    "session_types_list": ["Individual Therapy", "Couples Therapy"],
    "next_available_slot": "2025-10-08T14:00:00+11:00",
    
    // ============ PROFILE & BIO ============
    "bio": "I am a registered clinical psychologist with over 12 years of experience...",
    "average_rating": "4.80",
    "total_reviews": 45,
    
    // ============ SPECIALIZATIONS ============
    "specializations_list": [
      {
        "id": 1,
        "name": "Anxiety & Panic Disorders",
        "description": "Treatment for anxiety, panic attacks, and related disorders",
        "is_active": true
      },
      {
        "id": 2,
        "name": "Depression & Mood Disorders",
        "description": "Support for depression, bipolar, and mood-related conditions",
        "is_active": true
      }
    ],
    
    // ============ SERVICES OFFERED ============
    "services_list": [
      {
        "id": 1,
        "name": "Individual Therapy Session",
        "description": "One-on-one therapy session",
        "standard_fee": "180.00",
        "medicare_rebate": "87.45",
        "out_of_pocket_cost": "92.55",
        "duration_minutes": 50,
        "is_active": true
      },
      {
        "id": 2,
        "name": "Couples Therapy Session",
        "description": "Therapy for couples",
        "standard_fee": "220.00",
        "medicare_rebate": "0.00",
        "out_of_pocket_cost": "220.00",
        "duration_minutes": 60,
        "is_active": true
      }
    ],
    
    // ============ STATUS ============
    "is_active_practitioner": true
  }
]
```

---

## 🎯 Frontend Implementation Guide

### **1. Fetching Psychologists**

```typescript
// api/psychologist.service.ts
export const psychologistService = {
  /**
   * Get all psychologists
   * @param filters - Optional filters
   */
  async getAllPsychologists(filters?: {
    service?: number;
    specialization?: number;
    isAcceptingNewPatients?: boolean;
    telehealthAvailable?: boolean;
    inPersonAvailable?: boolean;
  }) {
    const params = new URLSearchParams();
    
    if (filters) {
      if (filters.service) params.append('service', filters.service.toString());
      if (filters.specialization) params.append('specialization', filters.specialization.toString());
      if (filters.isAcceptingNewPatients !== undefined) {
        params.append('is_accepting_new_patients', filters.isAcceptingNewPatients.toString());
      }
      if (filters.telehealthAvailable !== undefined) {
        params.append('telehealth_available', filters.telehealthAvailable.toString());
      }
      if (filters.inPersonAvailable !== undefined) {
        params.append('in_person_available', filters.inPersonAvailable.toString());
      }
    }
    
    const queryString = params.toString();
    const url = `/api/services/psychologists/${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch psychologists');
    
    return response.json();
  },
  
  /**
   * Get a single psychologist by ID
   */
  async getPsychologist(id: number) {
    const response = await fetch(`/api/services/psychologists/${id}/`);
    if (!response.ok) throw new Error('Failed to fetch psychologist');
    
    return response.json();
  }
};
```

### **2. React Component Example**

```tsx
// components/PsychologistSelectionPage.tsx
import { useState, useEffect } from 'react';
import { psychologistService } from '../api/psychologist.service';

interface Psychologist {
  id: number;
  user_name: string;
  user_gender: string;
  display_name: string;
  title: string;
  profile_image_url: string;
  has_profile_image: boolean;
  qualifications: string;
  years_experience: number;
  experience_level: string;
  bio: string;
  specializations_list: Array<{
    id: number;
    name: string;
    description: string;
  }>;
  consultation_fee: string;
  patient_cost_after_rebate: string;
  is_accepting_new_patients: boolean;
  telehealth_available: boolean;
  in_person_available: boolean;
  next_available_slot: string | null;
  average_rating: string;
  total_reviews: number;
  session_types_list: string[];
  working_days_list: string[];
}

export function PsychologistSelectionPage() {
  const [psychologists, setPsychologists] = useState<Psychologist[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    gender: '',
    specialization: null,
    sessionType: '',
    isAcceptingNewPatients: true
  });
  
  useEffect(() => {
    loadPsychologists();
  }, []);
  
  const loadPsychologists = async () => {
    try {
      setLoading(true);
      const data = await psychologistService.getAllPsychologists({
        isAcceptingNewPatients: filters.isAcceptingNewPatients
      });
      setPsychologists(data);
    } catch (error) {
      console.error('Failed to load psychologists:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // Client-side filtering
  const filteredPsychologists = psychologists.filter(psych => {
    // Gender filter
    if (filters.gender && psych.user_gender !== filters.gender) {
      return false;
    }
    
    // Specialization filter
    if (filters.specialization) {
      const hasSpecialization = psych.specializations_list.some(
        spec => spec.id === filters.specialization
      );
      if (!hasSpecialization) return false;
    }
    
    // Session type filter
    if (filters.sessionType && !psych.session_types_list.includes(filters.sessionType)) {
      return false;
    }
    
    return true;
  });
  
  return (
    <div className="psychologist-selection">
      <h1>Select Your Psychologist</h1>
      
      {/* Filters */}
      <div className="filters">
        <select 
          value={filters.gender} 
          onChange={(e) => setFilters({...filters, gender: e.target.value})}
        >
          <option value="">Any Gender</option>
          <option value="male">Male</option>
          <option value="female">Female</option>
          <option value="non_binary">Non-Binary</option>
        </select>
        
        <select 
          value={filters.sessionType} 
          onChange={(e) => setFilters({...filters, sessionType: e.target.value})}
        >
          <option value="">Any Session Type</option>
          <option value="Individual Therapy">Individual Therapy</option>
          <option value="Couples Therapy">Couples Therapy</option>
          <option value="Family Therapy">Family Therapy</option>
        </select>
      </div>
      
      {/* Psychologist Cards */}
      <div className="psychologist-grid">
        {loading ? (
          <div>Loading psychologists...</div>
        ) : filteredPsychologists.length === 0 ? (
          <div>No psychologists match your criteria</div>
        ) : (
          filteredPsychologists.map(psych => (
            <PsychologistCard key={psych.id} psychologist={psych} />
          ))
        )}
      </div>
    </div>
  );
}

function PsychologistCard({ psychologist }: { psychologist: Psychologist }) {
  const formatNextAvailable = (isoDate: string | null) => {
    if (!isoDate) return 'No availability';
    
    const date = new Date(isoDate);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    if (date.toDateString() === today.toDateString()) {
      return `Today, ${date.toLocaleTimeString('en-AU', { hour: '2-digit', minute: '2-digit' })}`;
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return `Tomorrow, ${date.toLocaleTimeString('en-AU', { hour: '2-digit', minute: '2-digit' })}`;
    } else {
      return date.toLocaleDateString('en-AU', { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
  };
  
  return (
    <div className="psychologist-card">
      <img 
        src={psychologist.profile_image_url || '/default-avatar.png'} 
        alt={psychologist.display_name}
        className="profile-image"
      />
      
      <div className="psychologist-info">
        <h3>{psychologist.display_name}</h3>
        <p className="qualifications">{psychologist.qualifications}</p>
        <p className="experience">{psychologist.experience_level} • {psychologist.years_experience} years</p>
        
        <div className="specializations">
          {psychologist.specializations_list.slice(0, 3).map(spec => (
            <span key={spec.id} className="badge">{spec.name}</span>
          ))}
        </div>
        
        <p className="bio">{psychologist.bio.substring(0, 150)}...</p>
        
        <div className="availability">
          <strong>Next Available:</strong> {formatNextAvailable(psychologist.next_available_slot)}
        </div>
        
        <div className="pricing">
          <strong>Fee:</strong> ${psychologist.consultation_fee}
          <span className="out-of-pocket">
            (${psychologist.patient_cost_after_rebate} after Medicare rebate)
          </span>
        </div>
        
        <div className="rating">
          ⭐ {psychologist.average_rating} ({psychologist.total_reviews} reviews)
        </div>
        
        <div className="session-options">
          {psychologist.telehealth_available && <span className="badge">Telehealth</span>}
          {psychologist.in_person_available && <span className="badge">In-Person</span>}
        </div>
        
        <button className="select-button">Select Psychologist</button>
      </div>
    </div>
  );
}
```

---

## 🔍 Filtering Capabilities

### **Server-Side Filtering**
Implemented on the backend (query parameters):
- Service ID
- Specialization ID
- Accepting new patients
- Telehealth availability
- In-person availability

### **Client-Side Filtering**
Should be implemented on the frontend:
- Gender preference
- Session types (Individual, Couples, Family)
- Availability by day/time
- Price range
- Rating threshold
- Experience level

---

## 📊 Data Fields Reference

### **Required Fields for Display**

| Field | Type | Purpose | Display Example |
|-------|------|---------|-----------------|
| `display_name` | string | Professional name | "Dr Sarah Johnson" |
| `profile_image_url` | string | Profile photo | `<img src={url}>` |
| `qualifications` | string | Education | "M.Psych (Clinical)" |
| `years_experience` | number | Experience | "12 years" |
| `experience_level` | string | Seniority | "Senior" |
| `bio` | string | Description | First 150 chars |
| `specializations_list` | array | Areas of expertise | Badge list |
| `consultation_fee` | string | Price | "$180.00" |
| `patient_cost_after_rebate` | string | Out-of-pocket | "$92.55" |
| `average_rating` | string | Rating | "4.8 ⭐" |
| `total_reviews` | number | Review count | "(45 reviews)" |

### **Optional Fields for Filtering**

| Field | Type | Purpose |
|-------|------|---------|
| `user_gender` | string | Gender filter |
| `session_types_list` | array | Session type filter |
| `telehealth_available` | boolean | Mode filter |
| `in_person_available` | boolean | Mode filter |
| `working_days_list` | array | Day availability |
| `start_time` | time | Working hours |
| `end_time` | time | Working hours |
| `next_available_slot` | datetime | Quick booking |

---

## 🚀 Additional Endpoints

### **GET /api/services/psychologists/{id}/**
Get detailed information about a specific psychologist.

**Response:** Same structure as list endpoint but for a single psychologist.

### **GET /api/services/psychologists/{id}/availability/**
Get detailed availability for a psychologist (for booking calendar).

**Response:**
```json
{
  "psychologist_id": 1,
  "psychologist_name": "Dr Sarah Johnson",
  "next_available_slot": "2025-10-08T14:00:00+11:00",
  "available_slots": [
    {
      "date": "2025-10-08",
      "time": "14:00:00",
      "datetime": "2025-10-08T14:00:00+11:00",
      "is_available": true
    },
    {
      "date": "2025-10-08",
      "time": "15:00:00",
      "datetime": "2025-10-08T15:00:00+11:00",
      "is_available": true
    }
  ]
}
```

### **GET /api/services/specializations/**
Get all available specializations for filtering.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Anxiety & Panic Disorders",
    "description": "Treatment for anxiety, panic attacks, and related disorders",
    "is_active": true
  },
  {
    "id": 2,
    "name": "Depression & Mood Disorders",
    "description": "Support for depression, bipolar, and mood-related conditions",
    "is_active": true
  }
]
```

---

## 🛠️ Testing with cURL

### **Get All Psychologists**
```bash
curl -X GET "http://localhost:8000/api/services/psychologists/" \
  -H "Accept: application/json"
```

### **Filter by Accepting New Patients**
```bash
curl -X GET "http://localhost:8000/api/services/psychologists/?is_accepting_new_patients=true" \
  -H "Accept: application/json"
```

### **Filter by Service**
```bash
curl -X GET "http://localhost:8000/api/services/psychologists/?service=1" \
  -H "Accept: application/json"
```

### **Filter by Multiple Criteria**
```bash
curl -X GET "http://localhost:8000/api/services/psychologists/?is_accepting_new_patients=true&telehealth_available=true&specialization=1" \
  -H "Accept: application/json"
```

### **Get Single Psychologist**
```bash
curl -X GET "http://localhost:8000/api/services/psychologists/1/" \
  -H "Accept: application/json"
```

---

## ✅ Summary

### **What We Have Ready:**
✅ Full psychologist profile data with all required fields  
✅ Gender field for filtering  
✅ Service relationships (services_offered)  
✅ Specialization relationships  
✅ Working days, start/end times  
✅ Next available slot calculation  
✅ Profile images with full URLs  
✅ Session types, telehealth/in-person availability  
✅ AHPRA verification status  
✅ Pricing with Medicare rebate calculations  
✅ Ratings and reviews  

### **Frontend Tasks:**
1. Implement the psychologist service API calls
2. Create the PsychologistSelectionPage component
3. Add filtering UI (gender, specialization, session type)
4. Display psychologist cards with all information
5. Implement "Next Available" slot display
6. Add selection functionality to pass to booking page

### **Backend Status:**
✅ **READY FOR FRONTEND INTEGRATION**

All required endpoints and data fields are implemented and migrated. The frontend can now integrate with the API to build the psychologist selection page.

