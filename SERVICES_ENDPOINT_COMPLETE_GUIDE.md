# 🏥 Services Endpoint - Complete Frontend Guide

## 🎯 **Endpoint**

**URL:** `GET /api/services/`

**Full URL:** `https://api.tailoredpsychology.com.au/api/services/`

**Authentication:** Not required (public endpoint)

---

## 📋 **Get All Services**

### **Request**

```http
GET /api/services/
```

### **Response (200 OK)**

```json
[
  {
    "id": 1,
    "name": "Individual Therapy Session",
    "description": "One-on-one therapy session with a registered psychologist",
    "standard_fee": "150.00",
    "medicare_rebate": "93.35",
    "out_of_pocket_cost": "56.65",
    "duration_minutes": 50,
    "is_active": true
  },
  {
    "id": 2,
    "name": "Couples Therapy Session",
    "description": "Therapy session for couples",
    "standard_fee": "200.00",
    "medicare_rebate": "0.00",
    "out_of_pocket_cost": "200.00",
    "duration_minutes": 60,
    "is_active": true
  }
]
```

### **Response Fields**

| Field | Type | Description |
|-------|------|-------------|
| `id` | integer | Unique service identifier |
| `name` | string | Service name |
| `description` | string | Detailed service description |
| `standard_fee` | string (decimal) | Standard consultation fee |
| `medicare_rebate` | string (decimal) | Medicare rebate amount |
| `out_of_pocket_cost` | string (decimal) | Cost after Medicare rebate |
| `duration_minutes` | integer | Session duration in minutes |
| `is_active` | boolean | Whether service is currently available |

---

## 🔍 **Get Single Service by ID**

### **Request**

```http
GET /api/services/{id}/
```

### **Example**

```http
GET /api/services/1/
```

### **Response (200 OK)**

```json
{
  "id": 1,
  "name": "Individual Therapy Session",
  "description": "One-on-one therapy session with a registered psychologist",
  "standard_fee": "150.00",
  "medicare_rebate": "93.35",
  "out_of_pocket_cost": "56.65",
  "duration_minutes": 50,
  "is_active": true
}
```

### **Error Response (404 Not Found)**

```json
{
  "detail": "Not found."
}
```

---

## 💻 **Frontend Implementation**

### **TypeScript Interface**

```typescript
// types/service.ts
export interface Service {
  id: number;
  name: string;
  description: string;
  standard_fee: string;
  medicare_rebate: string;
  out_of_pocket_cost: string;
  duration_minutes: number;
  is_active: boolean;
}
```

### **API Service**

```typescript
// services/api/services.ts
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://api.tailoredpsychology.com.au';

export const servicesAPI = {
  /**
   * Get all active services
   * @returns Promise with array of services
   */
  getAllServices: async (): Promise<Service[]> => {
    const response = await axios.get<Service[]>(`${API_BASE_URL}/api/services/`);
    return response.data;
  },

  /**
   * Get single service by ID
   * @param serviceId - Service ID
   * @returns Promise with service data
   * @throws Error if service not found
   */
  getServiceById: async (serviceId: number): Promise<Service> => {
    try {
      const response = await axios.get<Service>(
        `${API_BASE_URL}/api/services/${serviceId}/`
      );
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error(`Service with ID ${serviceId} not found`);
      }
      throw error;
    }
  },
};
```

### **React Hook**

```typescript
// hooks/useServices.ts
import { useState, useEffect, useCallback } from 'react';
import { servicesAPI, Service } from '../services/api/services';

export const useServices = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchServices = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await servicesAPI.getAllServices();
      setServices(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch services'));
      setServices([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchServices();
  }, [fetchServices]);

  return {
    services,
    loading,
    error,
    refetch: fetchServices,
  };
};

export const useService = (serviceId: number | null) => {
  const [service, setService] = useState<Service | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchService = useCallback(async (id: number) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await servicesAPI.getServiceById(id);
      setService(data);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch service'));
      setService(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (serviceId) {
      fetchService(serviceId);
    } else {
      setService(null);
      setError(null);
    }
  }, [serviceId, fetchService]);

  return {
    service,
    loading,
    error,
    refetch: () => serviceId && fetchService(serviceId),
  };
};
```

### **React Component Example**

