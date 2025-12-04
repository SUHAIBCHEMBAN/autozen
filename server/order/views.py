from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from django.core.cache import cache
from .models import Order, OrderItem, OrderStatus
from .serializers import (
    OrderSerializer, OrderCreateSerializer, 
    OrderUpdateSerializer, CheckoutSerializer
)
from products.models import Product
from .utils import (
    get_order_cache_key, get_user_orders_cache_key, 
    get_order_items_cache_key, send_order_confirmation_email
)


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Custom permission to only allow owners of an order or staff to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Staff have all permissions
        if request.user.is_staff:
            return True
        # Owners can view and cancel their own orders
        return obj.user == request.user

    def has_permission(self, request, view):
        # For list and create views, authenticated users can access
        if view.action == 'list' or view.action == 'history':
            return request.user.is_authenticated
        # For create, user must be authenticated
        if view.action == 'create':
            return request.user.is_authenticated
        # For other actions, defer to has_object_permission
        return True


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Order operations with Redis caching optimization.
    
    Implements caching for improved performance:
    - Orders list is cached per user
    - Individual orders are cached by ID
    - Order items are cached separately for efficient retrieval
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsOwnerOrStaff]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['status', 'payment_method', 'payment_status']
    search_fields = ['order_number', 'first_name', 'last_name', 'email', 'phone_number']
    ordering_fields = ['created_at', 'total_amount', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        This view should return a list of all orders
        for the currently authenticated user, or all orders for staff.
        """
        # Check if user is authenticated
        if not self.request.user.is_authenticated:
            return Order.objects.none()
            
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)
    
    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        This ensures the request is passed to the serializer context.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for serializing
        the input, and deserializing the output.
        This ensures the request context is passed to the serializer.
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrderUpdateSerializer
        return OrderSerializer
    
    def perform_create(self, serializer):
        """Set the user to the current user when creating an order"""
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of orders for the current user with caching.
        
        For authenticated users, retrieves orders from cache if available,
        otherwise fetches from database and caches the result.
        
        Returns:
            Response: Serialized orders data with HTTP 200 status
        """
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response([])
            
        # Try to get from cache first
        cache_key = get_user_orders_cache_key(request.user.id)
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
            
        # Get orders from database
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        # Cache the serialized data for 15 minutes
        cache.set(cache_key, serializer.data, 60 * 15)
        
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific order with caching.
        
        Gets order data from cache if available, otherwise fetches from
        database and caches the result.
        
        Returns:
            Response: Serialized order data with HTTP 200 status
        """
        # Try to get from cache first
        order_id = kwargs.get('pk')
        cache_key = get_order_cache_key(order_id)
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
            
        # Get order from database
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Cache the serialized data for 15 minutes
        cache.set(cache_key, serializer.data, 60 * 15)
        
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order if possible"""
        order = self.get_object()
        if not order.can_be_cancelled():
            return Response(
                {'error': 'Order cannot be cancelled in its current status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.update_status(OrderStatus.CANCELLED)
        return Response({'message': 'Order cancelled successfully'})
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update order status (staff only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can update order status'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        order = self.get_object()
        new_status = request.data.get('status')
        
        if not new_status:
            return Response(
                {'error': 'Status is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_status not in dict(OrderStatus.choices):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.update_status(new_status)
        return Response({'message': f'Order status updated to {new_status}'})
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get order history for the current user with caching"""
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response({'orders': []})
            
        # Try to get from cache first
        cache_key = get_user_orders_cache_key(request.user.id)
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
            
        if request.user.is_staff:
            orders = Order.objects.all()
        else:
            orders = Order.objects.filter(user=request.user)
        
        serializer = self.get_serializer(orders, many=True)
        
        # Cache the serialized data for 15 minutes
        cache.set(cache_key, serializer.data, 60 * 15)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[])
    def checkout(self, request):
        """Process checkout and create order"""
        serializer = CheckoutSerializer(data=request.data)
        if serializer.is_valid():
            # Process checkout logic here
            checkout_data = serializer.validated_data
            
            # Calculate totals
            subtotal = 0
            items_data = []
            
            # Validate items and calculate subtotal
            for item in checkout_data['items']:
                try:
                    product = Product.objects.get(id=item['product_id'])
                    quantity = int(item['quantity'])
                    
                    if product.stock_quantity < quantity:
                        return Response(
                            {'error': f'Insufficient stock for {product.name}'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    item_total = product.price * quantity
                    subtotal += item_total
                    
                    items_data.append({
                        'product': product.id,
                        'product_name': product.name,
                        'product_sku': product.sku,
                        'product_price': product.price,
                        'quantity': quantity,
                        'total_price': item_total
                    })
                except Product.DoesNotExist:
                    return Response(
                        {'error': f'Product with ID {item["product_id"]} not found'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except (ValueError, KeyError) as e:
                    return Response(
                        {'error': 'Invalid item data'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Calculate tax and total (simplified)
            tax_rate = 0.08  # 8% tax
            tax_amount = subtotal * tax_rate
            shipping_cost = 10.00  # Fixed shipping cost
            total_amount = subtotal + tax_amount + shipping_cost
            
            # Create order
            order_data = {
                'first_name': checkout_data['first_name'],
                'last_name': checkout_data['last_name'],
                'email': checkout_data['email'],
                'phone_number': checkout_data['phone_number'],
                'billing_address_line1': checkout_data['billing_address_line1'],
                'billing_address_line2': checkout_data.get('billing_address_line2', ''),
                'billing_city': checkout_data['billing_city'],
                'billing_state': checkout_data['billing_state'],
                'billing_postal_code': checkout_data['billing_postal_code'],
                'billing_country': checkout_data['billing_country'],
                'shipping_address_line1': checkout_data['shipping_address_line1'],
                'shipping_address_line2': checkout_data.get('shipping_address_line2', ''),
                'shipping_city': checkout_data['shipping_city'],
                'shipping_state': checkout_data['shipping_state'],
                'shipping_postal_code': checkout_data['shipping_postal_code'],
                'shipping_country': checkout_data['shipping_country'],
                'payment_method': checkout_data['payment_method'],
                'subtotal': subtotal,
                'tax_amount': tax_amount,
                'shipping_cost': shipping_cost,
                'discount_amount': 0,
                'total_amount': total_amount,
                'notes': checkout_data.get('notes', ''),
            }
            
            # Create order serializer
            order_serializer = OrderCreateSerializer(data=order_data, context=self.get_serializer_context())
            if order_serializer.is_valid():
                order = order_serializer.save(user=request.user if request.user.is_authenticated else None)
                
                # Create order items
                for item_data in items_data:
                    item_data.pop('product_name')
                    item_data.pop('product_sku')
                    item_data.pop('product_price')
                    item_data.pop('total_price')
                    item_data['order'] = order.id
                    OrderItem.objects.create(order=order, **item_data)
                
                # Update product stock
                for item in items_data:
                    product = Product.objects.get(id=item['product'])
                    product.stock_quantity -= item['quantity']
                    product.save()
                
                # Send order confirmation email
                send_order_confirmation_email(order)
                
                # Invalidate user orders cache
                if request.user.is_authenticated:
                    cache.delete(get_user_orders_cache_key(request.user.id))
                
                return Response({
                    'message': 'Order created successfully',
                    'order_number': order.order_number,
                    'total_amount': str(total_amount)
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)