from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.cache import cache
from django.conf import settings
import hashlib
import json
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, CartItemCreateSerializer, CartItemUpdateSerializer
from products.models import Product


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a cart to access it.
    
    This permission ensures that users can only access their own cart data,
    providing security and data isolation between users.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check if the cart belongs to the current user.
        
        Args:
            request: The HTTP request object
            view: The view being accessed
            obj: The cart object being accessed
            
        Returns:
            bool: True if the cart belongs to the current user, False otherwise
        """
        # Check if the cart belongs to the current user
        return obj.user == request.user

    def has_permission(self, request, view):
        """
        Check if the user has general permission to access cart views.
        
        Authenticated users can access cart views. Specific object-level
        permissions are checked in has_object_permission.
        
        Args:
            request: The HTTP request object
            view: The view being accessed
            
        Returns:
            bool: True if user is authenticated, False otherwise
        """
        # For list and create views, authenticated users can access
        return request.user.is_authenticated


class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Cart operations.
    
    Provides RESTful API endpoints for cart management including:
    - Retrieving user's cart
    - Adding items to cart
    - Updating item quantities
    - Removing items from cart
    - Clearing the entire cart
    
    Implements caching for performance optimization and uses proper
    authentication and permission checks.
    """
    serializer_class = CartSerializer
    permission_classes = [IsOwner]
    
    def _get_cart_cache_key(self, user_id):
        """
        Generate cache key for user's cart.
        
        Creates a unique cache key for storing/retrieving cart data
        for a specific user.
        
        Args:
            user_id (int): The ID of the user
            
        Returns:
            str: Cache key for the user's cart data
        """
        return f"cart_{user_id}"
    
    def _get_cart_items_cache_key(self, user_id):
        """
        Generate cache key for user's cart items.
        
        Creates a unique cache key for storing/retrieving cart items
        for a specific user.
        
        Args:
            user_id (int): The ID of the user
            
        Returns:
            str: Cache key for the user's cart items data
        """
        return f"cart_items_{user_id}"
    
    def _get_user_cache_key(self, user_id):
        """
        Generate cache key for user object.
        
        Creates a unique cache key for storing/retrieving user objects.
        User data is cached for 30 minutes as it rarely changes.
        
        Args:
            user_id (int): The ID of the user
            
        Returns:
            str: Cache key for the user object
        """
        return f"user_{user_id}"
    
    def get_queryset(self):
        """
        Return the cart for the current user with optimized queries.
        
        Filters carts to only return the cart belonging to the
        currently authenticated user.
        
        Returns:
            QuerySet: QuerySet containing the user's cart
        """
        if not self.request.user.is_authenticated:
            return Cart.objects.none()
        return Cart.objects.filter(user=self.request.user)
    
    def get_object(self):
        """
        Get or create the cart for the current user.
        
        Retrieves the existing cart for the user or creates a new one
        if it doesn't exist. Attempts to use cached user object for
        performance optimization.
        
        Returns:
            Cart: The user's cart object
        """
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication required")
        
        # Try to get user from cache first
        user_cache_key = self._get_user_cache_key(self.request.user.id)
        cached_user = cache.get(user_cache_key)
        
        if cached_user:
            # Use cached user
            user = cached_user
        else:
            # Cache the user for 30 minutes (since user data rarely changes)
            cache.set(user_cache_key, self.request.user, 60 * 30)
            user = self.request.user
        
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    
    def list(self, request, *args, **kwargs):
        """
        Get the user's cart with caching.
        
        Retrieves the user's cart data from cache if available,
        otherwise fetches from database and caches the result.
        Uses serialized data for caching to avoid serialization overhead.
        
        Args:
            request: The HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Returns:
            Response: Serialized cart data with HTTP 200 status
            Response: Error message with HTTP 400 status if exception occurs
        """
        try:
            # Try to get from cache first
            cache_key = self._get_cart_cache_key(request.user.id)
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return Response(cached_data)
            
            # Get cart
            cart = self.get_object()
            serializer = self.get_serializer(cart)
            
            # Cache the serialized data for 15 minutes
            cache.set(cache_key, serializer.data, 60 * 15)
            
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Add an item to the cart.
        
        Adds a product to the user's cart with the specified quantity.
        Validates product stock availability before adding. Invalidates
        cart cache upon successful addition.
        
        Args:
            request: The HTTP request object containing product_id and quantity
            
        Returns:
            Response: Success message with HTTP 201 status
            Response: Error message with HTTP 400/401/404 status
        """
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
            
            # Invalidate cache for this user's cart
            cache.delete(self._get_cart_cache_key(request.user.id))
            cache.delete(self._get_cart_items_cache_key(request.user.id))
            
            return Response(
                {'message': 'Product added to cart', 'item_id': cart_item.id}, 
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['put'])
    def update_item(self, request):
        """
        Update the quantity of an item in the cart.
        
        Updates the quantity of a product already in the user's cart.
        Validates product stock availability before updating. Invalidates
        cart cache upon successful update.
        
        Args:
            request: The HTTP request object containing product_id and quantity
            
        Returns:
            Response: Success message with HTTP 200 status
            Response: Error message with HTTP 400/401/404 status
        """
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
                # Invalidate cache for this user's cart
                cache.delete(self._get_cart_cache_key(request.user.id))
                cache.delete(self._get_cart_items_cache_key(request.user.id))
                
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
        """
        Remove an item from the cart.
        
        Removes a product from the user's cart entirely, regardless
        of quantity. Invalidates cart cache upon successful removal.
        
        Args:
            request: The HTTP request object containing product_id
            
        Returns:
            Response: Success message with HTTP 200 status
            Response: Error message with HTTP 400/401/404 status
        """
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
            # Invalidate cache for this user's cart
            cache.delete(self._get_cart_cache_key(request.user.id))
            cache.delete(self._get_cart_items_cache_key(request.user.id))
            
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
        """
        Clear all items from the cart.
        
        Removes all items from the user's cart, leaving an empty cart.
        Invalidates cart cache upon successful clearing.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: Success message with HTTP 200 status
            Response: Error message with HTTP 401/404 status
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            cart = Cart.objects.get(user=request.user)
            cart.clear()
            
            # Invalidate cache for this user's cart
            cache.delete(self._get_cart_cache_key(request.user.id))
            cache.delete(self._get_cart_items_cache_key(request.user.id))
            
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
        """
        Get all items in the cart with caching.
        
        Retrieves all items in the user's cart with product details.
        Uses caching for performance optimization and prefetches
        related product data to minimize database queries.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: List of cart items with HTTP 200 status
            Response: Empty list with HTTP 200 status if user not authenticated or cart empty
        """
        if not request.user.is_authenticated:
            return Response([], status=status.HTTP_200_OK)
        
        # Try to get from cache first
        cache_key = self._get_cart_items_cache_key(request.user.id)
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        try:
            # Get cart and items with prefetched related objects
            cart = Cart.objects.prefetch_related(
                'items__product__brand',
                'items__product__vehicle_model',
                'items__product__part_category'
            ).get(user=request.user)
            
            items = cart.items_with_products.all()
            serializer = CartItemSerializer(items, many=True, context=self.get_serializer_context())
            
            # Cache the serialized data for 15 minutes
            cache.set(cache_key, serializer.data, 60 * 15)
            
            return Response(serializer.data)
        except Cart.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)