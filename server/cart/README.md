# Cart App Documentation

This Django app provides a complete shopping cart system for an automotive spare parts and accessories e-commerce platform.

## Overview

The cart app allows users to add products to a temporary shopping cart before proceeding to checkout. It implements a clean, scalable architecture that integrates smoothly with the existing product and user systems.

## Key Features

### User-Centric Design
- Each user has one cart
- Automatic cart creation on first access
- User-specific access control

### Product Integration
- Full integration with existing product system
- Detailed product information in cart items
- Real-time product data (pricing, availability, etc.)

### Robust Functionality
- Add/remove items from cart
- Update item quantities
- Clear entire cart
- Prevent duplicate entries
- Stock validation
- Automatic price preservation
- Real-time calculations

### Performance Optimized
- Efficient database queries
- Proper indexing
- Prefetching related data
- Clean serialization
- **Redis caching for improved performance**

### Security Focused
- User-specific access control
- Authentication required for all operations
- Data validation
- Stock validation to prevent overselling

## Models

### Cart
Represents a user's shopping cart.

Key fields:
- `user`: One-to-one relationship with User model
- `created_at`: When the cart was created
- `updated_at`: When the cart was last modified

Properties:
- `items_count`: Number of items in the cart
- `total_quantity`: Total quantity of all items
- `subtotal`: Sum of all item prices

Methods:
- `add_item()`: Add item to cart
- `remove_item()`: Remove item from cart
- `update_item_quantity()`: Update item quantity
- `clear()`: Clear all items

### CartItem
Represents an item in a user's cart.

Key fields:
- `cart`: Foreign key to Cart
- `product`: Foreign key to Product
- `quantity`: Number of items
- `price`: Price at time of addition
- `added_at`: When the item was added
- `updated_at`: When the item was last modified

Properties:
- `total_price`: Quantity × price

## API Endpoints

See [API_DOCS.md](API_DOCS.md) for detailed API documentation.

## Security Features

- User-specific access control (users can only access their own carts)
- Authentication required for all operations
- Data validation to prevent invalid entries
- Stock validation to prevent overselling
- Price preservation to prevent price manipulation

## Admin Interface

All models are registered in the Django admin with:
- Custom list displays with relevant information
- Inline editing for cart items
- Filtering by key attributes
- Search functionality
- Read-only fields for calculated values

## Management Commands

### test_cart
Test the cart functionality:
```bash
python manage.py test_cart
```

## Helper Utilities

The `utils.py` file provides functions for:
- Adding items to cart
- Removing items from cart
- Updating cart item quantities
- Clearing cart
- Checking if product is in cart
- Getting cart summary
- Cache management utilities

## Performance Optimization

### Caching Strategy
The cart app implements a comprehensive caching strategy using Redis to improve performance:

1. **Cart Data Caching**
   - User carts are cached for 15 minutes
   - Cart items are cached separately for faster access
   - Cache keys are invalidated on cart modifications

2. **Property Caching**
   - Cart properties (items_count, total_quantity, subtotal) are cached individually
   - Property caches are invalidated when cart contents change

3. **Cache Invalidation**
   - Automatic cache invalidation on all cart operations
   - Targeted cache clearing to minimize performance impact
   - Graceful fallback to database when cache misses occur

### Cache Keys
- `cart_{user_id}`: Cached cart object
- `cart_items_{user_id}`: Cached cart items list
- `cart_items_count_{cart_id}`: Cached items count
- `cart_total_quantity_{cart_id}`: Cached total quantity
- `cart_subtotal_{cart_id}`: Cached subtotal

### Configuration
Cache timeout can be customized by setting `CART_CACHE_TIMEOUT` in settings.py (default: 900 seconds/15 minutes).

## Best Practices Implemented

1. **Data Integrity**
   - Unique constraints to prevent duplicates
   - Proper foreign key relationships
   - Data validation
   - Stock validation

2. **Security**
   - User-specific access control
   - Authentication required for all operations
   - Price preservation at time of addition

3. **Performance**
   - Proper indexing on frequently queried fields
   - Efficient querying patterns
   - Select/prefetch related optimizations
   - **Redis caching for frequently accessed data**

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
       'cart',
       ...
   ]
   ```

2. Add to `urls.py`:
   ```python
   urlpatterns = [
       ...
       path('api/cart/', include('cart.urls')),
       ...
   ]
   ```

3. Run migrations:
   ```bash
   python manage.py makemigrations cart
   python manage.py migrate cart
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

## Usage Examples

### Adding an Item to Cart
```python
from cart.utils import add_to_cart
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()
user = User.objects.get(email="customer@example.com")
product = Product.objects.get(sku="SW-001")

result = add_to_cart(user, product.id, quantity=2)
if result['success']:
    print(result['message'])
```

### Updating Cart Item Quantity
```python
from cart.utils import update_cart_item

result = update_cart_item(user, product.id, quantity=3)
if result['success']:
    print(result['message'])
```

### Getting Cart Summary
```python
from cart.utils import get_cart_summary

summary = get_cart_summary(user)
print(f"Items: {summary['items_count']}")
print(f"Total Quantity: {summary['total_quantity']}")
print(f"Subtotal: ${summary['subtotal']}")
```

## API Integration

### Frontend Integration Example
```javascript
// Add product to cart
fetch('/api/cart/cart/add_item/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    product_id: productId,
    quantity: 2
  })
})
.then(response => response.json())
.then(data => {
  console.log(data.message);
});

// Get cart
fetch('/api/cart/cart/', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
})
.then(response => response.json())
.then(data => {
  console.log('Cart items:', data.items);
  console.log('Subtotal:', data.subtotal);
});
```

## Integration with Order System

The cart system is designed to integrate seamlessly with the order system:
- Cart items can be converted to order items during checkout
- Product price preservation ensures accurate order pricing
- Stock validation prevents overselling during order creation

## Extending the App

The modular design makes it easy to extend:
- Add coupon/discount functionality
- Implement cart persistence across sessions
- Add product variant support
- Create cart sharing features
- Add cart expiration functionality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests if applicable
5. Submit a pull request

## License

[Your license information here]