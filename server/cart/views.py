from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, CartItemCreateSerializer, CartItemUpdateSerializer
from products.models import Product


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a cart to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the cart belongs to the current user
        return obj.user == request.user

    def has_permission(self, request, view):
        # For list and create views, authenticated users can access
        return request.user.is_authenticated


class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Cart operations
    """
    serializer_class = CartSerializer
    permission_classes = [IsOwner]
    
    def get_queryset(self):
        """Return the cart for the current user"""
        if not self.request.user.is_authenticated:
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user).prefetch_related('items__product')
    
    def get_object(self):
        """Get or create the cart for the current user"""
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication required")
        
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    def list(self, request, *args, **kwargs):
        """Get the user's cart"""
        try:
            cart = self.get_object()
            serializer = self.get_serializer(cart)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add an item to the cart"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = CartItemCreateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product_id']
            quantity = serializer.validated_data.get('quantity', 1)
            
            # Check product stock
            if product.stock_quantity < quantity:
                return Response(
                    {'error': f'Insufficient stock. Only {product.stock_quantity} available.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get or create cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            
            # Add item to cart
            cart_item = cart.add_item(product, quantity)
            
            return Response(
                {'message': 'Product added to cart', 'item_id': cart_item.id}, 
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['put'])
    def update_item(self, request):
        """Update the quantity of an item in the cart"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = CartItemUpdateSerializer(data=request.data)
        if serializer.is_valid():
            product_id = request.data.get('product_id')
            quantity = serializer.validated_data['quantity']
            
            if not product_id:
                return Response(
                    {'error': 'product_id is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response(
                    {'error': 'Product not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get cart
            try:
                cart = Cart.objects.get(user=request.user)
            except Cart.DoesNotExist:
                return Response(
                    {'error': 'Cart not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check product stock
            if product.stock_quantity < quantity:
                return Response(
                    {'error': f'Insufficient stock. Only {product.stock_quantity} available.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update item quantity
            cart_item = cart.update_item_quantity(product, quantity)
            if cart_item:
                return Response(
                    {'message': 'Cart item updated'}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Product not in cart'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove an item from the cart"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        product_id = request.data.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get cart
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Remove item from cart
        if cart.remove_item(product):
            return Response(
                {'message': 'Product removed from cart'}, 
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Product not in cart'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from the cart"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            cart = Cart.objects.get(user=request.user)
            cart.clear()
            return Response(
                {'message': 'Cart cleared'}, 
                status=status.HTTP_200_OK
            )
        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def items(self, request):
        """Get all items in the cart"""
        if not request.user.is_authenticated:
            return Response([], status=status.HTTP_200_OK)
        
        try:
            cart = Cart.objects.get(user=request.user)
            items = cart.items.all().select_related('product')
            serializer = CartItemSerializer(items, many=True)
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)