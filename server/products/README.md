# Products App

The products app manages automotive parts inventory with a hierarchical categorization system, brand management, vehicle model compatibility, and comprehensive product data.

## Features

1. **Brand Management**
   - Create and manage vehicle brands/manufacturers
   - Logo upload support
   - Active/inactive status management

2. **Vehicle Model Management**
   - Vehicle model database with year ranges
   - Brand association
   - Image support
   - Active/inactive status management

3. **Hierarchical Category System**
   - Multi-level part categories (e.g., Engine > Fuel System > Fuel Pump)
   - Parent-child relationships
   - Image support
   - Active/inactive status management

4. **Product Management**
   - Comprehensive product data (SKU, pricing, inventory, descriptions)
   - Brand, vehicle model, and category associations
   - Featured product support
   - OEM and manufacturer part numbers
   - Discount pricing (compare price)
   - Inventory tracking with stock levels
   - SEO-friendly URLs with automatic slug generation

5. **API Endpoints**
   - Full CRUD operations for all entities
   - Filtering, searching, and ordering capabilities
   - Detailed and list views for all entities
   - Relationship endpoints (brand models, category subcategories, etc.)

## Performance Optimization

### Caching Strategy
The products app implements a comprehensive caching strategy using Redis to improve performance:

1. **Model Instance Caching**
   - Frequently accessed PartCategory instances are cached
   - Automatic cache invalidation on model changes
   - Hierarchical data caching (parent/child relationships)

2. **Query Result Caching**
   - Brand, vehicle model, and category lists are cached
   - Featured products lists are cached
   - Filtered product collections are cached
   - Search results are cached
   - Navigation trees are cached

3. **Serializer-Level Caching**
   - Count properties are cached (models_count, products_count, etc.)
   - Hierarchical data is cached (subcategories, products, models)
   - Category metadata is cached (is_parent, full_path)

4. **View-Level Caching**
   - API endpoints utilize caching for improved response times
   - Cache invalidation on content updates
   - Configurable cache timeouts

### Cache Keys
- `brand_models_count_{id}`: Count of models for a brand
- `brand_models_{id}`: List of models for a brand
- `vehicle_model_products_count_{id}`: Count of products for a model
- `part_category_subcategories_count_{id}`: Count of subcategories
- `part_category_subcategories_{id}`: List of subcategories
- `part_category_products_{id}`: List of products in category
- `part_category_instance_{id}`: Cached category instance
- `part_category_is_parent_{id}`: Whether category has subcategories
- `part_category_full_path_{id}`: Full hierarchical path
- `featured_products_{limit}`: Featured products list
- `products_by_brand_{slug}_{limit}`: Products filtered by brand
- `products_by_category_{slug}_{limit}`: Products filtered by category
- `products_by_model_{slug}_{limit}`: Products filtered by model
- `product_by_slug_{slug}`: Individual product by slug
- `search_products_{query}_{limit}`: Search results
- `navigation_tree`: Complete navigation hierarchy

### Cache Invalidation
- Automatic cache invalidation on all content updates
- Targeted cache clearing to minimize performance impact
- Graceful fallback to database when cache misses occur

### Configuration
Cache timeout can be customized by setting `PRODUCTS_CACHE_TIMEOUT` in settings.py (default: 900 seconds/15 minutes).

See [CACHE_DOCS.md](CACHE_DOCS.md) for detailed caching documentation.

## Best Practices Implemented

1. **Database Optimization**
   - Proper indexing on frequently queried fields
   - Select/prefetch related optimizations
   - Efficient querying patterns

2. **Data Integrity**
   - Validation in serializers and models
   - Unique constraints where appropriate
   - Relationship validation

3. **Performance**
   - Proper indexing on frequently queried fields
   - Efficient querying patterns
   - Select/prefetch related optimizations
   - **Redis caching for frequently accessed data**

4. **Scalability**
   - Modular design with clear separation of concerns
   - Efficient serialization strategies
   - Pagination support

5. **Developer Experience**
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

4. Install Redis and required packages:
   ```bash
   pip install redis django-redis
   ```

5. Configure Redis in settings.py:
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
           }
       }
   }
   ```

## API Usage

See [API_USAGE.md](API_USAGE.md) for detailed API documentation.