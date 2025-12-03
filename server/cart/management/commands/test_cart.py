"""
Management command to test the cart functionality
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product
from cart.models import Cart, CartItem
import random


class Command(BaseCommand):
    help = 'Test the cart functionality'

    def handle(self, *args, **options):
        self.stdout.write('Testing cart functionality...')

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
        products = Product.objects.filter(is_active=True)[:3]
        if not products:
            self.stdout.write(self.style.WARNING('No products found. Please create some products first.'))
            return

        # Create or get cart
        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            self.stdout.write(f"Created new cart for {user}")
        else:
            self.stdout.write(f"Using existing cart for {user}")

        # Add random products to cart
        for product in products:
            # Check if item already exists
            if not CartItem.objects.filter(cart=cart, product=product).exists():
                quantity = random.randint(1, 3)
                CartItem.objects.create(cart=cart, product=product, quantity=quantity)
                self.stdout.write(f"Added {quantity} x {product.name} to cart")
            else:
                self.stdout.write(f"{product.name} already in cart")

        # Display cart contents
        items = cart.items.all().select_related('product')
        self.stdout.write(f"\nCart contains {items.count()} items:")
        for item in items:
            self.stdout.write(f"  - {item.quantity} x {item.product.name} (SKU: {item.product.sku}) - ${item.total_price}")

        self.stdout.write(f"\nCart Summary:")
        self.stdout.write(f"  Items Count: {cart.items_count}")
        self.stdout.write(f"  Total Quantity: {cart.total_quantity}")
        self.stdout.write(f"  Subtotal: ${cart.subtotal}")

        self.stdout.write(
            self.style.SUCCESS('Cart test completed successfully')
        )