"""
Test cases for wishlist caching functionality
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from products.models import Product, Brand, VehicleModel, PartCategory
from .models import Wishlist, WishlistItem
from .cache_utils import (
    get_cached_wishlist,
    get_cached_wishlist_items,
    get_cached_wishlist_count,
    add_to_wishlist_with_cache,
    remove_from_wishlist_with_cache,
    clear_wishlist_with_cache,
    is_product_in_wishlist_cached,
    invalidate_wishlist_cache
)


class WishlistCacheTestCase(TestCase):
    """Test case for wishlist caching functionality"""
    
    def setUp(self):
        """Set up test data"""
        # Create user
        User = get_user_model()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test brand
        self.brand = Brand.objects.create(
            name='Test Brand',
            slug='test-brand',
            is_active=True
        )
        
        # Create test vehicle model
        self.vehicle_model = VehicleModel.objects.create(
            brand=self.brand,
            name='Test Model',
            slug='test-model',
            is_active=True
        )
        
        # Create test category
        self.category = PartCategory.objects.create(
            name='Test Category',
            slug='test-category',
            is_active=True
        )
        
        # Create test products
        self.product1 = Product.objects.create(
            sku='TEST-001',
            name='Test Product 1',
            slug='test-product-1',
            brand=self.brand,
            vehicle_model=self.vehicle_model,
            part_category=self.category,
            description='Test product 1',
            price=100.00,
            is_active=True
        )
        
        self.product2 = Product.objects.create(
            sku='TEST-002',
            name='Test Product 2',
            slug='test-product-2',
            brand=self.brand,
            vehicle_model=self.vehicle_model,
            part_category=self.category,
            description='Test product 2',
            price=200.00,
            is_active=True
        )
    
    def test_get_cached_wishlist_creates_wishlist(self):
        """Test that get_cached_wishlist creates wishlist if it doesn't exist"""
        # Initially, no wishlist should exist
        self.assertFalse(Wishlist.objects.filter(user=self.user).exists())
        
        # Get cached wishlist - should create one
        wishlist = get_cached_wishlist(self.user.id)
        
        # Verify wishlist was created
        self.assertIsNotNone(wishlist)
        self.assertEqual(wishlist.user, self.user)
        self.assertTrue(Wishlist.objects.filter(user=self.user).exists())
    
    def test_get_cached_wishlist_returns_existing_wishlist(self):
        """Test that get_cached_wishlist returns existing wishlist"""
        # Create wishlist
        wishlist = Wishlist.objects.create(user=self.user)
        
        # Get cached wishlist
        cached_wishlist = get_cached_wishlist(self.user.id)
        
        # Verify it's the same wishlist
        self.assertEqual(cached_wishlist.id, wishlist.id)
    
    def test_get_cached_wishlist_items_empty(self):
        """Test getting cached wishlist items when wishlist is empty"""
        # Create empty wishlist
        Wishlist.objects.create(user=self.user)
        
        # Get cached items
        items = get_cached_wishlist_items(self.user.id)
        
        # Should be empty list
        self.assertEqual(items, [])
    
    def test_get_cached_wishlist_items_with_items(self):
        """Test getting cached wishlist items when wishlist has items"""
        # Create wishlist and add items
        wishlist = Wishlist.objects.create(user=self.user)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product1)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product2)
        
        # Get cached items
        items = get_cached_wishlist_items(self.user.id)
        
        # Should have 2 items
        self.assertEqual(len(items), 2)
        product_ids = [item.product_id for item in items]
        self.assertIn(self.product1.id, product_ids)
        self.assertIn(self.product2.id, product_ids)
    
    def test_get_cached_wishlist_count(self):
        """Test getting cached wishlist count"""
        # Create wishlist and add items
        wishlist = Wishlist.objects.create(user=self.user)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product1)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product2)
        
        # Get cached count
        count = get_cached_wishlist_count(self.user.id)
        
        # Should be 2
        self.assertEqual(count, 2)
    
    def test_is_product_in_wishlist_cached_true(self):
        """Test checking if product is in wishlist when it is"""
        # Create wishlist and add item
        wishlist = Wishlist.objects.create(user=self.user)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product1)
        
        # Check if product is in wishlist
        result = is_product_in_wishlist_cached(self.user.id, self.product1.id)
        
        # Should be True
        self.assertTrue(result)
    
    def test_is_product_in_wishlist_cached_false(self):
        """Test checking if product is in wishlist when it isn't"""
        # Create empty wishlist
        Wishlist.objects.create(user=self.user)
        
        # Check if product is in wishlist
        result = is_product_in_wishlist_cached(self.user.id, self.product1.id)
        
        # Should be False
        self.assertFalse(result)
    
    def test_add_to_wishlist_with_cache_new_item(self):
        """Test adding new item to wishlist with cache"""
        # Add item to wishlist
        result = add_to_wishlist_with_cache(self.user, self.product1.id)
        
        # Verify success
        self.assertTrue(result['success'])
        self.assertTrue(result['created'])
        self.assertEqual(result['message'], 'Product added to wishlist')
        
        # Verify item was added
        wishlist = Wishlist.objects.get(user=self.user)
        self.assertTrue(WishlistItem.objects.filter(
            wishlist=wishlist, 
            product=self.product1
        ).exists())
    
    def test_add_to_wishlist_with_cache_duplicate_item(self):
        """Test adding duplicate item to wishlist with cache"""
        # Add item to wishlist
        add_to_wishlist_with_cache(self.user, self.product1.id)
        
        # Try to add same item again
        result = add_to_wishlist_with_cache(self.user, self.product1.id)
        
        # Verify success but not created
        self.assertTrue(result['success'])
        self.assertFalse(result['created'])
        self.assertEqual(result['message'], 'Product already in wishlist')
    
    def test_remove_from_wishlist_with_cache_success(self):
        """Test removing item from wishlist with cache"""
        # Add item to wishlist
        wishlist = Wishlist.objects.create(user=self.user)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product1)
        
        # Remove item from wishlist
        result = remove_from_wishlist_with_cache(self.user, self.product1.id)
        
        # Verify success
        self.assertTrue(result['success'])
        self.assertEqual(result['message'], 'Product removed from wishlist')
        
        # Verify item was removed
        self.assertFalse(WishlistItem.objects.filter(
            wishlist=wishlist, 
            product=self.product1
        ).exists())
    
    def test_clear_wishlist_with_cache(self):
        """Test clearing wishlist with cache"""
        # Add items to wishlist
        wishlist = Wishlist.objects.create(user=self.user)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product1)
        WishlistItem.objects.create(wishlist=wishlist, product=self.product2)
        
        # Clear wishlist
        result = clear_wishlist_with_cache(self.user)
        
        # Verify success
        self.assertTrue(result['success'])
        self.assertIn('2 items removed from wishlist', result['message'])
        
        # Verify wishlist is empty
        self.assertEqual(wishlist.items.count(), 0)
    
    def test_cache_invalidation_on_wishlist_save(self):
        """Test that cache is invalidated when wishlist is saved"""
        # Create wishlist
        wishlist = Wishlist.objects.create(user=self.user)
        
        # Get cached wishlist to populate cache
        cached_wishlist = get_cached_wishlist(self.user.id)
        self.assertEqual(cached_wishlist.id, wishlist.id)
        
        # Modify wishlist
        wishlist.save()
        
        # Cache should be invalidated, so next call should hit database
        # We can't easily test this without mocking, but we can verify
        # the cache key no longer exists
        cache_key = f'wishlist_user_{self.user.id}'
        self.assertIsNone(cache.get(cache_key))
    
    def test_cache_invalidation_on_wishlist_item_operations(self):
        """Test that cache is invalidated when wishlist items are modified"""
        # Create wishlist and item
        wishlist = Wishlist.objects.create(user=self.user)
        item = WishlistItem.objects.create(wishlist=wishlist, product=self.product1)
        
        # Get cached items to populate cache
        cached_items = get_cached_wishlist_items(self.user.id)
        self.assertEqual(len(cached_items), 1)
        
        # Modify item
        item.save()
        
        # Cache should be invalidated
        cache_key = f'wishlist_items_user_{self.user.id}'
        self.assertIsNone(cache.get(cache_key))
    
    def test_invalidate_wishlist_cache_manual(self):
        """Test manual cache invalidation"""
        # Create wishlist
        wishlist = Wishlist.objects.create(user=self.user)
        
        # Get cached wishlist to populate cache
        cached_wishlist = get_cached_wishlist(self.user.id)
        self.assertEqual(cached_wishlist.id, wishlist.id)
        
        # Manually invalidate cache
        invalidate_wishlist_cache(self.user.id)
        
        # Cache should be cleared
        cache_key = f'wishlist_user_{self.user.id}'
        self.assertIsNone(cache.get(cache_key))