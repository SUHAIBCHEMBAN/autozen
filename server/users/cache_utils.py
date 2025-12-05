"""
Cache utility functions for the users app.

Implements zero-query caching with Redis for user data and OTP verification.
Provides functions for storing, retrieving, and validating cached data.
"""

from django.core.cache import cache
from django.conf import settings
from .models import User
import logging

logger = logging.getLogger(__name__)

# Cache timeout settings
USER_CACHE_TIMEOUT = getattr(settings, 'USER_CACHE_TIMEOUT', 60 * 15)  # 15 minutes
OTP_CACHE_TIMEOUT = getattr(settings, 'OTP_CACHE_TIMEOUT', 60 * 10)    # 10 minutes


def get_user_from_cache(identifier):
    """
    Retrieve user from cache using email or phone number as identifier.
    Implements zero-query pattern by caching user data.
    
    Args:
        identifier (str): Email or phone number
        
    Returns:
        User object or None if not found
    """
    cache_key = f"user_{identifier}"
    user_data = cache.get(cache_key)
    
    if user_data:
        logger.debug(f"Cache hit for user {identifier}")
        return user_data
    
    logger.debug(f"Cache miss for user {identifier}")
    # Fetch from database if not in cache
    try:
        if '@' in identifier:
            user = User.objects.get(email=identifier)
        else:
            user = User.objects.get(phone_number=identifier)
        
        # Cache the user data
        cache.set(cache_key, user, USER_CACHE_TIMEOUT)
        return user
    except User.DoesNotExist:
        return None


def cache_user(user):
    """
    Cache user data for both email and phone number identifiers.
    
    Args:
        user (User): User object to cache
    """
    if user.email:
        cache_key = f"user_{user.email}"
        cache.set(cache_key, user, USER_CACHE_TIMEOUT)
        
    if user.phone_number:
        cache_key = f"user_{user.phone_number}"
        cache.set(cache_key, user, USER_CACHE_TIMEOUT)


def invalidate_user_cache(identifier):
    """
    Invalidate user cache for a specific identifier.
    
    Args:
        identifier (str): Email or phone number
    """
    cache_key = f"user_{identifier}"
    cache.delete(cache_key)


def store_otp(identifier, otp):
    """
    Store OTP in cache with expiration.
    
    Args:
        identifier (str): Email or phone number
        otp (str): 6-digit OTP
    """
    cache_key = f"otp_{identifier}"
    cache.set(cache_key, otp, OTP_CACHE_TIMEOUT)


def verify_otp(identifier, otp):
    """
    Verify OTP from cache.
    
    Args:
        identifier (str): Email or phone number
        otp (str): 6-digit OTP to verify
        
    Returns:
        bool: True if OTP is valid, False otherwise
    """
    cache_key = f"otp_{identifier}"
    stored_otp = cache.get(cache_key)
    
    if stored_otp and stored_otp == otp:
        return True
    return False


def delete_otp(identifier):
    """
    Delete OTP from cache after successful verification.
    
    Args:
        identifier (str): Email or phone number
    """
    cache_key = f"otp_{identifier}"
    cache.delete(cache_key)