```typescript
// components/ServiceSelection.tsx
import React from 'react';
import { useServices } from '../hooks/useServices';

export const ServiceSelection: React.FC = () => {
  const { services, loading, error } = useServices();

  if (loading) {
    return <div>Loading services...</div>;
  }

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  return (
    <div>
      <h2>Select a Service</h2>
      {services.length === 0 ? (
        <p>No services available.</p>
      ) : (
        <div>
          {services.map((service) => (
            <div key={service.id} className="service-card">
              <h3>{service.name}</h3>
              <p>{service.description}</p>
              <p>Duration: {service.duration_minutes} minutes</p>
              <p>Fee: ${service.standard_fee}</p>
              <p>After Medicare: ${service.out_of_pocket_cost}</p>
              <button onClick={() => selectService(service.id)}>
                Select Service
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

### **DateTimeSelectionPage Component (Fixes "Service not found" Error)**

```typescript
// components/DateTimeSelectionPage.tsx
import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useService } from '../hooks/useServices';

export const DateTimeSelectionPage: React.FC = () => {
  const { serviceId } = useParams<{ serviceId: string }>();
  const navigate = useNavigate();
  
  // ✅ Convert string to number and handle null
  const serviceIdNum = serviceId ? parseInt(serviceId, 10) : null;
  
  const { service, loading, error } = useService(serviceIdNum);

  // ✅ Redirect if service not found
  useEffect(() => {
    if (!loading && serviceIdNum && !service && !error) {
      // Service ID provided but service not found
      console.warn(`[DateTimeSelectionPage] Service ${serviceIdNum} not found, redirecting`);
      navigate('/services'); // Redirect to service selection
    }
  }, [loading, service, error, serviceIdNum, navigate]);

  // ✅ Show error if service fetch failed
  useEffect(() => {
    if (error) {
      console.error(`[DateTimeSelectionPage] Error loading service:`, error);
      // Optionally show error message to user
    }
  }, [error]);

  // ✅ Handle missing serviceId in URL
  useEffect(() => {
    if (!serviceId) {
      console.warn('[DateTimeSelectionPage] No service ID in URL, redirecting');
      navigate('/services');
    }
  }, [serviceId, navigate]);

  if (loading) {
    return <div>Loading service details...</div>;
  }

  if (error || !service) {
    return (
      <div>
        <p>Service not found.</p>
        <button onClick={() => navigate('/services')}>
          Go Back to Services
        </button>
      </div>
    );
  }

  return (
    <div>
      <h2>Select Date & Time</h2>
      <p>Service: {service.name}</p>
      <p>Duration: {service.duration_minutes} minutes</p>
      {/* Date/time selection UI here */}
    </div>
  );
};
```

---

## 🚨 **Fixing "Service not found" Error**

### **Common Causes:**

1. **Service ID missing from URL/state**
   - ✅ Fix: Check URL params and redirect if missing

2. **Service ID is string instead of number**
   - ✅ Fix: Parse to integer: `parseInt(serviceId, 10)`

3. **Service doesn't exist in database**
   - ✅ Fix: Handle 404 error and redirect

4. **Service is inactive (`is_active: false`)**
   - ✅ Fix: Filter by `is_active: true` or check status

5. **Race condition (fetching before service ID is set)**
   - ✅ Fix: Only fetch when `serviceId` is available

### **Complete Error Handling**

```typescript
// components/DateTimeSelectionPage.tsx (Complete)
import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useService } from '../hooks/useServices';

