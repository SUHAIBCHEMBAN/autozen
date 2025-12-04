"""
Utility functions for the products app with Redis caching support.

This module provides utility functions for common product-related operations
and integrates with the caching system to improve performance.
"""

from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .models import Brand, VehicleModel, PartCategory, Product
from .cache_utils import (
    get_active_brands, get_active_models, get_active_categories,
    get_featured_products, get_navigation_tree
)


def create_brand(name, description="", logo=None):
    """
    Create a new brand with proper slug generation.
    
    Args:
        name (str): The name of the brand
        description (str): Optional description of the brand
        logo (File): Optional logo image file
        
    Returns:
        tuple: (Brand instance, created boolean)
    """
    brand, created = Brand.objects.get_or_create(
        name=name,
        defaults={
            'description': description,
            'logo': logo,
            'slug': slugify(name)
        }
    )
    return brand, created


def create_vehicle_model(brand, name, description="", year_from=None, year_to=None, image=None):
    """
    Create a new vehicle model with proper slug generation.
    
    Args:
        brand (Brand): The brand this model belongs to
        name (str): The name of the vehicle model
        description (str): Optional description of the model
        year_from (int): Optional starting year for this model
        year_to (int): Optional ending year for this model
        image (File): Optional image file
        
    Returns:
        tuple: (VehicleModel instance, created boolean)
    """
    model, created = VehicleModel.objects.get_or_create(
        brand=brand,
        name=name,
        defaults={
            'description': description,
            'year_from': year_from,
            'year_to': year_to,
            'image': image,
            'slug': slugify(f"{brand.name}-{name}")
        }
    )
    return model, created


def create_part_category(name, parent=None, description="", image=None):
    """
    Create a new part category with proper slug generation.
    
    Args:
        name (str): The name of the part category
        parent (PartCategory): Optional parent category for hierarchical structure
        description (str): Optional description of the category
        image (File): Optional image file
        
    Returns:
        tuple: (PartCategory instance, created boolean)
    """
    category, created = PartCategory.objects.get_or_create(
        name=name,
        parent=parent,
        defaults={
            'description': description,
            'image': image,
            'slug': slugify(name)
        }
    )
    return category, created


def create_product(brand, vehicle_model, part_category, name, sku, price, **kwargs):
    """
    Create a new product with validation.
    
    Args:
        brand (Brand): The brand this product belongs to
        vehicle_model (VehicleModel): The vehicle model this product fits
        part_category (PartCategory): The category this product belongs to
        name (str): The name of the product
        sku (str): The SKU of the product (must be unique)
        price (Decimal): The price of the product
        **kwargs: Additional product attributes
        
    Returns:
        tuple: (Product instance, created boolean)
        
    Raises:
        ValidationError: If validation fails
    """
    # Validate that the vehicle model belongs to the brand
    if vehicle_model.brand != brand:
        raise ValidationError("Vehicle model must belong to the specified brand")
    
    product, created = Product.objects.get_or_create(
        sku=sku,
        defaults={
            'brand': brand,
            'vehicle_model': vehicle_model,
            'part_category': part_category,
            'name': name,
            'price': price,
            'slug': slugify(name),
            **kwargs
        }
    )
    return product, created


def get_category_hierarchy(category):
    """
    Get the full hierarchy path for a category.
    
    Returns a list from root to current category.
    
    Args:
        category (PartCategory): The category to get hierarchy for
        
    Returns:
        list: List of PartCategory objects from root to current
    """
    hierarchy = []
    current = category
    while current:
        hierarchy.insert(0, current)
        current = current.parent
    return hierarchy


def get_products_by_hierarchy(brand_name=None, model_name=None, category_name=None):
    """
    Get products filtered by brand, model, and/or category.
    
    Args:
        brand_name (str): Optional brand name to filter by
        model_name (str): Optional model name to filter by
        category_name (str): Optional category name to filter by
        
    Returns:
        QuerySet: Filtered Product objects with related data prefetched
    """
    products = Product.objects.filter(is_active=True)
    
    if brand_name:
        products = products.filter(brand__name__iexact=brand_name)
    
    if model_name:
        products = products.filter(vehicle_model__name__iexact=model_name)
    
    if category_name:
        products = products.filter(part_category__name__iexact=category_name)
    
    return products.select_related('brand', 'vehicle_model', 'part_category')


def bulk_create_products(product_data_list):
    """
    Bulk create products from a list of dictionaries.
    
    Each dict should contain the required fields for product creation.
    
    Args:
        product_data_list (list): List of dictionaries with product data
        
    Returns:
        list: List of created Product instances
    """
    products = []
    for data in product_data_list:
        try:
            brand = data.pop('brand')
            vehicle_model = data.pop('vehicle_model')
            part_category = data.pop('part_category')
            
            product, created = create_product(
                brand=brand,
                vehicle_model=vehicle_model,
                part_category=part_category,
                **data
            )
            if created:
                products.append(product)
        except Exception as e:
            print(f"Error creating product {data.get('name', 'Unknown')}: {e}")
    
    return products


def get_navigation_tree_cached():
    """
    Generate a navigation tree for brands, models, and categories with caching.
    
    Useful for frontend navigation menus. Uses Redis caching for improved
    performance and reduced database queries.
    
    Returns:
        dict: Navigation data structure containing brands and categories
    """
    return get_navigation_tree()