from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from products.models import Product


class OrderStatus(models.TextChoices):
    """Order status choices"""
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    PROCESSING = 'processing', 'Processing'
    SHIPPED = 'shipped', 'Shipped'
    OUT_FOR_DELIVERY = 'out_for_delivery', 'Out for Delivery'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'
    RETURNED = 'returned', 'Returned'
    REFUNDED = 'refunded', 'Refunded'


class PaymentMethod(models.TextChoices):
    """Payment method choices"""
    CREDIT_CARD = 'credit_card', 'Credit Card'
    DEBIT_CARD = 'debit_card', 'Debit Card'
    PAYPAL = 'paypal', 'PayPal'
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
    CASH_ON_DELIVERY = 'cash_on_delivery', 'Cash on Delivery'
    UPI = 'upi', 'UPI'


class Order(models.Model):
    """
    Represents a customer order
    """
    # Order identification
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    
    # Customer information (copied from user profile for historical record)
    email = models.EmailField()
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    
    # Billing address
    billing_address_line1 = models.CharField(max_length=255)
    billing_address_line2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100)
    billing_postal_code = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=100)
    
    # Shipping address
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    
    # Order details
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    payment_status = models.BooleanField(default=False)  # False = pending, True = paid
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Notes
    notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True, help_text="Internal notes for staff")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        
        # Save first to ensure we have an ID
        super().save(*args, **kwargs)
        
        # Now invalidate cache for this order and user's orders
        if hasattr(self, 'id') and self.id:
            from .utils import invalidate_order_cache
            invalidate_order_cache(self.id)
        if hasattr(self, 'user') and hasattr(self.user, 'id'):
            from .utils import invalidate_user_orders_cache
            invalidate_user_orders_cache(self.user.id)

    def generate_order_number(self):
        """Generate a unique order number"""
        import uuid
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"

    def get_absolute_url(self):
        return reverse('orders:order-detail', kwargs={'order_number': self.order_number})

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def billing_address(self):
        address_parts = [
            self.billing_address_line1,
            self.billing_address_line2,
            f"{self.billing_city}, {self.billing_state} {self.billing_postal_code}",
            self.billing_country
        ]
        return ", ".join([part for part in address_parts if part])

    @property
    def shipping_address(self):
        address_parts = [
            self.shipping_address_line1,
            self.shipping_address_line2,
            f"{self.shipping_city}, {self.shipping_state} {self.shipping_postal_code}",
            self.shipping_country
        ]
        return ", ".join([part for part in address_parts if part])

    def can_be_cancelled(self):
        """Check if order can be cancelled"""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]
    
    def can_be_returned(self):
        """Check if order can be returned"""
        return self.status == OrderStatus.DELIVERED

    def update_status(self, new_status):
        """Update order status with timestamp tracking"""
        old_status = self.status
        self.status = new_status
        
        if new_status == OrderStatus.SHIPPED:
            self.shipped_at = timezone.now()
        elif new_status == OrderStatus.DELIVERED:
            self.delivered_at = timezone.now()
            
        self.save()
        # Create status change log
        OrderStatusLog.objects.create(
            order=self,
            old_status=old_status,
            new_status=new_status
        )
        
        # Invalidate cache for this order and user's orders
        if hasattr(self, 'id') and self.id:
            from .utils import invalidate_order_cache
            invalidate_order_cache(self.id)
        if hasattr(self, 'user') and hasattr(self.user, 'id'):
            from .utils import invalidate_user_orders_cache
            invalidate_user_orders_cache(self.user.id)


class OrderItem(models.Model):
    """
    Represents a single item in an order
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    
    # Product details at time of purchase (in case product changes)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=100)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Quantity and pricing
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only when creating new items
            # Copy product details for historical record
            self.product_name = self.product.name
            self.product_sku = self.product.sku
            self.product_price = self.product.price
            self.total_price = self.product_price * self.quantity
        super().save(*args, **kwargs)


class OrderStatusLog(models.Model):
    """
    Tracks order status changes
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_logs')
    old_status = models.CharField(max_length=20, choices=OrderStatus.choices)
    new_status = models.CharField(max_length=20, choices=OrderStatus.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'order_status_logs'
        verbose_name = 'Order Status Log'
        verbose_name_plural = 'Order Status Logs'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.order.order_number}: {self.old_status} → {self.new_status}"


class OrderNotification(models.Model):
    """
    Tracks notifications sent to customers about their orders
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50)  # e.g., 'order_confirmation', 'shipment_update'
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_to = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()

    class Meta:
        db_table = 'order_notifications'
        verbose_name = 'Order Notification'
        verbose_name_plural = 'Order Notifications'
        ordering = ['-sent_at']

    def __str__(self):
        return f"Notification for {self.order.order_number} - {self.notification_type}"