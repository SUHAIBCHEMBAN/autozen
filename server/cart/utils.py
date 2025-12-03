"""
Utility functions for the cart app
"""

from .models import Cart, CartItem
from products.models import Product


def add_to_cart(user, product_id, quantity=1):
    """
    Add a product to a user's cart
    """
    try:
        product = Product.objects.get(id=product_id)
        
        # Check product stock
        if product.stock_quantity < quantity:
            return {
                'success': False,
                'message': f'Insufficient stock. Only {product.stock_quantity} available.'
            }
        
        cart, created = Cart.objects.get_or_create(user=user)
        cart_item = cart.add_item(product, quantity)
        
        return {
            'success': True,
            'message': 'Product added to cart',
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
            'message': str(e)
        }


def remove_from_cart(user, product_id):
    """
    Remove a product from a user's cart
    """
    try:
        product = Product.objects.get(id=product_id)
        cart = Cart.objects.get(user=user)
        
        if cart.remove_item(product):
            return {
                'success': True,
                'message': 'Product removed from cart'
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
    except Cart.DoesNotExist:
        return {
            'success': False,
            'message': 'Cart not found'
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }


def update_cart_item(user, product_id, quantity):
    """
    Update the quantity of a product in a user's cart
    """
    try:
        product = Product.objects.get(id=product_id)
        
        # Check product stock
        if product.stock_quantity < quantity:
            return {
                'success': False,
                'message': f'Insufficient stock. Only {product.stock_quantity} available.'
            }
        
        cart = Cart.objects.get(user=user)
        cart_item = cart.update_item_quantity(product, quantity)
        
        if cart_item:
            return {
                'success': True,
                'message': 'Cart item updated'
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
    except Cart.DoesNotExist:
        return {
            'success': False,
            'message': 'Cart not found'
        }
    except Exception as e:
        return {
            'success': False,
            'message': str(e)
        }


def get_cart_items(user):
    """
    Get all items in a user's cart
    """
    try:
        cart = Cart.objects.get(user=user)
        return cart.items.all().select_related('product')
    except Cart.DoesNotExist:
        return []


def clear_cart(user):
    """
    Clear all items from a user's cart
    """
    try:
        cart = Cart.objects.get(user=user)
        cart.clear()
        
        return {
            'success': True,
            'message': 'Cart cleared'
        }
    except Cart.DoesNotExist:
        return {
            'success': False,
            'message': 'Cart not found'
        }


def get_cart_summary(user):
    """
    Get a summary of the user's cart
    """
    try:
        cart = Cart.objects.get(user=user)
        return {
            'items_count': cart.items_count,
            'total_quantity': cart.total_quantity,
            'subtotal': cart.subtotal
        }
    except Cart.DoesNotExist:
        return {
            'items_count': 0,
            'total_quantity': 0,
            'subtotal': 0
        }


def is_product_in_cart(user, product_id):
    """
    Check if a product is in a user's cart
    """
    try:
        cart = Cart.objects.get(user=user)
        return CartItem.objects.filter(
            cart=cart,
            product_id=product_id
        ).exists()
    except Cart.DoesNotExist:
        return False