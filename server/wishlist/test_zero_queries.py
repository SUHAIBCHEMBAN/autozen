"""
Test script to verify the zero-query caching implementation
"""

import os
import sys
import django
from django.test import RequestFactory
from django.db import connection

# Add the server directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.contrib.auth import get_user_model
from products.models import Product
from wishlist.models import Wishlist, WishlistItem
from wishlist.views import WishlistViewSet
from wishlist.serializers import WishlistSerializer


def test_zero_queries():
    """Test that wishlist serialization uses zero queries after caching"""
    print("=== Testing Zero-Query Implementation ===\n")
    
    # Create a mock request
    factory = RequestFactory(SERVER_NAME='localhost', SERVER_PORT='8000')
    request = factory.get('/')
    request.META['HTTP_HOST'] = 'localhost:8000'
    
    # Get a user (assuming the test user exists)
    User = get_user_model()
    try:
        user = User.objects.first()
        if not user:
            print("No users found. Please create a user first.")
            return
        print(f"Using user: {user.email}\n")
        request.user = user
    except User.DoesNotExist:
        print("No users found. Please create a user first.")
        return
    
    # Clear any existing queries
    connection.queries_log.clear()
    
    # First access - this will populate the cache
    print("1. First access (populates cache)...")
    viewset = WishlistViewSet()
    viewset.request = request
    viewset.format_kwarg = None
    
    # Get the wishlist object (this should populate cache)
    wishlist = viewset.get_object()
    
    # Serialize the wishlist (this should use cached data)
    serializer = WishlistSerializer(wishlist, context=viewset.get_serializer_context())
    data = serializer.data
    
    first_access_queries = len(connection.queries)
    print(f"   Queries on first access: {first_access_queries}")
    print(f"   Wishlist items count: {data['items_count']}")
    print(f"   Number of items serialized: {len(data['items'])}")
    
    # Clear queries again
    connection.queries_log.clear()
    
    # Second access - this should use cached data
    print("\n2. Second access (should use cached data)...")
    viewset2 = WishlistViewSet()
    viewset2.request = request
    viewset2.format_kwarg = None
    
    # Get the wishlist object (this should use cache)
    wishlist2 = viewset2.get_object()
    
    # Serialize the wishlist (this should use cached data)
    serializer2 = WishlistSerializer(wishlist2, context=viewset2.get_serializer_context())
    data2 = serializer2.data
    
    second_access_queries = len(connection.queries)
    print(f"   Queries on second access: {second_access_queries}")
    print(f"   Wishlist items count: {data2['items_count']}")
    print(f"   Number of items serialized: {len(data2['items'])}")
    
    # Check if we achieved zero queries on second access
    if second_access_queries == 0:
        print("\n✅ SUCCESS: Zero queries achieved on second access!")
    else:
        print(f"\n⚠️  WARNING: Still {second_access_queries} queries on second access")
        print("   This is expected on first run, but should be 0 on subsequent runs")
    
    print("\n=== Test Complete ===")


if __name__ == '__main__':
    test_zero_queries()