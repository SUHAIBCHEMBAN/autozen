"""
Cache utilities for the products app.

This module provides caching functions for common product-related queries
to improve performance and reduce database load.
"""

from django.core.cache import cache
from django.conf import settings
from .models import Brand, VehicleModel, PartCategory, Product


def get_products_cache_timeout():
    """
    Get cache timeout for products from settings or default to 15 minutes.
    
    Retrieves the PRODUCTS_CACHE_TIMEOUT setting from Django settings,
    defaulting to 15 minutes (900 seconds) if not configured.
    
    Returns:
        int: Cache timeout in seconds
    """
    return getattr(settings, 'PRODUCTS_CACHE_TIMEOUT', 60 * 15)


def invalidate_brand_cache(brand_id):
    """
    Invalidate all cache entries for a brand.
    
    Deletes cached data for brand-related information including:
    - Brand models count
    - Brand models list
    
    Args:
        brand_id (int): The ID of the brand whose cache to invalidate
    """
    cache_keys = [
        f'brand_models_count_{brand_id}',
        f'brand_models_{brand_id}',
    ]
    cache.delete_many(cache_keys)


def invalidate_vehicle_model_cache(model_id):
    """
    Invalidate all cache entries for a vehicle model.
    
    Deletes cached data for vehicle model-related information including:
    - Vehicle model products count
    - Vehicle model products list
    
    Args:
        model_id (int): The ID of the vehicle model whose cache to invalidate
    """
    cache_keys = [
        f'vehicle_model_products_count_{model_id}',
        f'vehicle_model_products_{model_id}',
    ]
    cache.delete_many(cache_keys)


def invalidate_part_category_cache(category_id):
    """
    Invalidate all cache entries for a part category.
    
    Deletes cached data for part category-related information including:
    - Part category subcategories count
    - Part category subcategories list
    - Part category products list
    - Part category instance
    - Part category is_parent flag
    - Part category full path
    
    Args:
        category_id (int): The ID of the part category whose cache to invalidate
    """
    cache_keys = [
        f'part_category_subcategories_count_{category_id}',
        f'part_category_subcategories_{category_id}',
        f'part_category_products_{category_id}',
        f'part_category_instance_{category_id}',
        f'part_category_is_parent_{category_id}',
        f'part_category_full_path_{category_id}',
    ]
    cache.delete_many(cache_keys)


def invalidate_product_cache(product_id=None, sku=None):
    """
    Invalidate cache entries for a product.
    
    Args:
        product_id (int, optional): The ID of the product whose cache to invalidate
        sku (str, optional): The SKU of the product whose cache to invalidate
    """
    cache_keys = []
    if product_id:
        cache_keys.append(f'product_instance_{product_id}')
    if sku:
        cache_keys.append(f'product_by_sku_{sku}')
    
    if cache_keys:
        cache.delete_many(cache_keys)


def get_active_brands():
    """
    Get all active brands with Redis caching.
    
    Retrieves all active brands ordered by name with caching for improved
    performance and reduced database queries.
    
    Returns:
        QuerySet: Active Brand objects ordered by name
    """
    cache_key = 'active_brands'
    cached_brands = cache.get(cache_key)
    
    if cached_brands is not None:
        return cached_brands
    
    brands = Brand.objects.filter(is_active=True).order_by('name')
    cache.set(cache_key, brands, get_products_cache_timeout())
    return brands


def get_active_categories():
    """
    Get all active categories with Redis caching.
    
    Retrieves all active categories ordered by name with caching for improved
    performance and reduced database queries.
    
    Returns:
        QuerySet: Active PartCategory objects ordered by name
    """
    cache_key = 'active_categories'
    cached_categories = cache.get(cache_key)
    
    if cached_categories is not None:
        return cached_categories
    
    categories = PartCategory.objects.filter(is_active=True).order_by('name')
    cache.set(cache_key, categories, get_products_cache_timeout())
    return categories


def get_active_models():
    """
    Get all active vehicle models with Redis caching.
    
    Retrieves all active vehicle models ordered by brand and name with caching
    for improved performance and reduced database queries.
    
    Returns:
        QuerySet: Active VehicleModel objects ordered by brand and name
    """
    cache_key = 'active_models'
    cached_models = cache.get(cache_key)
    
    if cached_models is not None:
        return cached_models
    
    models = VehicleModel.objects.filter(is_active=True).select_related('brand').order_by('brand', 'name')
    cache.set(cache_key, models, get_products_cache_timeout())
    return models


