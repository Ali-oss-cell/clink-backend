# 🎯 Psychology Clinic Backend - Complete TODO List

## 📊 **Current Status: 75% Complete**

### ✅ **Completed Features:**
- User Management System (100%)
- Authentication & JWT (100%)
- Intake Form System (100%)
- Progress Notes System (100%)
- Dashboard System (100%)
- Services System (100%)
- API Structure (100%)

### 🔄 **Dashboard Enhancements (IN PROGRESS)**
- Dashboard View Updates (0%)
- Psychologist Profile Management (0%)
- Enhanced Patient Management (0%)
- Schedule Management (0%)

### 🚧 **Pending Features:**
- Appointment System (0%)
- Billing System (0%)
- Resources System (0%)
- Third-party Integrations (0%)
- Privacy Policy publication (TODO)
- Production DB encryption (TODO)

---

## 📋 **Priority 1: Core Business Logic (HIGH PRIORITY)**

### 🗓️ **1. Appointment System Implementation**
**Status**: ❌ Pending | **Estimated Time**: 4-6 hours | **Priority**: HIGH

**Models to Create:**
```python
# appointments/models.py
class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient_appointments')
    psychologist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='psychologist_appointments')
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE)
    appoint ment_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    status = models.CharField(max_length=20, choices=[
        ('scheduled', 'Scheduled'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show')
    ])
    notes = models.TextField(blank=True)
    video_room_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['psychologist', 'appointment_date']
        ordering = ['appointment_date']

class AvailabilitySlot(models.Model):
    psychologist = models.ForeignKey(User, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['psychologist', 'day_of_week', 'start_time']

class TimeSlot(models.Model):
    """Available time slots for booking"""
    psychologist = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        unique_together = ['psychologist', 'start_time']
```

**Serializers to Create:**
```python
# appointments/serializers.py
class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    psychologist_name = serializers.CharField(source='psychologist.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)
    formatted_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = '__all__'
    
    def get_formatted_date(self, obj):
        return obj.appointment_date.strftime('%d/%m/%Y %I:%M %p')
```

**Views to Implement:**
- `AppointmentViewSet` - CRUD operations
- `BookAppointmentView` - Patient booking
- `AvailabilityView` - Check psychologist availability
- `UpcomingAppointmentsView` - Get upcoming appointments
- `CancelAppointmentView` - Cancel appointments
- `RescheduleAppointmentView` - Reschedule appointments

**Implementation Hints:**
- Use `django.utils.timezone` for timezone-aware datetime handling
- Add `unique_together` constraints to prevent double-booking
- Include status choices: 'scheduled', 'confirmed', 'completed', 'cancelled', 'no_show'
- Consider adding `recurring` field for regular appointments
- Use `django.utils.timezone.now()` for current time
- Add `unique_together = ['psychologist', 'appointment_date']` to prevent double-booking

---

### 💰 **2. Billing System Implementation**
**Status**: ❌ Pending | **Estimated Time**: 6-8 hours | **Priority**: HIGH

**Models to Create:**
```python
# billing/models.py
import uuid

class Invoice(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=20, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    medicare_rebate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    out_of_pocket = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled')
    ])
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=[
        ('stripe', 'Stripe'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('medicare', 'Medicare')
    ])
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ])
    processed_at = models.DateTimeField(auto_now_add=True)
    
class MedicareClaim(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    item_number = models.CharField(max_length=10)
    rebate_amount = models.DecimalField(max_digits=10, decimal_places=2)
    claim_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ])
    claim_date = models.DateField()
    processed_date = models.DateField(null=True, blank=True)
```

**Serializers to Create:**
```python
# billing/serializers.py
class InvoiceSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    appointment_date = serializers.DateTimeField(source='appointment.appointment_date', read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
```

**Views to Implement:**
- `InvoiceViewSet` - Invoice management
- `PaymentViewSet` - Payment processing
- `ProcessPaymentView` - Stripe payment processing
- `MedicareClaimView` - Medicare rebate processing
- `DownloadInvoiceView` - PDF invoice generation

**Implementation Hints:**
- Use `uuid.uuid4().hex[:8]` for invoice numbers
- Calculate GST as `total_amount * 0.10`
- Store Stripe payment intent IDs for tracking
- Include Medicare item numbers for rebate processing

---

### 📝 **3. Resources System Implementation**
**Status**: ❌ Pending | **Estimated Time**: 3-4 hours | **Priority**: MEDIUM

**Models to Create:**
```python
# resources/models.py
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f"/blog/category/{self.slug}/"

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=500)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    featured_image = models.ImageField(upload_to='blog/', blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-published_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f"/blog/{self.slug}/"

class Resource(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='resources/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Serializers to Create:**
```python
# resources/serializers.py
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class BlogPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = BlogPost
        fields = '__all__'
