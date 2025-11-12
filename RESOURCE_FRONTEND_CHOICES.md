# 🎯 Resource API - Exact Frontend Choices & File Types

## Complete list of all choices and file types for frontend implementation

---

## 📁 **FILE UPLOAD TYPES** (Server Storage)

**⚠️ IMPORTANT: The system only supports file uploads for Images and PDFs. Videos and audio must use external URLs.**

### **1. Image File Upload** (`image_file`) ✅

**Supported File Formats:**
```typescript
// Exact MIME types accepted
const IMAGE_ACCEPT_TYPES = [
  'image/jpeg',      // .jpg, .jpeg
  'image/png',       // .png
  'image/gif',       // .gif
  'image/webp',      // .webp
  'image/bmp',       // .bmp
  'image/tiff',      // .tiff, .tif
  'image/svg+xml'    // .svg (if supported)
];

// HTML accept attribute
accept="image/jpeg,image/png,image/gif,image/webp,image/bmp,image/tiff"

// Or simpler
accept="image/*"
```

**File Size Recommendations:**
- Maximum: 10MB (recommended)
- Optimal: 500KB - 2MB
- Dimensions: 1200x800px (recommended for thumbnails)

**Storage Location:**
- Server path: `media/resources/images/`
- URL format: `http://localhost:8000/media/resources/images/filename.jpg`

---

### **2. PDF File Upload** (`pdf_file`) ✅

**Supported File Formats:**
```typescript
// Exact MIME type
const PDF_ACCEPT_TYPE = [
  'application/pdf'  // .pdf
];

// HTML accept attribute
accept="application/pdf"
```

**File Size Recommendations:**
- Maximum: 50MB (recommended)
- Optimal: 1MB - 10MB
- Pages: Any number of pages

**Storage Location:**
- Server path: `media/resources/pdfs/`
- URL format: `http://localhost:8000/media/resources/pdfs/filename.pdf`

---

## 🔗 **EXTERNAL URLS** (Not File Uploads)

### **3. Video/Audio URLs** (`media_url`) ⚠️

**NOT a file upload** - Use external video/audio hosting services:

```typescript
// Examples of supported URLs:
const VIDEO_AUDIO_URLS = [
  'https://www.youtube.com/watch?v=...',      // YouTube
  'https://youtu.be/...',                      // YouTube short
  'https://vimeo.com/...',                     // Vimeo
  'https://www.youtube.com/embed/...',         // YouTube embed
  'https://example.com/video.mp4',             // Direct video URL
  'https://example.com/audio.mp3',             // Direct audio URL
  'https://soundcloud.com/...',                // SoundCloud
  // Any valid video/audio URL
];
```

**How to use:**
- Set `content_type` to `'video_url'` or `'audio_url'`
- Set `media_url` field to the external URL
- **Do NOT** try to upload video/audio files directly

**Example:**
```json
{
  "type": "video",
  "content_type": "video_url",
  "media_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

---

### **4. External Download URLs** (`download_url`) ⚠️

**NOT a file upload** - Use external file hosting:

```typescript
// Examples:
const DOWNLOAD_URLS = [
  'https://example.com/file.pdf',
  'https://drive.google.com/file/d/...',
  'https://dropbox.com/s/...',
  // Any valid file download URL
];
```

**How to use:**
- Set `download_url` field to the external URL
- **Do NOT** try to upload files other than images/PDFs

---

### **5. External Thumbnail URLs** (`thumbnail_url`) ⚠️

**NOT a file upload** - Use external image hosting:

```typescript
// Examples:
const THUMBNAIL_URLS = [
  'https://example.com/image.jpg',
  'https://imgur.com/...',
  'https://unsplash.com/...',
  // Any valid image URL
];
```

**How to use:**
- Set `thumbnail_url` field to the external URL
- **OR** use `image_file` to upload directly (preferred)

---

## 📋 **CATEGORY CHOICES**

**Exact values for frontend dropdown/select:**

```typescript
const CATEGORY_CHOICES = [
  { value: 'anxiety', label: 'Anxiety', icon: '😰' },
  { value: 'depression', label: 'Depression', icon: '💙' },
  { value: 'stress', label: 'Stress Management', icon: '😓' },
  { value: 'sleep', label: 'Sleep', icon: '😴' },
  { value: 'mindfulness', label: 'Mindfulness & Meditation', icon: '🧘' },
  { value: 'relationships', label: 'Relationships', icon: '💕' },
  { value: 'self-care', label: 'Self-Care', icon: '🌟' },
  { value: 'grief', label: 'Grief & Loss', icon: '🕊️' },
  { value: 'trauma', label: 'Trauma', icon: '🛡️' },
  { value: 'addiction', label: 'Addiction Support', icon: '🆘' }
];
```

**Frontend Usage:**
```tsx
<select name="category" required>
  <option value="anxiety">😰 Anxiety</option>
  <option value="depression">💙 Depression</option>
  <option value="stress">😓 Stress Management</option>
  <option value="sleep">😴 Sleep</option>
  <option value="mindfulness">🧘 Mindfulness & Meditation</option>
  <option value="relationships">💕 Relationships</option>
  <option value="self-care">🌟 Self-Care</option>
  <option value="grief">🕊️ Grief & Loss</option>
  <option value="trauma">🛡️ Trauma</option>
  <option value="addiction">🆘 Addiction Support</option>
