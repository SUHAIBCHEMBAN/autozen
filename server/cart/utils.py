from django.core.cache import cache
from django.conf import settings
from .models import Cart, CartItem
from products.models import Product


def get_cache_timeout():
    """
    Get cache timeout from settings or default to 15 minutes.
    
    Retrieves the CART_CACHE_TIMEOUT setting from Django settings,
    defaulting to 15 minutes (900 seconds) if not configured.
    
    Returns:
        int: Cache timeout in seconds
    """
    return getattr(settings, 'CART_CACHE_TIMEOUT', 60 * 15)


def invalidate_user_cart_cache(user_id):
    """
    Invalidate all cache entries for a user's cart.
    
    Deletes cached data for both cart and cart items for the specified user.
    This ensures data consistency when cart contents change.
    
    Args:
        user_id (int): The ID of the user whose cart cache to invalidate
    """
    cache_keys = [
        f"cart_{user_id}",
        f"cart_items_{user_id}",
    ]
    cache.delete_many(cache_keys)


def invalidate_cart_properties_cache(cart_id):
    """
    Invalidate cache entries for cart properties.
    
    Deletes cached data for cart properties (items_count, total_quantity, subtotal).
    This ensures data consistency when cart contents change.
    
    Args:
        cart_id (int): The ID of the cart whose property cache to invalidate
    """
    cache_keys = [
        f"cart_items_count_{cart_id}",
        f"cart_total_quantity_{cart_id}",
        f"cart_subtotal_{cart_id}",
    ]
    cache.delete_many(cache_keys)


def clear_all_cart_cache():
    """
    Clear all cart-related cache entries.
    
    WARNING: This should be used sparingly as it affects all users.
    Clears all cache data related to carts across the entire application.
    In a production environment, targeted cache invalidation is preferred.
    """
    # In a production environment, you might want to use a more targeted approach
    # This is a simple implementation that clears all cache
    cache.clear()


def add_to_cart(user, product_id, quantity=1):
    """
    Add a product to a user's cart.
    
    Adds the specified product with the given quantity to the user's cart.
    Performs stock validation and cache invalidation upon success.
    
    Args:
        user: User object
        product_id (int): ID of the product to add
        quantity (int): Quantity to add (default: 1)
    
    Returns:
        dict: Result with success status and message
    """
    try:
        product = Product.objects.get(id=product_id)
        
        # Check stock availability
        if product.stock_quantity < quantity:
            return {
                'success': False,
                'message': f'Insufficient stock. Only {product.stock_quantity} available.'
            }
        
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=user)
        
        # Add item to cart
        cart_item = cart.add_item(product, quantity)
        
        # Invalidate cache
        invalidate_user_cart_cache(user.id)
        invalidate_cart_properties_cache(cart.id)
        
        return {
            'success': True,
            'message': f'{quantity} x {product.name} added to cart',
            'item_id': cart_item.id
        }
    except Product.DoesNotExist:
        return {
            'success': False,
            'message': 'Product not found'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error adding product to cart: {str(e)}'
        }


def remove_from_cart(user, product_id):
    """
    Remove a product from a user's cart.
    
    Completely removes the specified product from the user's cart.
    Performs cache invalidation upon success.
    
    Args:
        user: User object
        product_id (int): ID of the product to remove
    
    Returns:
        dict: Result with success status and message
    """
    try:
        product = Product.objects.get(id=product_id)
        
        # Get cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return {
                'success': False,
                'message': 'Cart not found'
            }
        
        # Remove item from cart
        if cart.remove_item(product):
            # Invalidate cache
            invalidate_user_cart_cache(user.id)
            invalidate_cart_properties_cache(cart.id)
            
            return {
                'success': True,
                'message': f'{product.name} removed from cart'
            }
        else:
            return {
                'success': False,
                'message': 'Product not in cart'
            }
    except Product.DoesNotExist:
        return {
            'success': False,
            'message': 'Product not found'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error removing product from cart: {str(e)}'
        }


def update_cart_item(user, product_id, quantity):
    """
    Update the quantity of a product in a user's cart.
    
    Updates the quantity of the specified product in the user's cart.
    If quantity is 0 or negative, the product is removed from the cart.
    Performs stock validation and cache invalidation upon success.
    
    Args:
        user: User object
        product_id (int): ID of the product to update
        quantity (int): New quantity
    
    Returns:
        dict: Result with success status and message
    """
    if quantity <= 0:
        return remove_from_cart(user, product_id)
    
    try:
        product = Product.objects.get(id=product_id)
        
        # Check stock availability
        if product.stock_quantity < quantity:
            return {
                'success': False,
                'message': f'Insufficient stock. Only {product.stock_quantity} available.'
            }
        
        # Get cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return {
                'success': False,
                'message': 'Cart not found'
            }
        
        # Update item quantity
        cart_item = cart.update_item_quantity(product, quantity)
        if cart_item:
            # Invalidate cache
            invalidate_user_cart_cache(user.id)
            invalidate_cart_properties_cache(cart.id)
            
            return {
                'success': True,
                'message': f'{product.name} quantity updated to {quantity}'
            }
        else:
            return {
                'success': False,
                'message': 'Product not in cart'
            }
    except Product.DoesNotExist:
        return {
            'success': False,
            'message': 'Product not found'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error updating cart item: {str(e)}'
        }


def clear_cart(user):
    """
    Clear all items from a user's cart.
    
    Removes all items from the user's cart, leaving an empty cart.
    Performs cache invalidation upon success.
    
    Args:
        user: User object
    
    Returns:
        dict: Result with success status and message
    """
    try:
        cart = Cart.objects.get(user=user)
        cart.clear()
        
        # Invalidate cache
        invalidate_user_cart_cache(user.id)
        invalidate_cart_properties_cache(cart.id)
        
        return {
            'success': True,
            'message': 'Cart cleared successfully'
        }
    except Cart.DoesNotExist:
        return {
            'success': False,
            'message': 'Cart not found'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error clearing cart: {str(e)}'
        }


def get_cart_summary(user):
    """
    Get a summary of a user's cart.
    
    Retrieves key metrics about the user's cart including items count,
    total quantity, and subtotal. Uses caching for performance.
    
    Args:
        user: User object
    
    Returns:
        dict: Cart summary with items count, total quantity, and subtotal
    """
    try:
        # Try to get cart from cache first
        cache_key = f"cart_{user.id}"
        cached_cart = cache.get(cache_key)
        
        if cached_cart:
            cart = cached_cart
        else:
            cart, created = Cart.objects.get_or_create(user=user)
            # Cache for the specified timeout
            cache.set(cache_key, cart, get_cache_timeout())
        
        return {
            'items_count': cart.items_count,
            'total_quantity': cart.total_quantity,
            'subtotal': float(cart.subtotal),
            'currency': 'USD'  # Adjust as needed
        }
    except Exception as e:
        return {
            'items_count': 0,
            'total_quantity': 0,
            'subtotal': 0.00,
            'error': str(e)
        }


def is_product_in_cart(user, product_id):
    """
    Check if a product is in a user's cart.
    
    Determines whether the specified product exists in the user's cart.
    
    Args:
        user: User object
        product_id (int): ID of the product to check
    
    Returns:
        bool: True if product is in cart, False otherwise
    """
    try:
        cart = Cart.objects.get(user=user)
        return cart.items.filter(product_id=product_id).exists()
    except Cart.DoesNotExist:
        return False