```

**Views to Implement:**
- `BlogPostViewSet` - Blog post management
- `CategoryViewSet` - Category management
- `ResourceViewSet` - Resource management
- `PublishedPostsView` - Public blog posts
- `BlogPostDetailView` - Individual blog post

**Implementation Hints:**
- Use `django.utils.text.slugify` for automatic slug generation
- Add `get_absolute_url()` method for SEO-friendly URLs
- Include `ordering = ['-published_at']` in Meta class

---

## 📋 **Priority 1.5: Dashboard Enhancements (HIGH PRIORITY)**

### 📊 **1. Update Dashboard View**
**Status**: ❌ Pending | **Estimated Time**: 15 minutes | **Priority**: HIGH

**Features to Implement:**
- Integrate real appointment data from database
- Add comprehensive statistics (total appointments, revenue, patient count)
- Include quick actions (book appointment, view patients, generate reports)
- Real-time data updates
- Performance metrics and charts

**Implementation Steps:**
1. Update dashboard views to fetch real data
2. Add statistics calculations
3. Implement quick action buttons
4. Add data visualization components

---

### 👨‍⚕️ **2. Psychologist Profile Management**
**Status**: ❌ Pending | **Estimated Time**: 20 minutes | **Priority**: HIGH

**Features to Implement:**
- Profile image upload functionality
- Bio and qualifications management
- Specializations management (add/remove/edit)
- Availability settings configuration
- Professional information display

**Models to Enhance:**
```python
# users/models.py - Add to User model or create PsychologistProfile
class PsychologistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='psychologist_profiles/', blank=True)
    bio = models.TextField(blank=True)
    qualifications = models.TextField(blank=True)
    specializations = models.JSONField(default=list)  # List of specializations
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_accepting_patients = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Views to Implement:**
- `PsychologistProfileView` - Get/update profile
- `UploadProfileImageView` - Handle image uploads
- `SpecializationsView` - Manage specializations
- `AvailabilitySettingsView` - Configure availability

---

### 👥 **3. Enhanced Patient Management**
**Status**: ❌ Pending | **Estimated Time**: 30 minutes | **Priority**: HIGH

**Features to Implement:**
- Patient list with search and filter functionality
- Patient progress tracking and history
- Communication tools (notes, messages)
- Patient profile management
- Appointment history per patient

**Views to Implement:**
- `PatientListView` - List patients with search/filter
- `PatientDetailView` - Individual patient profile
- `PatientProgressView` - Track patient progress
- `PatientCommunicationView` - Communication tools
- `PatientAppointmentHistoryView` - Appointment history

**Search/Filter Features:**
- Search by name, email, phone
- Filter by appointment status, last visit date
- Sort by registration date, last appointment
- Export patient data

---

### 📅 **4. Schedule Management**
**Status**: ❌ Pending | **Estimated Time**: 25 minutes | **Priority**: HIGH

**Features to Implement:**
- Availability management (set working hours)
- Appointment booking interface
- Time slot management
- Calendar integration
- Recurring appointment support

**Models to Enhance:**
```python
# appointments/models.py - Enhance existing models
class AvailabilitySlot(models.Model):
    psychologist = models.ForeignKey(User, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['psychologist', 'day_of_week', 'start_time']

class TimeSlot(models.Model):
    psychologist = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        unique_together = ['psychologist', 'start_time']
```

**Views to Implement:**
- `AvailabilityManagementView` - Set working hours
- `TimeSlotView` - Manage available time slots
- `BookingCalendarView` - Calendar interface
- `RecurringAppointmentView` - Handle recurring appointments

---

## 📋 **Priority 2: Third-Party Integrations (MEDIUM PRIORITY)**

### 📹 **4. Twilio Video Integration**
**Status**: ❌ Pending | **Estimated Time**: 3-4 hours | **Priority**: MEDIUM

**Implementation Steps:**
1. Install Twilio SDK: `pip install twilio`
2. Create video room views
3. Generate access tokens
4. Integrate with appointment system

**Code Implementation:**
```python
# Create video_room_views.py
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
import uuid

def create_video_room(request, appointment_id):
    # Generate unique room name
    room_name = f"appointment-{appointment_id}-{uuid.uuid4().hex[:8]}"
    
    # Create access token
    token = AccessToken(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_API_KEY, settings.TWILIO_API_SECRET)
    token.identity = request.user.email
    grant = VideoGrant(room=room_name)
    token.add_grant(grant)
    
    return Response({
        'room_name': room_name,
        'access_token': token.to_jwt(),
        'expires_in': 3600
    })
```

**Environment Variables Needed:**
```bash
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_API_KEY=your_api_key
TWILIO_API_SECRET=your_api_secret
```

---

### 💳 **5. Stripe Payment Integration**
**Status**: ❌ Pending | **Estimated Time**: 4-5 hours | **Priority**: MEDIUM

**Implementation Steps:**
1. Install Stripe SDK: `pip install stripe`
2. Create payment views
3. Implement webhook handling
4. Add payment tracking

**Code Implementation:**
```python
# billing/stripe_views.py
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

def create_payment_intent(request):
    amount = int(request.data['amount'] * 100)  # Convert to cents
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency='aud',
        metadata={'invoice_id': request.data['invoice_id']}
    )
    return Response({'client_secret': intent.client_secret})

def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return Response({'error': 'Invalid payload'}, status=400)
    
    # Handle payment success
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Update payment status in database
        pass
    
    return Response({'status': 'success'})
```

