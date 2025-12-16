"""
Cache utilities for the products app
Provides optimized caching functions for brands, models, categories and products
"""
import logging
from django.core.cache import cache
from django.db import models

logger = logging.getLogger(__name__)

# Cache timeout constants (in seconds)
BRAND_CACHE_TIMEOUT = 60 * 15  # 15 minutes
MODEL_CACHE_TIMEOUT = 60 * 15  # 15 minutes
CATEGORY_CACHE_TIMEOUT = 60 * 15  # 15 minutes
PRODUCT_CACHE_TIMEOUT = 60 * 10  # 10 minutes

# Cache key prefixes
BRAND_PREFIX = 'products_brand'
MODEL_PREFIX = 'products_model'
CATEGORY_PREFIX = 'products_category'
PRODUCT_PREFIX = 'products_product'


def get_cache_key(prefix, identifier, extra_suffix=''):
    """
    Generate a standardized cache key
    
    Args:
        prefix (str): Key prefix for the cache type
        identifier (str/int): Unique identifier for the object
        extra_suffix (str): Additional suffix for specific cache keys
        
    Returns:
        str: Formatted cache key
    """
    if extra_suffix:
        return f"{prefix}_{identifier}_{extra_suffix}"
    return f"{prefix}_{identifier}"


def get_brand_list_cache_key():
    """Get cache key for the complete list of brands"""
    return f"{BRAND_PREFIX}_list"


def get_model_list_cache_key(brand_id=None):
    """Get cache key for the list of models, optionally filtered by brand"""
    if brand_id:
        return f"{MODEL_PREFIX}_list_brand_{brand_id}"
    return f"{MODEL_PREFIX}_list"


def get_category_list_cache_key(parent_id=None):
    """Get cache key for the list of categories, optionally filtered by parent"""
    if parent_id is not None:
        return f"{CATEGORY_PREFIX}_list_parent_{parent_id}"
    return f"{CATEGORY_PREFIX}_list"


def get_cached_brand(brand_id):
    """
    Get a brand by ID with caching
    
    Args:
        brand_id (int): The ID of the brand
        
    Returns:
        Brand: The brand instance or None if not found
    """
    from .models import Brand  # Import here to avoid circular import
    
    cache_key = get_cache_key(BRAND_PREFIX, brand_id)
    cached_brand = cache.get(cache_key)
    
    if cached_brand is not None:
        return cached_brand
        
    try:
        brand = Brand.objects.get(id=brand_id)
        cache.set(cache_key, brand, BRAND_CACHE_TIMEOUT)
        return brand
    except Brand.DoesNotExist:
        return None


def get_cached_brand_by_slug(slug):
    """
    Get a brand by slug with caching
    
    Args:
        slug (str): The slug of the brand
        
    Returns:
        Brand: The brand instance or None if not found
    """
    from .models import Brand  # Import here to avoid circular import
    
    cache_key = get_cache_key(BRAND_PREFIX, f"slug_{slug}")
    cached_brand = cache.get(cache_key)
    
    if cached_brand is not None:
        return cached_brand
        
    try:
        brand = Brand.objects.get(slug=slug)
        cache.set(cache_key, brand, BRAND_CACHE_TIMEOUT)
        return brand
    except Brand.DoesNotExist:
        return None


def get_cached_brands_list():
    """
    Get all active brands with caching
    
    Returns:
        QuerySet: Cached queryset of all active brands
    """
    from .models import Brand  # Import here to avoid circular import
    
    cache_key = get_brand_list_cache_key()
    cached_brands = cache.get(cache_key)
    
    if cached_brands is not None:
        return cached_brands
        
    brands = list(Brand.objects.filter(is_active=True).order_by('name'))
    cache.set(cache_key, brands, BRAND_CACHE_TIMEOUT)
    return brands


def get_cached_model(model_id):
    """
    Get a vehicle model by ID with caching
    
    Args:
        model_id (int): The ID of the vehicle model
        
    Returns:
        VehicleModel: The vehicle model instance or None if not found
    """
    from .models import VehicleModel  # Import here to avoid circular import
    
    cache_key = get_cache_key(MODEL_PREFIX, model_id)
    cached_model = cache.get(cache_key)
    
    if cached_model is not None:
        return cached_model
        
    try:
        model = VehicleModel.objects.select_related('brand').get(id=model_id)
        cache.set(cache_key, model, MODEL_CACHE_TIMEOUT)
        return model
    except VehicleModel.DoesNotExist:
        return None