def get_featured_products(limit=12):
    """
    Get featured products with Redis caching.
    
    Retrieves featured products ordered by creation date with caching
    for improved performance and reduced database queries.
    
    Args:
        limit (int): Maximum number of products to return (default: 12)
        
    Returns:
        QuerySet: Active featured Product objects ordered by creation date
    """
    cache_key = f'featured_products_{limit}'
    cached_products = cache.get(cache_key)
    
    if cached_products is not None:
        return cached_products
    
    products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related(
        'brand', 'vehicle_model', 'part_category'
    ).order_by('-created_at')[:limit]
    
    cache.set(cache_key, products, get_products_cache_timeout())
    return products


def get_products_by_brand(brand_slug, limit=50):
    """
    Get products by brand with Redis caching.
    
    Retrieves products for a specific brand with caching for improved
    performance and reduced database queries.
    
    Args:
        brand_slug (str): The slug of the brand to filter by
        limit (int): Maximum number of products to return (default: 50)
        
    Returns:
        QuerySet: Product objects for the specified brand
    """
    cache_key = f'products_by_brand_{brand_slug}_{limit}'
    cached_products = cache.get(cache_key)
    
    if cached_products is not None:
        return cached_products
    
    try:
        brand = Brand.objects.get(slug=brand_slug, is_active=True)
        products = Product.objects.filter(
            brand=brand,
            is_active=True
        ).select_related(
            'brand', 'vehicle_model', 'part_category'
        ).order_by('-created_at')[:limit]
        
        cache.set(cache_key, products, get_products_cache_timeout())
        return products
    except Brand.DoesNotExist:
        return Product.objects.none()


def get_products_by_category(category_slug, limit=50):
    """
    Get products by category with Redis caching.
    
    Retrieves products for a specific category with caching for improved
    performance and reduced database queries.
    
    Args:
        category_slug (str): The slug of the category to filter by
        limit (int): Maximum number of products to return (default: 50)
        
    Returns:
        QuerySet: Product objects for the specified category
    """
    cache_key = f'products_by_category_{category_slug}_{limit}'
    cached_products = cache.get(cache_key)
    
    if cached_products is not None:
        return cached_products
    
    try:
        category = PartCategory.objects.get(slug=category_slug, is_active=True)
        products = Product.objects.filter(
            part_category=category,
            is_active=True
        ).select_related(
            'brand', 'vehicle_model', 'part_category'
        ).order_by('-created_at')[:limit]
        
        cache.set(cache_key, products, get_products_cache_timeout())
        return products
    except PartCategory.DoesNotExist:
        return Product.objects.none()


def get_products_by_model(model_slug, limit=50):
    """
    Get products by vehicle model with Redis caching.
    
    Retrieves products for a specific vehicle model with caching for improved
    performance and reduced database queries.
    
    Args:
        model_slug (str): The slug of the vehicle model to filter by
        limit (int): Maximum number of products to return (default: 50)
        
    Returns:
        QuerySet: Product objects for the specified vehicle model
    """
    cache_key = f'products_by_model_{model_slug}_{limit}'
    cached_products = cache.get(cache_key)
    
    if cached_products is not None:
        return cached_products
    
    try:
        model = VehicleModel.objects.get(slug=model_slug, is_active=True)
        products = Product.objects.filter(
            vehicle_model=model,
            is_active=True
        ).select_related(
            'brand', 'vehicle_model', 'part_category'
        ).order_by('-created_at')[:limit]
        
        cache.set(cache_key, products, get_products_cache_timeout())
        return products
    except VehicleModel.DoesNotExist:
        return Product.objects.none()


def get_product_by_slug(product_slug):
    """
    Get a product by slug with Redis caching.
    
    Retrieves a specific product by its slug with caching for improved
    performance and reduced database queries.
    
    Args:
        product_slug (str): The slug of the product to retrieve
        
    Returns:
        Product: The product object or None if not found
    """
    cache_key = f'product_by_slug_{product_slug}'
    cached_product = cache.get(cache_key)
    
    if cached_product is not None:
        return cached_product
    
    try:
        product = Product.objects.select_related(
            'brand', 'vehicle_model', 'part_category'
        ).get(slug=product_slug, is_active=True)
        cache.set(cache_key, product, get_products_cache_timeout())
        return product
    except Product.DoesNotExist:
        return None


