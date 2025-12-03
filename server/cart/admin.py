from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Inline for cart items"""
    model = CartItem
    extra = 0
    readonly_fields = ['price', 'total_price', 'added_at', 'updated_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin for carts"""
    list_display = ['user', 'items_count', 'total_quantity', 'subtotal', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'user__phone_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    # Inlines
    inlines = [CartItemInline]
    
    def items_count(self, obj):
        return obj.items_count
    items_count.short_description = 'Items Count'
    
    def total_quantity(self, obj):
        return obj.total_quantity
    total_quantity.short_description = 'Total Quantity'
    
    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = 'Subtotal'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin for cart items"""
    list_display = ['cart', 'product', 'quantity', 'price', 'total_price', 'added_at']
    list_filter = ['added_at', 'updated_at']
    search_fields = [
        'cart__user__email', 
        'cart__user__phone_number',
        'product__name',
        'product__sku'
    ]
    readonly_fields = ['price', 'total_price', 'added_at', 'updated_at']
    ordering = ['-added_at']