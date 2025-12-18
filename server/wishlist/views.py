from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Wishlist, WishlistItem
from .serializers import WishlistSerializer, WishlistItemSerializer, WishlistCreateSerializer
from .cache_utils import (
    get_cached_wishlist,
    get_cached_wishlist_items,
    get_cached_wishlist_count,
    get_cached_wishlist_response,
    cache_wishlist_response,
    add_to_wishlist_with_cache,
    remove_from_wishlist_with_cache,
    clear_wishlist_with_cache,
    is_product_in_wishlist_cached
)
from products.models import Product


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a wishlist to access it.
    
    This permission ensures that users can only access their own wishlist data,
    providing security and data isolation between users.
    """
    def has_object_permission(self, request, view, obj):
        """
        Check if the wishlist belongs to the current user.
        
        Args:
            request: The HTTP request object
            view: The view being accessed
            obj: The wishlist object being accessed
            
        Returns:
            bool: True if the wishlist belongs to the current user, False otherwise
        """
        # Check if the wishlist belongs to the current user
        return obj.user == request.user

    def has_permission(self, request, view):
        """
        Check if the user has general permission to access wishlist views.
        
        Authenticated users can access wishlist views. Specific object-level
        permissions are checked in has_object_permission.
        
        Args:
            request: The HTTP request object
            view: The view being accessed
            
        Returns:
            bool: True if user is authenticated, False otherwise
        """
        # For list and create views, authenticated users can access
        return request.user.is_authenticated


class WishlistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Wishlist operations.
    
    Provides RESTful API endpoints for wishlist management including:
    - Retrieving user's wishlist
    - Adding items to wishlist
    - Removing items from wishlist
    - Clearing the entire wishlist
    
    Implements caching for performance optimization and uses proper
    authentication and permission checks.
    """
    serializer_class = WishlistSerializer
    permission_classes = [IsOwner]
    
    def get_serializer_context(self):
        """
        Return the context for the serializer.
        
        Adds the request object to the serializer context to enable
        proper URL generation for hyperlinked fields.
        
        Returns:
            dict: Context dictionary with request object
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        """
        Return the wishlist for the current user with optimized queries.
        
        Filters wishlists to only return the wishlist belonging to the
        currently authenticated user. Prefetches related product data
        to minimize database queries.
        
        Returns:
            QuerySet: QuerySet containing the user's wishlist with prefetched data
        """
        if not self.request.user.is_authenticated:
            return Wishlist.objects.none()
        return Wishlist.objects.filter(user=self.request.user).prefetch_related('items__product', 'items__product__brand', 'items__product__vehicle_model', 'items__product__part_category')
    
    def get_object(self):
        """
        Get or create the wishlist for the current user with caching.
        
        Retrieves the existing wishlist for the user or creates a new one
        if it doesn't exist. Uses caching to improve performance for
        repeated requests.
        
        Returns:
            Wishlist: The user's wishlist object
        
        Raises:
            PermissionDenied: If user is not authenticated
        """
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication required")
        
        # Try to get from cache first
        wishlist = get_cached_wishlist(self.request.user.id)
        if wishlist is None:
            # Not in cache, get from database
            wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist
    
    def list(self, request, *args, **kwargs):
        """
        Get the user's wishlist with caching.
        
        Retrieves the user's wishlist data from cache if available,
        otherwise fetches from database and caches the result.
        Uses serialized data for caching to avoid serialization overhead.
        
        Args:
            request: The HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Returns:
            Response: Serialized wishlist data with HTTP 200 status
            Response: Error message with HTTP 400 status if exception occurs
        """
        try:
            # Try to get cached response first
            cached_response = get_cached_wishlist_response(request.user.id)
            if cached_response:
                return Response(cached_response)
            
            wishlist = self.get_object()
            serializer = self.get_serializer(wishlist, context=self.get_serializer_context())
            response_data = serializer.data
            
            # Cache the response
            cache_wishlist_response(request.user.id, response_data)
            
            return Response(response_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """
        Add an item to the wishlist with caching.
        
        Adds a product to the user's wishlist. Uses cached functions
        for performance optimization and invalidates cache upon successful addition.
        
        Args:
            request: The HTTP request object containing product_id
            
        Returns:
            Response: Success message with HTTP 200/201 status
            Response: Error message with HTTP 400/401 status
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = WishlistCreateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product_id']
            
            # Use cached function to add item
            result = add_to_wishlist_with_cache(request.user, product.id)
            
            if result['success']:
                status_code = status.HTTP_201_CREATED if result['created'] else status.HTTP_200_OK
                return Response(
                    {'message': result['message']}, 
                    status=status_code
                )
            else:
                return Response(
                    {'error': result['message']}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """
        Remove an item from the wishlist with caching.
        
        Removes a product from the user's wishlist entirely.
        Uses cached functions for performance optimization and
        invalidates cache upon successful removal.
        
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
        
        serializer = WishlistCreateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product_id']
            
            # Use cached function to remove item
            result = remove_from_wishlist_with_cache(request.user, product.id)
            
            if result['success']:
                return Response(
                    {'message': result['message']}, 
                    status=status.HTTP_200_OK
                )
            else:
                status_code = status.HTTP_404_NOT_FOUND if 'not found' in result['message'].lower() else status.HTTP_400_BAD_REQUEST
                return Response(
                    {'error': result['message']}, 
                    status=status_code
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """
        Clear all items from the wishlist with caching.
        
        Removes all items from the user's wishlist, leaving an empty wishlist.
        Uses cached functions for performance optimization and
        invalidates cache upon successful clearing.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: Success message with HTTP 200 status
            Response: Error message with HTTP 400/401/404 status
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Use cached function to clear wishlist
        result = clear_wishlist_with_cache(request.user)
        
        if result['success']:
            return Response(
                {'message': result['message']}, 
                status=status.HTTP_200_OK
            )
        else:
            status_code = status.HTTP_404_NOT_FOUND if 'not found' in result['message'].lower() else status.HTTP_400_BAD_REQUEST
            return Response(
                {'error': result['message']}, 
                status=status_code
            )
    
    @action(detail=False, methods=['get'])
    def items(self, request):
        """
        Get all items in the wishlist with caching.
        
        Retrieves all items in the user's wishlist with product details.
        Uses caching for performance optimization and selects
        related product data to minimize database queries.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: List of wishlist items with HTTP 200 status
            Response: Empty list with HTTP 200 status if user not authenticated or wishlist empty
        """
        if not request.user.is_authenticated:
            return Response([], status=status.HTTP_200_OK)
        
        # Try to get items from cache
        items = get_cached_wishlist_items(request.user.id)
        if items:
            serializer = WishlistItemSerializer(items, many=True, context=self.get_serializer_context())
            return Response(serializer.data)
        else:
            # Fallback to database if not in cache
            try:
                wishlist = Wishlist.objects.get(user=request.user)
                items = wishlist.items.all().select_related('product', 'product__brand', 'product__vehicle_model', 'product__part_category')
                serializer = WishlistItemSerializer(items, many=True, context=self.get_serializer_context())
                return Response(serializer.data)
            except Wishlist.DoesNotExist:
                return Response([], status=status.HTTP_200_OK)