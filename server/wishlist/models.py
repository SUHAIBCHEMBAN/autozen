from django.db import models
from django.conf import settings
from products.models import Product


class Wishlist(models.Model):
    """
    Represents a user's wishlist
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'wishlists'
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user}'s Wishlist"
    
    @property
    def items_count(self):
        """Return the number of items in the wishlist"""
        return self.items.count()


class WishlistItem(models.Model):
    """
    Represents an item in a user's wishlist
    """
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'wishlist_items'
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        unique_together = ['wishlist', 'product']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.product.name} in {self.wishlist.user}'s Wishlist"