from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Page, FAQ
from .serializers import PageSerializer, FAQSerializer


class PageViewSet(viewsets.ViewSet):
    """
    ViewSet for handling Page operations
    """
    
    def list(self, request):
        """List all active pages"""
        pages = Page.objects.filter(is_active=True)
        serializer = PageSerializer(pages, many=True)
        return Response({'pages': serializer.data})
    
    def retrieve(self, request, pk=None):
        """Retrieve a specific page by slug"""
        page = get_object_or_404(Page, slug=pk, is_active=True)
        serializer = PageSerializer(page)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='type/(?P<page_type>[^/.]+)')
    def by_type(self, request, page_type=None):
        """Retrieve a specific page by type"""
        page = get_object_or_404(Page, page_type=page_type, is_active=True)
        serializer = PageSerializer(page)
        return Response(serializer.data)


class FAQViewSet(viewsets.ViewSet):
    """
    ViewSet for handling FAQ operations
    """
    
    def list(self, request):
        """Retrieve all active FAQs"""
        faqs = FAQ.objects.filter(is_active=True)
        serializer = FAQSerializer(faqs, many=True)
        return Response({'faqs': serializer.data})