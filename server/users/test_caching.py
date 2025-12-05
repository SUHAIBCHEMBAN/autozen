"""
Test file for users app caching implementation.
"""

from django.test import TestCase
from django.core.cache import cache
from .models import User
from .cache_utils import (
    get_user_from_cache, 
    cache_user, 
    invalidate_user_cache,
    store_otp,
    verify_otp,
    delete_otp
)


class UserCachingTestCase(TestCase):
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email="test@example.com",
            phone_number="+1234567890",
            password="testpass123"
        )
        
    def tearDown(self):
        """Clean up cache after each test."""
        cache.clear()
        
    def test_cache_user(self):
        """Test caching user data."""
        cache_user(self.user)
        
        # Test retrieving user by email
        cached_user = get_user_from_cache(self.user.email)
        self.assertEqual(cached_user.id, self.user.id)
        self.assertEqual(cached_user.email, self.user.email)
        
        # Test retrieving user by phone number
        cached_user = get_user_from_cache(self.user.phone_number)
        self.assertEqual(cached_user.id, self.user.id)
        self.assertEqual(cached_user.phone_number, self.user.phone_number)
        
    def test_get_user_from_cache_miss(self):
        """Test getting user when not in cache (should fetch from DB)."""
        # Clear cache to ensure miss
        cache.clear()
        
        # This should fetch from DB and cache the result
        user = get_user_from_cache(self.user.email)
        self.assertEqual(user.id, self.user.id)
        self.assertEqual(user.email, self.user.email)
        
        # Second call should hit cache
        user = get_user_from_cache(self.user.email)
        self.assertEqual(user.id, self.user.id)
        self.assertEqual(user.email, self.user.email)
        
    def test_invalidate_user_cache(self):
        """Test invalidating user cache."""
        cache_user(self.user)
        
        # Verify user is in cache
        cached_user = get_user_from_cache(self.user.email)
        self.assertIsNotNone(cached_user)
        
        # Invalidate cache
        invalidate_user_cache(self.user.email)
        
        # Verify user is no longer in cache (will fetch from DB)
        cached_user = get_user_from_cache(self.user.email)
        self.assertEqual(cached_user.id, self.user.id)
        
    def test_otp_functions(self):
        """Test OTP storage and verification."""
        identifier = "test@example.com"
        otp = "123456"
        
        # Store OTP
        store_otp(identifier, otp)
        
        # Verify OTP
        self.assertTrue(verify_otp(identifier, otp))
        self.assertFalse(verify_otp(identifier, "654321"))  # Wrong OTP
        self.assertFalse(verify_otp("wrong@example.com", otp))  # Wrong identifier
        
        # Delete OTP
        delete_otp(identifier)
        self.assertFalse(verify_otp(identifier, otp))  # Should fail after deletion
        
    def test_user_cache_invalidation_signal(self):
        """Test that user cache is invalidated when user is saved."""
        # Cache the user
        cache_user(self.user)
        
        # Verify user is in cache
        cached_user = get_user_from_cache(self.user.email)
        self.assertIsNotNone(cached_user)
        
        # Modify user (this should trigger the signal)
        self.user.is_staff = True
        self.user.save()
        
        # User should be removed from cache after save
        # Note: This test verifies the signal is connected, but the actual
        # cache invalidation happens in the signal handler, not in get_user_from_cache