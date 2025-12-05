"""
Signals for the products app
Handles cache invalidation when related objects are updated
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Brand, VehicleModel, PartCategory, Product
from .cache_utils import (
    invalidate_brand_cache, invalidate_model_cache, 
    invalidate_category_cache, invalidate_product_cache
)


@receiver(post_save, sender=Brand)
@receiver(post_delete, sender=Brand)
def invalidate_brand_related_cache(sender, instance, **kwargs):
    """Invalidate cache when brand is saved or deleted"""
    invalidate_brand_cache(instance.id)


@receiver(post_save, sender=VehicleModel)
@receiver(post_delete, sender=VehicleModel)
def invalidate_model_related_cache(sender, instance, **kwargs):
    """Invalidate cache when vehicle model is saved or deleted"""
    invalidate_model_cache(instance.id, instance.brand_id)


@receiver(post_save, sender=PartCategory)
@receiver(post_delete, sender=PartCategory)
def invalidate_category_related_cache(sender, instance, **kwargs):
    """Invalidate cache when part category is saved or deleted"""
    invalidate_category_cache(instance.id, instance.parent_id)


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def invalidate_product_related_cache(sender, instance, **kwargs):
    """Invalidate cache when product is saved or deleted"""
    invalidate_product_cache(instance.id)
