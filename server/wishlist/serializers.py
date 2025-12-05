from rest_framework import serializers
from products.serializers import ProductListSerializer
from products.models import Product
from .models import Wishlist, WishlistItem
from .cache_utils import get_cached_wishlist_items, get_cached_wishlist_count


class WishlistItemSerializer(serializers.ModelSerializer):
    """Serializer for wishlist items"""
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source='product', 
        queryset=Product.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'product_id', 'added_at']
        read_only_fields = ['added_at']


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlists"""
    items = WishlistItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'items', 'items_count', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        """Get items count from cache"""
        return get_cached_wishlist_count(obj.user_id)
    
    def to_representation(self, instance):
        """Override to use cached items when available"""
        representation = super().to_representation(instance)
        
        # Use cached items if available
        cached_items = get_cached_wishlist_items(instance.user_id)
        if cached_items:
            # Serialize cached items with context to support HyperlinkedIdentityField
            items_serializer = WishlistItemSerializer(cached_items, many=True, context=self.context)
            representation['items'] = items_serializer.data
        
        return representation


class WishlistCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating wishlist items"""
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = WishlistItem
        fields = ['product_id']