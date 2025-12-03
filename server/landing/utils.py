"""
Utility functions for the landing page app
"""

from django.utils import timezone
from .models import (
    HeroBanner, CategorySection, AdvertisementBanner, 
    Testimonial, LandingPageConfiguration
)
from products.models import Product, Brand


def get_landing_page_content():
    """
    Get all content for the landing page
    """
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
        
        return {
            'configuration': configuration,
            'hero_banners': hero_banners,
            'categories': categories,
            'featured_products': featured_products,
            'advertisements': advertisements,
            'testimonials': testimonials,
            'featured_brands': featured_brands
        }
    except Exception as e:
        return {
            'error': str(e)
        }


def get_active_hero_banners():
    """
    Get all active hero banners
    """
    return HeroBanner.objects.filter(is_active=True).order_by('order', '-created_at')


def get_active_category_sections():
    """
    Get all active category sections
    """
    return CategorySection.objects.filter(
        is_active=True
    ).select_related('category').order_by('order', '-created_at')


def get_new_arrival_products(limit=12):
    """
    Get new arrival products
    """
    return Product.objects.filter(
        is_active=True
    ).order_by('-created_at')[:limit]


def get_active_advertisements():
    """
    Get all active advertisements
    """
    from django.db import models
    return AdvertisementBanner.objects.filter(
        is_active=True,
        start_date__lte=timezone.now()
    ).filter(
        models.Q(end_date__gte=timezone.now()) | models.Q(end_date__isnull=True)
    ).order_by('order', '-created_at')


def get_featured_testimonials():
    """
    Get featured testimonials
    """
    return Testimonial.objects.filter(is_featured=True).order_by('order', '-created_at')


def get_featured_brands(limit=10):
    """
    Get featured brands
    """
    return Brand.objects.filter(is_active=True).order_by('name')[:limit]


def create_default_landing_configuration():
    """
    Create default landing page configuration
    """
    config, created = LandingPageConfiguration.objects.get_or_create(
        defaults={
            'site_title': 'AutoZen',
            'site_tagline': 'Premium Automotive Spare Parts',
            'meta_description': 'Your trusted partner for automotive spare parts and accessories'
        }
    )
    return config


def initialize_landing_page():
    """
    Initialize landing page with default content
    """
    # Create default configuration
    config = create_default_landing_configuration()
    
    # Create sample hero banners if none exist
    if not HeroBanner.objects.exists():
        HeroBanner.objects.create(
            title="Premium Automotive Parts",
            subtitle="Quality spare parts for all vehicle models",
            description="Discover our extensive collection of genuine and aftermarket parts",
            button_text="Shop Now",
            order=1
        )
        
        HeroBanner.objects.create(
            title="Fast Delivery Nationwide",
            subtitle="Get your parts delivered to your doorstep",
            description="Free shipping on orders over $100",
            button_text="Learn More",
            order=2
        )
    
    # Create sample category sections if none exist
    from products.models import PartCategory
    if not CategorySection.objects.exists() and PartCategory.objects.exists():
        categories = PartCategory.objects.filter(is_active=True)[:6]
        for i, category in enumerate(categories):
            CategorySection.objects.create(
                title=category.name,
                category=category,
                order=i+1
            )
    
    return config