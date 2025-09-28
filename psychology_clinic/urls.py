"""
URL Configuration for Psychology Clinic Backend

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/

API Endpoints:
- /api/auth/ - Authentication endpoints
- /api/users/ - User management
- /api/services/ - Psychology services
- /api/psychologists/ - Psychologist profiles
- /api/appointments/ - Appointment booking
- /api/billing/ - Payment processing
- /api/resources/ - Blog posts and resources
- /api/videocall/ - Video call management
- /docs/ - API documentation
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI Schema
schema_view = get_schema_view(
    openapi.Info(
        title="Psychology Clinic API",
        default_version='v1',
        description="Australian Psychology Clinic Management System API",
        terms_of_service="https://www.yourpsychologyclinic.com.au/terms/",
        contact=openapi.Contact(email="support@yourpsychologyclinic.com.au"),
        license=openapi.License(name="Proprietary License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # Authentication
    path('api/auth/', include('users.urls')),
    
    # API Endpoints
    path('api/users/', include('users.urls')),
    path('api/services/', include('services.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/resources/', include('resources.urls')),
    path('api/core/', include('core.urls')),
    
    # Django Allauth (for social authentication if needed)
    path('accounts/', include('allauth.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug Toolbar
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Custom error handlers
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'