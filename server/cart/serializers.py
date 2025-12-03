from rest_framework import serializers
from products.serializers import ProductListSerializer
from products.models import Product
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items"""
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
    """Serializer for carts"""
    items = CartItemSerializer(many=True, read_only=True)
    items_count = serializers.IntegerField(read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'items_count', 'total_quantity', 'subtotal', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class CartItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating cart items"""
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True
    )
    quantity = serializers.IntegerField(min_value=1, default=1)
    
    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']


class CartItemUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating cart item quantity"""
    quantity = serializers.IntegerField(min_value=1)
    
    class Meta:
        model = CartItem
        fields = ['quantity']