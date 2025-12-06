"""
Management command to bulk edit products in the database
"""

from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = 'Bulk edit products in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--set-featured',
            type=int,
            help='Set featured status for all products (0 for False, 1 for True)'
        )
        parser.add_argument(
            '--adjust-price',
            type=float,
            help='Adjust all product prices by a percentage (e.g., 10 for +10 percent, -5 for -5 percent)'
        )
        parser.add_argument(
            '--set-active',
            type=int,
            help='Set active status for all products (0 for False, 1 for True)'
        )
        parser.add_argument(
            '--increase-stock',
            type=int,
            help='Increase stock quantity for all products by this amount'
        )

    def handle(self, *args, **options):
        # Get all products
        products = Product.objects.all()
        count = products.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING('No products found in the database'))
            return

        self.stdout.write(f'Found {count} products to update...')
        
        # Track what changes we're making
        changes = []
        
        # Update featured status
        if options['set_featured'] is not None:
            featured_value = bool(options['set_featured'])
            products.update(is_featured=featured_value)
            status = "featured" if featured_value else "not featured"
            changes.append(f"Set all products as {status}")
            self.stdout.write(f"Updated featured status for {count} products")

        # Adjust prices
        if options['adjust_price'] is not None:
            percentage = options['adjust_price']
            updated_count = 0
            for product in products:
                old_price = float(product.price)
                new_price = old_price * (1 + percentage/100)
                product.price = round(new_price, 2)
                
                if product.compare_price:
                    old_compare = float(product.compare_price)
                    new_compare = old_compare * (1 + percentage/100)
                    product.compare_price = round(new_compare, 2)
                
                product.save()
                updated_count += 1
            
            changes.append(f"Adjusted prices by {percentage}%")
            self.stdout.write(f"Updated prices for {updated_count} products")

        # Update active status
        if options['set_active'] is not None:
            active_value = bool(options['set_active'])
            products.update(is_active=active_value)
            status = "active" if active_value else "inactive"
            changes.append(f"Set all products as {status}")
            self.stdout.write(f"Updated active status for {count} products")

        # Increase stock
        if options['increase_stock'] is not None:
            increase_amount = options['increase_stock']
            updated_count = 0
            for product in products:
                product.stock_quantity += increase_amount
                product.save()
                updated_count += 1
            
            changes.append(f"Increased stock by {increase_amount}")
            self.stdout.write(f"Updated stock for {updated_count} products")

        if not changes:
            self.stdout.write(self.style.WARNING('No updates specified. Use --help to see available options.'))
        else:
            change_list = "; ".join(changes)
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {count} products: {change_list}')
            )