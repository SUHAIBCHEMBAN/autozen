"""
Demonstration script for wishlist caching functionality
"""

import os
import sys
import django
from django.conf import settings

# Add the server directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.core.cache import cache
from products.models import Product
from wishlist.models import Wishlist, WishlistItem
from wishlist.cache_utils import (
    get_cached_wishlist,
    get_cached_wishlist_items,
    get_cached_wishlist_count,
    add_to_wishlist_with_cache,
    remove_from_wishlist_with_cache,
    is_product_in_wishlist_cached
)


def demonstrate_caching():
    """Demonstrate the caching functionality"""
    print("=== Wishlist Caching Demonstration ===\n")
    
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
    
    # Get some products
    products = Product.objects.filter(is_active=True)[:3]
    if not products:
        print("No products found. Please create some products first.")
        return
    
    product1, product2, product3 = products
    
    print("1. Testing wishlist creation/retrieval with caching...")
    # Test getting cached wishlist (creates if doesn't exist)
    wishlist = get_cached_wishlist(user.id)
    print(f"   Retrieved wishlist ID: {wishlist.id}")
    
    # Check cache
    cache_key = f'wishlist_user_{user.id}'
    cached_wishlist = cache.get(cache_key)
    print(f"   Cache hit: {cached_wishlist is not None}\n")
    
    print("2. Testing adding items to wishlist with caching...")
    # Add items using cached function
    result1 = add_to_wishlist_with_cache(user, product1.id)
    print(f"   Added {product1.name}: {result1['message']}")
    
    result2 = add_to_wishlist_with_cache(user, product2.id)
    print(f"   Added {product2.name}: {result2['message']}")
    
    # Try adding duplicate
    result3 = add_to_wishlist_with_cache(user, product1.id)
    print(f"   Added duplicate {product1.name}: {result3['message']}\n")
    
    print("3. Testing cached wishlist items retrieval...")
    # Get cached items
    items = get_cached_wishlist_items(user.id)
    print(f"   Retrieved {len(items)} items from cache")
    for item in items:
        print(f"     - {item.product.name}")
    
    print("\n4. Testing cached wishlist count...")
    count = get_cached_wishlist_count(user.id)
    print(f"   Wishlist count from cache: {count}")
    
    print("\n5. Testing product-in-wishlist check with caching...")
    # Check if products are in wishlist
    in_wishlist1 = is_product_in_wishlist_cached(user.id, product1.id)
    in_wishlist2 = is_product_in_wishlist_cached(user.id, product3.id)
    print(f"   {product1.name} in wishlist: {in_wishlist1}")
    print(f"   {product3.name} in wishlist: {in_wishlist2}")
    
    print("\n6. Testing removal with caching...")
    # Remove an item
    result = remove_from_wishlist_with_cache(user, product1.id)
    print(f"   Removed {product1.name}: {result['message']}")
    
    # Check cache invalidation
    items_after_removal = get_cached_wishlist_items(user.id)
    print(f"   Items after removal: {len(items_after_removal)}")
    
    print("\n=== Demonstration Complete ===")


if __name__ == '__main__':
    demonstrate_caching()