# Products API Usage Guide

This document provides examples of how to use the Products API for your automotive spare parts e-commerce platform.

## API Endpoints

All endpoints are prefixed with `/api/products/`.

### Brands

- `GET /api/products/brands/` - List all brands
- `POST /api/products/brands/` - Create a new brand
- `GET /api/products/brands/{slug}/` - Get details for a specific brand
- `PUT /api/products/brands/{slug}/` - Update a brand
- `DELETE /api/products/brands/{slug}/` - Delete a brand
- `GET /api/products/brands/{slug}/models/` - Get all models for a specific brand

### Vehicle Models

- `GET /api/products/models/` - List all vehicle models
- `POST /api/products/models/` - Create a new vehicle model
- `GET /api/products/models/{slug}/` - Get details for a specific vehicle model
- `PUT /api/products/models/{slug}/` - Update a vehicle model
- `DELETE /api/products/models/{slug}/` - Delete a vehicle model
- `GET /api/products/models/{slug}/products/` - Get all products for a specific model

### Part Categories

- `GET /api/products/categories/` - List all part categories
- `POST /api/products/categories/` - Create a new part category
- `GET /api/products/categories/{slug}/` - Get details for a specific part category
- `PUT /api/products/categories/{slug}/` - Update a part category
- `DELETE /api/products/categories/{slug}/` - Delete a part category
- `GET /api/products/categories/{slug}/products/` - Get all products for a specific category
- `GET /api/products/categories/parents/` - Get only parent categories
- `GET /api/products/categories/{slug}/subcategories/` - Get all subcategories for a category

### Products

- `GET /api/products/products/` - List all products
- `POST /api/products/products/` - Create a new product
- `GET /api/products/products/{slug}/` - Get details for a specific product
- `PUT /api/products/products/{slug}/` - Update a product
- `DELETE /api/products/products/{slug}/` - Delete a product
- `GET /api/products/products/featured/` - Get featured products
- `GET /api/products/products/by_brand/?brand={brand_slug}` - Get products by brand
- `GET /api/products/products/by_model/?model={model_slug}` - Get products by model
- `GET /api/products/products/by_category/?category={category_slug}` - Get products by category
- `GET /api/products/products/search/?q={query}` - Search products
- `GET /api/products/products/in_stock/` - Get products that are in stock

## Example API Requests

### Get all brands
```bash
curl -X GET http://localhost:8000/api/products/brands/
```

### Get products for a specific vehicle model
```bash
curl -X GET http://localhost:8000/api/products/models/innova-crysta/products/
```

### Search for products
```bash
curl -X GET "http://localhost:8000/api/products/products/search/?q=steering"
```

### Get all parent categories
```bash
curl -X GET http://localhost:8000/api/products/categories/parents/
```

### Get featured products
```bash
curl -X GET http://localhost:8000/api/products/products/featured/
```

## Filtering and Search

### Filtering Products
You can filter products using query parameters:
- `brand`: Filter by brand ID
- `vehicle_model`: Filter by vehicle model ID
- `part_category`: Filter by part category ID
- `is_featured`: Filter by featured status (true/false)

Example:
```bash
curl -X GET "http://localhost:8000/api/products/products/?brand=1&is_featured=true"
```

### Searching Products
Use the search endpoint with a query parameter:
```bash
curl -X GET "http://localhost:8000/api/products/products/search/?q=toyota"
```

### Ordering Results
You can order results using the `ordering` parameter:
- `name`: Order by name
- `-name`: Order by name (descending)
- `price`: Order by price
- `-price`: Order by price (descending)
- `created_at`: Order by creation date
- `-created_at`: Order by creation date (descending)

Example:
```bash
curl -X GET "http://localhost:8000/api/products/products/?ordering=-price"
```

## Helper Utilities

The `products/utils.py` file contains several helpful utility functions:

- `create_brand()`: Create a new brand
- `create_vehicle_model()`: Create a new vehicle model
- `create_part_category()`: Create a new part category
- `create_product()`: Create a new product with validation
- `get_category_hierarchy()`: Get the full hierarchy path for a category
- `get_products_by_hierarchy()`: Get products filtered by brand, model, and/or category
- `bulk_create_products()`: Bulk create products from a list
- `get_navigation_tree()`: Generate a navigation tree for frontend use

## Management Commands

### Populate Sample Data
```bash
python manage.py populate_products
```

This command creates sample brands, models, categories, and products for testing.

## Admin Interface

All models are registered in the Django admin interface where you can:
- Manage brands, models, categories, and products
- View statistics and relationships
- Edit product details with organized fieldsets
- See inventory status with color-coded indicators
- View discount information and savings