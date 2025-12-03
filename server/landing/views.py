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


class LandingPageContentView(APIView):
    """
    View to retrieve all content for the landing page
    """
    
    def get(self, request):
        """Get all landing page content"""
        try:
            # Get landing page configuration
            configuration = LandingPageConfiguration.get_config()
            
            # Get active hero banners
            hero_banners = HeroBanner.objects.filter(is_active=True)
            
            # Get active category sections
            categories = CategorySection.objects.filter(is_active=True).select_related('category')
            
            # Get featured products (new arrivals)
            featured_products = Product.objects.filter(
                is_active=True, 
                is_featured=True
            ).order_by('-created_at')[:8]  # Limit to 8 products
            
            # Get active advertisements
            advertisements = AdvertisementBanner.objects.filter(
                is_active=True,
                start_date__lte=timezone.now()
            ).filter(
                models.Q(end_date__gte=timezone.now()) | models.Q(end_date__isnull=True)
            )
            
            # Get featured testimonials
            testimonials = Testimonial.objects.filter(is_featured=True)
            
            # Get featured brands
            featured_brands = Brand.objects.filter(is_active=True)[:10]
            
            # Prepare data for serializer
            data = {
                'configuration': configuration,
                'hero_banners': hero_banners,
                'categories': categories,
                'featured_products': featured_products,
                'advertisements': advertisements,
                'testimonials': testimonials,
                'featured_brands': featured_brands
            }
            
            serializer = LandingPageContentSerializer(data, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HeroBannerListView(APIView):
    """View to retrieve hero banners"""
    
    def get(self, request):
        """Get active hero banners"""
        banners = HeroBanner.objects.filter(is_active=True).order_by('order', '-created_at')
        serializer = HeroBannerSerializer(banners, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategorySectionListView(APIView):
    """View to retrieve category sections"""
    
    def get(self, request):
        """Get active category sections"""
        categories = CategorySection.objects.filter(
            is_active=True
        ).select_related('category').order_by('order', '-created_at')
        serializer = CategorySectionSerializer(categories, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class NewArrivalsListView(APIView):
    """View to retrieve new arrival products"""
    
    def get(self, request):
        """Get new arrival products"""
        products = Product.objects.filter(
            is_active=True
        ).order_by('-created_at')[:12]  # Limit to 12 newest products
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdvertisementBannerListView(APIView):
    """View to retrieve advertisement banners"""
    
    def get(self, request):
        """Get active advertisement banners"""
        advertisements = AdvertisementBanner.objects.filter(
            is_active=True,
            start_date__lte=timezone.now()
        ).filter(
            models.Q(end_date__gte=timezone.now()) | models.Q(end_date__isnull=True)
        ).order_by('order', '-created_at')
        serializer = AdvertisementBannerSerializer(advertisements, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class TestimonialListView(APIView):
    """View to retrieve testimonials"""
    
    def get(self, request):
        """Get featured testimonials"""
        testimonials = Testimonial.objects.filter(is_featured=True).order_by('order', '-created_at')
        serializer = TestimonialSerializer(testimonials, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class FeaturedBrandsListView(APIView):
    """View to retrieve featured brands"""
    
    def get(self, request):
        """Get featured brands"""
        brands = Brand.objects.filter(is_active=True).order_by('name')[:10]
        serializer = BrandSerializer(brands, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)