#!/usr/bin/env python3
"""
Simple test script to verify cart caching functionality
"""
import os
import sys
import django
from django.conf import settings

# Add the server directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

# Setup Django
django.setup()

from django.contrib.auth import get_user_model
from django.core.cache import cache
from products.models import Product, Brand, VehicleModel, PartCategory
from cart.models import Cart, CartItem
from cart.utils import add_to_cart, get_cart_summary

User = get_user_model()

def test_cart_caching():
    print("Testing cart caching functionality...")
    
    # Clear cache first
    cache.clear()
    print("Cache cleared")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email='testcache@example.com',
        defaults={
            'phone_number': '+1234567890'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("Created test user")
    
    # Get existing brand, model, and category
    brand = Brand.objects.first()
    model = VehicleModel.objects.first()
    category = PartCategory.objects.first()
    
    if not brand or not model or not category:
        print("Error: Missing required product relationships")
        return
    
    print(f"Using brand: {brand.name}, model: {model.name}, category: {category.name}")
    
    # Create test product
    product, created = Product.objects.get_or_create(
        sku='CACHE-TEST-001',
        defaults={
            'name': 'Cache Test Product',
            'description': 'Product for testing cache functionality',
            'price': 29.99,
            'stock_quantity': 100,
            'brand': brand,
            'vehicle_model': model,
            'part_category': category
        }
    )
    if created:
        print("Created test product")
    
    # Create second test product
    product2, created = Product.objects.get_or_create(
        sku='CACHE-TEST-002',
        defaults={
            'name': 'Cache Test Product 2',
            'description': 'Second product for testing cache functionality',
            'price': 49.99,
            'stock_quantity': 50,
            'brand': brand,
            'vehicle_model': model,
            'part_category': category
        }
    )
    if created:
        print("Created second test product")
    
    # Get or create cart
    cart, created = Cart.objects.get_or_create(user=user)
    if created:
        print("Created test cart")
    
    # Clear existing items
    cart.clear()
    print("Cleared existing cart items")
    
    # Add item to cart
    result = add_to_cart(user, product.id, 2)
    print(f"Add to cart result: {result}")
    
    # Get cart summary (should populate cache)
    summary1 = get_cart_summary(user)
    print(f"First cart summary: {summary1}")
    
    # Get cart summary again (should use cache)
    summary2 = get_cart_summary(user)
    print(f"Second cart summary: {summary2}")
    
    # Check if summaries are the same
    if summary1 == summary2:
        print("✓ Cache test passed - summaries match")
    else:
        print("✗ Cache test failed - summaries don't match")
    
    # Add another item to invalidate cache
    result = add_to_cart(user, product2.id, 1)
    print(f"Add second product result: {result}")
    
    # Get updated cart summary
    summary3 = get_cart_summary(user)
    print(f"Third cart summary: {summary3}")
    
    # Check if summary was updated
    if summary3['items_count'] > summary1['items_count']:
        print("✓ Cache invalidation test passed - item count increased")
    else:
        print("✗ Cache invalidation test failed - item count not updated")
    
    print("\nTest completed!")

if __name__ == '__main__':
    test_cart_caching()