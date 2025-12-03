"""
Utility functions for the order app
"""

from django.core.mail import send_mail
from django.conf import settings
from .models import Order, OrderStatus


def send_order_confirmation_email(order):
    """
    Send order confirmation email to customer
    """
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