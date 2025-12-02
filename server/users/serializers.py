from rest_framework import serializers
from django.core.validators import EmailValidator, RegexValidator
from .models import User
import re


class LoginSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField(max_length=255, required=True)
    
    def validate_email_or_phone(self, value):
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
    email_or_phone = serializers.CharField(max_length=255, required=True)
    otp = serializers.CharField(max_length=6, required=True)
    
    def validate_otp(self, value):
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError("OTP must be a 6-digit number.")
        return value
    
    def validate_email_or_phone(self, value):
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