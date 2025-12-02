from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings
from .serializers import LoginSerializer, OTPVerificationSerializer
from .models import User
import random


class SendOTPView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email_or_phone = serializer.validated_data['email_or_phone']
            
            # Generate 6 digit OTP
            otp = str(random.randint(100000, 999999))
            
            # Store OTP in cache for 10 minutes
            cache.set(f"otp_{email_or_phone}", otp, 600)  # 600 seconds = 10 minutes
            
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
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            email_or_phone = serializer.validated_data['email_or_phone']
            otp = serializer.validated_data['otp']
            
            # Get stored OTP from cache
            stored_otp = cache.get(f"otp_{email_or_phone}")
            
            if not stored_otp:
                return Response({
                    'error': 'OTP expired or not generated.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            if stored_otp != otp:
                return Response({
                    'error': 'Invalid OTP.'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # OTP is valid, create or get user
            try:
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
            except Exception as e:
                return Response({
                    'error': 'Failed to create/get user.'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Delete OTP from cache after successful verification
            cache.delete(f"otp_{email_or_phone}")
            
            # In a real application, you would generate a token here
            # For simplicity, we're just returning success
            return Response({
                'message': 'Login successful.',
                'user_id': user.id,
                'email': user.email,
                'phone_number': user.phone_number
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)