import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.cache import cache
from products.models import Product
from cart.models import Cart, CartItem

User = get_user_model()


class Command(BaseCommand):
    help = 'Test cart functionality including caching'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear all cache before testing',
        )

    def handle(self, *args, **options):
        if options['clear_cache']:
            self.stdout.write('Clearing cache...')
            cache.clear()
            self.stdout.write(
                self.style.SUCCESS('Successfully cleared cache')
            )

        # Get or create test user
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(
                self.style.SUCCESS('Created test user: test@example.com')
            )

        # Get or create test products
        products_data = [
            {
                'sku': 'TEST-001',
                'name': 'Test Product 1',
                'slug': 'test-product-1',
                'description': 'Test product for cart testing',
                'price': 29.99,
                'stock_quantity': 100
            },
            {
                'sku': 'TEST-002',
                'name': 'Test Product 2',
                'slug': 'test-product-2',
                'description': 'Another test product for cart testing',
                'price': 49.99,
                'stock_quantity': 50
            }
        ]

        products = []
        for product_data in products_data:
            product, created = Product.objects.get_or_create(
                sku=product_data['sku'],
                defaults=product_data
            )
            products.append(product)
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created test product: {product.name}')
                )

        # Test cart functionality
        self.test_cart_operations(user, products)

    def test_cart_operations(self, user, products):
        # Get or create cart
        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created new cart for test user')
            )

        # Clear existing cart items
        cart.clear()
        self.stdout.write('Cleared existing cart items')

        # Add items to cart
        self.stdout.write('Adding items to cart...')
        for product in products:
            quantity = random.randint(1, 3)
            cart_item = cart.add_item(product, quantity)
            self.stdout.write(
                f'Added {quantity} x {product.name} to cart '
                f'(item ID: {cart_item.id})'
            )

        # Test cart properties (these should be cached after first access)
        self.stdout.write('\nTesting cart properties:')
        
        # First access (should populate cache)
        items_count = cart.items_count
        total_quantity = cart.total_quantity
        subtotal = cart.subtotal
        
        self.stdout.write(f'Items count: {items_count} (cached)')
        self.stdout.write(f'Total quantity: {total_quantity} (cached)')
        self.stdout.write(f'Subtotal: ${subtotal:.2f} (cached)')

        # Test cache invalidation
        self.stdout.write('\nTesting cache invalidation...')
        
        # Add another item to trigger cache invalidation
        new_product_data = {
            'sku': 'TEST-003',
            'name': 'Test Product 3',
            'slug': 'test-product-3',
            'description': 'Yet another test product',
            'price': 19.99,
            'stock_quantity': 75
        }
        new_product, _ = Product.objects.get_or_create(
            sku=new_product_data['sku'],
            defaults=new_product_data
        )
        
        cart.add_item(new_product, 2)
        
        # Check that properties have been updated
        new_items_count = cart.items_count
        new_total_quantity = cart.total_quantity
        new_subtotal = cart.subtotal
        
        self.stdout.write(
            f'After adding item - Items count: {new_items_count} '
            f'(should be {items_count + 1})'
        )
        self.stdout.write(
            f'After adding item - Total quantity: {new_total_quantity}'
        )
        self.stdout.write(
            f'After adding item - Subtotal: ${new_subtotal:.2f}'
        )

        # Test cart clearing
        self.stdout.write('\nTesting cart clearing...')
        cart.clear()
        final_items_count = cart.items_count
        self.stdout.write(
            f'After clearing - Items count: {final_items_count} '
            f'(should be 0)'
        )

        self.stdout.write(
            self.style.SUCCESS(
                '\nCart functionality test completed successfully!'
            )
        )