</select>
```

---

## 📝 **TYPE CHOICES**

**Exact values for resource type:**

```typescript
const TYPE_CHOICES = [
  { value: 'article', label: 'Article', icon: '📄' },
  { value: 'video', label: 'Video', icon: '🎥' },
  { value: 'audio', label: 'Audio/Meditation', icon: '🎧' },
  { value: 'guide', label: 'Guide', icon: '📖' },
  { value: 'worksheet', label: 'Worksheet/PDF', icon: '📋' },
  { value: 'quiz', label: 'Quiz/Assessment', icon: '❓' },
  { value: 'infographic', label: 'Infographic', icon: '📊' }
];
```

**Frontend Usage:**
```tsx
<select name="type" required>
  <option value="article">📄 Article</option>
  <option value="video">🎥 Video</option>
  <option value="audio">🎧 Audio/Meditation</option>
  <option value="guide">📖 Guide</option>
  <option value="worksheet">📋 Worksheet/PDF</option>
  <option value="quiz">❓ Quiz/Assessment</option>
  <option value="infographic">📊 Infographic</option>
</select>
```

---

## 🎚️ **DIFFICULTY LEVEL CHOICES**

**Exact values:**

```typescript
const DIFFICULTY_CHOICES = [
  { value: 'beginner', label: 'Beginner', color: 'green' },
  { value: 'intermediate', label: 'Intermediate', color: 'orange' },
  { value: 'advanced', label: 'Advanced', color: 'red' }
];
```

**Frontend Usage:**
```tsx
<select name="difficulty_level" defaultValue="beginner">
  <option value="beginner">Beginner</option>
  <option value="intermediate">Intermediate</option>
  <option value="advanced">Advanced</option>
</select>
```

---

## 📄 **CONTENT TYPE CHOICES**

**Exact values for content format:**

```typescript
const CONTENT_TYPE_CHOICES = [
  { value: 'html', label: 'HTML', description: 'Rich HTML content' },
  { value: 'markdown', label: 'Markdown', description: 'Markdown formatted text' },
  { value: 'video_url', label: 'Video URL', description: 'External video link (YouTube, Vimeo)' },
  { value: 'audio_url', label: 'Audio URL', description: 'External audio link' },
  { value: 'pdf_url', label: 'PDF URL', description: 'External PDF link' }
];
```

**Frontend Usage:**
```tsx
<select name="content_type" defaultValue="html">
  <option value="html">HTML</option>
  <option value="markdown">Markdown</option>
  <option value="video_url">Video URL</option>
  <option value="audio_url">Audio URL</option>
  <option value="pdf_url">PDF URL</option>
</select>
```

---

## 🎨 **ICON CHOICES** (Optional)

**Recommended emoji icons (can be any emoji):**

```typescript
const ICON_SUGGESTIONS = {
  anxiety: '😰',
  depression: '💙',
  stress: '😓',
  sleep: '😴',
  mindfulness: '🧘',
  relationships: '💕',
  selfCare: '🌟',
  grief: '🕊️',
  trauma: '🛡️',
  addiction: '🆘',
  article: '📄',
  video: '🎥',
  audio: '🎧',
  guide: '📖',
  worksheet: '📋',
  quiz: '❓',
  infographic: '📊'
};
```

**Default:** `📚` (if not provided)

---

## ✅ **COMPLETE FRONTEND FORM EXAMPLE**

```tsx
import React, { useState } from 'react';

interface ResourceFormData {
  title: string;
  description: string;
  category: string;
  type: string;
  difficulty_level: string;
  content_type: string;
  content: string;
  media_url?: string;
  download_url?: string;
  thumbnail_url?: string;
  icon?: string;
  duration_minutes: number;
  author?: string;
  tags: string[];
  is_published: boolean;
  is_featured: boolean;
  image_file?: File;
  pdf_file?: File;
}

