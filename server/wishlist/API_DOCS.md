# Wishlist API Documentation

This document provides detailed information about the Wishlist API endpoints for your automotive e-commerce platform.

## Base URL

All endpoints are prefixed with `/api/wishlist/`.

## Authentication

All endpoints require authentication. Include your JWT token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## Wishlist Endpoints

### Get User's Wishlist
```
GET /api/wishlist/wishlist/
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
      "added_at": "2025-12-03T10:00:00Z"
    }
  ],
  "items_count": 1,
  "created_at": "2025-12-03T10:00:00Z",
  "updated_at": "2025-12-03T10:00:00Z"
}
```

### Add Item to Wishlist
```
POST /api/wishlist/wishlist/add_item/
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
  "message": "Product added to wishlist"
}
```

### Remove Item from Wishlist
```
POST /api/wishlist/wishlist/remove_item/
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
  "message": "Product removed from wishlist"
}
```

### Clear Wishlist
```
DELETE /api/wishlist/wishlist/clear/
```

**Response:**
```json
{
  "message": "Wishlist cleared"
}
```

### Get Wishlist Items
```
GET /api/wishlist/wishlist/items/
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
    "added_at": "2025-12-03T10:00:00Z"
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
- `404 Not Found`: Wishlist or product not found
- `400 Bad Request`: Invalid request data

## Example Usage

### Get user's wishlist
```bash
curl -X GET \
  http://localhost:8000/api/wishlist/wishlist/ \
  -H 'Authorization: Bearer <your_token>'
```

### Add product to wishlist
```bash
curl -X POST \
  http://localhost:8000/api/wishlist/wishlist/add_item/ \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "product_id": 1
  }'
```

### Remove product from wishlist
```bash
curl -X POST \
  http://localhost:8000/api/wishlist/wishlist/remove_item/ \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "product_id": 1
  }'
```

### Clear wishlist
```bash
curl -X DELETE \
  http://localhost:8000/api/wishlist/wishlist/clear/ \
  -H 'Authorization: Bearer <your_token>'
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Exceeding the limit will result in a 429 Too Many Requests response.

## Implementation Details

### Models

1. **Wishlist**: Represents a user's wishlist
   - One-to-one relationship with User
   - Automatically created when first accessed
   - Tracks creation and update timestamps

2. **WishlistItem**: Represents an item in a wishlist
   - Foreign key to Wishlist and Product
   - Unique constraint to prevent duplicates
   - Tracks when item was added

### Features

- **Automatic Wishlist Creation**: Wishlists are automatically created when first accessed
- **Duplicate Prevention**: Same product cannot be added twice to a wishlist
- **Real-time Updates**: Wishlist timestamp updates when items are added/removed
- **Efficient Queries**: Uses select_related and prefetch_related for performance
- **Proper Permissions**: Users can only access their own wishlists
- **Clean API**: RESTful endpoints with clear responses

### Security

- User-specific access control
- Authentication required for all operations
- Proper data validation
- Prevention of duplicate entries

### Performance

- Database indexing on frequently queried fields
- Efficient serialization with nested product data
- Prefetching related objects to minimize database queries
- Proper use of select_related and prefetch_related

## Integration with Other Systems

The wishlist system integrates with:

1. **User System**: Uses the custom User model
2. **Product System**: Links to Product model with full product details
3. **Authentication System**: Works with JWT token authentication

## Extensibility

The system can be easily extended to:

- Add wishlist sharing features
- Implement wishlist notifications
- Add priority levels to wishlist items
- Create wishlist collections
- Add expiration dates to wishlist items