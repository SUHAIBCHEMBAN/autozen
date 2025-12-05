"""
Test script to verify the HyperlinkedIdentityField fix
"""

import os
import sys
import django
from django.test import RequestFactory

# Add the server directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from products.models import Product
from wishlist.models import Wishlist, WishlistItem
from wishlist.serializers import WishlistSerializer, WishlistItemSerializer


def test_serializers_with_context():
    """Test that serializers work correctly with context"""
    print("=== Testing HyperlinkedIdentityField Fix ===\n")
    
    # Create a mock request
    factory = RequestFactory(SERVER_NAME='localhost', SERVER_PORT='8000')
    request = factory.get('/')
    request.META['HTTP_HOST'] = 'localhost:8000'
    request.user = AnonymousUser()
    
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
    
    # Get some products
    products = Product.objects.filter(is_active=True)[:2]
    if not products:
        print("No products found. Please create some products first.")
        return
    
    product1, product2 = products
    
    print("1. Testing WishlistItemSerializer with context...")
    # Create a wishlist item
    wishlist, _ = Wishlist.objects.get_or_create(user=user)
    wishlist_item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product1
    )
    
    # Test serializer with context
    context = {'request': request}
    serializer = WishlistItemSerializer(wishlist_item, context=context)
    
    try:
        data = serializer.data
        print("   SUCCESS: WishlistItemSerializer serialized correctly with context")
        print(f"   Product name: {data['product']['name']}")
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    print("\n2. Testing WishlistSerializer with context...")
    # Add another item to make it more interesting
    WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product2
    )
    
    # Test wishlist serializer with context
    serializer = WishlistSerializer(wishlist, context=context)
    
    try:
        data = serializer.data
        print("   SUCCESS: WishlistSerializer serialized correctly with context")
        print(f"   Wishlist items count: {data['items_count']}")
        print(f"   Number of items serialized: {len(data['items'])}")
        if data['items']:
            print(f"   First item product: {data['items'][0]['product']['name']}")
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    print("\n=== Test Complete ===")


if __name__ == '__main__':
    test_serializers_with_context()