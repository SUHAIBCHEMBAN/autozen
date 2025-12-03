"""
Management command to populate the database with sample automotive products data
"""

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from products.models import Brand, VehicleModel, PartCategory, Product
from products.utils import create_brand, create_vehicle_model, create_part_category, create_product


class Command(BaseCommand):
    help = 'Populate the database with sample automotive products data'

    def handle(self, *args, **options):
        self.stdout.write('Starting to populate sample data...')

        # Create brands
        toyota, _ = create_brand("Toyota", "Japanese automobile manufacturer")
        honda, _ = create_brand("Honda", "Japanese public multinational conglomerate corporation")
        ford, _ = create_brand("Ford", "American multinational automaker")

        # Create vehicle models
        innova, _ = create_vehicle_model(toyota, "Innova Crysta", "MPV model by Toyota", 2015, 2023)
        camry, _ = create_vehicle_model(toyota, "Camry", "Mid-size car", 2012, 2023)
        civic, _ = create_vehicle_model(honda, "Civic", "Compact car", 2015, 2023)
        accord, _ = create_vehicle_model(honda, "Accord", "Mid-size car", 2013, 2023)
        f150, _ = create_vehicle_model(ford, "F-150", "Full-size pickup truck", 2015, 2023)
        mustang, _ = create_vehicle_model(ford, "Mustang", "Sports car", 2015, 2023)

        # Create part categories (hierarchical)
        # Top level categories
        engine, _ = create_part_category("Engine")
        brakes, _ = create_part_category("Brakes")
        steering, _ = create_part_category("Steering")
        suspension, _ = create_part_category("Suspension")
        electrical, _ = create_part_category("Electrical")
        body, _ = create_part_category("Body & Frame")

        # Subcategories
        engine_parts, _ = create_part_category("Engine Parts", parent=engine)
        brake_pads, _ = create_part_category("Brake Pads", parent=brakes)
        steering_wheel, _ = create_part_category("Steering Wheel", parent=steering)
        shock_absorber, _ = create_part_category("Shock Absorber", parent=suspension)
        battery, _ = create_part_category("Battery", parent=electrical)
        bumper, _ = create_part_category("Bumper", parent=body)

        # Create sample products
        sample_products = [
            # Steering wheels for Innova Crysta
            {
                'brand': toyota,
                'vehicle_model': innova,
                'part_category': steering_wheel,
                'name': "Innova Crysta Leather Steering Wheel",
                'sku': "TOY-INN-SW-001",
                'price': 85.99,
                'compare_price': 120.00,
                'description': "Premium leather steering wheel for Toyota Innova Crysta with comfortable grip and elegant design.",
                'oem_number': "44410-60J00",
                'manufacturer_part_number': "LUXE-SW-IC-001",
                'stock_quantity': 15
            },
            {
                'brand': toyota,
                'vehicle_model': innova,
                'part_category': steering_wheel,
                'name': "Innova Crysta Wooden Finish Steering Wheel",
                'sku': "TOY-INN-SW-002",
                'price': 95.50,
                'compare_price': 135.00,
                'description': "Wooden finish steering wheel for Toyota Innova Crysta with ergonomic design and premium materials.",
                'oem_number': "44410-60J01",
                'manufacturer_part_number': "WOOD-SW-IC-001",
                'stock_quantity': 8
            },
            # Brake pads for various models
            {
                'brand': toyota,
                'vehicle_model': innova,
                'part_category': brake_pads,
                'name': "Front Brake Pads for Innova Crysta",
                'sku': "TOY-INN-BP-FR-001",
                'price': 45.75,
                'compare_price': 65.00,
                'description': "High-quality front brake pads specifically designed for Toyota Innova Crysta.",
                'oem_number': "43542-60J00",
                'manufacturer_part_number': "BP-FR-IC-001",
                'stock_quantity': 25
            },
            {
                'brand': honda,
                'vehicle_model': civic,
                'part_category': brake_pads,
                'name': "Rear Brake Pads for Honda Civic",
                'sku': "HON-CIV-BP-RR-001",
                'price': 38.99,
                'compare_price': 55.00,
                'description': "Durable rear brake pads for Honda Civic with excellent stopping power.",
                'oem_number': "43543-TBA-003",
                'manufacturer_part_number': "BP-RR-HC-001",
                'stock_quantity': 30
            },
            # Engine parts
            {
                'brand': toyota,
                'vehicle_model': camry,
                'part_category': engine_parts,
                'name': "Air Filter for Toyota Camry",
                'sku': "TOY-CAM-AF-001",
                'price': 18.50,
                'compare_price': 25.00,
                'description': "High-flow air filter for Toyota Camry engines to improve performance and fuel efficiency.",
                'oem_number': "17801-60J00",
                'manufacturer_part_number': "AF-CAM-001",
                'stock_quantity': 40
            },
            # Suspension parts
            {
                'brand': ford,
                'vehicle_model': f150,
                'part_category': shock_absorber,
                'name': "Front Shock Absorber for Ford F-150",
                'sku': "FOR-F15-SA-FR-001",
                'price': 125.99,
                'compare_price': 180.00,
                'description': "Heavy-duty front shock absorber for Ford F-150 trucks, perfect for off-road use.",
                'oem_number': "18210-00J00",
                'manufacturer_part_number': "SA-FR-F15-001",
                'stock_quantity': 12
            },
            # Electrical parts
            {
                'brand': honda,
                'vehicle_model': accord,
                'part_category': battery,
                'name': "12V Battery for Honda Accord",
                'sku': "HON-ACC-BAT-001",
                'price': 145.00,
                'compare_price': 195.00,
                'description': "Maintenance-free 12V battery for Honda Accord with 5-year warranty.",
                'oem_number': "01251-TBA-003",
                'manufacturer_part_number': "BAT-HAC-001",
                'stock_quantity': 20
            },
            # Body parts
            {
                'brand': ford,
                'vehicle_model': mustang,
                'part_category': bumper,
                'name': "Front Bumper for Ford Mustang",
                'sku': "FOR-MUS-BUM-FR-001",
                'price': 299.99,
                'compare_price': 425.00,
                'description': "Carbon fiber front bumper for Ford Mustang with integrated fog lights.",
                'oem_number': "17401-00J00",
                'manufacturer_part_number': "BUM-FR-MUS-001",
                'stock_quantity': 5
            }
        ]

        # Create products
        created_count = 0
        for product_data in sample_products:
            try:
                product, created = create_product(**product_data)
                if created:
                    created_count += 1
                    self.stdout.write(f"Created product: {product.name}")
                else:
                    self.stdout.write(f"Product already exists: {product.name}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating product {product_data['name']}: {e}"))

        self.stdout.write(
            self.style.SUCCESS(f'Successfully populated {created_count} sample products')
        )