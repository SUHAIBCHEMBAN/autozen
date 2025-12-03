from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cart'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'cart', views.CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]