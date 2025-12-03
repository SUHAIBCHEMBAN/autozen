from django.contrib import admin
from .models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    """Inline for wishlist items"""
    model = WishlistItem
    extra = 0
    readonly_fields = ['added_at']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin for wishlists"""
    list_display = ['user', 'items_count', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'user__phone_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    # Inlines
    inlines = [WishlistItemInline]
    
    def items_count(self, obj):
        return obj.items_count
    items_count.short_description = 'Items Count'


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    """Admin for wishlist items"""
    list_display = ['wishlist', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = [
        'wishlist__user__email', 
        'wishlist__user__phone_number',
        'product__name',
        'product__sku'
    ]
    readonly_fields = ['added_at']
    ordering = ['-added_at']