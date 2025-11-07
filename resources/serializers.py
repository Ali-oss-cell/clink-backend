"""
Serializers for resources app
"""

from rest_framework import serializers
from .models import Resource, ResourceBookmark, ResourceView, ResourceRating, ResourceProgress


class ResourceListSerializer(serializers.ModelSerializer):
    """Serializer for resource list view"""
    
    is_bookmarked = serializers.SerializerMethodField()
    
    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'description', 'category', 'type', 'icon',
            'duration_minutes', 'difficulty_level', 'view_count', 'is_bookmarked',
            'thumbnail_url', 'created_at', 'updated_at'
        ]
    
    def get_is_bookmarked(self, obj):
        """Check if resource is bookmarked by current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ResourceBookmark.objects.filter(user=request.user, resource=obj).exists()
        return False


class RelatedResourceSerializer(serializers.ModelSerializer):
    """Serializer for related resources"""
    
    class Meta:
        model = Resource
        fields = ['id', 'title', 'type', 'thumbnail_url']


class ResourceDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed resource view"""
    
    is_bookmarked = serializers.SerializerMethodField()
    user_progress = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()
    estimated_reading_time = serializers.CharField(read_only=True)
    related_resources = serializers.SerializerMethodField()
    
    class Meta:
        model = Resource
        fields = [
            'id', 'title', 'description', 'category', 'type', 'icon',
            'duration_minutes', 'difficulty_level', 'content', 'content_type',
            'media_url', 'download_url', 'author', 'reviewer', 'last_reviewed_date',
            'tags', 'view_count', 'average_rating', 'total_ratings', 'is_bookmarked',
            'user_progress', 'estimated_reading_time', 'references', 'related_resources',
            'thumbnail_url', 'created_at', 'updated_at'
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

