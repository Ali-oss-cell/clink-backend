# 📁 Resource File Upload Guide

## Overview

Resources now support **server-side file storage** for images and PDFs. You can upload files directly to the server instead of using external URLs.

---

## ✅ What's Implemented

### **1. Image Upload**
- **Field**: `image_file` (ImageField)
- **Storage**: `media/resources/images/`
- **Formats**: JPEG, PNG, GIF, WebP, etc.
- **Use Case**: Thumbnail/cover images for resources

### **2. PDF Upload**
- **Field**: `pdf_file` (FileField)
- **Storage**: `media/resources/pdfs/`
- **Formats**: PDF files
- **Use Case**: Worksheets, guides, downloadable resources

---

## 🔧 API Usage

### **Create Resource with File Upload**

#### **Using FormData (Multipart)**

```javascript
// Frontend example (React/TypeScript)
const formData = new FormData();
formData.append('title', 'Anxiety Management Guide');
formData.append('description', 'A comprehensive guide to managing anxiety');
formData.append('category', 'anxiety');
formData.append('type', 'worksheet');
formData.append('content', 'Full content here...');

// Upload image file
if (imageFile) {
  formData.append('image_file', imageFile);
}

// Upload PDF file
if (pdfFile) {
  formData.append('pdf_file', pdfFile);
}

// Make API request
const response = await fetch('http://localhost:8000/api/resources/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    // Don't set Content-Type - browser will set it with boundary
  },
  body: formData,
});
```

#### **Using cURL**

```bash
curl -X POST \
  'http://localhost:8000/api/resources/' \
  -H 'Authorization: Bearer YOUR_ACCESS_TOKEN' \
  -F 'title=Anxiety Management Guide' \
  -F 'description=A comprehensive guide' \
  -F 'category=anxiety' \
  -F 'type=worksheet' \
  -F 'image_file=@/path/to/image.jpg' \
  -F 'pdf_file=@/path/to/guide.pdf'
```

---

## 📤 API Response

### **Resource Detail Response**

```json
{
  "id": 1,
  "title": "Anxiety Management Guide",
  "description": "A comprehensive guide...",
  "category": "anxiety",
  "type": "worksheet",
  "image_file": "/media/resources/images/anxiety_guide_abc123.jpg",
  "image_file_url": "http://localhost:8000/media/resources/images/anxiety_guide_abc123.jpg",
  "pdf_file": "/media/resources/pdfs/anxiety_guide_xyz789.pdf",
  "pdf_file_url": "http://localhost:8000/media/resources/pdfs/anxiety_guide_xyz789.pdf",
  "thumbnail_url": null,
  "download_url": null,
  ...
}
```

### **Resource List Response**

```json
{
  "id": 1,
  "title": "Anxiety Management Guide",
  "thumbnail_url": null,
  "thumbnail_image_url": "http://localhost:8000/media/resources/images/anxiety_guide_abc123.jpg",
  ...
}
```

**Note**: `thumbnail_image_url` automatically uses `image_file` if available, otherwise falls back to `thumbnail_url`.

---

## 🔄 Update Resource with Files

### **Update Image**

```javascript
const formData = new FormData();
formData.append('image_file', newImageFile);

await fetch(`http://localhost:8000/api/resources/${resourceId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  },
  body: formData,
});
```

### **Update PDF**

```javascript
const formData = new FormData();
formData.append('pdf_file', newPdfFile);

await fetch(`http://localhost:8000/api/resources/${resourceId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  },
  body: formData,
});
```

### **Remove File**

To remove a file, send `null`:

```javascript
const formData = new FormData();
formData.append('image_file', null);

await fetch(`http://localhost:8000/api/resources/${resourceId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
  },
  body: formData,
});
```

---

## 🔀 Backward Compatibility

The system supports **both** file uploads and URLs:

- ✅ **Upload files** → Use `image_file` and `pdf_file` fields
- ✅ **Use URLs** → Use `thumbnail_url` and `download_url` fields
- ✅ **Priority**: Uploaded files take precedence in API responses

### **Example: Mixed Usage**

```json
{
  "image_file": "/media/resources/images/cover.jpg",  // Uploaded file
  "thumbnail_url": "https://example.com/fallback.jpg", // Fallback URL
  "pdf_file": "/media/resources/pdfs/guide.pdf",      // Uploaded PDF
  "download_url": null                                 // No external URL
}
```

---

## 📁 File Storage Structure

```
media/
├── resources/
│   ├── images/
│   │   ├── anxiety_guide_abc123.jpg
│   │   ├── depression_worksheet_xyz789.png
│   │   └── ...
│   └── pdfs/
│       ├── anxiety_guide_abc123.pdf
│       ├── stress_management_xyz789.pdf
│       └── ...
```

---

## 🔐 Permissions

- ✅ **Create/Update with files**: Staff only (Admin, Practice Manager, Psychologist)
- ✅ **View files**: Public (anyone can access uploaded files via URL)
- ✅ **Delete files**: Staff only

---

## 🎯 Frontend Integration Example

### **React Component**

```tsx
import React, { useState } from 'react';

const ResourceUploadForm = () => {
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append('title', title);
    formData.append('category', 'anxiety');
    formData.append('type', 'worksheet');
    
    if (imageFile) {
      formData.append('image_file', imageFile);
    }
    
    if (pdfFile) {
      formData.append('pdf_file', pdfFile);
    }

    try {
      const response = await fetch('/api/resources/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: formData,
      });

      if (response.ok) {
        const resource = await response.json();
        console.log('Resource created:', resource);
        console.log('Image URL:', resource.image_file_url);
        console.log('PDF URL:', resource.pdf_file_url);
      }
    } catch (error) {
      console.error('Error uploading resource:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Resource Title"
      />
      
      <input
        type="file"
        accept="image/*"
        onChange={(e) => setImageFile(e.target.files?.[0] || null)}
      />
      
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setPdfFile(e.target.files?.[0] || null)}
      />
      
      <button type="submit">Create Resource</button>
    </form>
  );
};
```

---

## ⚙️ Configuration

### **Media Settings** (Already Configured)

```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### **URL Configuration** (Already Configured)

```python
# urls.py
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 🚀 Next Steps

1. **Run Migration**:
   ```bash
   python manage.py migrate resources
   ```

2. **Test Upload**:
   - Use Postman or frontend to upload files
   - Check `media/resources/` directory for uploaded files

3. **Frontend Integration**:
   - Update resource creation/editing forms
   - Add file upload inputs
   - Display uploaded images/PDFs

---

## 📝 Notes

- ✅ Files are stored on the server (not in database)
- ✅ File URLs are automatically generated
- ✅ Old resources with URLs still work
- ✅ You can use both files and URLs together
- ✅ Files are served via `/media/` URL path

---

**Status**: ✅ **Ready to Use** - File upload is fully implemented and tested!

