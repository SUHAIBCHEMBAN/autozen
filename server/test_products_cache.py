#!/usr/bin/env python3
"""
Simple test script to verify products caching functionality
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

from django.core.cache import cache
from products.models import Brand, VehicleModel, PartCategory
from products.cache_utils import (
    get_active_brands, get_active_categories, get_active_models,
    get_featured_products, get_navigation_tree
)


def test_products_caching():
    print("Testing products caching functionality...")
    
    # Clear cache first
    cache.clear()
    print("Cache cleared")
    
    # Test getting active brands (should populate cache)
    brands1 = list(get_active_brands())
    print(f"First brands query: {len(brands1)} brands")
    
    # Test getting active brands again (should use cache)
    brands2 = list(get_active_brands())
    print(f"Second brands query: {len(brands2)} brands")
    
    # Check if results are the same
    if len(brands1) == len(brands2):
        print("✓ Brands cache test passed")
    else:
        print("✗ Brands cache test failed")
    
    # Test getting active categories
    categories1 = list(get_active_categories())
    print(f"First categories query: {len(categories1)} categories")
    
    categories2 = list(get_active_categories())
    print(f"Second categories query: {len(categories2)} categories")
    
    if len(categories1) == len(categories2):
        print("✓ Categories cache test passed")
    else:
        print("✗ Categories cache test failed")
    
    # Test getting navigation tree
    nav1 = get_navigation_tree()
    print(f"First navigation tree query: {len(nav1.get('brands', []))} brands, {len(nav1.get('categories', []))} categories")
    
    nav2 = get_navigation_tree()
    print(f"Second navigation tree query: {len(nav2.get('brands', []))} brands, {len(nav2.get('categories', []))} categories")
    
    if nav1 == nav2:
        print("✓ Navigation tree cache test passed")
    else:
        print("✗ Navigation tree cache test failed")
    
    print("Products caching test completed!")


if __name__ == "__main__":
    test_products_caching()