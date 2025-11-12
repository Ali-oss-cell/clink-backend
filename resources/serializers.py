"""
Serializers for resources app
"""

from rest_framework import serializers
from .models import Resource, ResourceBookmark, ResourceView, ResourceRating, ResourceProgress


class ResourceListSerializer(serializers.ModelSerializer):
    """Serializer for resource list view - Frontend ready"""
    
    is_bookmarked = serializers.SerializerMethodField()
    thumbnail_image_url = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_level_display', read_only=True)
    estimated_time = serializers.SerializerMethodField()
    
    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'description', 'category', 'category_display', 
            'type', 'type_display', 'icon', 'duration_minutes', 'estimated_time',
            'difficulty_level', 'difficulty_display', 'view_count', 'is_bookmarked',
            'thumbnail_url', 'thumbnail_image_url', 'is_featured', 
            'created_at', 'updated_at'
        ]
    
    def get_is_bookmarked(self, obj):
        """Check if resource is bookmarked by current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ResourceBookmark.objects.filter(user=request.user, resource=obj).exists()
        return False
    
    def get_thumbnail_image_url(self, obj):
        """Get thumbnail image URL (prefer uploaded file over URL)"""
        if obj.image_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_file.url)
            return obj.image_file.url
        return obj.thumbnail_url
    
    def get_estimated_time(self, obj):
        """Get formatted estimated time"""
        if obj.type in ['video', 'audio']:
            return f"{obj.duration_minutes} min"
        return f"{obj.duration_minutes} min read"


class RelatedResourceSerializer(serializers.ModelSerializer):
    """Serializer for related resources - Frontend ready"""
    
    thumbnail_image_url = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    
    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'type', 'type_display', 
            'thumbnail_url', 'thumbnail_image_url', 'icon'
        ]
    
    def get_thumbnail_image_url(self, obj):
        """Get thumbnail image URL"""
        if obj.image_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_file.url)
            return obj.image_file.url
        return obj.thumbnail_url


class ResourceDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed resource view and creation/update - Frontend ready"""
    
    is_bookmarked = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()
    estimated_reading_time = serializers.CharField(read_only=True)
    related_resources = serializers.SerializerMethodField()
    image_file_url = serializers.SerializerMethodField()
    pdf_file_url = serializers.SerializerMethodField()
    thumbnail_image_url = serializers.SerializerMethodField()
    download_file_url = serializers.SerializerMethodField()
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_level_display', read_only=True)
    content_type_display = serializers.CharField(source='get_content_type_display', read_only=True)
    has_media = serializers.SerializerMethodField()
    has_download = serializers.SerializerMethodField()
    has_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Resource
        fields = [
            # Basic Info
            'id', 'title', 'description', 'category', 'category_display',
            'type', 'type_display', 'icon', 'is_featured',
            
            # Content
            'content', 'content_type', 'content_type_display',
            'media_url', 'download_url', 'thumbnail_url',
            
            # File URLs (frontend ready)
            'image_file', 'image_file_url', 'thumbnail_image_url',
            'pdf_file', 'pdf_file_url', 'download_file_url',
            
            # Media flags (for frontend conditional rendering)
            'has_media', 'has_download', 'has_image',
            
            # Metadata
            'author', 'reviewer', 'last_reviewed_date',
            'tags', 'references',
            
            # Duration & Difficulty
            'duration_minutes', 'difficulty_level', 'difficulty_display',
            'estimated_reading_time',
            
            # Statistics
            'view_count', 'average_rating', 'total_ratings',
            
            # User-specific data
            'is_bookmarked', 'user_progress', 'user_rating',
            
            # Related
            'related_resources',
            
            # Status
            'is_published',
            
            # Timestamps
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'view_count', 'average_rating', 'total_ratings', 'is_bookmarked',
            'user_progress', 'user_rating', 'estimated_reading_time', 'related_resources',
            'image_file_url', 'pdf_file_url', 'thumbnail_image_url', 'download_file_url',
            'has_media', 'has_download', 'has_image', 'category_display', 'type_display',
            'difficulty_display', 'content_type_display', 'created_at', 'updated_at'
        ]
    
    def get_is_bookmarked(self, obj):
        """Check if resource is bookmarked by current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ResourceBookmark.objects.filter(user=request.user, resource=obj).exists()
        return False
    
    def get_user_progress(self, obj):
        """Get user's progress on this resource"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = ResourceProgress.objects.get(user=request.user, resource=obj)
                return progress.progress_percentage
            except ResourceProgress.DoesNotExist:
                return 0
        return 0
    
    def get_average_rating(self, obj):
        """Get average rating"""
        return obj.average_rating
    
    def get_total_ratings(self, obj):
        """Get total number of ratings"""
        return obj.total_ratings
    
    def get_related_resources(self, obj):
        """Get related resources from same category"""
        related = Resource.objects.filter(
            category=obj.category,
            is_published=True
        ).exclude(id=obj.id)[:5]
        return RelatedResourceSerializer(related, many=True).data
    
    def get_image_file_url(self, obj):
        """Get full URL for uploaded image file"""
        if obj.image_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_file.url)
            return obj.image_file.url
        return None
    
    def get_pdf_file_url(self, obj):
        """Get full URL for uploaded PDF file"""
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return None
    
    def get_thumbnail_image_url(self, obj):
        """Get thumbnail image URL (prefer uploaded file over URL)"""
        if obj.image_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_file.url)
            return obj.image_file.url
        return obj.thumbnail_url
    
    def get_download_file_url(self, obj):
        """Get download file URL (prefer PDF file over download URL)"""
        if obj.pdf_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.pdf_file.url)
            return obj.pdf_file.url
        return obj.download_url
    
    def get_user_rating(self, obj):
        """Get current user's rating for this resource"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                rating = ResourceRating.objects.get(user=request.user, resource=obj)
                return {
                    'rating': rating.rating,
                    'review': rating.review,
                    'created_at': rating.created_at,
                    'updated_at': rating.updated_at
                }
            except ResourceRating.DoesNotExist:
                return None
        return None
    
    def get_has_media(self, obj):
        """Check if resource has media (video/audio)"""
        return bool(obj.media_url)
    
    def get_has_download(self, obj):
        """Check if resource has downloadable file"""
        return bool(obj.pdf_file or obj.download_url)
    
    def get_has_image(self, obj):
        """Check if resource has image"""
        return bool(obj.image_file or obj.thumbnail_url)


class ResourceBookmarkSerializer(serializers.ModelSerializer):
    """Serializer for bookmarked resources"""
    
    title = serializers.CharField(source='resource.title', read_only=True)
    category = serializers.CharField(source='resource.category', read_only=True)
    type = serializers.CharField(source='resource.type', read_only=True)
    thumbnail_url = serializers.CharField(source='resource.thumbnail_url', read_only=True)
    resource_id = serializers.IntegerField(source='resource.id', read_only=True)
    
    class Meta:
        model = ResourceBookmark
        fields = ['id', 'resource_id', 'title', 'category', 'type', 'thumbnail_url', 'created_at']


class ResourceViewSerializer(serializers.ModelSerializer):
    """Serializer for resource view history"""
    
    title = serializers.CharField(source='resource.title', read_only=True)
    category = serializers.CharField(source='resource.category', read_only=True)
    type = serializers.CharField(source='resource.type', read_only=True)
    thumbnail_url = serializers.CharField(source='resource.thumbnail_url', read_only=True)
    resource_id = serializers.IntegerField(source='resource.id', read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = ResourceView
        fields = ['id', 'resource_id', 'title', 'category', 'type', 'thumbnail_url', 'viewed_at', 'progress_percentage']
    
    def get_progress_percentage(self, obj):
        """Get progress for this resource"""
        try:
            progress = ResourceProgress.objects.get(user=obj.user, resource=obj.resource)
            return progress.progress_percentage
        except ResourceProgress.DoesNotExist:
            return 0


class ResourceRatingSerializer(serializers.ModelSerializer):
    """Serializer for resource ratings"""
    
    class Meta:
        model = ResourceRating
        fields = ['id', 'resource', 'rating', 'review', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ResourceProgressSerializer(serializers.ModelSerializer):
    """Serializer for resource progress"""
    
    class Meta:
        model = ResourceProgress
        fields = ['id', 'resource', 'progress_percentage', 'current_time_seconds', 'is_completed', 'last_accessed']
        read_only_fields = ['id', 'is_completed', 'last_accessed']


class CategorySerializer(serializers.Serializer):
    """Serializer for resource categories"""
    
    id = serializers.CharField()
    name = serializers.CharField()
    icon = serializers.CharField()
    description = serializers.CharField()
    resource_count = serializers.IntegerField()

