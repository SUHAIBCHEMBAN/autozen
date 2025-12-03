from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, OrderStatusLog, OrderNotification


class OrderItemInline(admin.TabularInline):
    """Inline for order items"""
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_sku', 'product_price', 'total_price']


class OrderStatusLogInline(admin.TabularInline):
    """Inline for order status logs"""
    model = OrderStatusLog
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'timestamp', 'notes']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for orders"""
    list_display = [
        'id', 'order_number', 'full_name', 'status', 'payment_status', 
        'total_amount', 'created_at'
    ]
    list_filter = [
        'status', 'payment_method', 'payment_status', 
        'created_at', 'updated_at'
    ]
    search_fields = [
        'order_number', 'first_name', 'last_name', 
        'email', 'phone_number'
    ]
    readonly_fields = [
        'order_number', 'created_at', 'updated_at', 
        'shipped_at', 'delivered_at'
    ]
    ordering = ['-created_at']
    
    # Inlines
    inlines = [OrderItemInline, OrderStatusLogInline]
    
    # Fieldsets for organized display
    fieldsets = (
        ('Order Information', {
            'fields': (
                'order_number', 'user', 'status', 
                'payment_method', 'payment_status'
            )
        }),
        ('Customer Information', {
            'fields': (
                'first_name', 'last_name', 'email', 'phone_number'
            )
        }),
        ('Billing Address', {
            'fields': (
                'billing_address_line1', 'billing_address_line2',
                'billing_city', 'billing_state', 
                'billing_postal_code', 'billing_country'
            )
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_address_line1', 'shipping_address_line2',
                'shipping_city', 'shipping_state', 
                'shipping_postal_code', 'shipping_country'
            )
        }),
        ('Pricing', {
            'fields': (
                'subtotal', 'tax_amount', 'shipping_cost', 
                'discount_amount', 'total_amount'
            )
        }),
        ('Notes', {
            'fields': ('notes', 'internal_notes'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at', 
                'shipped_at', 'delivered_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return obj.full_name
    full_name.short_description = 'Customer Name'
    
    def payment_status_display(self, obj):
        if obj.payment_status:
            return format_html('<span style="color: green;">Paid</span>')
        return format_html('<span style="color: orange;">Pending</span>')
    payment_status_display.short_description = 'Payment Status'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin for order items"""
    list_display = [
        'id', 'order', 'product_name', 'quantity', 'product_price', 'total_price'
    ]
    list_filter = ['order__status', 'order__created_at']
    search_fields = [
        'product_name', 'product_sku', 'order__order_number'
    ]
    readonly_fields = [
        'product_name', 'product_sku', 'product_price', 'total_price'
    ]


@admin.register(OrderStatusLog)
class OrderStatusLogAdmin(admin.ModelAdmin):
    """Admin for order status logs"""
    list_display = [
        'id','order', 'old_status', 'new_status', 'timestamp'
    ]
    list_filter = ['old_status', 'new_status', 'timestamp']
    search_fields = ['order__order_number']
    readonly_fields = ['old_status', 'new_status', 'timestamp']


@admin.register(OrderNotification)
class OrderNotificationAdmin(admin.ModelAdmin):
    """Admin for order notifications"""
    list_display = [
        'id','order', 'notification_type', 'sent_at', 'sent_to'
    ]
    list_filter = ['notification_type', 'sent_at']
    search_fields = ['order__order_number', 'sent_to', 'subject']
    readonly_fields = ['order', 'notification_type', 'sent_at', 'sent_to', 'subject', 'message']