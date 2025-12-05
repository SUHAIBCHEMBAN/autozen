"""
Serializers for the users app.

This module defines serializers for user authentication operations,
including login and OTP verification.
"""

from rest_framework import serializers
from django.core.validators import EmailValidator, RegexValidator
from django.contrib.auth import get_user_model
import re

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login requests.
    
    Validates that the provided identifier is either a valid email or phone number.
    """
    email_or_phone = serializers.CharField(max_length=255, required=True)
    
    def validate_email_or_phone(self, value):
        """
        Validate that the input is either a valid email or phone number.
        
        Args:
            value (str): The email or phone number to validate
            
        Returns:
            str: The validated email or phone number
            
        Raises:
            ValidationError: If the input is neither a valid email nor phone number
        """
        # Check if it's a valid email
        email_validator = EmailValidator()
        phone_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$')
        
        is_email = False
        is_phone = False
        
        try:
            email_validator(value)
            is_email = True
        except:
            pass
            
        try:
            phone_validator(value)
            is_phone = True
        except:
            pass
            
        if not is_email and not is_phone:
            raise serializers.ValidationError("Enter a valid email or phone number.")
            
        return value


class OTPVerificationSerializer(serializers.Serializer):
    """
    Serializer for OTP verification requests.
    
    Validates both the identifier (email or phone) and the OTP code.
    """
    email_or_phone = serializers.CharField(max_length=255, required=True)
    otp = serializers.CharField(max_length=6, required=True)
    
    def validate_otp(self, value):
        """
        Validate that OTP is a 6-digit number.
        
        Args:
            value (str): The OTP code to validate
            
        Returns:
            str: The validated OTP code
            
        Raises:
            ValidationError: If the OTP is not a 6-digit number
        """
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError("OTP must be a 6-digit number.")
        return value
    
    def validate_email_or_phone(self, value):
        """
        Validate that the input is either a valid email or phone number.
        
        Args:
            value (str): The email or phone number to validate
            
        Returns:
            str: The validated email or phone number
            
        Raises:
            ValidationError: If the input is neither a valid email nor phone number
        """
        # Check if it's a valid email
        email_validator = EmailValidator()
        phone_validator = RegexValidator(regex=r'^\+?1?\d{9,15}$')
        
        is_email = False
        is_phone = False
        
        try:
            email_validator(value)
            is_email = True
        except:
            pass
            
        try:
            phone_validator(value)
            is_phone = True
        except:
            pass
            
        if not is_email and not is_phone:
            raise serializers.ValidationError("Enter a valid email or phone number.")
            
        return value