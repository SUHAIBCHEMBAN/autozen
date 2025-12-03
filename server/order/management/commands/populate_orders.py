"""
Management command to populate the database with sample orders
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product
from order.models import Order, OrderItem, OrderStatus, PaymentMethod
import random
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate the database with sample orders'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate sample orders...')

        # Get user model
        User = get_user_model()
        
        # Get some users
        users = User.objects.all()[:3]  # Limit to first 3 users
        if not users:
            self.stdout.write(self.style.WARNING('No users found. Please create some users first.'))
            return

        # Get some products
        products = Product.objects.filter(is_active=True)[:10]
        if not products:
            self.stdout.write(self.style.WARNING('No products found. Please create some products first.'))
            return

        # Create sample orders
        sample_orders = []
        for i in range(5):  # Create 5 sample orders
            user = random.choice(users)
            
            # Random order data
            first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David']
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones']
            
            order_data = {
                'user': user,
                'first_name': random.choice(first_names),
                'last_name': random.choice(last_names),
                'email': user.email or f"{random.choice(first_names).lower()}.{random.choice(last_names).lower()}@example.com",
                'phone_number': f"+1{random.randint(1000000000, 9999999999)}",
                'billing_address_line1': f"{random.randint(100, 999)} Main St",
                'billing_address_line2': f"Apt {random.randint(1, 100)}" if random.choice([True, False]) else "",
                'billing_city': 'New York',
                'billing_state': 'NY',
                'billing_postal_code': f"1000{random.randint(1, 99)}",
                'billing_country': 'USA',
                'shipping_address_line1': f"{random.randint(100, 999)} Oak Ave",
                'shipping_address_line2': f"Apt {random.randint(1, 100)}" if random.choice([True, False]) else "",
                'shipping_city': 'Los Angeles',
                'shipping_state': 'CA',
                'shipping_postal_code': f"9000{random.randint(1, 99)}",
                'shipping_country': 'USA',
                'payment_method': random.choice([PaymentMethod.CREDIT_CARD, PaymentMethod.PAYPAL, PaymentMethod.CASH_ON_DELIVERY]),
                'payment_status': random.choice([True, False]),
                'subtotal': Decimal('0'),
                'tax_amount': Decimal('0'),
                'shipping_cost': Decimal('10.00'),
                'discount_amount': Decimal('0'),
                'total_amount': Decimal('0'),
                'notes': 'Sample order for testing purposes',
                'internal_notes': 'Created by populate_orders management command',
            }

            # Create order
            order = Order.objects.create(**order_data)
            
            # Add random items to order
            num_items = random.randint(1, 3)
            selected_products = random.sample(list(products), min(num_items, len(products)))
            
            subtotal = Decimal('0')
            for product in selected_products:
                quantity = random.randint(1, 3)
                item_total = product.price * quantity
                subtotal += item_total
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    product_sku=product.sku,
                    product_price=product.price,
                    quantity=quantity,
                    total_price=item_total
                )
            
            # Update order totals
            order.subtotal = subtotal
            order.tax_amount = subtotal * Decimal('0.08')  # 8% tax
            order.total_amount = subtotal + order.tax_amount + order.shipping_cost
            order.save()
            
            # Randomly set order status
            statuses = list(OrderStatus.values)
            order.status = random.choice(statuses)
            order.save()
            
            sample_orders.append(order)
            self.stdout.write(f"Created order: {order.order_number}")

        self.stdout.write(
            self.style.SUCCESS(f'Successfully populated {len(sample_orders)} sample orders')
        )