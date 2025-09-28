"""
Resources app URLs - Blog posts and content management
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'posts', views.BlogPostViewSet, basename='blog-post')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'resources', views.ResourceViewSet, basename='resource')

urlpatterns = [
    path('', include(router.urls)),
    path('posts/published/', views.PublishedPostsView.as_view(), name='published-posts'),
    path('posts/<slug:slug>/', views.BlogPostDetailView.as_view(), name='blog-post-detail'),
]
