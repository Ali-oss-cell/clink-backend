"""
Resources app URLs - Mental health resources and educational materials
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.ResourceViewSet, basename='resource')

urlpatterns = [
    path('', include(router.urls)),
]
