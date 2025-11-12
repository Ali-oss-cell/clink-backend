# 📋 Resource API - Frontend Response Format

## Complete API Response Structure for Frontend Development

All resource endpoints now return **frontend-ready data** with display names, formatted URLs, and user-specific information.

---

## 🔹 **GET /api/resources/** - List Resources

### Response Format:

```json
{
  "count": 50,
  "next": "http://localhost:8000/api/resources/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Understanding Anxiety",
      "description": "A comprehensive guide to understanding and managing anxiety...",
      
      // Category (both code and display name)
      "category": "anxiety",
      "category_display": "Anxiety",
      
      // Type (both code and display name)
      "type": "article",
      "type_display": "Article",
      
      // Visual
      "icon": "😰",
      "thumbnail_url": null,
      "thumbnail_image_url": "http://localhost:8000/media/resources/images/anxiety_guide.jpg",
      
      // Duration
      "duration_minutes": 15,
      "estimated_time": "15 min read",
      
      // Difficulty
      "difficulty_level": "beginner",
      "difficulty_display": "Beginner",
      
      // Statistics
      "view_count": 1250,
      "is_featured": true,
      
      // User-specific
      "is_bookmarked": false,
      
      // Timestamps
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-20T14:30:00Z"
    }
  ]
}
```

---

## 🔹 **GET /api/resources/{id}/** - Single Resource Detail

### Complete Response Format:

```json
{
  // ========== BASIC INFO ==========
  "id": 1,
  "title": "Understanding Anxiety: A Complete Guide",
  "description": "A comprehensive guide to understanding and managing anxiety disorders...",
  
  // Category
  "category": "anxiety",
  "category_display": "Anxiety",
  
  // Type
  "type": "worksheet",
  "type_display": "Worksheet/PDF",
  
  // Visual
  "icon": "😰",
  "is_featured": true,
  
  // ========== CONTENT ==========
  "content": "<h1>Understanding Anxiety</h1><p>Full HTML content here...</p>",
  "content_type": "html",
  "content_type_display": "HTML",
  
  // Media URLs (legacy - for external links)
  "media_url": null,
  "download_url": null,
  "thumbnail_url": null,
  
  // ========== FILE URLs (FRONTEND READY) ==========
  // Image files
  "image_file": "/media/resources/images/anxiety_guide_abc123.jpg",
  "image_file_url": "http://localhost:8000/media/resources/images/anxiety_guide_abc123.jpg",
  "thumbnail_image_url": "http://localhost:8000/media/resources/images/anxiety_guide_abc123.jpg",
  
  // PDF files
  "pdf_file": "/media/resources/pdfs/anxiety_worksheet_xyz789.pdf",
  "pdf_file_url": "http://localhost:8000/media/resources/pdfs/anxiety_worksheet_xyz789.pdf",
  "download_file_url": "http://localhost:8000/media/resources/pdfs/anxiety_worksheet_xyz789.pdf",
  
  // ========== MEDIA FLAGS (for conditional rendering) ==========
  "has_media": false,        // true if media_url exists
  "has_download": true,      // true if pdf_file or download_url exists
  "has_image": true,         // true if image_file or thumbnail_url exists
  
  // ========== METADATA ==========
  "author": "Dr. Sarah Johnson",
  "reviewer": "Dr. Michael Chen",
  "last_reviewed_date": "2024-01-10",
  "tags": ["anxiety", "coping-strategies", "self-help"],
  "references": [
    {
      "title": "Anxiety Research Study",
      "url": "https://example.com/study"
    }
  ],
  
  // ========== DURATION & DIFFICULTY ==========
  "duration_minutes": 20,
  "difficulty_level": "intermediate",
  "difficulty_display": "Intermediate",
  "estimated_reading_time": "20 min read",
  
  // ========== STATISTICS ==========
  "view_count": 1250,
  "average_rating": 4.5,
  "total_ratings": 42,
  
  // ========== USER-SPECIFIC DATA ==========
  "is_bookmarked": true,
  "user_progress": 75,  // 0-100 percentage
  "user_rating": {
    "rating": 5,
    "review": "This guide was very helpful!",
    "created_at": "2024-01-18T10:00:00Z",
    "updated_at": "2024-01-18T10:00:00Z"
  },
  // OR null if user hasn't rated:
  // "user_rating": null,
  
  // ========== RELATED RESOURCES ==========
  "related_resources": [
    {
      "id": 2,
      "title": "Coping with Panic Attacks",
      "type": "article",
      "type_display": "Article",
      "icon": "😰",
      "thumbnail_url": null,
      "thumbnail_image_url": "http://localhost:8000/media/resources/images/panic_guide.jpg"
    },
    {
      "id": 3,
      "title": "Breathing Exercises for Anxiety",
      "type": "video",
      "type_display": "Video",
      "icon": "🧘",
      "thumbnail_url": null,
      "thumbnail_image_url": "http://localhost:8000/media/resources/images/breathing.jpg"
    }
  ],
  
  // ========== STATUS ==========
  "is_published": true,
  
  // ========== TIMESTAMPS ==========
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-20T14:30:00Z"
}
```

