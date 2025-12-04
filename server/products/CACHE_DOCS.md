# Products App Caching Documentation

## Overview

The products app implements a comprehensive caching strategy using Redis to improve performance and reduce database load. This document outlines the caching implementation, cache keys, invalidation strategies, and configuration options.

## Caching Strategy

### 1. Model-Level Caching
- Individual model instances are cached when accessed frequently
- Cache invalidation occurs automatically when models are updated or deleted
- PartCategory instances are cached for hierarchical operations

### 2. Query Result Caching
- Frequently accessed query results are cached (brands, categories, models)
- Search results are cached with sanitized query keys
- Navigation trees are cached for frontend performance

### 3. Serializer-Level Caching
- Count properties (models_count, products_count, subcategories_count)
- Hierarchical data (subcategories, products, models)
- Category metadata (is_parent, full_path)

### 4. View-Level Caching
- Featured products lists
- Filtered product collections (by brand, category, model)
- Search results
- Navigation data

## Cache Keys

### Brand Cache Keys
- `brand_models_count_{id}`: Count of models for a brand
- `brand_models_{id}`: List of models for a brand
- `active_brands`: List of all active brands

### Vehicle Model Cache Keys
- `vehicle_model_products_count_{id}`: Count of products for a model
- `vehicle_model_products_{id}`: List of products for a model
- `active_models`: List of all active models

### Part Category Cache Keys
- `part_category_subcategories_count_{id}`: Count of subcategories
- `part_category_subcategories_{id}`: List of subcategories
- `part_category_products_{id}`: List of products in category
- `part_category_instance_{id}`: Cached category instance
- `part_category_is_parent_{id}`: Whether category has subcategories
- `part_category_full_path_{id}`: Full hierarchical path
- `active_categories`: List of all active categories

### Product Cache Keys
- `featured_products_{limit}`: Featured products list
- `products_by_brand_{slug}_{limit}`: Products filtered by brand
- `products_by_category_{slug}_{limit}`: Products filtered by category
- `products_by_model_{slug}_{limit}`: Products filtered by model
- `product_by_slug_{slug}`: Individual product by slug
- `product_by_sku_{sku}`: Individual product by SKU
- `search_products_{query}_{limit}`: Search results
- `in_stock_products_{limit}`: In-stock products list
- `navigation_tree`: Complete navigation hierarchy

## Cache Invalidation

Cache invalidation follows these principles:

1. **Automatic Invalidation**: When models are saved or deleted, related cache entries are automatically invalidated
2. **Targeted Clearing**: Only specific cache keys related to changed data are cleared
3. **Graceful Fallback**: When cache misses occur, data is fetched from the database and re-cached

### Invalidation Triggers

- **Brand changes**: Invalidates brand-related cache keys
- **VehicleModel changes**: Invalidates model-related cache keys
- **PartCategory changes**: Invalidates category-related cache keys
- **Product changes**: Invalidates product-related cache keys

## Configuration

Cache timeout can be customized by setting `PRODUCTS_CACHE_TIMEOUT` in settings.py (default: 900 seconds/15 minutes).

```python
# settings.py
PRODUCTS_CACHE_TIMEOUT = 60 * 15  # 15 minutes
```

## Performance Benefits

1. **Reduced Database Queries**: Cached results eliminate repetitive database lookups
2. **Faster Response Times**: Cached data is served directly from Redis memory
3. **Improved Scalability**: Reduced database load allows handling more concurrent requests
4. **Consistent Performance**: Cache hit ratios provide predictable response times

## Cache Utility Functions

The `cache_utils.py` module provides helper functions for common caching operations:

- `get_active_brands()`: Get cached list of active brands
- `get_active_categories()`: Get cached list of active categories
- `get_active_models()`: Get cached list of active models
- `get_featured_products(limit)`: Get cached featured products
- `get_products_by_brand(slug, limit)`: Get cached products by brand
- `get_products_by_category(slug, limit)`: Get cached products by category
- `get_products_by_model(slug, limit)`: Get cached products by model
- `get_product_by_slug(slug)`: Get cached product by slug
- `get_product_by_sku(sku)`: Get cached product by SKU
- `search_products(query, limit)`: Get cached search results
- `get_in_stock_products(limit)`: Get cached in-stock products
- `get_navigation_tree()`: Get cached navigation hierarchy

## Best Practices

1. **Cache Key Naming**: Use descriptive, consistent naming patterns
2. **Cache Timeouts**: Set appropriate timeouts based on data volatility
3. **Memory Management**: Monitor cache memory usage and evict stale entries
4. **Error Handling**: Implement graceful fallback when cache is unavailable
5. **Testing**: Verify cache behavior with integration tests

## Monitoring

Monitor these metrics to ensure caching effectiveness:

- Cache hit ratio
- Average response time improvement
- Database query reduction
- Memory usage patterns