const ResourceForm: React.FC = () => {
  const [formData, setFormData] = useState<ResourceFormData>({
    title: '',
    description: '',
    category: 'anxiety',
    type: 'article',
    difficulty_level: 'beginner',
    content_type: 'html',
    content: '',
    duration_minutes: 10,
    tags: [],
    is_published: true,
    is_featured: false
  });

  const [imageFile, setImageFile] = useState<File | null>(null);
  const [pdfFile, setPdfFile] = useState<File | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const formDataToSend = new FormData();
    
    // Text fields
    formDataToSend.append('title', formData.title);
    formDataToSend.append('description', formData.description);
    formDataToSend.append('category', formData.category);
    formDataToSend.append('type', formData.type);
    formDataToSend.append('difficulty_level', formData.difficulty_level);
    formDataToSend.append('content_type', formData.content_type);
    formDataToSend.append('content', formData.content);
    formDataToSend.append('duration_minutes', formData.duration_minutes.toString());
    formDataToSend.append('is_published', formData.is_published.toString());
    formDataToSend.append('is_featured', formData.is_featured.toString());
    
    // Optional fields
    if (formData.icon) formDataToSend.append('icon', formData.icon);
    if (formData.author) formDataToSend.append('author', formData.author);
    if (formData.media_url) formDataToSend.append('media_url', formData.media_url);
    if (formData.download_url) formDataToSend.append('download_url', formData.download_url);
    if (formData.thumbnail_url) formDataToSend.append('thumbnail_url', formData.thumbnail_url);
    if (formData.tags.length > 0) {
      formDataToSend.append('tags', JSON.stringify(formData.tags));
    }
    
    // File uploads
    if (imageFile) {
      formDataToSend.append('image_file', imageFile);
    }
    if (pdfFile) {
      formDataToSend.append('pdf_file', pdfFile);
    }

    // Submit to API
    const response = await fetch('/api/resources/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: formDataToSend
    });

    if (response.ok) {
      const resource = await response.json();
      console.log('Resource created:', resource);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Title */}
      <input
        type="text"
        name="title"
        value={formData.title}
        onChange={(e) => setFormData({...formData, title: e.target.value})}
        placeholder="Resource Title"
        required
        maxLength={255}
      />

      {/* Description */}
      <textarea
        name="description"
        value={formData.description}
        onChange={(e) => setFormData({...formData, description: e.target.value})}
        placeholder="Brief description"
        required
      />

      {/* Category */}
      <select
        name="category"
        value={formData.category}
        onChange={(e) => setFormData({...formData, category: e.target.value})}
        required
      >
        <option value="anxiety">😰 Anxiety</option>
        <option value="depression">💙 Depression</option>
        <option value="stress">😓 Stress Management</option>
        <option value="sleep">😴 Sleep</option>
        <option value="mindfulness">🧘 Mindfulness & Meditation</option>
        <option value="relationships">💕 Relationships</option>
        <option value="self-care">🌟 Self-Care</option>
        <option value="grief">🕊️ Grief & Loss</option>
        <option value="trauma">🛡️ Trauma</option>
        <option value="addiction">🆘 Addiction Support</option>
      </select>

      {/* Type */}
      <select
        name="type"
        value={formData.type}
        onChange={(e) => setFormData({...formData, type: e.target.value})}
        required
      >
        <option value="article">📄 Article</option>
        <option value="video">🎥 Video</option>
        <option value="audio">🎧 Audio/Meditation</option>
        <option value="guide">📖 Guide</option>
        <option value="worksheet">📋 Worksheet/PDF</option>
        <option value="quiz">❓ Quiz/Assessment</option>
        <option value="infographic">📊 Infographic</option>
      </select>

      {/* Difficulty */}
      <select
        name="difficulty_level"
        value={formData.difficulty_level}
        onChange={(e) => setFormData({...formData, difficulty_level: e.target.value})}
      >
        <option value="beginner">Beginner</option>
        <option value="intermediate">Intermediate</option>
        <option value="advanced">Advanced</option>
      </select>

      {/* Content Type */}
      <select
        name="content_type"
        value={formData.content_type}
        onChange={(e) => setFormData({...formData, content_type: e.target.value})}
      >
        <option value="html">HTML</option>
        <option value="markdown">Markdown</option>
        <option value="video_url">Video URL</option>
        <option value="audio_url">Audio URL</option>
        <option value="pdf_url">PDF URL</option>
      </select>

      {/* Content */}
      <textarea
        name="content"
        value={formData.content}
        onChange={(e) => setFormData({...formData, content: e.target.value})}
        placeholder="Full content (HTML/Markdown)"
      />

      {/* Image File Upload */}
      <input
        type="file"
        accept="image/jpeg,image/png,image/gif,image/webp,image/bmp,image/tiff"
        onChange={(e) => setImageFile(e.target.files?.[0] || null)}
      />
      <small>✅ Upload: JPEG, PNG, GIF, WebP, BMP, TIFF (Max 10MB)</small>

      {/* PDF File Upload */}
      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setPdfFile(e.target.files?.[0] || null)}
      />
      <small>✅ Upload: PDF only (Max 50MB)</small>

      {/* Video/Audio URL (NOT file upload) */}
      {formData.content_type === 'video_url' || formData.content_type === 'audio_url' ? (
        <input
          type="url"
          name="media_url"
          value={formData.media_url || ''}
          onChange={(e) => setFormData({...formData, media_url: e.target.value})}
          placeholder="https://www.youtube.com/watch?v=... or https://vimeo.com/..."
        />
      ) : null}
      <small>⚠️ Video/Audio: Use external URLs (YouTube, Vimeo, etc.) - NOT file uploads</small>

      {/* Duration */}
      <input
        type="number"
        name="duration_minutes"
        value={formData.duration_minutes}
        onChange={(e) => setFormData({...formData, duration_minutes: parseInt(e.target.value)})}
        min="1"
        placeholder="Duration in minutes"
      />

      {/* Published */}
      <label>
        <input
          type="checkbox"
          checked={formData.is_published}
          onChange={(e) => setFormData({...formData, is_published: e.target.checked})}
        />
        Published
      </label>

      {/* Featured */}
      <label>
        <input
          type="checkbox"
          checked={formData.is_featured}
          onChange={(e) => setFormData({...formData, is_featured: e.target.checked})}
        />
        Featured
      </label>

      <button type="submit">Create Resource</button>
    </form>
  );
};

