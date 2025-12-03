"""
Management command to test the wishlist functionality
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product
from wishlist.models import Wishlist, WishlistItem
import random


class Command(BaseCommand):
    help = 'Test the wishlist functionality'

    def handle(self, *args, **options):
        self.stdout.write('Testing wishlist functionality...')

        # Get user model
        User = get_user_model()
        
        # Get a user
        try:
            user = User.objects.first()
            if not user:
                self.stdout.write(self.style.WARNING('No users found. Please create a user first.'))
                return
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING('No users found. Please create a user first.'))
            return

        # Get some products
        products = Product.objects.filter(is_active=True)[:5]
        if not products:
            self.stdout.write(self.style.WARNING('No products found. Please create some products first.'))
            return

        # Create or get wishlist
        wishlist, created = Wishlist.objects.get_or_create(user=user)
        if created:
            self.stdout.write(f"Created new wishlist for {user}")
        else:
            self.stdout.write(f"Using existing wishlist for {user}")

        # Add random products to wishlist
        for product in products:
            # Check if item already exists
            if not WishlistItem.objects.filter(wishlist=wishlist, product=product).exists():
                WishlistItem.objects.create(wishlist=wishlist, product=product)
                self.stdout.write(f"Added {product.name} to wishlist")
            else:
                self.stdout.write(f"{product.name} already in wishlist")

        # Display wishlist contents
        items = wishlist.items.all().select_related('product')
        self.stdout.write(f"\nWishlist contains {items.count()} items:")
        for item in items:
            self.stdout.write(f"  - {item.product.name} (SKU: {item.product.sku})")

        self.stdout.write(
            self.style.SUCCESS('Wishlist test completed successfully')
        )