**Environment Variables Needed:**
```bash
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

### 📱 **6. Celery Background Tasks**
**Status**: ❌ Pending | **Estimated Time**: 2-3 hours | **Priority**: LOW

**Implementation Steps:**
1. Configure Celery settings
2. Create task functions
3. Set up Redis backend
4. Implement notification tasks

**Code Implementation:**
```python
# tasks.py
from celery import shared_task
from twilio.rest import Client
from django.core.mail import send_mail

@shared_task
def send_appointment_reminder(appointment_id):
    """Send WhatsApp reminder 24 hours before appointment"""
    appointment = Appointment.objects.get(id=appointment_id)
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    message = client.messages.create(
        body=f"Reminder: You have an appointment tomorrow at {appointment.appointment_date}",
        from_=settings.TWILIO_WHATSAPP_FROM,
        to=f"whatsapp:+61{appointment.patient.phone_number}"
    )
    return message.sid

@shared_task
def send_payment_reminder(invoice_id):
    """Send email reminder for overdue payments"""
    invoice = Invoice.objects.get(id=invoice_id)
    send_mail(
        'Payment Reminder',
        f'Your invoice {invoice.invoice_number} is overdue.',
        settings.DEFAULT_FROM_EMAIL,
        [invoice.patient.email],
        fail_silently=False,
    )
```

---

## 📋 **Priority 3: Testing & Deployment (LOW PRIORITY)**

### 🧪 **7. API Testing**
**Status**: ❌ Pending | **Estimated Time**: 2-3 hours | **Priority**: LOW

**Testing Commands:**
```bash
# Test authentication
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "test123"}'

# Test intake form
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://127.0.0.1:8000/api/auth/intake-form/

# Test appointment booking
curl -X POST http://127.0.0.1:8000/api/appointments/book/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"psychologist_id": 1, "appointment_date": "2024-01-15T10:00:00Z"}'
```

**Test Coverage:**
- Authentication endpoints
- User management
- Intake form submission
- Appointment booking
- Payment processing
- Progress notes

---

### 🚀 **8. Frontend Integration**
**Status**: ❌ Pending | **Estimated Time**: 8-10 hours | **Priority**: LOW

**React Integration:**
```typescript
// React frontend integration
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Authentication service
class AuthService {
  async login(email: string, password: string) {
    const response = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return response.json();
  }
  
  async getIntakeForm() {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/auth/intake-form/`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return response.json();
  }
}

// Appointment service
class AppointmentService {
  async bookAppointment(appointmentData: any) {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${API_BASE_URL}/appointments/book/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(appointmentData)
    });
    return response.json();
  }
}
```

---

## 🎯 **Implementation Strategy**

### **Week 1: Dashboard Enhancements & Core Business Logic**
- **Day 1**: Dashboard view updates (15 min) + Psychologist profile management (20 min)
- **Day 2**: Enhanced patient management (30 min) + Schedule management (25 min)
- **Day 3-4**: Appointment models and serializers
- **Day 5**: Appointment views and booking logic

### **Week 2: Billing & Integrations**
- **Day 1**: Billing models and basic invoice generation
- **Day 2-3**: Stripe payment processing
- **Day 4**: Twilio video integration
- **Day 5**: Celery background tasks

### **Week 3: Resources & Testing**
- **Day 1**: Resources system (blog posts)
- **Day 2-3**: API testing and debugging
- **Day 4-5**: React frontend integration

---

## 💡 **Quick Start Hints**

### **For Appointment System:**
- Start with `Appointment` model first
- Use `django.utils.timezone.now()` for current time
- Add `unique_together = ['psychologist', 'appointment_date']` to prevent double-booking

### **For Billing System:**
- Calculate GST as `total_amount * 0.10`
- Use `uuid.uuid4().hex[:8]` for invoice numbers
- Store Stripe payment intent IDs for tracking

### **For Twilio Integration:**
- Install: `pip install twilio`
- Use environment variables for API keys
- Generate unique room names for each appointment

### **For Stripe Integration:**
- Install: `pip install stripe`
- Test with Stripe test keys first
- Use webhooks for payment confirmation

---

## 🚀 **Ready to Start?**

Pick any todo item and implement it step by step! The appointment system is probably the most important next step since it's core to the psychology clinic functionality.

**Recommended Order:**
1. **Dashboard Enhancements** (Quick wins - 90 minutes total)
   - Dashboard View Updates (15 min)
   - Psychologist Profile Management (20 min)
   - Enhanced Patient Management (30 min)
   - Schedule Management (25 min)
2. **Appointment System** (Core functionality)
3. **Billing System** (Payment processing)
4. **Twilio Integration** (Video calls)
5. **Stripe Integration** (Payments)
6. **Resources System** (Content management)
7. **Celery Tasks** (Background processing)
8. **API Testing** (Quality assurance)
9. **Frontend Integration** (User interface)

---

**Total Estimated Time**: 30-40 hours
**Current Progress**: 75% complete
**Remaining Work**: 25% (8-10 hours for core features)
**Dashboard Enhancements**: 90 minutes (1.5 hours) - Quick wins for immediate improvement

