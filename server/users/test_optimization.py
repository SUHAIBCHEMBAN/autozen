"""
Performance test for users app caching implementation.
"""

from django.test import TestCase
from django.core.cache import cache
from django.contrib.auth import get_user_model
from .cache_utils import (
    get_user_from_cache, 
    cache_user, 
    store_otp,
    verify_otp,
    delete_otp
)

User = get_user_model()


class UserOptimizationTestCase(TestCase):
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
        
    def test_user_caching_performance(self):
        """Test that user caching improves performance."""
        # First access (cache miss)
        user = get_user_from_cache(self.user.email)
        self.assertEqual(user.id, self.user.id)
        
        # Second access (cache hit)
        user = get_user_from_cache(self.user.email)
        self.assertEqual(user.id, self.user.id)
        
    def test_otp_caching_performance(self):
        """Test that OTP caching works correctly."""
        identifier = "test@example.com"
        otp = "123456"
        
        # Store OTP
        store_otp(identifier, otp)
        
        # Verify OTP (should be fast)
        self.assertTrue(verify_otp(identifier, otp))
        
        # Delete OTP
        delete_otp(identifier)
        self.assertFalse(verify_otp(identifier, otp))
        
    def test_cache_user_function(self):
        """Test that cache_user function works correctly."""
        # Cache the user
        cache_user(self.user)
        
        # Retrieve by email
        cached_user = get_user_from_cache(self.user.email)
        self.assertEqual(cached_user.id, self.user.id)
        
        # Retrieve by phone
        cached_user = get_user_from_cache(self.user.phone_number)
        self.assertEqual(cached_user.id, self.user.id)