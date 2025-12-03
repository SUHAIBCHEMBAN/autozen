from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'products'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'brands', views.BrandViewSet, basename='brand')
router.register(r'models', views.VehicleModelViewSet, basename='model')
router.register(r'categories', views.PartCategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]