def get_cached_model_by_slug(slug):
    """
    Get a vehicle model by slug with caching
    
    Args:
        slug (str): The slug of the vehicle model
        
    Returns:
        VehicleModel: The vehicle model instance or None if not found
    """
    from .models import VehicleModel  # Import here to avoid circular import
    
    cache_key = get_cache_key(MODEL_PREFIX, f"slug_{slug}")
    cached_model = cache.get(cache_key)
    
    if cached_model is not None:
        return cached_model
        
    try:
        model = VehicleModel.objects.select_related('brand').get(slug=slug)
        cache.set(cache_key, model, MODEL_CACHE_TIMEOUT)
        return model
    except VehicleModel.DoesNotExist:
        return None


def get_cached_models_list(brand_id=None):
    """
    Get all active models with caching, optionally filtered by brand
    
    Args:
        brand_id (int, optional): Filter models by brand ID
        
    Returns:
        list: Cached list of vehicle models
    """
    from .models import VehicleModel  # Import here to avoid circular import
    
    cache_key = get_model_list_cache_key(brand_id)
    cached_models = cache.get(cache_key)
    
    if cached_models is not None:
        return cached_models
        
    queryset = VehicleModel.objects.filter(is_active=True).select_related('brand')
    if brand_id:
        queryset = queryset.filter(brand_id=brand_id)
        
    models = list(queryset.order_by('brand', 'name'))
    cache.set(cache_key, models, MODEL_CACHE_TIMEOUT)
    return models


def get_cached_category(category_id):
    """
    Get a part category by ID with caching
    
    Args:
        category_id (int): The ID of the part category
        
    Returns:
        PartCategory: The part category instance or None if not found
    """
    from .models import PartCategory  # Import here to avoid circular import
    
    cache_key = get_cache_key(CATEGORY_PREFIX, category_id)
    cached_category = cache.get(cache_key)
    
    if cached_category is not None:
        return cached_category
        
    try:
        category = PartCategory.objects.get(id=category_id)
        cache.set(cache_key, category, CATEGORY_CACHE_TIMEOUT)
        return category
    except PartCategory.DoesNotExist:
        return None


def get_cached_category_by_slug(slug):
    """
    Get a part category by slug with caching
    
    Args:
        slug (str): The slug of the part category
        
    Returns:
        PartCategory: The part category instance or None if not found
    """
    from .models import PartCategory  # Import here to avoid circular import
    
    cache_key = get_cache_key(CATEGORY_PREFIX, f"slug_{slug}")
    cached_category = cache.get(cache_key)
    
    if cached_category is not None:
        return cached_category
        
    try:
        category = PartCategory.objects.get(slug=slug)
        cache.set(cache_key, category, CATEGORY_CACHE_TIMEOUT)
        return category
    except PartCategory.DoesNotExist:
        return None


def get_cached_categories_list(parent_id=None):
    """
    Get all active categories with caching, optionally filtered by parent
    
    Args:
        parent_id (int, optional): Filter categories by parent ID (None for top-level)
        
    Returns:
        list: Cached list of part categories
    """
    from .models import PartCategory  # Import here to avoid circular import
    
    cache_key = get_category_list_cache_key(parent_id)
    cached_categories = cache.get(cache_key)
    
    if cached_categories is not None:
        return cached_categories
        
    queryset = PartCategory.objects.filter(is_active=True)
    if parent_id is not None:
        queryset = queryset.filter(parent_id=parent_id)
        
    categories = list(queryset.order_by('name'))
    cache.set(cache_key, categories, CATEGORY_CACHE_TIMEOUT)
    return categories


def get_cached_product(product_id):
    """
    Get a product by ID with caching
    
    Args:
        product_id (int): The ID of the product
        
    Returns:
        Product: The product instance or None if not found
    """
    from .models import Product  # Import here to avoid circular import
    
    cache_key = get_cache_key(PRODUCT_PREFIX, product_id)
    cached_product = cache.get(cache_key)
    
    if cached_product is not None:
        return cached_product
        
    try:
        product = Product.objects.select_related(
            'brand', 'vehicle_model', 'part_category'
        ).get(id=product_id)
        cache.set(cache_key, product, PRODUCT_CACHE_TIMEOUT)
        return product
    except Product.DoesNotExist:
        return None


def get_cached_product_by_slug(slug):
    """
    Get a product by slug with caching
    
    Args:
        slug (str): The slug of the product
        
    Returns:
        Product: The product instance or None if not found
    """
    from .models import Product  # Import here to avoid circular import
    
    cache_key = get_cache_key(PRODUCT_PREFIX, f"slug_{slug}")
    cached_product = cache.get(cache_key)
    
    if cached_product is not None:
        return cached_product
        
    try:
        product = Product.objects.select_related(
            'brand', 'vehicle_model', 'part_category'
        ).get(slug=slug)
        cache.set(cache_key, product, PRODUCT_CACHE_TIMEOUT)
        return product
    except Product.DoesNotExist:
        return None


