from rest_framework import serializers
from products.serializers import ProductListSerializer
from products.models import Product
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for cart items.
    
    Serializes cart item data including the associated product information.
    The product field uses ProductListSerializer to provide detailed
    product information, while product_id is write-only for creating items.
    """
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source='product', 
        queryset=Product.objects.all(),
        write_only=True
    )
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price', 'total_price', 'added_at', 'updated_at']
        read_only_fields = ['price', 'total_price', 'added_at', 'updated_at']


class CartSerializer(serializers.ModelSerializer):
    """
    Serializer for carts.
    
    Serializes cart data including all items and computed properties.
    Optimizes database queries by prefetching related objects when
    serializing cart data.
    """
    items = CartItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'items_count', 'total_quantity', 'subtotal', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """
        Override to prefetch related objects to reduce database queries.
        
        When serializing cart data, this method ensures that related
        objects (cart items and their products) are prefetched to
        minimize database queries during serialization.
        
        Args:
            instance (Cart): The cart instance being serialized
            
        Returns:
            dict: Serialized cart data
        """
        # Prefetch related objects if they're not already prefetched
        if hasattr(instance, '_prefetched_objects_cache'):
            # Already prefetched, use as is
            pass
        else:
            # Prefetch related objects to reduce queries
            from django.db import models
            if not isinstance(instance.items, models.Prefetch):
                # Re-fetch with prefetch_related if not already done
                instance = instance.__class__.objects.prefetch_related(
                    'items__product__brand',
                    'items__product__vehicle_model',
                    'items__product__part_category'
                ).get(pk=instance.pk)
        
        return super().to_representation(instance)


class CartItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating cart items.
    
    Used specifically for adding new items to a cart. Requires
    product_id and accepts optional quantity (defaults to 1).
    """
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True
    )
    quantity = serializers.IntegerField(min_value=1, default=1)
    
    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']


class CartItemUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating cart item quantity.
    
    Used specifically for updating the quantity of existing
    cart items. Requires quantity value.
    """
    quantity = serializers.IntegerField(min_value=1)
    
    class Meta:
        model = CartItem
        fields = ['quantity']