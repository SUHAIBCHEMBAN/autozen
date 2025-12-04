"""
Utility functions for the order app
"""

from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache


def get_order_cache_key(order_id):
    """
    Generate cache key for order data.
    
    Creates a unique cache key for storing/retrieving order data.
    
    Args:
        order_id (int): The ID of the order
        
    Returns:
        str: Cache key for the order data
    """
    return f"order_{order_id}"


def get_user_orders_cache_key(user_id):
    """
    Generate cache key for user's orders list.
    
    Creates a unique cache key for storing/retrieving a user's orders list.
    
    Args:
        user_id (int): The ID of the user
        
    Returns:
        str: Cache key for the user's orders list
    """
    return f"user_orders_{user_id}"


def get_order_items_cache_key(order_id):
    """
    Generate cache key for order items.
    
    Creates a unique cache key for storing/retrieving order items.
    
    Args:
        order_id (int): The ID of the order
        
    Returns:
        str: Cache key for the order items
    """
    return f"order_items_{order_id}"


def invalidate_order_cache(order_id):
    """
    Invalidate all cache entries for an order.
    
    Deletes cached values for order data and items to ensure data consistency
    when order data changes.
    
    Args:
        order_id (int): The ID of the order to invalidate cache for
    """
    cache_keys = [
        get_order_cache_key(order_id),
        get_order_items_cache_key(order_id),
    ]
    cache.delete_many(cache_keys)


def invalidate_user_orders_cache(user_id):
    """
    Invalidate cache entries for a user's orders.
    
    Deletes cached values for a user's orders list to ensure data consistency
    when orders are added or modified.
    
    Args:
        user_id (int): The ID of the user to invalidate orders cache for
    """
    cache_key = get_user_orders_cache_key(user_id)
    cache.delete(cache_key)


def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer
    """
    # Import here to avoid circular imports
    from .models import OrderNotification, OrderStatus
    
    subject = f"Order Confirmation - {order.order_number}"
    message = f"""
    Dear {order.full_name},
    
    Thank you for your order! Here are the details:
    
    Order Number: {order.order_number}
    Order Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}
    Total Amount: ${order.total_amount}
    
    Items:
    """
    
    for item in order.items.all():
        message += f"- {item.product_name} x {item.quantity} = ${item.total_price}\n"
    
    message += f"""
    
    Shipping Address:
    {order.shipping_address}
    
    Billing Address:
    {order.billing_address}
    
    Payment Method: {order.get_payment_method_display()}
    
    You will receive another email when your order is shipped.
    
    Thank you for shopping with us!
    
    Best regards,
    {settings.SITE_NAME} Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=False,
        )
        # Log the notification
        OrderNotification.objects.create(
            order=order,
            notification_type='order_confirmation',
            sent_to=order.email,
            subject=subject,
            message=message
        )
        return True
    except Exception as e:
        print(f"Failed to send order confirmation email: {e}")
        return False


def send_shipping_notification(order):
    """
    Send shipping notification email to customer
    """
    # Import here to avoid circular imports
    from .models import OrderNotification, OrderStatus
    
    if order.status != OrderStatus.SHIPPED:
        return False
        
    subject = f"Your Order Has Been Shipped - {order.order_number}"
    message = f"""
    Dear {order.full_name},
    
    Great news! Your order has been shipped.
    
    Order Number: {order.order_number}
    Tracking Number: {order.tracking_number if hasattr(order, 'tracking_number') else 'Not available yet'}
    
    You will receive another email when your order is delivered.
    
    Thank you for shopping with us!
    
    Best regards,
    {settings.SITE_NAME} Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=False,
        )
        # Log the notification
        OrderNotification.objects.create(
            order=order,
            notification_type='shipment_notification',
            sent_to=order.email,
            subject=subject,
            message=message
        )
        return True
    except Exception as e:
        print(f"Failed to send shipping notification email: {e}")
        return False


def send_delivery_notification(order):
    """
    Send delivery notification email to customer
    """
    # Import here to avoid circular imports
    from .models import OrderNotification, OrderStatus
    
    if order.status != OrderStatus.DELIVERED:
        return False
        
    subject = f"Your Order Has Been Delivered - {order.order_number}"
    message = f"""
    Dear {order.full_name},
    
    Your order has been delivered successfully!
    
    Order Number: {order.order_number}
    
    We hope you're satisfied with your purchase. If you have any questions or concerns,
    please don't hesitate to contact us.
    
    Thank you for shopping with us!
    
    Best regards,
    {settings.SITE_NAME} Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.email],
            fail_silently=False,
        )
        # Log the notification
        OrderNotification.objects.create(
            order=order,
            notification_type='delivery_notification',
            sent_to=order.email,
            subject=subject,
            message=message
        )
        return True
    except Exception as e:
        print(f"Failed to send delivery notification email: {e}")
        return False


def calculate_order_totals(order_items):
    """
    Calculate order totals from items
    """
    subtotal = sum(item['product_price'] * item['quantity'] for item in order_items)
    return {
        'subtotal': subtotal,
        'tax_amount': subtotal * 0.08,  # 8% tax
        'shipping_cost': 10.00,  # Fixed shipping
        'discount_amount': 0,
        'total_amount': subtotal * 1.08 + 10.00  # Subtotal + tax + shipping
    }


def validate_stock_availability(items):
    """
    Validate that all items have sufficient stock
    """
    from products.models import Product
    
    for item in items:
        try:
            product = Product.objects.get(id=item['product_id'])
            if product.stock_quantity < item['quantity']:
                return {
                    'valid': False,
                    'error': f'Insufficient stock for {product.name}. Available: {product.stock_quantity}, Requested: {item["quantity"]}'
                }
        except Product.DoesNotExist:
            return {
                'valid': False,
                'error': f'Product with ID {item["product_id"]} not found'
            }
    
    return {'valid': True}


def update_product_stock(order, decrease=True):
    """
    Update product stock quantities based on order items
    """
    for item in order.items.all():
        if decrease:
            item.product.stock_quantity -= item.quantity
        else:
            item.product.stock_quantity += item.quantity
        item.product.save()