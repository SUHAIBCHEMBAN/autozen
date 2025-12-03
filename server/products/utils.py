"""
Utility functions for the products app
"""

from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .models import Brand, VehicleModel, PartCategory, Product


def create_brand(name, description="", logo=None):
    """
    Create a new brand with proper slug generation
    """
    brand, created = Brand.objects.get_or_create(
        name=name,
        defaults={
            'description': description,
            'logo': logo,
            'slug': slugify(name)
        }
    )
    return brand, created


def create_vehicle_model(brand, name, description="", year_from=None, year_to=None, image=None):
    """
    Create a new vehicle model with proper slug generation
    """
    model, created = VehicleModel.objects.get_or_create(
        brand=brand,
        name=name,
        defaults={
            'description': description,
            'year_from': year_from,
            'year_to': year_to,
            'image': image,
            'slug': slugify(f"{brand.name}-{name}")
        }
    )
    return model, created


def create_part_category(name, parent=None, description="", image=None):
    """
    Create a new part category with proper slug generation
    """
    category, created = PartCategory.objects.get_or_create(
        name=name,
        parent=parent,
        defaults={
            'description': description,
            'image': image,
            'slug': slugify(name)
        }
    )
    return category, created


def create_product(brand, vehicle_model, part_category, name, sku, price, **kwargs):
    """
    Create a new product with validation
    """
    # Validate that the vehicle model belongs to the brand
    if vehicle_model.brand != brand:
        raise ValidationError("Vehicle model must belong to the specified brand")
    
    product, created = Product.objects.get_or_create(
        sku=sku,
        defaults={
            'brand': brand,
            'vehicle_model': vehicle_model,
            'part_category': part_category,
            'name': name,
            'price': price,
            'slug': slugify(name),
            **kwargs
        }
    )
    return product, created


def get_category_hierarchy(category):
    """
    Get the full hierarchy path for a category
    Returns a list from root to current category
    """
    hierarchy = []
    current = category
    while current:
        hierarchy.insert(0, current)
        current = current.parent
    return hierarchy


def get_products_by_hierarchy(brand_name=None, model_name=None, category_name=None):
    """
    Get products filtered by brand, model, and/or category
    """
    products = Product.objects.filter(is_active=True)
    
    if brand_name:
        products = products.filter(brand__name__iexact=brand_name)
    
    if model_name:
        products = products.filter(vehicle_model__name__iexact=model_name)
    
    if category_name:
        products = products.filter(part_category__name__iexact=category_name)
    
    return products.select_related('brand', 'vehicle_model', 'part_category')


def bulk_create_products(product_data_list):
    """
    Bulk create products from a list of dictionaries
    Each dict should contain the required fields for product creation
    """
    products = []
    for data in product_data_list:
        try:
            brand = data.pop('brand')
            vehicle_model = data.pop('vehicle_model')
            part_category = data.pop('part_category')
            
            product, created = create_product(
                brand=brand,
                vehicle_model=vehicle_model,
                part_category=part_category,
                **data
            )
            if created:
                products.append(product)
        except Exception as e:
            print(f"Error creating product {data.get('name', 'Unknown')}: {e}")
    
    return products


def get_navigation_tree():
    """
    Generate a navigation tree for brands, models, and categories
    Useful for frontend navigation menus
    """
    # Get all active brands with their models
    brands = Brand.objects.filter(is_active=True).prefetch_related('models')
    
    # Get top-level categories with subcategories
    categories = PartCategory.objects.filter(
        is_active=True, 
        parent=None
    ).prefetch_related('subcategories')
    
    navigation_data = {
        'brands': [],
        'categories': []
    }
    
    # Build brand hierarchy
    for brand in brands:
        brand_data = {
            'id': brand.id,
            'name': brand.name,
            'slug': brand.slug,
            'models': [
                {
                    'id': model.id,
                    'name': model.name,
                    'slug': model.slug
                }
                for model in brand.models.filter(is_active=True)
            ]
        }
        navigation_data['brands'].append(brand_data)
    
    # Build category hierarchy
    for category in categories:
        category_data = {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'subcategories': [
                {
                    'id': subcat.id,
                    'name': subcat.name,
                    'slug': subcat.slug
                }
                for subcat in category.subcategories.filter(is_active=True)
            ]
        }
        navigation_data['categories'].append(category_data)
    
    return navigation_data