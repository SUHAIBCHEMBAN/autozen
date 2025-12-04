from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import models
from .models import (
    HeroBanner, CategorySection, AdvertisementBanner, 
    Testimonial, LandingPageConfiguration
)
from products.models import Product, Brand
from .serializers import LandingPageContentSerializer, HeroBannerSerializer, CategorySectionSerializer
from products.serializers import ProductListSerializer, BrandSerializer
from .utils import (
    get_landing_page_content, get_active_hero_banners, get_active_category_sections,
    get_new_arrival_products, get_active_advertisements, get_featured_testimonials,
    get_featured_brands
)


class LandingPageContentView(APIView):
    """
    View to retrieve all content for the landing page with Redis caching.
    
    This view aggregates all landing page content and serves it with caching
    for optimal performance. It uses utility functions that implement Redis
    caching to reduce database queries.
    """
    
    def get(self, request):
        """
        Get all landing page content with caching.
        
        Retrieves all landing page content including hero banners, categories,
        featured products, advertisements, testimonials, and brands. Uses
        Redis caching to improve response times and reduce database load.
        
        Returns:
            Response: Serialized landing page content with HTTP 200 status
                     or error message with HTTP 500 status
        """
        try:
            # Get all landing page content using cached utility function
            content_data = get_landing_page_content()
            
            # Check if there was an error in retrieving content
            if 'error' in content_data:
                return Response(
                    {'error': content_data['error']}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            serializer = LandingPageContentSerializer(content_data, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HeroBannerListView(APIView):
    """
    View to retrieve hero banners with Redis caching.
    
    Provides a list of active hero banners with optimized caching
    to reduce database queries for frequently accessed content.
    """
    
    def get(self, request):
        """
        Get active hero banners with caching.
        
        Retrieves all active hero banners ordered by display order
        and creation date. Uses Redis caching for improved performance.
        
        Returns:
            Response: Serialized hero banners with HTTP 200 status
        """
        banners = get_active_hero_banners()
        serializer = HeroBannerSerializer(banners, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategorySectionListView(APIView):
    """
    View to retrieve category sections with Redis caching.
    
    Provides a list of active category sections with related category data
    and optimized caching for improved performance.
    """
    
    def get(self, request):
        """
        Get active category sections with caching.
        
        Retrieves all active category sections with related category data,
        ordered by display order and creation date. Uses Redis caching
        for improved performance.
        
        Returns:
            Response: Serialized category sections with HTTP 200 status
        """
        categories = get_active_category_sections()
        serializer = CategorySectionSerializer(categories, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class NewArrivalsListView(APIView):
    """
    View to retrieve new arrival products with Redis caching.
    
    Provides a list of newest products with optimized caching
    to reduce database queries for frequently accessed content.
    """
    
    def get(self, request):
        """
        Get new arrival products with caching.
        
        Retrieves newest products ordered by creation date with a limit of 12.
        Uses Redis caching for improved performance.
        
        Returns:
            Response: Serialized products with HTTP 200 status
        """
        products = get_new_arrival_products(12)
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdvertisementBannerListView(APIView):
    """
    View to retrieve advertisement banners with Redis caching.
    
    Provides a list of active advertisement banners with scheduled publishing
    and optimized caching for improved performance.
    """
    
    def get(self, request):
        """
        Get active advertisement banners with caching.
        
        Retrieves all active advertisement banners that are currently
        within their scheduled publishing period, ordered by display order
        and creation date. Uses Redis caching for improved performance.
        
        Returns:
            Response: Serialized advertisement banners with HTTP 200 status
        """
        advertisements = get_active_advertisements()
        serializer = AdvertisementBannerSerializer(advertisements, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class TestimonialListView(APIView):
    """
    View to retrieve testimonials with Redis caching.
    
    Provides a list of featured testimonials with optimized caching
    to reduce database queries for frequently accessed content.
    """
    
    def get(self, request):
        """
        Get featured testimonials with caching.
        
        Retrieves all featured testimonials ordered by display order
        and creation date. Uses Redis caching for improved performance.
        
        Returns:
            Response: Serialized testimonials with HTTP 200 status
        """
        testimonials = get_featured_testimonials()
        from .serializers import TestimonialSerializer  # Import here to avoid circular imports
        serializer = TestimonialSerializer(testimonials, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class FeaturedBrandsListView(APIView):
    """
    View to retrieve featured brands with Redis caching.
    
    Provides a list of featured brands with optimized caching
    to reduce database queries for frequently accessed content.
    """
    
    def get(self, request):
        """
        Get featured brands with caching.
        
        Retrieves featured brands ordered by name with a limit of 10.
        Uses Redis caching for improved performance.
        
        Returns:
            Response: Serialized brands with HTTP 200 status
        """
        brands = get_featured_brands(10)
        serializer = BrandSerializer(brands, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)