export default ResourceForm;
```

---

## 📊 **TYPE CONSTANTS FOR FRONTEND**

```typescript
// Copy-paste ready constants
export const RESOURCE_CATEGORIES = [
  { value: 'anxiety', label: 'Anxiety', icon: '😰' },
  { value: 'depression', label: 'Depression', icon: '💙' },
  { value: 'stress', label: 'Stress Management', icon: '😓' },
  { value: 'sleep', label: 'Sleep', icon: '😴' },
  { value: 'mindfulness', label: 'Mindfulness & Meditation', icon: '🧘' },
  { value: 'relationships', label: 'Relationships', icon: '💕' },
  { value: 'self-care', label: 'Self-Care', icon: '🌟' },
  { value: 'grief', label: 'Grief & Loss', icon: '🕊️' },
  { value: 'trauma', label: 'Trauma', icon: '🛡️' },
  { value: 'addiction', label: 'Addiction Support', icon: '🆘' }
] as const;

export const RESOURCE_TYPES = [
  { value: 'article', label: 'Article', icon: '📄' },
  { value: 'video', label: 'Video', icon: '🎥' },
  { value: 'audio', label: 'Audio/Meditation', icon: '🎧' },
  { value: 'guide', label: 'Guide', icon: '📖' },
  { value: 'worksheet', label: 'Worksheet/PDF', icon: '📋' },
  { value: 'quiz', label: 'Quiz/Assessment', icon: '❓' },
  { value: 'infographic', label: 'Infographic', icon: '📊' }
] as const;

export const DIFFICULTY_LEVELS = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'intermediate', label: 'Intermediate' },
  { value: 'advanced', label: 'Advanced' }
] as const;

export const CONTENT_TYPES = [
  { value: 'html', label: 'HTML' },
  { value: 'markdown', label: 'Markdown' },
  { value: 'video_url', label: 'Video URL' },
  { value: 'audio_url', label: 'Audio URL' },
  { value: 'pdf_url', label: 'PDF URL' }
] as const;

// File upload accept strings
export const IMAGE_ACCEPT = 'image/jpeg,image/png,image/gif,image/webp,image/bmp,image/tiff';
export const PDF_ACCEPT = 'application/pdf';
```

---

## ✅ **SUMMARY**

### **File Uploads (Server Storage):**
- ✅ **Images**: JPEG, PNG, GIF, WebP, BMP, TIFF (Max 10MB) - Upload via `image_file`
- ✅ **PDFs**: PDF only (Max 50MB) - Upload via `pdf_file`

### **External URLs (NOT File Uploads):**
- ⚠️ **Videos**: Use external URLs (YouTube, Vimeo, etc.) - Set `media_url` field
- ⚠️ **Audio**: Use external URLs (SoundCloud, direct links, etc.) - Set `media_url` field
- ⚠️ **Other Files**: Use external URLs - Set `download_url` field
- ⚠️ **Thumbnails**: Use external URLs OR upload via `image_file` (preferred)

### **Choices:**
- ✅ **10 Categories** (anxiety, depression, stress, sleep, mindfulness, relationships, self-care, grief, trauma, addiction)
- ✅ **7 Types** (article, video, audio, guide, worksheet, quiz, infographic)
- ✅ **3 Difficulty Levels** (beginner, intermediate, advanced)
- ✅ **5 Content Types** (html, markdown, video_url, audio_url, pdf_url)

**All values are exact and ready to use in your frontend!** 🎉

