# Products App Documentation

This Django app provides a complete backend solution for an automotive spare parts and accessories e-commerce platform with a hierarchical product structure.

## Overview

The products app implements a four-level hierarchy for organizing automotive parts:
1. **Brand** (e.g., Toyota, Honda, Ford)
2. **Vehicle Model** (e.g., Innova Crysta, Civic, F-150)
3. **Part Category** (e.g., Steering, Brakes, Engine) with support for subcategories
4. **Product** (e.g., specific steering wheels, brake pads, etc.)

## Key Features

### Hierarchical Structure
- Clear separation between brand, model, category, and product entities
- Proper foreign key relationships ensuring data integrity
- Support for hierarchical categories with parent-child relationships
- Validation to ensure vehicle models belong to the correct brand

### Rich Product Information
- Comprehensive product attributes including pricing, inventory, and automotive-specific fields
- Support for OEM numbers, manufacturer part numbers, and compatibility notes
- Physical attributes like weight and dimensions
- SEO-friendly fields for improved search visibility

### Advanced Functionality
- Slug-based URLs for SEO-friendly linking
- Automatic slug generation from names
- Discount calculation and display
- Stock status management with configurable thresholds
- Featured product designation

### Developer Experience
- Django REST Framework integration with viewsets and serializers
- Comprehensive admin interface with custom displays and filters
- Utility functions for common operations
- Management command for populating sample data
- Detailed API documentation

## Models

### Brand
Represents a vehicle manufacturer (Toyota, Honda, etc.)

Key fields:
- `name`: Unique brand name
- `slug`: URL-friendly identifier
- `description`: Brand description
- `logo`: Brand logo image
- `is_active`: Active status

### VehicleModel
Represents a specific vehicle model (Innova Crysta, Civic, etc.)

Key fields:
- `brand`: Foreign key to Brand
- `name`: Model name
- `slug`: URL-friendly identifier
- `year_from`, `year_to`: Manufacturing years
- `is_active`: Active status

### PartCategory
Represents a part type/category with hierarchical support

Key fields:
- `name`: Category name
- `slug`: URL-friendly identifier
- `parent`: Self-referential foreign key for hierarchy
- `is_active`: Active status

### Product
Represents a specific automotive part/product

Key fields:
- `brand`, `vehicle_model`, `part_category`: Hierarchical relationships
- `name`, `sku`: Product identification
- `price`, `compare_price`: Pricing information
- `stock_quantity`: Inventory management
- `featured_image`: Main product image
- `oem_number`, `manufacturer_part_number`: Automotive identifiers
- `is_active`, `is_featured`: Status flags

## API Endpoints

See [API_USAGE.md](API_USAGE.md) for detailed API documentation.

## Admin Interface

All models are registered in the Django admin with:
- Custom list displays showing related counts
- Filtering by key attributes
- Search functionality
- Organized fieldsets for easy editing
- Color-coded stock status indicators
- Discount information display

## Management Commands

### populate_products
Creates sample data for testing:
```bash
python manage.py populate_products
```

## Helper Utilities

The `utils.py` file provides functions for:
- Creating entities with proper validation
- Navigating category hierarchies
- Filtering products by hierarchy
- Bulk operations
- Navigation tree generation for frontend use

## Best Practices Implemented

1. **Database Optimization**
   - Proper indexing on frequently queried fields
   - Select/prefetch related optimizations
   - Efficient querying patterns

2. **Data Integrity**
   - Validation in serializers and models
   - Unique constraints where appropriate
   - Relationship validation

3. **Scalability**
   - Modular design with clear separation of concerns
   - Efficient serialization strategies
   - Pagination support

4. **Developer Experience**
   - Comprehensive documentation
   - Consistent naming conventions
   - Clear error handling
   - Helpful admin interface

## Installation

1. Ensure the app is in `INSTALLED_APPS` in `settings.py`:
   ```python
   INSTALLED_APPS = [
       ...
       'products',
       ...
   ]
   ```

2. Add to `urls.py`:
   ```python
   urlpatterns = [
       ...
       path('api/products/', include('products.urls')),
       ...
   ]
   ```

3. Run migrations:
   ```bash
   python manage.py makemigrations products
   python manage.py migrate products
   ```

4. Install required packages:
   ```bash
   pip install django-filter
   ```

## Usage Examples

### Creating a Product Hierarchy
```python
from products.utils import create_brand, create_vehicle_model, create_part_category, create_product

# Create brand
toyota, _ = create_brand("Toyota", "Japanese automobile manufacturer")

# Create vehicle model
innova, _ = create_vehicle_model(toyota, "Innova Crysta", "MPV model by Toyota", 2015, 2023)

# Create category
steering, _ = create_part_category("Steering")

# Create subcategory
steering_wheel, _ = create_part_category("Steering Wheel", parent=steering)

# Create product
product, _ = create_product(
    brand=toyota,
    vehicle_model=innova,
    part_category=steering_wheel,
    name="Innova Crysta Leather Steering Wheel",
    sku="TOY-INN-SW-001",
    price=85.99
)
```

### Getting Navigation Tree
```python
from products.utils import get_navigation_tree

navigation_data = get_navigation_tree()
# Returns structured data for frontend navigation menus
```

## Extending the App

The modular design makes it easy to extend:
- Add new fields to existing models
- Create additional serializers for specific use cases
- Implement custom views for specialized queries
- Add new management commands for data operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests if applicable
5. Submit a pull request

## License

[Your license information here]