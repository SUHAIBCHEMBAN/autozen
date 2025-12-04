# Cart API Documentation

This document provides detailed information about the Cart API endpoints for your automotive e-commerce platform.

## Base URL

All endpoints are prefixed with `/api/cart/`.

## Authentication

All endpoints require authentication. Include your JWT token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## Cart Endpoints

### Get User's Cart
```
GET /api/cart/cart/
```

**Response:**
```json
{
  "id": 1,
  "user": 1,
  "items": [
    {
      "id": 1,
      "product": {
        "id": 1,
        "name": "Innova Crysta Leather Steering Wheel",
        "slug": "innova-crysta-leather-steering-wheel",
        "short_description": "Premium leather steering wheel for Toyota Innova Crysta with comfortable grip and elegant design.",
        "featured_image": null,
        "sku": "TOY-INN-SW-001",
        "price": "85.99",
        "compare_price": "120.00",
        "is_active": true,
        "is_featured": false,
        "brand": 1,
        "brand_name": "Toyota",
        "vehicle_model": 1,
        "model_name": "Innova Crysta",
        "part_category": 3,
        "category_name": "Steering Wheel",
        "stock_quantity": 15,
        "amount_saved": "34.01",
        "discount_percentage": 28,
        "is_in_stock": true,
        "created_at": "2025-12-02T06:39:00Z",
        "url": "http://localhost:8000/api/products/products/innova-crysta-leather-steering-wheel/"
      },
      "quantity": 2,
      "price": "85.99",
      "total_price": "171.98",
      "added_at": "2025-12-03T10:00:00Z",
      "updated_at": "2025-12-03T10:00:00Z"
    }
  ],
  "items_count": 1,
  "total_quantity": 2,
  "subtotal": "171.98",
  "created_at": "2025-12-03T10:00:00Z",
  "updated_at": "2025-12-03T10:00:00Z"
}
```

### Add Item to Cart
```
POST /api/cart/cart/add_item/
```

**Request Body:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**Response:**
```json
{
  "message": "Product added to cart",
  "item_id": 1
}
```

### Update Cart Item Quantity
```
PUT /api/cart/cart/update_item/
```

**Request Body:**
```json
{
  "product_id": 1,
  "quantity": 3
}
```

**Response:**
```json
{
  "message": "Cart item updated"
}
```

### Remove Item from Cart
```
POST /api/cart/cart/remove_item/
```

**Request Body:**
```json
{
  "product_id": 1
}
```

**Response:**
```json
{
  "message": "Product removed from cart"
}
```

### Clear Cart
```
DELETE /api/cart/cart/clear/
```

**Response:**
```json
{
  "message": "Cart cleared"
}
```

### Get Cart Items
```
GET /api/cart/cart/items/
```

**Response:**
```json
[
  {
    "id": 1,
    "product": {
      "id": 1,
      "name": "Innova Crysta Leather Steering Wheel",
      "slug": "innova-crysta-leather-steering-wheel",
      "short_description": "Premium leather steering wheel for Toyota Innova Crysta with comfortable grip and elegant design.",
      "featured_image": null,
      "sku": "TOY-INN-SW-001",
      "price": "85.99",
      "compare_price": "120.00",
      "is_active": true,
      "is_featured": false,
      "brand": 1,
      "brand_name": "Toyota",
      "vehicle_model": 1,
      "model_name": "Innova Crysta",
      "part_category": 3,
      "category_name": "Steering Wheel",
      "stock_quantity": 15,
      "amount_saved": "34.01",
      "discount_percentage": 28,
      "is_in_stock": true,
      "created_at": "2025-12-02T06:39:00Z",
      "url": "http://localhost:8000/api/products/products/innova-crysta-leather-steering-wheel/"
    },
    "quantity": 2,
    "price": "85.99",
    "total_price": "171.98",
    "added_at": "2025-12-03T10:00:00Z",
    "updated_at": "2025-12-03T10:00:00Z"
  }
]
```

## Error Responses

All error responses follow this format:
```json
{
  "detail": "Error message"
}
```

Or for validation errors:
```json
{
  "field_name": ["Error message"]
}
```

Or for custom errors:
```json
{
  "error": "Error message"
}
```

## Common Error Codes

- `401 Unauthorized`: Authentication required
- `404 Not Found`: Cart or product not found
- `400 Bad Request`: Invalid request data or insufficient stock

## Example Usage

### Get user's cart
```bash
curl -X GET \
  http://localhost:8000/api/cart/cart/ \
  -H 'Authorization: Bearer <your_token>'
```

### Add product to cart
```bash
curl -X POST \
  http://localhost:8000/api/cart/cart/add_item/ \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

### Update cart item quantity
```bash
curl -X PUT \
  http://localhost:8000/api/cart/cart/update_item/ \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "product_id": 1,
    "quantity": 3
  }'
```

### Remove product from cart
```bash
curl -X POST \
  http://localhost:8000/api/cart/cart/remove_item/ \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "product_id": 1
  }'
```

### Clear cart
```bash
curl -X DELETE \
  http://localhost:8000/api/cart/cart/clear/ \
  -H 'Authorization: Bearer <your_token>'
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Exceeding the limit will result in a 429 Too Many Requests response.

## Implementation Details

### Models

1. **Cart**: Represents a user's shopping cart
   - One-to-one relationship with User
   - Automatically created when first accessed
   - Tracks creation and update timestamps
   - Provides utility methods for cart operations

2. **CartItem**: Represents an item in a cart
   - Foreign key to Cart and Product
   - Unique constraint to prevent duplicates
   - Tracks quantity and price at time of addition
   - Tracks when item was added and updated

### Features

- **Automatic Cart Creation**: Carts are automatically created when first accessed
- **Stock Validation**: Prevents adding more items than available in stock
- **Quantity Management**: Update quantities or remove items completely
- **Real-time Calculations**: Automatic subtotal and total quantity calculations
- **Price Preservation**: Stores product price at time of addition to cart
- **Real-time Updates**: Cart timestamp updates when items are added/removed/modified

### Security

- User-specific access control (users can only access their own carts)
- Authentication required for all operations
- Data validation
- Stock validation to prevent overselling

### Performance

- Database indexing on frequently queried fields
- Efficient serialization with nested product data
- Prefetching related objects to minimize database queries
- Proper use of select_related and prefetch_related
- **Redis caching for improved API response times**
- **Automatic cache invalidation on cart modifications**
- **Configurable cache timeouts**

## Caching

The Cart API implements a comprehensive caching strategy using Redis to improve performance:

### Cached Endpoints
- `GET /api/cart/cart/` - User's cart data
- `GET /api/cart/cart/items/` - Cart items list

### Cache Invalidation
Cache is automatically invalidated when:
- Items are added to cart
- Item quantities are updated
- Items are removed from cart
- Cart is cleared

### Cache Configuration
- Default cache timeout: 15 minutes
- Configurable via `CART_CACHE_TIMEOUT` setting
- Automatic fallback to database when cache misses occur

## Integration with Other Systems

The cart system integrates with:

1. **User System**: Uses the custom User model
2. **Product System**: Links to Product model with full product details
3. **Authentication System**: Works with JWT token authentication
4. **Order System**: Can be converted to orders during checkout

## Extensibility

The system can be easily extended to:

- Add coupon/discount functionality
- Implement cart persistence across sessions
- Add product variant support
- Create cart sharing features
- Add cart expiration functionality