def invalidate_brand_cache(brand_id):
    """
    Invalidate all cache entries related to a brand
    
    Args:
        brand_id (int): The ID of the brand to invalidate
    """
    from .models import Brand  # Import here to avoid circular import
    
    try:
        brand = Brand.objects.get(id=brand_id)
        cache_keys = [
            get_cache_key(BRAND_PREFIX, brand_id),
            get_cache_key(BRAND_PREFIX, f"slug_{brand.slug}"),
            get_brand_list_cache_key(),
            get_model_list_cache_key(brand_id),
        ]
        cache.delete_many(cache_keys)
        logger.info(f"Invalidated cache for brand {brand_id}")
    except Brand.DoesNotExist:
        # If brand doesn't exist, just invalidate the list cache
        cache_keys = [
            get_brand_list_cache_key(),
        ]
        cache.delete_many(cache_keys)
        logger.info(f"Invalidated brand list cache after brand {brand_id} deletion")


def invalidate_model_cache(model_id, brand_id=None):
    """
    Invalidate all cache entries related to a vehicle model
    
    Args:
        model_id (int): The ID of the vehicle model to invalidate
        brand_id (int, optional): The brand ID if known
    """
    from .models import VehicleModel  # Import here to avoid circular import
    
    cache_keys = [
        get_cache_key(MODEL_PREFIX, model_id),
        get_model_list_cache_key(),
    ]
    
    try:
        model = VehicleModel.objects.get(id=model_id)
        cache_keys.append(get_cache_key(MODEL_PREFIX, f"slug_{model.slug}"))
        if brand_id or model.brand_id:
            brand_id = brand_id or model.brand_id
            cache_keys.append(get_model_list_cache_key(brand_id))
    except VehicleModel.DoesNotExist:
        # If model doesn't exist, we still want to invalidate lists
        if brand_id:
            cache_keys.append(get_model_list_cache_key(brand_id))
    
    cache.delete_many(cache_keys)
    logger.info(f"Invalidated cache for model {model_id}")


def invalidate_category_cache(category_id, parent_id=None):
    """
    Invalidate all cache entries related to a part category
    
    Args:
        category_id (int): The ID of the part category to invalidate
        parent_id (int, optional): The parent ID if known
    """
    from .models import PartCategory  # Import here to avoid circular import
    
    cache_keys = [
        get_cache_key(CATEGORY_PREFIX, category_id),
        get_category_list_cache_key(),
    ]
    
    # Always invalidate both parent-specific and general category lists
    cache_keys.append(get_category_list_cache_key(None))
    
    try:
        category = PartCategory.objects.get(id=category_id)
        cache_keys.append(get_cache_key(CATEGORY_PREFIX, f"slug_{category.slug}"))
        # Invalidate cache for this category's parent if it exists
        if category.parent_id:
            cache_keys.append(get_category_list_cache_key(category.parent_id))
        # Also invalidate cache for subcategories of this category
        cache_keys.append(get_category_list_cache_key(category_id))
    except PartCategory.DoesNotExist:
        # If category doesn't exist, we still want to invalidate lists
        if parent_id is not None:
            cache_keys.append(get_category_list_cache_key(parent_id))
        cache_keys.append(get_category_list_cache_key(None))
    
    cache.delete_many(cache_keys)
    logger.info(f"Invalidated cache for category {category_id}")


def invalidate_product_cache(product_id):
    """
    Invalidate all cache entries related to a product
    
    Args:
        product_id (int): The ID of the product to invalidate
    """
    from .models import Product  # Import here to avoid circular import
    
    cache_keys = [
        get_cache_key(PRODUCT_PREFIX, product_id),
    ]
    try:
        product = Product.objects.get(id=product_id)
        cache_keys.append(get_cache_key(PRODUCT_PREFIX, f"slug_{product.slug}"))
    except Product.DoesNotExist:
        pass
    cache.delete_many(cache_keys)
    logger.info(f"Invalidated cache for product {product_id}")


def invalidate_all_products_cache():
    """
    Invalidate all product-related cache entries
    This should be called when bulk operations affect products
    """
    # This is a more aggressive invalidation that clears all product caches
    # In production, you might want to be more selective
    cache.delete_pattern(f"{PRODUCT_PREFIX}_*")
    cache.delete_pattern(f"{BRAND_PREFIX}_*")
    cache.delete_pattern(f"{MODEL_PREFIX}_*")
    cache.delete_pattern(f"{CATEGORY_PREFIX}_*")
    logger.info("Invalidated all product-related cache entries")
