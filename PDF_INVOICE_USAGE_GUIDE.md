# 📄 PDF Invoice Usage Guide

## 🎯 **When to Use PDF Invoices**

The PDF invoice feature generates professional, downloadable invoices for psychology clinic services. Here's when and how to use it:

---

## 📋 **Invoice Creation Flow**

### **1. When Invoices Are Created**

Invoices are typically created **after an appointment is completed**:

```
Appointment Completed
    ↓
Invoice Created (manually or automatically)
    ↓
Invoice Status: "Draft" → "Sent"
    ↓
Patient/Admin Downloads PDF Invoice
    ↓
Payment Processed
    ↓
Invoice Status: "Paid"
```

**Invoice Creation Scenarios:**
- ✅ **After appointment completion** - When a session is marked as "completed"
- ✅ **Manual creation** - Admin/Practice Manager creates invoice via API
- ✅ **Automatic generation** - (Future: Auto-generate on appointment completion)

---

## 👥 **Who Can Download PDF Invoices**

### **Access Permissions:**

| User Role | Can Download? | Access Level |
|-----------|---------------|--------------|
| **Patient** | ✅ Yes | Only their own invoices |
| **Psychologist** | ❌ No | Cannot download invoices |
| **Practice Manager** | ✅ Yes | All invoices |
| **Admin** | ✅ Yes | All invoices |

### **Permission Check:**
```python
# Only these users can download:
- Admin users
- Practice Managers  
- The patient who owns the invoice
```

---

## 🎯 **Use Cases for PDF Invoices**

### **1. Patient Use Cases**

#### **📧 Email to Patient**
```javascript
// After invoice is created, send email with PDF link
GET /api/billing/invoices/{id}/download/
// Patient clicks link → Downloads PDF → Saves for records
```

**Why patients need PDFs:**
- ✅ **Tax records** - Keep for tax deductions (medical expenses)
- ✅ **Insurance claims** - Submit to private health insurance
- ✅ **Medicare claims** - Submit for Medicare rebate
- ✅ **Personal records** - Keep track of medical expenses
- ✅ **Reimbursement** - Submit to employer health plans

#### **💳 Payment Reference**
- Patient downloads PDF before making payment
- Uses invoice number for payment reference
- Keeps PDF as proof of payment

---

### **2. Clinic/Admin Use Cases**

#### **📊 Accounting & Bookkeeping**
```javascript
// Admin downloads all invoices for accounting period
GET /api/billing/invoices/?status=paid&created_at__gte=2024-01-01
// Download each invoice PDF for records
```

**Why clinic needs PDFs:**
- ✅ **Financial records** - Keep for accounting
- ✅ **Tax compliance** - GST reporting (Australian tax law)
- ✅ **Audit trail** - Proof of services provided
- ✅ **Client records** - Professional documentation
- ✅ **Legal compliance** - Required business records

#### **📧 Send to Patients**
- Email PDF invoice to patient automatically
- Include in appointment confirmation emails
- Send payment reminders with invoice PDF

#### **💼 Business Operations**
- Print invoices for in-person payments
- Archive invoices for record keeping
- Share with accountants/bookkeepers

---

### **3. Medicare & Insurance Claims**

#### **🏥 Medicare Claims**
```javascript
// Patient downloads invoice PDF
// Submits to Medicare with claim form
// Medicare processes rebate
```

**Medicare Requirements:**
- ✅ Invoice must show Medicare item number
- ✅ Must include service date and description
- ✅ Must show GST breakdown (Australian requirement)
- ✅ Must include ABN (Australian Business Number)

#### **🏥 Private Health Insurance**
- Patient submits PDF to insurance company
- Insurance processes claim
- Patient receives reimbursement

---

## 🔄 **Integration with Billing Flow**

### **Complete Billing Workflow:**

```
1. Appointment Completed
   ↓
2. Invoice Created
   POST /api/billing/invoices/
   {
     "patient": 1,
     "appointment": 5,
     "service_description": "Individual Therapy Session",
     "subtotal_amount": "180.00",
     "medicare_item_number": 1,
     "due_date": "2024-02-15"
   }
   ↓
3. Invoice Status: "sent"
   PUT /api/billing/invoices/{id}/
   { "status": "sent" }
   ↓
4. Patient Downloads PDF
   GET /api/billing/invoices/{id}/download/
   → Returns PDF file
   ↓
5. Patient Makes Payment
   POST /api/billing/payments/
   {
     "invoice": 1,
     "amount": "92.55",
     "payment_method": "stripe"
   }
   ↓
6. Invoice Status: "paid"
   PUT /api/billing/invoices/{id}/
   { "status": "paid", "paid_date": "2024-01-20" }
   ↓
7. Patient Downloads Updated PDF (shows "Paid" status)
   GET /api/billing/invoices/{id}/download/
```

---

## 💻 **Frontend Integration Examples**

### **React/TypeScript Example:**

