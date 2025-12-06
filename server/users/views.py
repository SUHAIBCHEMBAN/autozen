"""
Views for the users app.

This module defines API views for user authentication operations,
including sending and verifying OTP codes with caching implementation.
"""

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from django.conf import settings
from .serializers import LoginSerializer, OTPVerificationSerializer, UserSerializer
from .models import User
from .cache_utils import store_otp, verify_otp, delete_otp, get_user_from_cache, cache_user
import random
import logging

# Set up logging
logger = logging.getLogger(__name__)

class SendOTPView(APIView):
    """
    API view for sending OTP codes to users.
    
    Handles POST requests to send OTP codes via email or SMS.
    Uses caching to store OTP codes for verification.
    """
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
    def post(self, request):
        """
        Handle POST request to send OTP code.
        
        Args:
            request: The HTTP request object containing email_or_phone
            
        Returns:
            Response: JSON response with success/error message
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email_or_phone = serializer.validated_data['email_or_phone']
            
            # Generate 6 digit OTP
            otp = str(random.randint(100000, 999999))
            
            # Store OTP in cache using cache utility
            store_otp(email_or_phone, otp)
            
            # Print OTP to terminal for development
            if settings.DEBUG:
                print(f"\n{'='*50}")
                print(f"DEVELOPMENT MODE - OTP for {email_or_phone}: {otp}")
                print(f"{'='*50}\n")
                # Also log it
                logger.info(f"DEVELOPMENT MODE - OTP for {email_or_phone}: {otp}")
            
            # Check if it's email or phone
            if '@' in email_or_phone:
                # Send email
                try:
                    send_mail(
                        'Your OTP for Login',
                        f'Your OTP is: {otp}',
                        settings.EMAIL_HOST_USER,
                        [email_or_phone],
                        fail_silently=False,
                    )
                    return Response({
                        'message': 'OTP sent successfully to your email.',
                        'identifier': email_or_phone
                    }, status=status.HTTP_200_OK)
                except Exception as e:
                    return Response({
                        'error': 'Failed to send OTP email.'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # For phone, in a real application you would integrate with an SMS service
                # For now, we'll just simulate it
                return Response({
                    'message': 'OTP sent successfully to your phone.',
                    'identifier': email_or_phone
                }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    """
    API view for verifying OTP codes from users.
    
    Handles POST requests to verify OTP codes and authenticate users.
    Implements zero-query pattern using caching for user data.
    """
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
    def post(self, request):
        """
        Handle POST request to verify OTP code.
        
        Args:
            request: The HTTP request object containing email_or_phone and otp
            
        Returns:
            Response: JSON response with authentication result and user data
        """
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email_or_phone = serializer.validated_data['email_or_phone']
            otp = serializer.validated_data['otp']
            
            # Verify OTP using cache utility (zero-query pattern)
            if not verify_otp(email_or_phone, otp):
                # Check if OTP expired or is invalid
                return Response({
                    'error': 'OTP expired or invalid.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # OTP is valid, create or get user with caching
            try:
                # Try to get user from cache first (zero-query pattern)
                user = get_user_from_cache(email_or_phone)
                
                if not user:
                    # User not in cache, get from database
                    if '@' in email_or_phone:
                        user, created = User.objects.get_or_create(email=email_or_phone)
                        if created:
                            user.phone_number = None  # Since user logged in with email
                            user.save()
                    else:
                        user, created = User.objects.get_or_create(phone_number=email_or_phone)
                        if created:
                            user.email = None  # Since user logged in with phone
                            user.save()
                    
                    # Cache the user data for future requests
                    cache_user(user)
                
            except Exception as e:
                return Response({
                    'error': 'Failed to create/get user.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Delete OTP from cache after successful verification
            delete_otp(email_or_phone)
            
            # Create or get auth token for the user
            token, created = Token.objects.get_or_create(user=user)
            
            # In a real application, you would generate a token here
            # For simplicity, we're just returning success
            return Response({
                'message': 'Login successful.',
                'token': token.key,
                'user_id': user.id,
                'email': user.email,
                'phone_number': user.phone_number,
                'username': user.username,
                'profile': user.profile
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    API view for managing user profile.
    
    Handles GET requests to retrieve user profile and PUT requests to update it.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Handle GET request to retrieve user profile.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: JSON response with user profile data
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        """
        Handle PUT request to update user profile.
        
        Args:
            request: The HTTP request object containing profile data
            
        Returns:
            Response: JSON response with updated user profile data
        """
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)