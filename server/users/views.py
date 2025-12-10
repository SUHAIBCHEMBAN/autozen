"""
Views for the users app.

This module defines views for user authentication operations,
including OTP sending and verification, and user profile management.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache
from django.core.exceptions import ValidationError
from .models import User, Address
from .serializers import UserSerializer, UserProfileSerializer, AddressSerializer, AddressCreateSerializer
import logging
import random

logger = logging.getLogger(__name__)


class SendOTPView(APIView):
    """
    View for sending OTP to user's email or phone number.
    
    Generates a 6-digit OTP and sends it to the provided email or phone number.
    In development, OTP is logged to console instead of being sent via email/SMS.
    """
    permission_classes = [AllowAny]  # Make this endpoint publicly accessible
    
    def post(self, request):
        """
        Send OTP to the provided email or phone number.
        
        Args:
            request (Request): The HTTP request containing email_or_phone
            
        Returns:
            Response: Success or error response with appropriate status code
        """
        email_or_phone = request.data.get('email_or_phone')
        
        if not email_or_phone:
            return Response(
                {'error': 'Email or phone number is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Cache OTP for 10 minutes with the email/phone as key
        cache_key = f"otp_{email_or_phone}"
        cache.set(cache_key, otp, 600)  # 600 seconds = 10 minutes
        
        # In development, print OTP to console instead of sending email/SMS
        logger.info(f"OTP for {email_or_phone}: {otp}")
        print(f"\n===== DEVELOPMENT OTP =====")
        print(f"OTP for {email_or_phone}: {otp}")
        print(f"========================\n")
        
        return Response({
            'message': 'OTP sent successfully',
            'identifier': email_or_phone
        }, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    """
    View for verifying OTP provided by the user.
    
    Validates the OTP against the cached value and creates/authenticates the user.
    """
    permission_classes = [AllowAny]  # Make this endpoint publicly accessible
    
    def post(self, request):
        """
        Verify the provided OTP and authenticate/create the user.
        
        Args:
            request (Request): The HTTP request containing email_or_phone and otp
            
        Returns:
            Response: Authentication token and user data or error response
        """
        email_or_phone = request.data.get('email_or_phone')
        otp = request.data.get('otp')
        
        if not email_or_phone or not otp:
            return Response(
                {'error': 'Email/Phone and OTP are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get cached OTP
        cache_key = f"otp_{email_or_phone}"
        cached_otp = cache.get(cache_key)
        
        if not cached_otp:
            return Response(
                {'error': 'OTP expired or not sent'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if otp != cached_otp:
            return Response(
                {'error': 'Invalid OTP'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # OTP is valid, delete it from cache
        cache.delete(cache_key)
        
        # Check if user exists, create if not
        user = None
        try:
            if '@' in email_or_phone:
                user = User.objects.get(email=email_or_phone)
            else:
                user = User.objects.get(phone_number=email_or_phone)
        except User.DoesNotExist:
            # Create new user
            try:
                if '@' in email_or_phone:
                    user = User.objects.create_user(email=email_or_phone)
                else:
                    user = User.objects.create_user(phone_number=email_or_phone)
            except ValidationError as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        # Create or get authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        # Serialize user data
        serializer = UserSerializer(user)
        
        return Response({
            'message': 'OTP verified successfully',
            'token': token.key,
            'user': serializer.data
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    View for managing user profile information.
    
    Allows authenticated users to view and update their profile data.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get the authenticated user's profile information.
        
        Args:
            request (Request): The authenticated HTTP request
            
        Returns:
            Response: User profile data
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        """
        Update the authenticated user's profile information.
        
        Args:
            request (Request): The authenticated HTTP request with profile data
            
        Returns:
            Response: Updated user profile data or error response
        """
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAddressListView(APIView):
    """
    View for listing and creating user addresses.
    
    Allows authenticated users to view their saved addresses and add new ones.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get all addresses for the authenticated user.
        
        Args:
            request (Request): The authenticated HTTP request
            
        Returns:
            Response: List of user's addresses
        """
        addresses = Address.objects.filter(user=request.user)
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        """
        Create a new address for the authenticated user.
        
        Args:
            request (Request): The authenticated HTTP request with address data
            
        Returns:
            Response: Created address data or error response
        """
        serializer = AddressCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Set the user to the authenticated user
            address = serializer.save(user=request.user)
            # Return the full serialized address
            full_serializer = AddressSerializer(address)
            return Response(full_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAddressDetailView(APIView):
    """
    View for managing individual user addresses.
    
    Allows authenticated users to view, update, or delete specific addresses.
    """
    permission_classes = [IsAuthenticated]
    
    def get_object(self, user, pk):
        """
        Get an address belonging to the user.
        
        Args:
            user (User): The authenticated user
            pk (int): The primary key of the address
            
        Returns:
            Address: The address object if it belongs to the user
            
        Raises:
            Address.DoesNotExist: If the address doesn't exist or doesn't belong to the user
        """
        try:
            return Address.objects.get(pk=pk, user=user)
        except Address.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """
        Get a specific address for the authenticated user.
        
        Args:
            request (Request): The authenticated HTTP request
            pk (int): The primary key of the address
            
        Returns:
            Response: Address data or error response
        """
        address = self.get_object(request.user, pk)
        if not address:
            return Response(
                {'error': 'Address not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AddressSerializer(address)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        """
        Update a specific address for the authenticated user.
        
        Args:
            request (Request): The authenticated HTTP request with address data
            pk (int): The primary key of the address
            
        Returns:
            Response: Updated address data or error response
        """
        address = self.get_object(request.user, pk)
        if not address:
            return Response(
                {'error': 'Address not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """
        Delete a specific address for the authenticated user.
        
        Args:
            request (Request): The authenticated HTTP request
            pk (int): The primary key of the address
            
        Returns:
            Response: Success response or error response
        """
        address = self.get_object(request.user, pk)
        if not address:
            return Response(
                {'error': 'Address not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        address.delete()
        return Response(
            {'message': 'Address deleted successfully'}, 
            status=status.HTTP_204_NO_CONTENT
        )