def get_product_by_sku(product_sku):
    """
    Get a product by SKU with Redis caching.
    
    Retrieves a specific product by its SKU with caching for improved
    performance and reduced database queries.
    
    Args:
        product_sku (str): The SKU of the product to retrieve
        
    Returns:
        Product: The product object or None if not found
    """
    cache_key = f'product_by_sku_{product_sku}'
    cached_product = cache.get(cache_key)
    
    if cached_product is not None:
        return cached_product
    
    try:
        product = Product.objects.select_related(
            'brand', 'vehicle_model', 'part_category'
        ).get(sku=product_sku, is_active=True)
        cache.set(cache_key, product, get_products_cache_timeout())
        return product
    except Product.DoesNotExist:
        return None


def search_products(query, limit=50):
    """
    Search products with Redis caching.
    
    Searches products by name, description, SKU, and related fields with
    caching for improved performance and reduced database queries.
    
    Args:
        query (str): The search query
        limit (int): Maximum number of products to return (default: 50)
        
    Returns:
        QuerySet: Product objects matching the search query
    """
    # Sanitize query for cache key
    sanitized_query = ''.join(c if c.isalnum() or c in '-_' else '_' for c in query)[:50]
    cache_key = f'search_products_{sanitized_query}_{limit}'
    cached_products = cache.get(cache_key)
    
    if cached_products is not None:
        return cached_products
    
    from django.db.models import Q
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(short_description__icontains=query) |
        Q(sku__icontains=query) |
        Q(brand__name__icontains=query) |
        Q(vehicle_model__name__icontains=query) |
        Q(part_category__name__icontains=query)
    ).filter(
        is_active=True
    ).select_related(
        'brand', 'vehicle_model', 'part_category'
    ).distinct().order_by('-created_at')[:limit]
    
    cache.set(cache_key, products, get_products_cache_timeout())
    return products


def get_in_stock_products(limit=50):
    """
    Get in-stock products with Redis caching.
    
    Retrieves products that are currently in stock with caching for improved
    performance and reduced database queries.
    
    Args:
        limit (int): Maximum number of products to return (default: 50)
        
    Returns:
        QuerySet: In-stock Product objects ordered by creation date
    """
    cache_key = f'in_stock_products_{limit}'
    cached_products = cache.get(cache_key)
    
    if cached_products is not None:
        return cached_products
    
    from django.db.models import Q
    products = Product.objects.filter(
        Q(is_active=True) & (
            Q(track_inventory=False) | 
            Q(stock_quantity__gt=0) | 
            Q(continue_selling=True)
        )
    ).select_related(
        'brand', 'vehicle_model', 'part_category'
    ).order_by('-created_at')[:limit]
    
    cache.set(cache_key, products, get_products_cache_timeout())
    return products


def get_navigation_tree():
    """
    Generate a navigation tree for brands, models, and categories with caching.
    
    Creates a hierarchical navigation structure for frontend menus with caching
    for improved performance and reduced database queries.
    
    Returns:
        dict: Navigation data structure containing brands and categories
    """
    cache_key = 'navigation_tree'
    cached_nav = cache.get(cache_key)
    
    if cached_nav is not None:
        return cached_nav
    
    # Get all active brands with their models
    brands = Brand.objects.filter(is_active=True).prefetch_related('models')
    
    # Get top-level categories with subcategories
    categories = PartCategory.objects.filter(
        is_active=True, 
        parent=None
    ).prefetch_related('subcategories')
    
    navigation_data = {
        'brands': [],
        'categories': []
    }
    
    # Build brand hierarchy
    for brand in brands:
        brand_data = {
            'id': brand.id,
            'name': brand.name,
            'slug': brand.slug,
            'models': [
                {
                    'id': model.id,
                    'name': model.name,
                    'slug': model.slug
                }
                for model in brand.models.filter(is_active=True)
            ]
        }
        navigation_data['brands'].append(brand_data)
    
    # Build category hierarchy
    for category in categories:
        category_data = {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'subcategories': [
                {
                    'id': subcat.id,
                    'name': subcat.name,
                    'slug': subcat.slug
                }
                for subcat in category.subcategories.filter(is_active=True)
            ]
        }
        navigation_data['categories'].append(category_data)
    
    cache.set(cache_key, navigation_data, get_products_cache_timeout())
    return navigation_data