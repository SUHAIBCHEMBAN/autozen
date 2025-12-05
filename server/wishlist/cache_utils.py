"""
Cache utilities for the wishlist app
Provides optimized caching functions for wishlist operations with Redis
"""

import logging
from django.core.cache import cache
from django.conf import settings

# Cache timeout settings
WISHLIST_CACHE_TIMEOUT = getattr(settings, 'WISHLIST_CACHE_TIMEOUT', 60 * 15)  # 15 minutes
WISHLIST_ITEM_CACHE_TIMEOUT = getattr(settings, 'WISHLIST_ITEM_CACHE_TIMEOUT', 60 * 15)  # 15 minutes

logger = logging.getLogger(__name__)


def get_wishlist_cache_key(user_id):
    """
    Generate cache key for user's wishlist
    
    Args:
        user_id (int): The ID of the user
        
    Returns:
        str: Formatted cache key
    """
    return f"wishlist_user_{user_id}"


def get_wishlist_items_cache_key(user_id):
    """
    Generate cache key for user's wishlist items
    
    Args:
        user_id (int): The ID of the user
        
    Returns:
        str: Formatted cache key
    """
    return f"wishlist_items_user_{user_id}"


def get_wishlist_item_cache_key(wishlist_id, product_id):
    """
    Generate cache key for a specific wishlist item
    
    Args:
        wishlist_id (int): The ID of the wishlist
        product_id (int): The ID of the product
        
    Returns:
        str: Formatted cache key
    """
    return f"wishlist_item_{wishlist_id}_{product_id}"


def get_wishlist_count_cache_key(user_id):
    """
    Generate cache key for user's wishlist count
    
    Args:
        user_id (int): The ID of the user
        
    Returns:
        str: Formatted cache key
    """
    return f"wishlist_count_user_{user_id}"


def get_cached_wishlist(user_id):
    """
    Get a user's wishlist with caching
    
    Args:
        user_id (int): The ID of the user
        
    Returns:
        Wishlist: The wishlist instance or None if not found
    """
    from .models import Wishlist  # Import here to avoid circular import
    
    cache_key = get_wishlist_cache_key(user_id)
    cached_wishlist = cache.get(cache_key)
    
    if cached_wishlist is not None:
        return cached_wishlist
        
    try:
        wishlist = Wishlist.objects.get(user_id=user_id)
        cache.set(cache_key, wishlist, WISHLIST_CACHE_TIMEOUT)
        return wishlist
    except Wishlist.DoesNotExist:
        return None


def get_cached_wishlist_items(user_id):
    """
    Get all items in a user's wishlist with caching
    
    Args:
        user_id (int): The ID of the user
        
    Returns:
        list: Cached list of wishlist items
    """
    from .models import Wishlist, WishlistItem  # Import here to avoid circular import
    
    cache_key = get_wishlist_items_cache_key(user_id)
    cached_items = cache.get(cache_key)
    
    if cached_items is not None:
        return cached_items
        
    try:
        wishlist = Wishlist.objects.get(user_id=user_id)
        items = list(wishlist.items.all().select_related('product', 'product__brand', 'product__vehicle_model', 'product__part_category'))
        cache.set(cache_key, items, WISHLIST_ITEM_CACHE_TIMEOUT)
        return items
    except Wishlist.DoesNotExist:
        return []


def get_cached_wishlist_count(user_id):
    """
    Get the number of items in a user's wishlist with caching
    
    Args:
        user_id (int): The ID of the user
        
    Returns:
        int: Number of items in the wishlist
    """
    cache_key = get_wishlist_count_cache_key(user_id)
    cached_count = cache.get(cache_key)
    
    if cached_count is not None:
        return cached_count
    
    # If not in cache, get from database and cache it
    from .models import Wishlist  # Import here to avoid circular import
    try:
        wishlist = Wishlist.objects.get(user_id=user_id)
        count = wishlist.items.count()
        cache.set(cache_key, count, WISHLIST_CACHE_TIMEOUT)
        return count
    except Wishlist.DoesNotExist:
        return 0


def is_product_in_wishlist_cached(user_id, product_id):
    """
    Check if a product is in a user's wishlist with caching
    
    Args:
        user_id (int): The ID of the user
        product_id (int): The ID of the product
        
    Returns:
        bool: True if product is in wishlist, False otherwise
    """
    from .models import Wishlist, WishlistItem  # Import here to avoid circular import
    
    # First check if we have cached wishlist items
    cache_key = get_wishlist_items_cache_key(user_id)
    cached_items = cache.get(cache_key)
    
    if cached_items is not None:
        # Check in cached items
        for item in cached_items:
            if item.product_id == product_id:
                return True
        return False
    
    # If not cached, check in database
    try:
        wishlist = Wishlist.objects.get(user_id=user_id)
        return WishlistItem.objects.filter(
            wishlist=wishlist,
            product_id=product_id
        ).exists()
    except Wishlist.DoesNotExist:
        return False


