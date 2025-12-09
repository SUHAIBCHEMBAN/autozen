from rest_framework import viewsets, status, permissions
from decimal import Decimal, ROUND_HALF_UP
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
from cart.models import Cart, CartItem
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
    lookup_field = 'order_number'
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
        lookup_value = kwargs.get(self.lookup_field)
        cache_key = f"order_{lookup_value}"
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
    
    @action(detail=True, methods=['get'], permission_classes=[], authentication_classes=[])
    def invoice(self, request, pk=None, **kwargs):
        """Generate invoice view (HTML)"""
        from django.http import HttpResponse
        from django.shortcuts import get_object_or_404
        
        # Get the order number from the URL kwargs
        order_number = self.kwargs.get('order_number') or pk
        
        # Get the order object using the order number
        order = get_object_or_404(Order, order_number=order_number)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Invoice - {order.order_number}</title>
            <meta charset="utf-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
                
                :root {{
                    --primary: #ef4444; /* AutoZen Red */
                    --secondary: #0f172a; /* Dark Slate */
                    --text: #334155;
                    --light: #f8fafc;
                    --border: #e2e8f0;
                }}
                
                body {{ 
                    font-family: 'Inter', system-ui, -apple-system, sans-serif;
                    color: var(--text);
                    line-height: 1.5;
                    margin: 0;
                    padding: 0;
                    background: #fff;
                    font-size: 14px;
                }}
                
                .invoice-container {{
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 40px;
                    background: white;
                }}
                
                /* Header */
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 40px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid var(--primary);
                }}
                
                .brand-section h1 {{
                    color: var(--primary);
                    margin: 0;
                    font-size: 32px;
                    font-weight: 800;
                    letter-spacing: -1px;
                }}
                
                .brand-section p {{
                    margin: 4px 0 0;
                    color: #64748b;
                    font-size: 13px;
                }}
                
                .invoice-info {{
                    text-align: right;
                }}
                
                .invoice-label {{
                    font-size: 12px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    color: #64748b;
                    font-weight: 600;
                }}
                
                .invoice-number {{
                    font-size: 18px;
                    font-weight: 700;
                    color: var(--secondary);
                    margin: 4px 0 12px;
                }}
                
                .status-badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    background: var(--light);
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    color: var(--secondary);
                    border: 1px solid var(--border);
                    text-transform: uppercase;
                }}
                
                /* Address Grid */
                .address-section {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 40px;
                    margin-bottom: 40px;
                }}
                
                .address-box h3 {{
                    font-size: 11px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    color: #64748b;
                    margin: 0 0 12px;
                    border-bottom: 1px solid var(--border);
                    padding-bottom: 8px;
                }}
                
                .recipient-name {{
                    font-weight: 700;
                    font-size: 15px;
                    color: var(--secondary);
                    margin-bottom: 4px;
                }}
                
                .address-lines {{
                    color: var(--text);
                }}
                
                /* Dates Grid */
                .dates-grid {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 20px;
                    margin-bottom: 40px;
                    background: var(--light);
                    padding: 20px;
                    border-radius: 8px;
                }}
                
                .date-box label {{
                    display: block;
                    font-size: 11px;
                    color: #64748b;
                    margin-bottom: 4px;
                    text-transform: uppercase;
                    font-weight: 600;
                }}
                
                .date-box div {{
                    font-weight: 600;
                    color: var(--secondary);
                }}
                
                /* Table */
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 40px;
                }}
                
                th {{
                    text-align: left;
                    padding: 16px;
                    background: var(--secondary);
                    color: white;
                    font-weight: 600;
                    font-size: 12px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                
                th:first-child {{ border-top-left-radius: 6px; }}
                th:last-child {{ border-top-right-radius: 6px; }}
                
                td {{
                    padding: 16px;
                    border-bottom: 1px solid var(--border);
                    vertical-align: top;
                }}
                
                tr:last-child td {{
                    border-bottom: none;
                }}
                
                .item-name {{
                    font-weight: 600;
                    color: var(--secondary);
                    display: block;
                    margin-bottom: 2px;
                }}
                
                .item-sku {{
                    font-size: 11px;
                    color: #94a3b8;
                    font-family: monospace;
                }}
                
                .text-right {{ text-align: right; }}
                .text-center {{ text-align: center; }}
                
                /* Summary */
                .summary-section {{
                    display: flex;
                    justify-content: flex-end;
                }}
                
                .summary-table {{
                    width: 300px;
                }}
                
                .summary-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    color: #64748b;
                }}
                
                .summary-row.total {{
                    border-top: 2px solid var(--secondary);
                    margin-top: 12px;
                    padding-top: 12px;
                    font-weight: 700;
                    color: var(--secondary);
                    font-size: 18px;
                }}
                
                /* Footer */
                .footer {{
                    margin-top: 60px;
                    padding-top: 30px;
                    border-top: 1px solid var(--border);
                    text-align: center;
                    color: #94a3b8;
                    font-size: 12px;
                }}
                
                /* Print Button */
                .print-button {{
                    display: block;
                    margin: 20px auto;
                    padding: 10px 20px;
                    background-color: var(--primary);
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 16px;
                    cursor: pointer;
                }}
                
                .print-button:hover {{
                    background-color: #dc2626;
                }}
                
                @media print {{
                    body {{ background: white; -webkit-print-color-adjust: exact; }}
                    .invoice-container {{ width: 100%; max-width: none; padding: 0; }}
                    .print-button {{ display: none; }}
                }}
            </style>
        </head>
        <body>
            <div class="invoice-container">
                <button class="print-button" onclick="window.print()">Print Invoice</button>
                
                <div class="header">
                    <div class="brand-section">
                        <h1>AutoZen .</h1>
                        <p>Premium Automotive Parts</p>
                    </div>
                    <div class="invoice-info">
                        <div class="invoice-label">Invoice Number</div>
                        <div class="invoice-number">{order.order_number}</div>
                        <span class="status-badge">{order.status.replace('_', ' ')}</span>
                    </div>
                </div>
                
                <div class="address-section">
                    <div class="address-box">
                        <h3>Billed To</h3>
                        <div class="recipient-name">{order.first_name} {order.last_name}</div>
                        <div class="address-lines">
                            {order.billing_address_line1}<br>
                            {f"{order.billing_address_line2}<br>" if order.billing_address_line2 else ""}
                            {order.billing_city}, {order.billing_state} {order.billing_postal_code}<br>
                            {order.billing_country}<br>
                            {order.email}
                        </div>
                    </div>
                    <div class="address-box">
                        <h3>Shipped To</h3>
                        <div class="recipient-name">{order.first_name} {order.last_name}</div>
                        <div class="address-lines">
                            {order.shipping_address_line1}<br>
                            {f"{order.shipping_address_line2}<br>" if order.shipping_address_line2 else ""}
                            {order.shipping_city}, {order.shipping_state} {order.shipping_postal_code}<br>
                            {order.shipping_country}
                        </div>
                    </div>
                </div>
                
                <div class="dates-grid">
                    <div class="date-box">
                        <label>Order Date</label>
                        <div>{order.created_at.strftime('%b %d, %Y')}</div>
                    </div>
                    <div class="date-box">
                        <label>Payment Method</label>
                        <div>{order.payment_method.replace('_', ' ').title()}</div>
                    </div>
                    <div class="date-box">
                        <label>Payment Status</label>
                        <div>{'Paid' if order.payment_status else 'Pending'}</div>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th style="width: 50%">Item Details</th>
                            <th class="text-center">Qty</th>
                            <th class="text-right">Price</th>
                            <th class="text-right">Total</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for item in order.items.all():
            html_content += f"""
                        <tr>
                            <td>
                                <span class="item-name">{item.product_name}</span>
                                <span class="item-sku">SKU: {item.product_sku}</span>
                            </td>
                            <td class="text-center">{item.quantity}</td>
                            <td class="text-right">₹{item.product_price}</td>
                            <td class="text-right">₹{item.total_price}</td>
                        </tr>
            """
            
        html_content += f"""
                    </tbody>
                </table>
                
                <div class="summary-section">
                    <div class="summary-table">
                        <div class="summary-row">
                            <span>Subtotal</span>
                            <span>₹{order.subtotal}</span>
                        </div>
                        <div class="summary-row">
                            <span>Shipping</span>
                            <span>₹{order.shipping_cost}</span>
                        </div>
                        <div class="summary-row">
                            <span>Tax (8%)</span>
                            <span>₹{order.tax_amount}</span>
                        </div>
                        <div class="summary-row total">
                            <span>Total Due</span>
                            <span>₹{order.total_amount}</span>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Thank you for choosing AutoZen! We appreciate your business.</p>
                    <p>For support, please contact help@autozen.com or visit www.autozen.com</p>
                    <p style="margin-top: 20px; font-size: 11px;">AutoZen Inc • 1234 Car Part Lane, Automall City, AC 56789</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(html_content, content_type='text/html')

    @action(detail=False, methods=['post'], permission_classes=[])
    def track(self, request):
        """
        Track an order by order number (public access).
        Requires order_number and matches optional email for verification if provided.
        """
        order_number = request.data.get('order_number')
        email = request.data.get('email')
        
        if not order_number:
            return Response(
                {'error': 'Order number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Case-insensitive lookup for order number
            order = Order.objects.get(order_number__iexact=order_number)
            
            # If email is provided, verify it matches
            if email and order.email.lower() != email.lower():
                return Response(
                    {'error': 'Order found but email does not match'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            serializer = self.get_serializer(order)
            return Response(serializer.data)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'], permission_classes=[])
    def checkout(self, request):
        """Process checkout and create order"""
        serializer = CheckoutSerializer(data=request.data)
        if serializer.is_valid():
            # Process checkout logic here
            checkout_data = serializer.validated_data
            
            # Calculate totals
            subtotal = Decimal('0.00')
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
            tax_rate = Decimal('0.08')  # 8% tax
            tax_amount = (subtotal * tax_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            shipping_cost = Decimal('10.00')  # Fixed shipping cost
            total_amount = (subtotal + tax_amount + shipping_cost).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
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
                'items': items_data
            }
            
            # Create order serializer
            order_serializer = OrderCreateSerializer(data=order_data, context=self.get_serializer_context())
            if order_serializer.is_valid():
                order = order_serializer.save(user=request.user if request.user.is_authenticated else None)
                
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
                    
                    # Remove ordered items from cart
                    try:
                        cart = Cart.objects.get(user=request.user)
                        product_ids = [item['product'] for item in items_data]
                        CartItem.objects.filter(cart=cart, product_id__in=product_ids).delete()
                        # Update cart timestamp and invalidate cache
                        cart.save()
                        cart._invalidate_cache()
                        # Also invalidate view-level caches
                        cache.delete(f"cart_{request.user.id}")
                        cache.delete(f"cart_items_{request.user.id}")
                    except Cart.DoesNotExist:
                        pass
                
                return Response({
                    'message': 'Order created successfully',
                    'order_number': order.order_number,
                    'total_amount': str(total_amount)
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(order_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)