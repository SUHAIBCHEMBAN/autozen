"""
Utility functions for the landing page app with Redis caching support
"""

from django.core.cache import cache
from django.utils import timezone
from django.conf import settings


# Cache timeout settings (15 minutes for most content, 1 hour for configuration)
LANDING_CONTENT_CACHE_TIMEOUT = getattr(settings, 'LANDING_CONTENT_CACHE_TIMEOUT', 60 * 15)
LANDING_CONFIG_CACHE_TIMEOUT = getattr(settings, 'LANDING_CONFIG_CACHE_TIMEOUT', 60 * 60)


def get_landing_page_content():
    """
    Get all content for the landing page with Redis caching.
    
    This function retrieves all landing page content from cache if available,
    otherwise fetches from database and stores in cache for future requests.
    
    Returns:
        dict: Dictionary containing all landing page content including:
            - configuration: LandingPageConfiguration object
            - hero_banners: QuerySet of active HeroBanner objects with prefetched featured vehicles
            - categories: QuerySet of active CategorySection objects
            - featured_products: QuerySet of featured Product objects
            - advertisements: QuerySet of active AdvertisementBanner objects
            - testimonials: QuerySet of featured Testimonial objects
            - featured_brands: QuerySet of active Brand objects
    """
    cache_key = 'landing_page_content'
    cached_content = cache.get(cache_key)
    
    if cached_content is not None:
        return cached_content
    
    try:
        # Import models inside function to avoid circular imports
        from .models import (
            HeroBanner, CategorySection, AdvertisementBanner, 
            Testimonial, LandingPageConfiguration
        )
        from products.models import Product, Brand
        from django.db import models  # Import models module for Q objects
        
        # Get landing page configuration
        configuration = LandingPageConfiguration.get_config()
        
        # Get active hero banners with prefetched featured vehicles
        hero_banners = HeroBanner.objects.filter(is_active=True).prefetch_related('featured_vehicles')
        
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
        
        content = {
            'configuration': configuration,
            'hero_banners': hero_banners,
            'categories': categories,
            'featured_products': featured_products,
            'advertisements': advertisements,
            'testimonials': testimonials,
            'featured_brands': featured_brands
        }
        
        # Cache the content for future requests
        cache.set(cache_key, content, LANDING_CONTENT_CACHE_TIMEOUT)
        return content
    except Exception as e:
        return {
            'error': str(e)
        }


def get_active_hero_banners():
    """
    Get all active hero banners with Redis caching.
    
    Returns:
        QuerySet: Active HeroBanner objects ordered by display order and creation date
                 with prefetched featured vehicles
    """
    cache_key = 'active_hero_banners'
    cached_banners = cache.get(cache_key)
    
    if cached_banners is not None:
        return cached_banners
    
    # Import model inside function to avoid circular imports
    from .models import HeroBanner
    banners = HeroBanner.objects.filter(is_active=True).prefetch_related('featured_vehicles').order_by('order', '-created_at')
    cache.set(cache_key, banners, LANDING_CONTENT_CACHE_TIMEOUT)
    return banners


def get_active_category_sections():
    """
    Get all active category sections with Redis caching.
    
    Returns:
        QuerySet: Active CategorySection objects ordered by display order and creation date
    """
    cache_key = 'active_category_sections'
    cached_categories = cache.get(cache_key)
    
    if cached_categories is not None:
        return cached_categories
    
    # Import model inside function to avoid circular imports
    from .models import CategorySection
    categories = CategorySection.objects.filter(
        is_active=True
    ).select_related('category').order_by('order', '-created_at')
    cache.set(cache_key, categories, LANDING_CONTENT_CACHE_TIMEOUT)
    return categories


def get_new_arrival_products(limit=12):
    """
    Get new arrival products with Redis caching.
    
    Args:
        limit (int): Maximum number of products to return (default: 12)
        
    Returns:
        QuerySet: Active Product objects ordered by creation date
    """
    cache_key = f'new_arrival_products_{limit}'
    cached_products = cache.get(cache_key)
    
    if cached_products is not None:
        return cached_products
    
    # Import model inside function to avoid circular imports
    from products.models import Product
    products = Product.objects.filter(
        is_active=True
    ).order_by('-created_at')[:limit]
    cache.set(cache_key, products, LANDING_CONTENT_CACHE_TIMEOUT)
    return products


def get_active_advertisements():
    """
    Get all active advertisements with Redis caching.
    
    Returns:
        QuerySet: Active AdvertisementBanner objects ordered by display order and creation date
    """
    cache_key = 'active_advertisements'
    cached_ads = cache.get(cache_key)
    
    if cached_ads is not None:
        return cached_ads
    
    # Import models inside function to avoid circular imports
    from django.db import models
    from .models import AdvertisementBanner
    advertisements = AdvertisementBanner.objects.filter(
        is_active=True,
        start_date__lte=timezone.now()
    ).filter(
        models.Q(end_date__gte=timezone.now()) | models.Q(end_date__isnull=True)
    ).order_by('order', '-created_at')
    cache.set(cache_key, advertisements, LANDING_CONTENT_CACHE_TIMEOUT)
    return advertisements


def get_featured_testimonials():
    """
    Get featured testimonials with Redis caching.
    
    Returns:
        QuerySet: Featured Testimonial objects ordered by display order and creation date
    """
    cache_key = 'featured_testimonials'
    cached_testimonials = cache.get(cache_key)
    
    if cached_testimonials is not None:
        return cached_testimonials
    
    # Import model inside function to avoid circular imports
    from .models import Testimonial
    testimonials = Testimonial.objects.filter(is_featured=True).order_by('order', '-created_at')
    cache.set(cache_key, testimonials, LANDING_CONTENT_CACHE_TIMEOUT)
    return testimonials


def get_featured_brands(limit=10):
    """
    Get featured brands with Redis caching.
    
    Args:
        limit (int): Maximum number of brands to return (default: 10)
        
    Returns:
        QuerySet: Active Brand objects ordered by name
    """
    cache_key = f'featured_brands_{limit}'
    cached_brands = cache.get(cache_key)
    
    if cached_brands is not None:
        return cached_brands
    
    # Import model inside function to avoid circular imports
    from products.models import Brand
    brands = Brand.objects.filter(is_active=True).order_by('name')[:limit]
    cache.set(cache_key, brands, LANDING_CONTENT_CACHE_TIMEOUT)
    return brands


def create_default_landing_configuration():
    """
    Create default landing page configuration.
    
    Returns:
        LandingPageConfiguration: The default or existing configuration object
    """
    # Import model inside function to avoid circular imports
    from .models import LandingPageConfiguration
    config, created = LandingPageConfiguration.objects.get_or_create(
        defaults={
            'site_title': 'AutoZen',
            'site_tagline': 'Premium Automotive Spare Parts',
            'meta_description': 'Your trusted partner for automotive spare parts and accessories'
        }
    )
    return config