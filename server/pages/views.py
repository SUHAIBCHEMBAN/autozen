from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Page, FAQ
from .serializers import PageSerializer, FAQSerializer
from .utils import get_active_pages, get_page_by_slug, get_page_by_type, get_active_faqs


class PageViewSet(viewsets.ViewSet):
    """
    ViewSet for handling Page operations with Redis caching optimization.
    
    Implements caching for improved performance:
    - Pages list is cached
    - Individual pages are cached by slug
    - Pages by type are cached separately
    """
    
    def list(self, request):
        """
        List all active pages with caching.
        
        Retrieves all active pages ordered by creation date.
        Uses Redis caching for improved performance.
        
        Returns:
            Response: Serialized pages with HTTP 200 status
        """
        pages = get_active_pages()
        serializer = PageSerializer(pages, many=True)
        return Response({'pages': serializer.data})
    
    def retrieve(self, request, pk=None):
        """
        Retrieve a specific page by slug with caching.
        
        Retrieves a page by its slug if it's active.
        Uses Redis caching for improved performance.
        
        Args:
            pk (str): The slug of the page to retrieve
            
        Returns:
            Response: Serialized page data with HTTP 200 status
                     or HTTP 404 if page not found
        """
        page = get_page_by_slug(pk)
        if page is None:
            return Response({'detail': 'Page not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PageSerializer(page)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='type/(?P<page_type>[^/.]+)')
    def by_type(self, request, page_type=None):
        """
        Retrieve a specific page by type with caching.
        
        Retrieves a page by its type if it's active.
        Uses Redis caching for improved performance.
        
        Args:
            page_type (str): The type of the page to retrieve
            
        Returns:
            Response: Serialized page data with HTTP 200 status
                     or HTTP 404 if page not found
        """
        page = get_page_by_type(page_type)
        if page is None:
            return Response({'detail': 'Page not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PageSerializer(page)
        return Response(serializer.data)


class FAQViewSet(viewsets.ViewSet):
    """
    ViewSet for handling FAQ operations with Redis caching optimization.
    
    Implements caching for improved performance:
    - FAQs list is cached
    """
    
    def list(self, request):
        """
        Retrieve all active FAQs with caching.
        
        Retrieves all active FAQs ordered by display order and creation date.
        Uses Redis caching for improved performance.
        
        Returns:
            Response: Serialized FAQs with HTTP 200 status
        """
        faqs = get_active_faqs()
        serializer = FAQSerializer(faqs, many=True)
        return Response({'faqs': serializer.data})