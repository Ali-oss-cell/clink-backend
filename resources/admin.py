"""
Admin configuration for resources app
"""

from django.contrib import admin
from .models import Resource, ResourceBookmark, ResourceView, ResourceRating, ResourceProgress


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """Admin for Resource model"""
    
    list_display = ['title', 'category', 'type', 'difficulty_level', 'view_count', 'is_published', 'created_at']
    list_filter = ['category', 'type', 'difficulty_level', 'is_published', 'is_featured']
    search_fields = ['title', 'description', 'author']
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'type', 'icon')
        }),
        ('Content', {
            'fields': ('content', 'content_type', 'media_url', 'download_url', 'thumbnail_url')
        }),
        ('Metadata', {
            'fields': ('author', 'reviewer', 'last_reviewed_date', 'tags', 'references')
        }),
        ('Duration & Difficulty', {
            'fields': ('duration_minutes', 'difficulty_level')
        }),
        ('Status', {
            'fields': ('is_published', 'is_featured', 'view_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ResourceBookmark)
class ResourceBookmarkAdmin(admin.ModelAdmin):
    """Admin for ResourceBookmark model"""
    
    list_display = ['user', 'resource', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'resource__title']
    date_hierarchy = 'created_at'


@admin.register(ResourceView)
class ResourceViewAdmin(admin.ModelAdmin):
    """Admin for ResourceView model"""
    
    list_display = ['user', 'resource', 'viewed_at']
    list_filter = ['viewed_at']
    search_fields = ['user__email', 'resource__title']
    date_hierarchy = 'viewed_at'


@admin.register(ResourceRating)
class ResourceRatingAdmin(admin.ModelAdmin):
    """Admin for ResourceRating model"""
    
    list_display = ['user', 'resource', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__email', 'resource__title', 'review']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(ResourceProgress)
class ResourceProgressAdmin(admin.ModelAdmin):
    """Admin for ResourceProgress model"""
    
    list_display = ['user', 'resource', 'progress_percentage', 'is_completed', 'last_accessed']
    list_filter = ['is_completed', 'last_accessed']
    search_fields = ['user__email', 'resource__title']
    readonly_fields = ['is_completed', 'last_accessed']
    date_hierarchy = 'last_accessed'
