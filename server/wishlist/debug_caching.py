"""
Debug script to check if caching is working properly
"""

import os
import sys
import django
from django.db import connection

# Add the server directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth import get_user_model
from wishlist.cache_utils import get_cached_wishlist_items


def debug_caching():
    """Debug the caching implementation"""
    print("=== Debugging Caching Implementation ===\n")
    
    # Get a user (assuming the test user exists)
    User = get_user_model()
    try:
        user = User.objects.first()
        if not user:
            print("No users found. Please create a user first.")
            return
        print(f"Using user: {user.email}\n")
    except User.DoesNotExist:
        print("No users found. Please create a user first.")
        return
    
    # Clear any existing queries
    connection.queries_log.clear()
    
    # First access - this will populate the cache
    print("1. First access (populates cache)...")
    items = get_cached_wishlist_items(user.id)
    first_access_queries = len(connection.queries)
    print(f"   Queries on first access: {first_access_queries}")
    print(f"   Number of items retrieved: {len(items)}")
    
    # Show some details about the items
    if items:
        first_item = items[0]
        print(f"   First item product: {first_item.product.name}")
        print(f"   First item product brand: {first_item.product.brand.name}")
        print(f"   First item product model: {first_item.product.vehicle_model.name}")
    
    # Clear queries again
    connection.queries_log.clear()
    
    # Second access - this should use cached data
    print("\n2. Second access (should use cached data)...")
    items2 = get_cached_wishlist_items(user.id)
    second_access_queries = len(connection.queries)
    print(f"   Queries on second access: {second_access_queries}")
    print(f"   Number of items retrieved: {len(items2)}")
    
    # Check if we achieved zero queries on second access
    if second_access_queries == 0:
        print("\n✅ SUCCESS: Zero queries achieved on second access!")
    else:
        print(f"\n⚠️  WARNING: Still {second_access_queries} queries on second access")
        print("   This means caching is not working properly")
    
    print("\n=== Debug Complete ===")


if __name__ == '__main__':
    debug_caching()