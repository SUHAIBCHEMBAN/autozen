# Wishlist App Documentation

This Django app provides a complete wishlist system for an automotive spare parts and accessories e-commerce platform.

## Overview

The wishlist app allows users to save products they're interested in for later purchase. It implements a clean, scalable architecture that integrates smoothly with the existing product and user systems.

## Key Features

### User-Centric Design
- Each user has one wishlist
- Automatic wishlist creation on first access
- User-specific access control

### Product Integration
- Full integration with existing product system
- Detailed product information in wishlist items
- Real-time product data (pricing, availability, etc.)

### Robust Functionality
- Add/remove items from wishlist
- Clear entire wishlist
- Prevent duplicate entries
- Automatic timestamp updates

### Performance Optimized
- Efficient database queries
- Proper indexing
- Prefetching related data
- Clean serialization
- **Redis caching for 0 database queries**
- Automatic cache invalidation
- Configurable cache timeouts

### Security Focused
- User-specific access control
- Authentication required for all operations
- Data validation

## Models

### Wishlist
Represents a user's wishlist.

Key fields:
- `user`: One-to-one relationship with User model
- `created_at`: When the wishlist was created
- `updated_at`: When the wishlist was last modified

Properties:
- `items_count`: Number of items in the wishlist

### WishlistItem
Represents an item in a user's wishlist.

Key fields:
- `wishlist`: Foreign key to Wishlist
- `product`: Foreign key to Product
- `added_at`: When the item was added

## API Endpoints

See [API_DOCS.md](API_DOCS.md) for detailed API documentation.

## Security Features

- User-specific access control (users can only access their own wishlists)
- Authentication required for all operations
- Data validation to prevent invalid entries
- Prevention of duplicate items

## Admin Interface

All models are registered in the Django admin with:
- Custom list displays with relevant information
- Inline editing for wishlist items
- Filtering by key attributes
- Search functionality

## Management Commands

### test_wishlist
Test the wishlist functionality:
```bash
python manage.py test_wishlist
```

## Helper Utilities

The `utils.py` file provides legacy functions (deprecated).

The `cache_utils.py` file provides enhanced caching functions for:
- Adding items to wishlist with automatic cache invalidation
- Removing items from wishlist with automatic cache invalidation
- Clearing wishlist with automatic cache invalidation
- Checking if product is in wishlist using cache
- Getting wishlist item count from cache
- Retrieving wishlist and wishlist items from cache

See [CACHING_README.md](CACHING_README.md) for detailed caching implementation documentation.

## Best Practices Implemented

1. **Data Integrity**
   - Unique constraints to prevent duplicates
   - Proper foreign key relationships
   - Data validation

2. **Security**
   - User-specific access control
   - Authentication required for all operations

3. **Performance**
   - Proper indexing on frequently queried fields
   - Efficient querying patterns
   - Select/prefetch related optimizations
   - **Redis caching for 0 database queries on repeated requests**
   - **Automatic cache invalidation on data changes**
   - **Configurable cache timeouts for optimal performance**

4. **Scalability**
   - Modular design with clear separation of concerns
   - Efficient serialization strategies

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
       'wishlist',
       ...
   ]
   ```

2. Add to `urls.py`:
   ```python
   urlpatterns = [
       ...
       path('api/wishlist/', include('wishlist.urls')),
       ...
   ]
   ```

3. Run migrations:
   ```bash
   python manage.py makemigrations wishlist
   python manage.py migrate wishlist
   ```

## Usage Examples

### Adding an Item to Wishlist
```python
from wishlist.cache_utils import add_to_wishlist_with_cache
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()
user = User.objects.get(email="customer@example.com")
product = Product.objects.get(sku="SW-001")

result = add_to_wishlist_with_cache(user, product.id)
if result['success']:
    print(result['message'])
```

### Checking if Product is in Wishlist
```python
from wishlist.cache_utils import is_product_in_wishlist_cached

if is_product_in_wishlist_cached(user.id, product.id):
    print("Product is in wishlist")
```

### Getting Wishlist Items
```python
from wishlist.cache_utils import get_cached_wishlist_items

items = get_cached_wishlist_items(user.id)
for item in items:
    print(f"{item.product.name} - Added: {item.added_at}")
```

## API Integration

### Frontend Integration Example
```javascript
// Add product to wishlist
fetch('/api/wishlist/wishlist/add_item/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    product_id: productId
  })
})
.then(response => response.json())
.then(data => {
  console.log(data.message);
});

// Get wishlist
fetch('/api/wishlist/wishlist/', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
.then(response => response.json())
.then(data => {
  console.log('Wishlist items:', data.items);
});
```

## Extending the App

The modular design makes it easy to extend:
- Add wishlist sharing features
- Implement wishlist notifications
- Add priority levels to wishlist items
- Create wishlist collections
- Add expiration dates to wishlist items

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests if applicable
5. Submit a pull request

## License

[Your license information here]