---

## 🎨 Frontend Usage Examples

### **1. Display Resource Card**

```tsx
interface ResourceCard {
  id: number;
  title: string;
  description: string;
  category: string;
  category_display: string;
  type: string;
  type_display: string;
  icon: string;
  thumbnail_image_url: string | null;
  estimated_time: string;
  difficulty_display: string;
  view_count: number;
  is_bookmarked: boolean;
  is_featured: boolean;
}

function ResourceCard({ resource }: { resource: ResourceCard }) {
  return (
    <div className="resource-card">
      {/* Image */}
      {resource.thumbnail_image_url && (
        <img src={resource.thumbnail_image_url} alt={resource.title} />
      )}
      
      {/* Category Badge */}
      <span className="category">{resource.category_display}</span>
      
      {/* Title */}
      <h3>{resource.title}</h3>
      
      {/* Description */}
      <p>{resource.description}</p>
      
      {/* Meta Info */}
      <div className="meta">
        <span>{resource.type_display}</span>
        <span>{resource.estimated_time}</span>
        <span>{resource.difficulty_display}</span>
      </div>
      
      {/* Bookmark Button */}
      <button onClick={() => toggleBookmark(resource.id)}>
        {resource.is_bookmarked ? '⭐' : '☆'}
      </button>
    </div>
  );
}
```

### **2. Display Resource Detail Page**

