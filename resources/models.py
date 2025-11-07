"""
Resources models for mental health resources and educational materials
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()


class Resource(models.Model):
    """Mental health resource model"""
    
    CATEGORY_CHOICES = [
        ('anxiety', 'Anxiety'),
        ('depression', 'Depression'),
        ('stress', 'Stress Management'),
        ('sleep', 'Sleep'),
        ('mindfulness', 'Mindfulness & Meditation'),
        ('relationships', 'Relationships'),
        ('self-care', 'Self-Care'),
        ('grief', 'Grief & Loss'),
        ('trauma', 'Trauma'),
        ('addiction', 'Addiction Support'),
    ]
    
    TYPE_CHOICES = [
        ('article', 'Article'),
        ('video', 'Video'),
        ('audio', 'Audio/Meditation'),
        ('guide', 'Guide'),
        ('worksheet', 'Worksheet/PDF'),
        ('quiz', 'Quiz/Assessment'),
        ('infographic', 'Infographic'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    CONTENT_TYPE_CHOICES = [
        ('html', 'HTML'),
        ('markdown', 'Markdown'),
        ('video_url', 'Video URL'),
        ('audio_url', 'Audio URL'),
        ('pdf_url', 'PDF URL'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=255, help_text="Resource title")
    description = models.TextField(help_text="Brief description of the resource")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    icon = models.CharField(max_length=10, default='📚', help_text="Emoji icon for display")
    
    # Content
    content = models.TextField(blank=True, help_text="Full content (HTML/Markdown)")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='html')
    media_url = models.URLField(blank=True, null=True, help_text="URL for video/audio resources")
    download_url = models.URLField(blank=True, null=True, help_text="URL for downloadable files")
    thumbnail_url = models.URLField(blank=True, null=True, help_text="Thumbnail image URL")
    
    # Metadata
    author = models.CharField(max_length=255, blank=True, help_text="Author name")
    reviewer = models.CharField(max_length=255, blank=True, help_text="Reviewer name")
    last_reviewed_date = models.DateField(null=True, blank=True)
    tags = models.JSONField(default=list, help_text="List of tags")
    references = models.JSONField(default=list, help_text="List of reference objects")
    
    # Duration and Difficulty
    duration_minutes = models.PositiveIntegerField(
        default=10,
        help_text="Estimated time to complete in minutes"
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='beginner'
    )
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0, help_text="Total number of views")
    
    # Status
    is_published = models.BooleanField(default=True, help_text="Whether resource is published")
    is_featured = models.BooleanField(default=False, help_text="Featured resource")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resources_resource'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['type']),
            models.Index(fields=['is_published']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
    
    @property
    def average_rating(self):
        """Calculate average rating"""
        ratings = self.ratings.all()
        if not ratings.exists():
            return 0.0
        return round(sum(r.rating for r in ratings) / ratings.count(), 1)
    
    @property
    def total_ratings(self):
        """Get total number of ratings"""
        return self.ratings.count()
    
    @property
    def estimated_reading_time(self):
        """Estimated reading time string"""
        if self.type in ['video', 'audio']:
            return f"{self.duration_minutes} minutes"
        else:
            return f"{self.duration_minutes} min read"


class ResourceBookmark(models.Model):
    """User bookmarks for resources"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_bookmarks')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'resources_bookmark'
        unique_together = ['user', 'resource']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.resource.title}"


class ResourceView(models.Model):
    """Track resource views for analytics"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_views')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='views')
    viewed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'resources_view'
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['user', 'resource']),
        ]
    
    def __str__(self):
        return f"{self.user.email} viewed {self.resource.title}"


class ResourceRating(models.Model):
    """User ratings and reviews for resources"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_ratings')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    review = models.TextField(blank=True, help_text="Optional review text")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resources_rating'
        unique_together = ['user', 'resource']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} rated {self.resource.title}: {self.rating}/5"


class ResourceProgress(models.Model):
    """Track user progress on video/audio resources"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_progress')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, related_name='progress')
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Progress from 0 to 100%"
    )
    current_time_seconds = models.PositiveIntegerField(
        default=0,
        help_text="Current playback position in seconds"
    )
    is_completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'resources_progress'
        unique_together = ['user', 'resource']
        ordering = ['-last_accessed']
    
    def __str__(self):
        return f"{self.user.email} - {self.resource.title}: {self.progress_percentage}%"
    
    def save(self, *args, **kwargs):
        # Mark as completed if progress is 100%
        if self.progress_percentage >= 100:
            self.is_completed = True
        super().save(*args, **kwargs)
