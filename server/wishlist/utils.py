"""
Utility functions for the wishlist app
"""

from .models import Wishlist, WishlistItem
from products.models import Product


def add_to_wishlist(user, product_id):
    """
    Add a product to a user's wishlist
    """
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


def remove_from_wishlist(user, product_id):
    """
    Remove a product from a user's wishlist
    """
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


def get_wishlist_items(user):
    """
    Get all items in a user's wishlist
    """
    try:
        wishlist = Wishlist.objects.get(user=user)
        return wishlist.items.all().select_related('product')
    except Wishlist.DoesNotExist:
        return []


def clear_wishlist(user):
    """
    Clear all items from a user's wishlist
    """
    try:
        wishlist = Wishlist.objects.get(user=user)
        count = wishlist.items.count()
        wishlist.items.all().delete()
        wishlist.save()
        
        return {
            'success': True,
            'message': f'{count} items removed from wishlist'
        }
    except Wishlist.DoesNotExist:
        return {
            'success': False,
            'message': 'Wishlist not found'
        }


def is_product_in_wishlist(user, product_id):
    """
    Check if a product is in a user's wishlist
    """
    try:
        wishlist = Wishlist.objects.get(user=user)
        return WishlistItem.objects.filter(
            wishlist=wishlist,
            product_id=product_id
        ).exists()
    except Wishlist.DoesNotExist:
        return False


def get_wishlist_count(user):
    """
    Get the number of items in a user's wishlist
    """
    try:
        wishlist = Wishlist.objects.get(user=user)
        return wishlist.items.count()
    except Wishlist.DoesNotExist:
        return 0