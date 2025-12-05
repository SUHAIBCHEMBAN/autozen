# Wishlist App Caching Implementation

This document describes the Redis caching implementation for the wishlist app, which enables 0 database queries for frequently accessed data.

## Overview

The wishlist caching system implements Redis-based caching for:

1. User wishlists
2. Wishlist items
3. Wishlist item counts
4. Product-in-wishlist checks

## Cache Keys

The following cache keys are used:

- `wishlist_user_{user_id}` - Stores the user's wishlist object
- `wishlist_items_user_{user_id}` - Stores the user's wishlist items
- `wishlist_count_user_{user_id}` - Stores the count of items in the user's wishlist

## Cache Timeout Settings

Cache timeouts are configured in `settings.py`:

```python
WISHLIST_CACHE_TIMEOUT = 60 * 15  # 15 minutes
WISHLIST_ITEM_CACHE_TIMEOUT = 60 * 15  # 15 minutes
```

## Implementation Details

### Cache Utility Functions

All caching functionality is implemented in `cache_utils.py`:

1. `get_cached_wishlist(user_id)` - Retrieves a user's wishlist from cache or database
2. `get_cached_wishlist_items(user_id)` - Retrieves wishlist items from cache or database
3. `get_cached_wishlist_count(user_id)` - Retrieves wishlist item count from cache or database
4. `is_product_in_wishlist_cached(user_id, product_id)` - Checks if a product is in wishlist using cache
5. `add_to_wishlist_with_cache(user, product_id)` - Adds item to wishlist with automatic cache invalidation
6. `remove_from_wishlist_with_cache(user, product_id)` - Removes item from wishlist with automatic cache invalidation
7. `clear_wishlist_with_cache(user)` - Clears wishlist with automatic cache invalidation
8. `invalidate_wishlist_cache(user_id)` - Manually invalidates all wishlist-related cache entries

### Model-Level Cache Invalidation

Cache invalidation is automatically handled through Django signals:

- When a Wishlist is saved or deleted, all related cache entries are invalidated
- When a WishlistItem is saved or deleted, all related cache entries are invalidated

### Serializer Integration

The `WishlistSerializer` has been updated to:

1. Use `SerializerMethodField` for `items_count` to retrieve from cache
2. Override `to_representation` to use cached items when available

### View Integration

All view methods have been updated to use cached functions:

1. `get_object()` - Attempts to retrieve wishlist from cache first
2. `add_item()` - Uses `add_to_wishlist_with_cache()` for automatic cache invalidation
3. `remove_item()` - Uses `remove_from_wishlist_with_cache()` for automatic cache invalidation
4. `clear()` - Uses `clear_wishlist_with_cache()` for automatic cache invalidation
5. `items()` - Attempts to retrieve items from cache first

## Performance Benefits

With this caching implementation:

1. **0 Database Queries**: After the first request, subsequent requests for the same data are served from Redis cache
2. **Automatic Invalidation**: Cache is automatically invalidated when data changes, ensuring data consistency
3. **Reduced Latency**: Eliminates database round trips for frequently accessed data
4. **Scalability**: Reduces database load, allowing the system to handle more concurrent users

## Testing

To test the caching implementation:

1. Make a request to retrieve a user's wishlist
2. Check Redis to confirm data is cached
3. Make the same request again and verify it's served from cache
4. Modify the wishlist (add/remove items)
5. Verify cache is properly invalidated
6. Confirm subsequent requests repopulate the cache

## Monitoring

Cache performance can be monitored by:

1. Checking Redis hit/miss ratios
2. Monitoring cache key expiration
3. Observing reduced database query counts in Django Debug Toolbar