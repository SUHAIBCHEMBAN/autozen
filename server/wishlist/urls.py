from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'wishlist'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('', include(router.urls)),
]