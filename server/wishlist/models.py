from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
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
        # Import here to avoid circular imports
        from .cache_utils import get_cached_wishlist_count
        return get_cached_wishlist_count(self.user_id)


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


# Signal handlers for cache invalidation
@receiver(post_save, sender=Wishlist)
def invalidate_wishlist_cache_on_save(sender, instance, **kwargs):
    """Invalidate wishlist cache when wishlist is saved"""
    from .cache_utils import invalidate_wishlist_cache
    invalidate_wishlist_cache(instance.user_id)


@receiver(post_delete, sender=Wishlist)
def invalidate_wishlist_cache_on_delete(sender, instance, **kwargs):
    """Invalidate wishlist cache when wishlist is deleted"""
    from .cache_utils import invalidate_wishlist_cache
    invalidate_wishlist_cache(instance.user_id)


@receiver(post_save, sender=WishlistItem)
def invalidate_wishlist_items_cache_on_save(sender, instance, **kwargs):
    """Invalidate wishlist items cache when wishlist item is saved"""
    from .cache_utils import invalidate_wishlist_cache
    invalidate_wishlist_cache(instance.wishlist.user_id)


@receiver(post_delete, sender=WishlistItem)
def invalidate_wishlist_items_cache_on_delete(sender, instance, **kwargs):
    """Invalidate wishlist items cache when wishlist item is deleted"""
    from .cache_utils import invalidate_wishlist_cache
    invalidate_wishlist_cache(instance.wishlist.user_id)