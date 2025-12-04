from rest_framework import serializers
from django.core.cache import cache
from .models import Order, OrderItem, OrderStatusLog, OrderStatus, PaymentMethod
from .utils import get_order_items_cache_key


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items with caching optimization"""
    product_url = serializers.HyperlinkedRelatedField(
        view_name='products:product-detail',
        read_only=True,
        source='product',
        lookup_field='slug'
    )
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'product_price',
            'quantity', 'total_price', 'product_url'
        ]
        read_only_fields = ['product_name', 'product_sku', 'product_price', 'total_price']


class OrderStatusLogSerializer(serializers.ModelSerializer):
    """Serializer for order status logs"""
    class Meta:
        model = OrderStatusLog
        fields = ['id', 'old_status', 'new_status', 'timestamp', 'notes']
        read_only_fields = ['old_status', 'new_status', 'timestamp']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders with caching optimization"""
    items = serializers.SerializerMethodField()
    status_logs = OrderStatusLogSerializer(many=True, read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    can_be_cancelled = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_email',
            'first_name', 'last_name', 'email', 'phone_number',
            'billing_address_line1', 'billing_address_line2',
            'billing_city', 'billing_state', 'billing_postal_code', 'billing_country',
            'shipping_address_line1', 'shipping_address_line2',
            'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country',
            'status', 'payment_method', 'payment_status',
            'subtotal', 'tax_amount', 'shipping_cost', 'discount_amount', 'total_amount',
            'notes', 'internal_notes',
            'created_at', 'updated_at', 'shipped_at', 'delivered_at',
            'items', 'status_logs', 'can_be_cancelled'
        ]
        read_only_fields = [
            'order_number', 'user', 'user_email', 'created_at', 'updated_at',
            'shipped_at', 'delivered_at', 'can_be_cancelled'
        ]
    
    def get_items(self, obj):
        """
        Get order items with caching.
        
        Retrieves order items from cache if available, otherwise fetches from
        database and caches the result.
        
        Args:
            obj (Order): The order object
            
        Returns:
            list: Serialized order items data
        """
        # Try to get from cache first
        cache_key = get_order_items_cache_key(obj.id)
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return cached_data
            
        # Get items from database
        items = obj.items.all()
        # Pass context to ensure hyperlinked fields work correctly
        serializer = OrderItemSerializer(items, many=True, context=self.context)
        
        # Cache the serialized data for 15 minutes
        cache.set(cache_key, serializer.data, 60 * 15)
        
        return serializer.data


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders"""
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'billing_address_line1', 'billing_address_line2',
            'billing_city', 'billing_state', 'billing_postal_code', 'billing_country',
            'shipping_address_line1', 'shipping_address_line2',
            'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country',
            'payment_method', 'subtotal', 'tax_amount', 'shipping_cost', 
            'discount_amount', 'total_amount', 'notes', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
            
        return order


class OrderUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating orders (staff only)"""
    class Meta:
        model = Order
        fields = [
            'status', 'payment_status', 'internal_notes',
            'shipped_at', 'delivered_at'
        ]


class CheckoutSerializer(serializers.Serializer):
    """Serializer for checkout data"""
    # Customer information
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=15)
    
    # Billing address
    billing_address_line1 = serializers.CharField(max_length=255)
    billing_address_line2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    billing_city = serializers.CharField(max_length=100)
    billing_state = serializers.CharField(max_length=100)
    billing_postal_code = serializers.CharField(max_length=20)
    billing_country = serializers.CharField(max_length=100)
    
    # Shipping address
    shipping_address_line1 = serializers.CharField(max_length=255)
    shipping_address_line2 = serializers.CharField(max_length=255, required=False, allow_blank=True)
    shipping_city = serializers.CharField(max_length=100)
    shipping_state = serializers.CharField(max_length=100)
    shipping_postal_code = serializers.CharField(max_length=20)
    shipping_country = serializers.CharField(max_length=100)
    
    # Payment
    payment_method = serializers.ChoiceField(choices=PaymentMethod.choices)
    
    # Cart items (list of product IDs and quantities)
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        )
    )
    
    # Notes
    notes = serializers.CharField(required=False, allow_blank=True)