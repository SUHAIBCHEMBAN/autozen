"""
URL configuration for the users app.

This module defines the URL patterns for user authentication endpoints,
including OTP sending and verification.
"""

from django.urls import path, include
from .views import SendOTPView, VerifyOTPView, UserProfileView, UserAddressListView, UserAddressDetailView

app_name = 'users'

urlpatterns = [
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('addresses/', UserAddressListView.as_view(), name='user-addresses'),
    path('addresses/<int:pk>/', UserAddressDetailView.as_view(), name='user-address-detail'),
]