```typescript
// Download Invoice PDF
const downloadInvoicePDF = async (invoiceId: number) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(
    `http://localhost:8000/api/billing/invoices/${invoiceId}/download/`,
    {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );
  
  if (response.ok) {
    // Get PDF blob
    const blob = await response.blob();
    
    // Create download link
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Invoice_${invoiceId}.pdf`;
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
};

// Use in component
<button onClick={() => downloadInvoicePDF(invoice.id)}>
  Download Invoice PDF
</button>
```

### **Email Integration:**

```python
# In your email service, attach PDF
from django.core.mail import EmailMessage

def send_invoice_email(invoice):
    # Generate PDF
    pdf_service = InvoicePDFService()
    pdf_buffer = pdf_service.generate_invoice_pdf(invoice)
    
    # Create email
    email = EmailMessage(
        subject=f'Invoice {invoice.invoice_number}',
        body='Please find your invoice attached.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[invoice.patient.email],
    )
    
    # Attach PDF
    email.attach(
        f'Invoice_{invoice.invoice_number}.pdf',
        pdf_buffer.read(),
        'application/pdf'
    )
    
    email.send()
```

---

## 📱 **User Interface Examples**

### **Patient Dashboard:**

```jsx
// Patient Invoice List
{invoices.map(invoice => (
  <div key={invoice.id} className="invoice-card">
    <h3>Invoice {invoice.invoice_number}</h3>
    <p>Amount: ${invoice.out_of_pocket}</p>
    <p>Status: {invoice.status}</p>
    <p>Due Date: {invoice.due_date}</p>
    
    {/* Download PDF Button */}
    <button onClick={() => downloadInvoicePDF(invoice.id)}>
      📄 Download Invoice PDF
    </button>
    
    {/* Payment Button */}
    {invoice.status !== 'paid' && (
      <button onClick={() => makePayment(invoice.id)}>
        💳 Pay Now
      </button>
    )}
  </div>
))}
```

### **Admin Invoice Management:**

```jsx
// Admin can download any invoice
{invoices.map(invoice => (
  <div key={invoice.id}>
    <span>{invoice.patient_name}</span>
    <span>{invoice.invoice_number}</span>
    <span>${invoice.total_amount}</span>
    <span>{invoice.status}</span>
    
    {/* Download PDF */}
    <button onClick={() => downloadInvoicePDF(invoice.id)}>
      📥 Download PDF
    </button>
    
    {/* Email PDF to Patient */}
    <button onClick={() => emailInvoicePDF(invoice.id)}>
      📧 Email PDF
    </button>
  </div>
))}
```

---

## 🎨 **PDF Invoice Contents**

The generated PDF includes:

### **Header:**
- ✅ Clinic name and logo
- ✅ Clinic address, phone, email
- ✅ ABN (Australian Business Number)
- ✅ "INVOICE" label

### **Invoice Details:**
- ✅ Invoice number (unique)
- ✅ Invoice date
- ✅ Due date
- ✅ Status (Draft/Sent/Paid/Overdue)

### **Patient Information:**
- ✅ Patient name
- ✅ Email address
- ✅ Phone number
- ✅ Address
- ✅ Medicare number (if applicable)

### **Service Details:**
- ✅ Service description
- ✅ Service date
- ✅ Psychologist name
- ✅ Session type (Telehealth/In-Person)
- ✅ Duration
- ✅ Medicare item number (if applicable)

### **Financial Breakdown:**
- ✅ Subtotal (ex. GST)
- ✅ GST amount (10%)
- ✅ Total (inc. GST)
- ✅ Medicare rebate (if applicable)
- ✅ **Amount Due** (out-of-pocket)

### **Payment Information:**
- ✅ Payment due date
- ✅ Payment methods accepted
- ✅ Overdue warnings (if applicable)
- ✅ Paid date (if paid)

### **Footer:**
- ✅ ABN
- ✅ GST compliance notice
- ✅ Payment terms
- ✅ Contact information

---

## ⚡ **Best Practices**

### **1. Download Timing:**
- ✅ **After invoice creation** - Send PDF immediately
- ✅ **Before payment** - Patient downloads to review
- ✅ **After payment** - Download updated PDF showing "Paid"
- ✅ **For records** - Download anytime for tax/insurance

### **2. Email Integration:**
- ✅ Attach PDF to invoice email
- ✅ Include download link in email
- ✅ Send PDF with payment reminders

### **3. Storage:**
- ✅ Patients: Save PDFs for tax records (7 years in Australia)
- ✅ Clinic: Archive PDFs for accounting records
- ✅ Both: Keep for Medicare/insurance claims

### **4. Security:**
- ✅ Only authorized users can download
- ✅ PDFs contain sensitive financial information
- ✅ Use HTTPS for downloads
- ✅ Log download activity (for audit)

---

## 🔗 **API Endpoint**

### **Download Invoice PDF:**

```http
GET /api/billing/invoices/{invoice_id}/download/

Headers:
  Authorization: Bearer {access_token}

Response:
  Content-Type: application/pdf
  Content-Disposition: attachment; filename="Invoice_INV-12345678.pdf"
  
  [PDF file binary data]
```

### **Example cURL:**

```bash
curl -X GET \
  'http://localhost:8000/api/billing/invoices/1/download/' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  --output invoice.pdf
```

---

## 📊 **Summary**

**Use PDF invoices when:**
1. ✅ **Sending to patients** - Email or download link
2. ✅ **Payment processing** - Patient needs invoice for payment
3. ✅ **Tax records** - Patient/clinic needs for tax purposes
4. ✅ **Medicare claims** - Patient submits to Medicare
5. ✅ **Insurance claims** - Patient submits to private insurance
6. ✅ **Accounting** - Clinic needs for bookkeeping
7. ✅ **Legal compliance** - Required business records
8. ✅ **Audit trail** - Proof of services and payments

**The PDF invoice is a professional, legally compliant document that serves multiple purposes in the psychology clinic billing workflow!** 📄✨

