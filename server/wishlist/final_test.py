"""
Final test script to verify the zero-query implementation
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
from wishlist.views import WishlistViewSet
from wishlist.serializers import WishlistSerializer


def final_test():
    """Final test to verify zero-query implementation"""
    print("=== Final Test for Zero-Query Implementation ===\n")
    
    # Create a mock request
    factory = RequestFactory(SERVER_NAME='localhost', SERVER_PORT='8000')
    request = factory.get('/api/wishlist/wishlist/')
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
    
    # First access - this will populate caches
    print("1. First access (populates caches)...")
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
    
    if data['items']:
        first_item = data['items'][0]
        print(f"   First item product: {first_item['product']['name']}")
        print(f"   First item product brand: {first_item['product']['brand_name']}")
        print(f"   First item product model: {first_item['product']['model_name']}")
    
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
        print("🎉 The wishlist API now achieves 0 database queries for repeated requests!")
    elif second_access_queries < first_access_queries:
        print(f"\n✅ IMPROVEMENT: Reduced from {first_access_queries} to {second_access_queries} queries")
        print("   This is good progress toward zero queries!")
    else:
        print(f"\n⚠️  NO IMPROVEMENT: Still {second_access_queries} queries on second access")
        print("   Further optimization may be needed")
    
    print("\n=== Test Complete ===")


if __name__ == '__main__':
    final_test()