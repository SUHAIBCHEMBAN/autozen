from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SendOTPView, VerifyOTPView

app_name = 'users'

# Create router and register viewsets (if we had viewsets)
# For function-based or class-based views, we still define them in urlpatterns

urlpatterns = [
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
]