```tsx
interface ResourceDetail {
  id: number;
  title: string;
  description: string;
  category_display: string;
  type_display: string;
  content: string;
  thumbnail_image_url: string | null;
  pdf_file_url: string | null;
  download_file_url: string | null;
  has_media: boolean;
  has_download: boolean;
  has_image: boolean;
  media_url: string | null;
  duration_minutes: number;
  difficulty_display: string;
  average_rating: number;
  total_ratings: number;
  is_bookmarked: boolean;
  user_progress: number;
  user_rating: {
    rating: number;
    review: string;
  } | null;
  related_resources: Array<{
    id: number;
    title: string;
    type_display: string;
    thumbnail_image_url: string | null;
  }>;
}

function ResourceDetailPage({ resource }: { resource: ResourceDetail }) {
  return (
    <div className="resource-detail">
      {/* Header Image */}
      {resource.has_image && resource.thumbnail_image_url && (
        <img 
          src={resource.thumbnail_image_url} 
          alt={resource.title}
          className="header-image"
        />
      )}
      
      {/* Title & Meta */}
      <h1>{resource.title}</h1>
      <div className="meta">
        <span>{resource.category_display}</span>
        <span>{resource.type_display}</span>
        <span>{resource.difficulty_display}</span>
        <span>{resource.duration_minutes} min</span>
      </div>
      
      {/* Rating */}
      <div className="rating">
        <span>⭐ {resource.average_rating}</span>
        <span>({resource.total_ratings} ratings)</span>
      </div>
      
      {/* User Progress (for videos/audio) */}
      {resource.user_progress > 0 && (
        <div className="progress">
          <progress value={resource.user_progress} max={100} />
          <span>{resource.user_progress}% complete</span>
        </div>
      )}
      
      {/* User Rating */}
      {resource.user_rating && (
        <div className="user-rating">
          <p>Your rating: {resource.user_rating.rating} ⭐</p>
          <p>{resource.user_rating.review}</p>
        </div>
      )}
      
      {/* Media Player (if video/audio) */}
      {resource.has_media && resource.media_url && (
        <video src={resource.media_url} controls />
      )}
      
      {/* Content */}
      <div 
        className="content"
        dangerouslySetInnerHTML={{ __html: resource.content }}
      />
      
      {/* Download Button */}
      {resource.has_download && resource.download_file_url && (
        <a 
          href={resource.download_file_url} 
          download
          className="download-btn"
        >
          📥 Download PDF
        </a>
      )}
      
      {/* Actions */}
      <div className="actions">
        <button onClick={() => toggleBookmark(resource.id)}>
          {resource.is_bookmarked ? '⭐ Bookmarked' : '☆ Bookmark'}
        </button>
        <button onClick={() => openRatingModal(resource.id)}>
          Rate this resource
        </button>
      </div>
      
      {/* Related Resources */}
      {resource.related_resources.length > 0 && (
        <div className="related-resources">
          <h2>Related Resources</h2>
          {resource.related_resources.map(related => (
            <ResourceCard key={related.id} resource={related} />
          ))}
        </div>
      )}
    </div>
  );
}
```

### **3. Conditional Rendering Helpers**

```tsx
// Use the flags for easy conditional rendering
function ResourceMedia({ resource }: { resource: ResourceDetail }) {
  if (resource.has_media && resource.media_url) {
    return <VideoPlayer src={resource.media_url} />;
  }
  
  if (resource.has_image && resource.thumbnail_image_url) {
    return <img src={resource.thumbnail_image_url} alt={resource.title} />;
  }
  
  return <div className="placeholder">No media available</div>;
}

function ResourceDownload({ resource }: { resource: ResourceDetail }) {
  if (!resource.has_download) return null;
  
  const downloadUrl = resource.download_file_url || resource.download_url;
  
  return (
    <a href={downloadUrl} download className="download-btn">
      📥 Download {resource.type_display}
    </a>
  );
}
```

---

## 📊 Field Reference

### **Display Fields** (Use these for UI)
- `category_display` - "Anxiety", "Depression", etc.
- `type_display` - "Article", "Video", "Worksheet/PDF", etc.
- `difficulty_display` - "Beginner", "Intermediate", "Advanced"
- `content_type_display` - "HTML", "Markdown", "Video URL", etc.
- `estimated_time` - "15 min read" or "20 min"

### **URL Fields** (Use these for images/files)
- `thumbnail_image_url` - **Primary image URL** (prefers uploaded file)
- `image_file_url` - Full URL to uploaded image
- `pdf_file_url` - Full URL to uploaded PDF
- `download_file_url` - **Primary download URL** (prefers PDF file)

### **Boolean Flags** (For conditional rendering)
- `has_media` - true if video/audio URL exists
- `has_download` - true if PDF or download URL exists
- `has_image` - true if image file or thumbnail URL exists

### **User-Specific Data**
- `is_bookmarked` - boolean
- `user_progress` - 0-100 (percentage)
- `user_rating` - object with rating/review or null

---

## ✅ Summary

**All data is frontend-ready:**
- ✅ Display names for all choices (category, type, difficulty)
- ✅ Full URLs for all files (images, PDFs)
- ✅ Boolean flags for conditional rendering
- ✅ User-specific data (bookmarks, progress, ratings)
- ✅ Related resources included
- ✅ Formatted time strings
- ✅ All timestamps in ISO 8601 format

**The frontend can build the entire UI using just this response!** 🎉

