from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Wishlist, WishlistItem
from .serializers import WishlistSerializer, WishlistItemSerializer, WishlistCreateSerializer
from products.models import Product


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a wishlist to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the wishlist belongs to the current user
        return obj.user == request.user

    def has_permission(self, request, view):
        # For list and create views, authenticated users can access
        return request.user.is_authenticated


class WishlistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling Wishlist operations
    """
    serializer_class = WishlistSerializer
    permission_classes = [IsOwner]
    
    def get_queryset(self):
        """Return the wishlist for the current user"""
        if not self.request.user.is_authenticated:
            return Wishlist.objects.none()
        return Wishlist.objects.filter(user=self.request.user).prefetch_related('items__product')
    
    def get_object(self):
        """Get or create the wishlist for the current user"""
        if not self.request.user.is_authenticated:
            raise PermissionDenied("Authentication required")
        
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        return wishlist
    
    def list(self, request, *args, **kwargs):
        """Get the user's wishlist"""
        try:
            wishlist = self.get_object()
            serializer = self.get_serializer(wishlist)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add an item to the wishlist"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = WishlistCreateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product_id']
            
            # Get or create wishlist
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            
            # Check if item already exists
            if WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
                return Response(
                    {'message': 'Product already in wishlist'}, 
                    status=status.HTTP_200_OK
                )
            
            # Add item to wishlist
            wishlist_item = WishlistItem.objects.create(
                wishlist=wishlist,
                product=product
            )
            
            # Update wishlist timestamp
            wishlist.save()
            
            return Response(
                {'message': 'Product added to wishlist'}, 
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove an item from the wishlist"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        serializer = WishlistCreateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product_id']
            
            # Get wishlist
            try:
                wishlist = Wishlist.objects.get(user=request.user)
            except Wishlist.DoesNotExist:
                return Response(
                    {'error': 'Wishlist not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Remove item from wishlist
            try:
                wishlist_item = WishlistItem.objects.get(
                    wishlist=wishlist, 
                    product=product
                )
                wishlist_item.delete()
                
                # Update wishlist timestamp
                wishlist.save()
                
                return Response(
                    {'message': 'Product removed from wishlist'}, 
                    status=status.HTTP_200_OK
                )
            except WishlistItem.DoesNotExist:
                return Response(
                    {'error': 'Product not in wishlist'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from the wishlist"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            wishlist.items.all().delete()
            wishlist.save()
            return Response(
                {'message': 'Wishlist cleared'}, 
                status=status.HTTP_200_OK
            )
        except Wishlist.DoesNotExist:
            return Response(
                {'error': 'Wishlist not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def items(self, request):
        """Get all items in the wishlist"""
        if not request.user.is_authenticated:
            return Response([], status=status.HTTP_200_OK)
        
        try:
            wishlist = Wishlist.objects.get(user=request.user)
            items = wishlist.items.all().select_related('product')
            serializer = WishlistItemSerializer(items, many=True)
            return Response(serializer.data)
        except Wishlist.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)