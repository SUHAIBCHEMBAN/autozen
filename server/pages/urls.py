from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'pages'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'pages', views.PageViewSet, basename='page')
router.register(r'faqs', views.FAQViewSet, basename='faq')

urlpatterns = [
    path('', include(router.urls)),
]