def add_to_wishlist_with_cache(user, product_id):
    """
    Add a product to a user's wishlist with caching
    
    Args:
        user (User): The user instance
        product_id (int): The ID of the product
        
    Returns:
        dict: Result dictionary with success status and message
    """
    from products.models import Product
    from .models import Wishlist, WishlistItem
    
    try:
        product = Product.objects.get(id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        
        # Check if item already exists
        if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
            return {
                'success': True,
                'message': 'Product already in wishlist',
                'created': False
            }
        
        # Add item to wishlist
        wishlist_item = WishlistItem.objects.create(
            wishlist=wishlist,
            product=product
        )
        
        # Update wishlist timestamp
        wishlist.save()
        
        # Invalidate cache for this user's wishlist
        invalidate_wishlist_cache(user.id)
        
        return {
            'success': True,
            'message': 'Product added to wishlist',
            'created': True,
            'item_id': wishlist_item.id
        }
    except Product.DoesNotExist:
        return {
            'success': False,
            'message': 'Product not found'
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }


def remove_from_wishlist_with_cache(user, product_id):
    """
    Remove a product from a user's wishlist with caching
    
    Args:
        user (User): The user instance
        product_id (int): The ID of the product
        
    Returns:
        dict: Result dictionary with success status and message
    """
    from products.models import Product
    from .models import Wishlist, WishlistItem
    
    try:
        wishlist = Wishlist.objects.get(user=user)
        product = Product.objects.get(id=product_id)
        
        # Remove item from wishlist
        wishlist_item = WishlistItem.objects.get(
            wishlist=wishlist,
            product=product
        )
        wishlist_item.delete()
        
        # Update wishlist timestamp
        wishlist.save()
        
        # Invalidate cache for this user's wishlist
        invalidate_wishlist_cache(user.id)
        
        return {
            'success': True,
            'message': 'Product removed from wishlist'
        }
    except Wishlist.DoesNotExist:
        return {
            'success': False,
            'message': 'Wishlist not found'
        }
    except Product.DoesNotExist:
        return {
            'success': False,
            'message': 'Product not found'
        }
    except WishlistItem.DoesNotExist:
        return {
            'success': False,
            'message': 'Product not in wishlist'
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }


def clear_wishlist_with_cache(user):
    """
    Clear all items from a user's wishlist with caching
    
    Args:
        user (User): The user instance
        
    Returns:
        dict: Result dictionary with success status and message
    """
    from .models import Wishlist
    
    try:
        wishlist = Wishlist.objects.get(user=user)
        count = wishlist.items.count()
        wishlist.items.all().delete()
        wishlist.save()
        
        # Invalidate cache for this user's wishlist
        invalidate_wishlist_cache(user.id)
        
        return {
            'success': True,
            'message': f'{count} items removed from wishlist'
        }
    except Wishlist.DoesNotExist:
        return {
            'success': False,
            'message': 'Wishlist not found'
        }


def get_cached_wishlist_response(user_id):
    """
    Get a fully serialized wishlist response with caching
    
    Args:
        user_id (int): The ID of the user
        
    Returns:
        dict: Serialized wishlist response or None if not cached
    """
    cache_key = f'wishlist_response_{user_id}'
    cached_response = cache.get(cache_key)
    
    if cached_response is not None:
        return cached_response
    
    return None


def cache_wishlist_response(user_id, response_data):
    """
    Cache a fully serialized wishlist response
    
    Args:
        user_id (int): The ID of the user
        response_data (dict): The serialized wishlist response
    """
    cache_key = f'wishlist_response_{user_id}'
    cache.set(cache_key, response_data, WISHLIST_CACHE_TIMEOUT)


def invalidate_wishlist_cache(user_id):
    """
    Invalidate all cache entries related to a user's wishlist
    
    Args:
        user_id (int): The ID of the user
    """
    cache_keys = [
        get_wishlist_cache_key(user_id),
        get_wishlist_items_cache_key(user_id),
        get_wishlist_count_cache_key(user_id),
        f'wishlist_response_{user_id}',
    ]
    
    cache.delete_many(cache_keys)
    logger.info(f"Invalidated cache for user {user_id}'s wishlist")