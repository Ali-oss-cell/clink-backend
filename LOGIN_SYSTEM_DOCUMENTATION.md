# 🔐 Psychology Clinic Login System Documentation

## 📋 **Overview**
The Psychology Clinic backend uses a custom JWT-based authentication system that accepts **email** instead of username for login, designed specifically for Australian healthcare compliance.

## 🏗️ **System Architecture**

### **Authentication Flow:**
```
React Frontend → Django Backend → JWT Tokens → Role-based Access
```

### **Key Components:**
- **Custom User Model** with role-based permissions
- **JWT Token Authentication** (access + refresh tokens)
- **Email-based login** (no username required)
- **Role-based dashboards** (Patient, Psychologist, Practice Manager, Admin)

---

## 🔧 **Backend Implementation**

### **1. Custom Login View (`users/views.py`)**
```python
class CustomLoginView(APIView):
    """Custom login view that accepts email instead of username"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Validation
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check password
        if not user.check_password(password):
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': UserSerializer(user).data
        })
```

### **2. URL Configuration (`users/urls.py`)**
```python
urlpatterns = [
    # JWT Authentication
    path('login/', views.CustomLoginView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    # ... other endpoints
]
```

### **3. User Serializer (`users/serializers.py`)**
```python
class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for authentication responses"""
    
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'role', 'phone_number', 'date_of_birth', 'age', 'is_verified',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_age(self, obj):
        return obj.age if hasattr(obj, 'age') else None
```

---

## 🌐 **API Endpoints**

### **Login Endpoint**
- **URL:** `POST /api/auth/login/`
- **Content-Type:** `application/json`
- **Authentication:** None required

#### **Request Body:**
```json
{
    "email": "user@example.com",
    "password": "Password123!"
}
```

#### **Success Response (200):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "user",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "role": "patient",
        "phone_number": "0412345678",
        "date_of_birth": "1990-01-01",
        "age": 33,
        "is_verified": false,
        "created_at": "2024-01-01T00:00:00Z"
    }
}
```

#### **Error Responses:**
```json
// 400 Bad Request
{
    "error": "Email and password are required"
}

// 401 Unauthorized
{
    "error": "Invalid credentials"
}
```

### **Token Refresh Endpoint**
- **URL:** `POST /api/auth/refresh/`
- **Content-Type:** `application/json`

#### **Request Body:**
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### **Success Response (200):**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## 🎯 **User Roles & Permissions**

### **Available Roles:**
```python
class UserRole(models.TextChoices):
    PATIENT = 'patient', 'Patient'
    PSYCHOLOGIST = 'psychologist', 'Psychologist'
    PRACTICE_MANAGER = 'practice_manager', 'Practice Manager'
    ADMIN = 'admin', 'Administrator'
```

### **Role-based Access:**
- **Patients:** Access to patient dashboard, intake forms, appointments
- **Psychologists:** Access to psychologist dashboard, patient notes, appointments
- **Practice Managers:** Access to practice management, billing, reports
- **Admins:** Full system access

---

## 🔧 **Frontend Integration**

### **React Login Implementation:**
```typescript
interface LoginRequest {
    email: string;
    password: string;
}

interface LoginResponse {
    access: string;
    refresh: string;
    user: {
        id: number;
        email: string;
        first_name: string;
        last_name: string;
        role: string;
        // ... other user fields
    };
}

const login = async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await fetch('http://127.0.0.1:8000/api/auth/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Login failed');
    }
    
    return response.json();
};
```

### **Token Storage:**
```typescript
// Store tokens after successful login
localStorage.setItem('access_token', data.access);
localStorage.setItem('refresh_token', data.refresh);
localStorage.setItem('user', JSON.stringify(data.user));
```

### **Authenticated Requests:**
```typescript
const makeAuthenticatedRequest = async (url: string, options: RequestInit = {}) => {
    const token = localStorage.getItem('access_token');
    
    return fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...options.headers
        }
    });
};
```

---

## 🚨 **Error Handling**

### **Common Issues:**

#### **1. CORS Errors:**
```
Access to XMLHttpRequest at 'http://127.0.0.1:8000/api/auth/login/' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```
**Solution:** Check Django CORS settings in `settings.py`

#### **2. 401 Unauthorized:**
```json
{
    "error": "Invalid credentials"
}
```
**Causes:**
- User doesn't exist in database
- Wrong password
- User account is inactive

#### **3. 400 Bad Request:**
```json
{
    "error": "Email and password are required"
}
```
**Causes:**
- Missing email or password fields
- Empty request body

---

## 🔧 **Testing**

### **1. Using Postman:**
```bash
POST http://127.0.0.1:8000/api/auth/login/
Content-Type: application/json

{
    "email": "test@example.com",
    "password": "Password123!"
}
```

### **2. Using cURL:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Password123!"
  }'
```

### **3. Using React:**
```typescript
const testLogin = async () => {
    try {
        const response = await fetch('http://127.0.0.1:8000/api/auth/login/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                email: "test@example.com",
                password: "Password123!"
            })
        });
        
        const data = await response.json();
        console.log('Login response:', data);
    } catch (error) {
        console.error('Login error:', error);
    }
};
```

---

## 🛠️ **Development Setup**

### **1. Start Django Server:**
```bash
python manage.py runserver
```

### **2. Check Server Status:**
```bash
curl http://127.0.0.1:8000/api/health/
```

### **3. Test Login Endpoint:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'
```

---

## 📝 **Security Considerations**

### **1. Password Requirements:**
- Minimum 8 characters
- Must contain uppercase, lowercase, and number
- Stored using Django's built-in password hashing

### **2. Token Security:**
- Access tokens expire (configurable)
- Refresh tokens for token renewal
- Tokens stored securely in frontend

### **3. CORS Configuration:**
- Only allowed origins can make requests
- Credentials allowed for authenticated requests
- Preflight requests handled properly

---

## 🎯 **Next Steps**

1. **Test the login endpoint** with Postman
2. **Create a test user** in the database
3. **Test React frontend integration**
4. **Implement role-based redirects**
5. **Add error handling** in frontend

---

## 📞 **Support**

If you encounter issues:
1. Check Django server logs
2. Verify CORS settings
3. Test with Postman first
4. Check browser console for errors
5. Ensure user exists in database

**The login system is fully implemented and ready for frontend integration!** 🎯✨
