from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Page, FAQ
from .serializers import PageSerializer, FAQSerializer

class PageDetailView(APIView):
    """
    Retrieve a specific page by slug
    """
    def get(self, request, slug):
        page = get_object_or_404(Page, slug=slug, is_active=True)
        serializer = PageSerializer(page)
        return Response(serializer.data)

class PageByTypeView(APIView):
    """
    Retrieve a specific page by type
    """
    def get(self, request, page_type):
        page = get_object_or_404(Page, page_type=page_type, is_active=True)
        serializer = PageSerializer(page)
        return Response(serializer.data)

class FaqListView(APIView):
    """
    Retrieve all active FAQs
    """
    def get(self, request):
        faqs = FAQ.objects.filter(is_active=True)
        serializer = FAQSerializer(faqs, many=True)
        return Response({'faqs': serializer.data})

class PageListView(APIView):
    """
    List all active pages
    """
    def get(self, request):
        pages = Page.objects.filter(is_active=True)
        serializer = PageSerializer(pages, many=True)
        return Response({'pages': serializer.data})