export const DateTimeSelectionPage: React.FC = () => {
  const { serviceId } = useParams<{ serviceId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  
  // ✅ Get serviceId from URL params or location state
  const serviceIdFromState = location.state?.serviceId;
  const finalServiceId = serviceId || serviceIdFromState;
  
  // ✅ Parse to number
  const serviceIdNum = finalServiceId ? parseInt(finalServiceId, 10) : null;
  
  // ✅ Validate serviceId is a valid number
  const isValidServiceId = serviceIdNum !== null && !isNaN(serviceIdNum) && serviceIdNum > 0;
  
  const { service, loading, error } = useService(isValidServiceId ? serviceIdNum : null);
  const [redirecting, setRedirecting] = useState(false);

  // ✅ Handle missing or invalid serviceId
  useEffect(() => {
    if (!loading && !isValidServiceId && !redirecting) {
      console.warn('[DateTimeSelectionPage] Service ID missing or invalid, redirecting');
      setRedirecting(true);
      navigate('/services', { 
        replace: true,
        state: { error: 'Please select a service first' }
      });
    }
  }, [loading, isValidServiceId, navigate, redirecting]);

  // ✅ Handle service not found (404)
  useEffect(() => {
    if (!loading && isValidServiceId && !service && error && !redirecting) {
      console.warn(`[DateTimeSelectionPage] Service ${serviceIdNum} not found, redirecting`);
      setRedirecting(true);
      navigate('/services', { 
        replace: true,
        state: { error: `Service not found (ID: ${serviceIdNum})` }
      });
    }
  }, [loading, service, error, serviceIdNum, navigate, isValidServiceId, redirecting]);

  // ✅ Handle inactive service
  useEffect(() => {
    if (service && !service.is_active && !redirecting) {
      console.warn(`[DateTimeSelectionPage] Service ${service.id} is inactive, redirecting`);
      setRedirecting(true);
      navigate('/services', { 
        replace: true,
        state: { error: 'This service is no longer available' }
      });
    }
  }, [service, navigate, redirecting]);

  if (redirecting) {
    return <div>Redirecting...</div>;
  }

  if (loading) {
    return <div>Loading service details...</div>;
  }

  if (error || !service) {
    return (
      <div>
        <p>Unable to load service details.</p>
        <button onClick={() => navigate('/services')}>
          Go Back to Services
        </button>
      </div>
    );
  }

  return (
    <div>
      <h2>Select Date & Time</h2>
      <div className="service-info">
        <h3>{service.name}</h3>
        <p>{service.description}</p>
        <p>Duration: {service.duration_minutes} minutes</p>
        <p>Fee: ${service.standard_fee}</p>
        {parseFloat(service.medicare_rebate) > 0 && (
          <p>After Medicare rebate: ${service.out_of_pocket_cost}</p>
        )}
      </div>
      
      {/* Date/time selection UI */}
      <div className="datetime-selection">
        {/* Your date/time picker component here */}
      </div>
    </div>
  );
};
```

---

## 🔄 **Booking Flow Integration**

### **Step 1: Service Selection**

```typescript
// When user selects a service
const handleServiceSelect = (service: Service) => {
  // ✅ Store service in state or URL
  navigate(`/book/${service.id}/datetime`, {
    state: { serviceId: service.id, service } // Pass service data
  });
};
```

### **Step 2: DateTime Selection (Your Page)**

```typescript
// DateTimeSelectionPage receives serviceId from URL
// Use the hook to fetch service details
// Handle errors and redirect if needed
```

### **Step 3: Continue Booking**

```typescript
// After date/time selection, proceed with service data
const handleContinue = () => {
  navigate('/book/confirm', {
    state: {
      serviceId: service.id,
      service: service, // Pass full service object
      selectedDateTime: selectedDateTime,
    }
  });
};
```

---

## ✅ **Best Practices**

1. **Always validate serviceId**
   - Check if it's a valid number
   - Check if it exists before using

2. **Handle loading states**
   - Show loading indicator while fetching
   - Don't render UI until service is loaded

3. **Handle errors gracefully**
   - Show user-friendly error messages
   - Provide navigation back to service selection

4. **Check service status**
   - Verify `is_active: true` before allowing booking
   - Redirect if service is inactive

5. **Use location state**
   - Pass service data via `navigate()` state
   - Reduces need for additional API calls

6. **Prevent race conditions**
   - Only fetch when serviceId is available
   - Use proper dependency arrays in useEffect

---

## 🔗 **Related Endpoints**

- **Psychologists:** `GET /api/services/psychologists/`
- **Specializations:** `GET /api/services/specializations/`
- **Book Appointment:** `POST /api/appointments/book-enhanced/`

---

## 📝 **Quick Reference**

```typescript
// Get all services
GET /api/services/

// Get service by ID
GET /api/services/1/

// Response structure
{
  id: number,
  name: string,
  description: string,
  standard_fee: string,
  medicare_rebate: string,
  out_of_pocket_cost: string,
  duration_minutes: number,
  is_active: boolean
}
```

---

## 🐛 **Debugging Tips**

1. **Check Network Tab**
   - Verify request is being made
   - Check response status (200, 404, etc.)
   - Inspect response data

2. **Check Console Logs**
   - Look for "Service not found" warnings
   - Check serviceId value in URL params
   - Verify service data structure

3. **Verify Service Exists**
   - Test endpoint directly: `GET /api/services/1/`
   - Check database for active services
   - Verify `is_active: true`

4. **Check URL Parameters**
   - Ensure serviceId is in URL: `/book/:serviceId/datetime`
   - Verify serviceId is a number, not string
   - Check if serviceId is being passed correctly

---

**This guide should fix your "Service not found" error!** 🎯

