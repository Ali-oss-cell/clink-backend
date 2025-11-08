"""
Resources app views - Mental health resources and educational materials
"""

from rest_framework import viewsets, status, permissions     
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count
from django.utils import timezone

from .models import Resource, ResourceBookmark, ResourceView, ResourceRating, ResourceProgress
from .serializers import (
    ResourceListSerializer, ResourceDetailSerializer, ResourceBookmarkSerializer,
    ResourceViewSerializer, ResourceRatingSerializer, ResourceProgressSerializer,
    CategorySerializer
)


class ResourcePagination(PageNumberPagination):
    """Custom pagination for resources"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ResourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing mental health resources
    
    Endpoints:
    - GET /api/resources/ - List all resources with filters (public)
    - GET /api/resources/{id}/ - Get single resource (public)
    - POST /api/resources/ - Create new resource (staff only)
    - PUT/PATCH /api/resources/{id}/ - Update resource (staff only)
    - DELETE /api/resources/{id}/ - Delete resource (staff only)
    - POST /api/resources/{id}/bookmark/ - Bookmark resource
    - POST /api/resources/{id}/track-view/ - Track resource view
    - POST /api/resources/{id}/progress/ - Update progress
    - POST /api/resources/{id}/rate/ - Rate resource
    - GET /api/resources/bookmarks/ - Get user bookmarks
    - GET /api/resources/history/ - Get user history
    - GET /api/resources/categories/ - Get categories
    - GET /api/resources/search/ - Advanced search
    """
    
    queryset = Resource.objects.filter(is_published=True)
    pagination_class = ResourcePagination
    
    def get_permissions(self):
        """
        Allow public read access, require authentication for modifications
        Only staff (admin, practice manager, psychologist) can create/update/delete
        """
        if self.action in ['list', 'retrieve', 'categories', 'search']:
            # Public can view resources
            return [permissions.AllowAny()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only authenticated staff can modify resources
            return [IsAuthenticated()]
        else:
            # Other actions (bookmark, rate, etc.) require authentication
            return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return ResourceDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            # Use detail serializer for create/update to include all fields
            return ResourceDetailSerializer
        return ResourceListSerializer
    
    def get_queryset(self):
        """Filter resources based on query parameters and user permissions"""
        user = self.request.user
        
        # Staff can see all resources (including unpublished)
        if user.is_authenticated and (user.is_admin_user() or user.is_practice_manager() or user.is_psychologist()):
            queryset = Resource.objects.all()
        else:
            # Public can only see published resources
            queryset = Resource.objects.filter(is_published=True)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by type
        resource_type = self.request.query_params.get('type')
        if resource_type:
            queryset = queryset.filter(type=resource_type)
        
        # Filter by difficulty
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Search by title or description
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create resource - only staff can create"""
        user = self.request.user
        if not (user.is_admin_user() or user.is_practice_manager() or user.is_psychologist()):
            raise permissions.PermissionDenied("Only staff members can create resources")
        serializer.save()
    
    def perform_update(self, serializer):
        """Update resource - only staff can update"""
        user = self.request.user
        if not (user.is_admin_user() or user.is_practice_manager() or user.is_psychologist()):
            raise permissions.PermissionDenied("Only staff members can update resources")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete resource - only staff can delete"""
        user = self.request.user
        if not (user.is_admin_user() or user.is_practice_manager() or user.is_psychologist()):
            raise permissions.PermissionDenied("Only staff members can delete resources")
        instance.delete()
    
    def retrieve(self, request, *args, **kwargs):
        """Get single resource with detailed information"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def bookmark(self, request, pk=None):
        """
        Bookmark or unbookmark a resource
        
        POST /api/resources/{id}/bookmark/
        Body: {"action": "add" or "remove"}
        """
        resource = self.get_object()
        action_type = request.data.get('action', 'add')
        
        if action_type == 'add':
            bookmark, created = ResourceBookmark.objects.get_or_create(
                user=request.user,
                resource=resource
            )
            return Response({
                'message': 'Resource bookmarked successfully',
                'is_bookmarked': True
            })
        elif action_type == 'remove':
            ResourceBookmark.objects.filter(
                user=request.user,
                resource=resource
            ).delete()
            return Response({
                'message': 'Resource removed from bookmarks',
                'is_bookmarked': False
            })
        else:
            return Response(
                {'error': 'Invalid action. Use "add" or "remove"'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def track_view(self, request, pk=None):
        """
        Track when user views a resource
        
        POST /api/resources/{id}/track-view/
        """
        resource = self.get_object()
        
        # Create view record
        ResourceView.objects.create(
            user=request.user,
            resource=resource
        )
        
        # Increment view count
        resource.view_count += 1
        resource.save(update_fields=['view_count'])
        
        return Response({
            'message': 'View tracked',
            'total_views': resource.view_count
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def progress(self, request, pk=None):
        """
        Update user progress on video/audio resources
        
        POST /api/resources/{id}/progress/
        Body: {
            "progress_percentage": 45,
            "current_time_seconds": 180
        }
        """
        resource = self.get_object()
        progress_percentage = request.data.get('progress_percentage', 0)
        current_time_seconds = request.data.get('current_time_seconds', 0)
        
        # Validate progress
        if not (0 <= progress_percentage <= 100):
            return Response(
                {'error': 'Progress percentage must be between 0 and 100'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update or create progress
        progress, created = ResourceProgress.objects.update_or_create(
            user=request.user,
            resource=resource,
            defaults={
                'progress_percentage': progress_percentage,
                'current_time_seconds': current_time_seconds
            }
        )
        
        return Response({
            'message': 'Progress updated',
            'progress_percentage': progress.progress_percentage,
            'is_completed': progress.is_completed
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate(self, request, pk=None):
        """
        Rate a resource
        
        POST /api/resources/{id}/rate/
        Body: {
            "rating": 5,
            "review": "Very helpful!"
        }
        """
        resource = self.get_object()
        rating_value = request.data.get('rating')
        review_text = request.data.get('review', '')
        
        # Validate rating
        if not rating_value or not (1 <= int(rating_value) <= 5):
            return Response(
                {'error': 'Rating must be between 1 and 5'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update or create rating
        rating, created = ResourceRating.objects.update_or_create(
            user=request.user,
            resource=resource,
            defaults={
                'rating': rating_value,
                'review': review_text
            }
        )
        
        return Response({
            'message': 'Rating submitted successfully',
            'average_rating': resource.average_rating,
            'total_ratings': resource.total_ratings
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def bookmarks(self, request):
        """
        Get all bookmarked resources for current user
        
        GET /api/resources/bookmarks/
        """
        bookmarks = ResourceBookmark.objects.filter(user=request.user).order_by('-created_at')
        
        page = self.paginate_queryset(bookmarks)
        if page is not None:
            serializer = ResourceBookmarkSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ResourceBookmarkSerializer(bookmarks, many=True)
        return Response({
            'count': bookmarks.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def history(self, request):
        """
        Get user's resource view history
        
        GET /api/resources/history/
        """
        # Get unique resource views (most recent view per resource)
        viewed_resources = ResourceView.objects.filter(
            user=request.user
        ).order_by('resource', '-viewed_at').distinct('resource').order_by('-viewed_at')[:20]
        
        serializer = ResourceViewSerializer(viewed_resources, many=True)
        return Response({
            'count': viewed_resources.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def categories(self, request):
        """
        Get list of resource categories with counts
        
        GET /api/resources/categories/
        """
        category_data = []
        
        # Category definitions
        categories_info = {
            'anxiety': {
                'name': 'Anxiety',
                'icon': '😰',
                'description': 'Resources for managing anxiety and worry'
            },
            'depression': {
                'name': 'Depression',
                'icon': '💙',
                'description': 'Understanding and coping with depression'
            },
            'stress': {
                'name': 'Stress Management',
                'icon': '😓',
                'description': 'Tools and techniques for managing stress'
            },
            'sleep': {
                'name': 'Sleep',
                'icon': '😴',
                'description': 'Improving sleep quality and habits'
            },
            'mindfulness': {
                'name': 'Mindfulness & Meditation',
                'icon': '🧘',
                'description': 'Mindfulness practices and meditation guides'
            },
            'relationships': {
                'name': 'Relationships',
                'icon': '💕',
                'description': 'Building healthy relationships'
            },
            'self-care': {
                'name': 'Self-Care',
                'icon': '🌟',
                'description': 'Self-care practices and wellness'
            },
            'grief': {
                'name': 'Grief & Loss',
                'icon': '🕊️',
                'description': 'Coping with grief and loss'
            },
            'trauma': {
                'name': 'Trauma',
                'icon': '🛡️',
                'description': 'Trauma recovery and healing'
            },
            'addiction': {
                'name': 'Addiction Support',
                'icon': '🆘',
                'description': 'Support for addiction recovery'
            },
        }
        
        # Get counts for each category
        category_counts = Resource.objects.filter(is_published=True).values('category').annotate(
            count=Count('id')
        )
        counts_dict = {item['category']: item['count'] for item in category_counts}
        
        # Build response
        for category_id, info in categories_info.items():
            category_data.append({
                'id': category_id,
                'name': info['name'],
                'icon': info['icon'],
                'description': info['description'],
                'resource_count': counts_dict.get(category_id, 0)
            })
        
        return Response(category_data)
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def search(self, request):
        """
        Advanced search with multiple filters
        
        GET /api/resources/search/?q=anxiety&categories[]=anxiety&types[]=article
        """
        queryset = Resource.objects.filter(is_published=True)
        
        # Search query
        q = request.query_params.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(tags__contains=[q])
            )
        
        # Category filter (multiple)
        categories = request.query_params.getlist('categories[]')
        if categories:
            queryset = queryset.filter(category__in=categories)
        
        # Type filter (multiple)
        types = request.query_params.getlist('types[]')
        if types:
            queryset = queryset.filter(type__in=types)
        
        # Difficulty filter
        difficulty = request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Duration filters
        min_duration = request.query_params.get('min_duration')
        if min_duration:
            queryset = queryset.filter(duration_minutes__gte=int(min_duration))
        
        max_duration = request.query_params.get('max_duration')
        if max_duration:
            queryset = queryset.filter(duration_minutes__lte=int(max_duration))
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ResourceListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ResourceListSerializer(queryset, many=True, context={'request': request})
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
