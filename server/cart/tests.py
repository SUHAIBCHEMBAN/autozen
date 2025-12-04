from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from products.models import Product
from .models import Cart, CartItem
from .utils import (
    add_to_cart, remove_from_cart, update_cart_item, 
    clear_cart, get_cart_summary, is_product_in_cart
)

User = get_user_model()


class CartCacheTestCase(TestCase):
    """
    Test case for cart caching functionality.
    
    Tests the caching implementation for cart operations including
    property caching, cache invalidation, and utility function integration.
    """
    
    def setUp(self):
        """
        Set up test data before each test method.
        
        Creates a test user, test products, and a test cart for use in tests.
        """
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test products
        self.product1 = Product.objects.create(
            sku='TEST-001',
            name='Test Product 1',
            slug='test-product-1',
            description='Test product for cart testing',
            price=29.99,
            stock_quantity=100
        )
        
        self.product2 = Product.objects.create(
            sku='TEST-002',
            name='Test Product 2',
            slug='test-product-2',
            description='Another test product',
            price=49.99,
            stock_quantity=50
        )
        
        # Create cart
        self.cart = Cart.objects.create(user=self.user)

    def tearDown(self):
        """
        Clean up after each test method.
        
        Clears the cache to ensure test isolation.
        """
        # Clear cache after each test
        cache.clear()

    def test_cart_property_caching(self):
        """
        Test that cart properties are cached correctly.
        
        Verifies that cart properties (items_count, total_quantity, subtotal)
        are calculated correctly and that caching works as expected.
        """
        # Initially, cart should be empty
        self.assertEqual(self.cart.items_count, 0)
        self.assertEqual(self.cart.total_quantity, 0)
        self.assertEqual(float(self.cart.subtotal), 0.00)
        
        # Add items to cart
        self.cart.add_item(self.product1, 2)
        self.cart.add_item(self.product2, 1)
        
        # Check that properties are updated (cache invalidated)
        self.assertEqual(self.cart.items_count, 2)
        self.assertEqual(self.cart.total_quantity, 3)
        expected_subtotal = (29.99 * 2) + (49.99 * 1)
        self.assertEqual(float(self.cart.subtotal), expected_subtotal)

    def test_utils_caching(self):
        """
        Test that utility functions work with caching.
        
        Verifies that utility functions properly interact with the caching
        system and return correct results.
        """
        # Add item using utility function
        result = add_to_cart(self.user, self.product1.id, 3)
        self.assertTrue(result['success'])
        
        # Check cart summary
        summary = get_cart_summary(self.user)
        self.assertEqual(summary['items_count'], 1)
        self.assertEqual(summary['total_quantity'], 3)
        self.assertEqual(summary['subtotal'], 89.97)
        
        # Add another item
        result = add_to_cart(self.user, self.product2.id, 2)
        self.assertTrue(result['success'])
        
        # Check updated summary
        summary = get_cart_summary(self.user)
        self.assertEqual(summary['items_count'], 2)
        self.assertEqual(summary['total_quantity'], 5)
        expected_subtotal = (29.99 * 3) + (49.99 * 2)
        self.assertEqual(summary['subtotal'], expected_subtotal)

    def test_cache_invalidation_on_updates(self):
        """
        Test that cache is properly invalidated on cart updates.
        
        Verifies that when cart contents are modified, the cache is
        properly invalidated and fresh data is retrieved.
        """
        # Add items
        self.cart.add_item(self.product1, 2)
        
        # Check initial values
        initial_count = self.cart.items_count
        initial_quantity = self.cart.total_quantity
        initial_subtotal = float(self.cart.subtotal)
        
        # Update item quantity
        self.cart.update_item_quantity(self.product1, 5)
        
        # Check that values are updated (cache invalidated)
        self.assertEqual(self.cart.items_count, initial_count)  # Same number of items
        self.assertEqual(self.cart.total_quantity, 5)  # Updated quantity
        self.assertGreater(float(self.cart.subtotal), initial_subtotal)  # Higher subtotal

    @override_settings(CART_CACHE_TIMEOUT=1)
    def test_custom_cache_timeout(self):
        """
        Test that custom cache timeout setting works.
        
        Verifies that the CART_CACHE_TIMEOUT setting can be customized
        and affects cache behavior.
        """
        from .utils import get_cache_timeout
        self.assertEqual(get_cache_timeout(), 1)