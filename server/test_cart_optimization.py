#!/usr/bin/env python3
"""
Test script to verify cart optimization and caching functionality
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
from django.db import connection
from products.models import Product, Brand, VehicleModel, PartCategory
from cart.models import Cart, CartItem
from cart.utils import add_to_cart, get_cart_summary

User = get_user_model()

def reset_queries():
    """Reset the query log"""
    connection.queries_log.clear()

def get_query_count():
    """Get the number of queries executed"""
    return len(connection.queries)

def test_cart_performance():
    print("Testing cart performance optimizations...")
    
    # Clear cache first
    cache.clear()
    print("Cache cleared")
    
    # Reset query counter
    reset_queries()
    
    # Create test user
    user, created = User.objects.get_or_create(
        email='testperf@example.com',
        defaults={
            'phone_number': '+1234567891'
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
    
    # Create test products
    products_data = [
        {
            'sku': 'PERF-TEST-001',
            'name': 'Performance Test Product 1',
            'description': 'First product for testing performance',
            'price': 29.99,
            'stock_quantity': 100,
        },
        {
            'sku': 'PERF-TEST-002',
            'name': 'Performance Test Product 2',
            'description': 'Second product for testing performance',
            'price': 49.99,
            'stock_quantity': 50,
        },
        {
            'sku': 'PERF-TEST-003',
            'name': 'Performance Test Product 3',
            'description': 'Third product for testing performance',
            'price': 19.99,
            'stock_quantity': 75,
        }
    ]
    
    products = []
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            sku=product_data['sku'],
            defaults={
                **product_data,
                'brand': brand,
                'vehicle_model': model,
                'part_category': category
            }
        )
        if created:
            print(f"Created test product: {product.name}")
        products.append(product)
    
    # Get or create cart
    reset_queries()
    cart, created = Cart.objects.get_or_create(user=user)
    initial_queries = get_query_count()
    print(f"Cart creation queries: {initial_queries}")
    
    if created:
        print("Created test cart")
    
    # Clear existing items
    cart.clear()
    print("Cleared existing cart items")
    
    # Add items to cart and measure queries
    reset_queries()
    for i, product in enumerate(products):
        result = add_to_cart(user, product.id, i + 1)
        print(f"Add product {i+1} result: {result['message']}")
    
    add_queries = get_query_count()
    print(f"Queries for adding {len(products)} items: {add_queries}")
    
    # Test cart summary (first access - should populate cache)
    reset_queries()
    summary1 = get_cart_summary(user)
    summary1_queries = get_query_count()
    print(f"First cart summary: {summary1}")
    print(f"Queries for first summary: {summary1_queries}")
    
    # Test cart summary (second access - should use cache)
    reset_queries()
    summary2 = get_cart_summary(user)
    summary2_queries = get_query_count()
    print(f"Second cart summary: {summary2}")
    print(f"Queries for second summary: {summary2_queries}")
    
    # Check if caching reduced queries
    if summary2_queries < summary1_queries:
        print("✓ Caching reduced queries for cart summary")
    elif summary2_queries == summary1_queries == 0:
        print("✓ No queries needed for cached cart summary")
    else:
        print("⚠ Caching did not reduce queries for cart summary")
    
    # Test cart properties
    reset_queries()
    items_count = cart.items_count
    total_quantity = cart.total_quantity
    subtotal = float(cart.subtotal)
    properties_queries = get_query_count()
    print(f"Cart properties - Items: {items_count}, Quantity: {total_quantity}, Subtotal: ${subtotal}")
    print(f"Queries for cart properties: {properties_queries}")
    
    # Test cart properties again (should use cache)
    reset_queries()
    items_count2 = cart.items_count
    total_quantity2 = cart.total_quantity
    subtotal2 = float(cart.subtotal)
    properties2_queries = get_query_count()
    print(f"Cart properties (cached) - Items: {items_count2}, Quantity: {total_quantity2}, Subtotal: ${subtotal2}")
    print(f"Queries for cached cart properties: {properties2_queries}")
    
    # Check if caching reduced queries for properties
    if properties2_queries < properties_queries:
        print("✓ Caching reduced queries for cart properties")
    elif properties2_queries == properties_queries == 0:
        print("✓ No queries needed for cached cart properties")
    else:
        print("⚠ Caching did not reduce queries for cart properties")
    
    print("\nTest completed!")

if __name__ == '__main__':
    test_cart_performance()