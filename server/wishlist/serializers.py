from rest_framework import serializers
from products.serializers import ProductListSerializer
from products.models import Product
from .models import Wishlist, WishlistItem


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
    items_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'items', 'items_count', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class WishlistCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating wishlist items"""
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True
    )
    
    class Meta:
        model = WishlistItem
        fields = ['product_id']