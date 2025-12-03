# Order API Documentation

This document provides detailed information about the Order API endpoints for your automotive e-commerce platform.

## Base URL

All endpoints are prefixed with `/api/orders/`.

## Authentication

Most endpoints require authentication. Include your JWT token in the Authorization header:

```
Authorization: Bearer <your_token>
```

## Order Endpoints

### List Orders
```
GET /api/orders/orders/
```

**Query Parameters:**
- `status`: Filter by order status
- `payment_method`: Filter by payment method
- `payment_status`: Filter by payment status (true/false)
- `search`: Search by order number, customer name, email, or phone
- `ordering`: Order results (-created_at, created_at, total_amount, status)

**Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "order_number": "ORD-A1B2C3D4",
      "user": 1,
      "user_email": "customer@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "email": "customer@example.com",
      "phone_number": "+1234567890",
      "billing_address_line1": "123 Main St",
      "billing_address_line2": "",
      "billing_city": "New York",
      "billing_state": "NY",
      "billing_postal_code": "10001",
      "billing_country": "USA",
      "shipping_address_line1": "123 Main St",
      "shipping_address_line2": "",
      "shipping_city": "New York",
      "shipping_state": "NY",
      "shipping_postal_code": "10001",
      "shipping_country": "USA",
      "status": "pending",
      "payment_method": "credit_card",
      "payment_status": false,
      "subtotal": "100.00",
      "tax_amount": "8.00",
      "shipping_cost": "10.00",
      "discount_amount": "0.00",
      "total_amount": "118.00",
      "notes": "",
      "internal_notes": "",
      "created_at": "2025-12-03T10:00:00Z",
      "updated_at": "2025-12-03T10:00:00Z",
      "shipped_at": null,
      "delivered_at": null,
      "items": [
        {
          "id": 1,
          "product": 1,
          "product_name": "Steering Wheel",
          "product_sku": "SW-001",
          "product_price": "50.00",
          "quantity": 2,
          "total_price": "100.00",
          "product_url": "http://localhost:8000/api/products/products/steering-wheel/"
        }
      ],
      "status_logs": [],
      "can_be_cancelled": true
    }
  ]
}
```

### Retrieve Order
```
GET /api/orders/orders/{order_number}/
```

**Response:**
Same as list endpoint but for a single order.

### Create Order
```
POST /api/orders/orders/
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "customer@example.com",
  "phone_number": "+1234567890",
  "billing_address_line1": "123 Main St",
  "billing_address_line2": "",
  "billing_city": "New York",
  "billing_state": "NY",
  "billing_postal_code": "10001",
  "billing_country": "USA",
  "shipping_address_line1": "123 Main St",
  "shipping_address_line2": "",
  "shipping_city": "New York",
  "shipping_state": "NY",
  "shipping_postal_code": "10001",
  "shipping_country": "USA",
  "payment_method": "credit_card",
  "subtotal": "100.00",
  "tax_amount": "8.00",
  "shipping_cost": "10.00",
  "discount_amount": "0.00",
  "total_amount": "118.00",
  "notes": "",
  "items": [
    {
      "product": 1,
      "quantity": 2
    }
  ]
}
```

### Update Order (Staff Only)
```
PUT/PATCH /api/orders/orders/{order_number}/
```

**Request Body:**
```json
{
  "status": "confirmed",
  "payment_status": true,
  "internal_notes": "Order confirmed and payment received"
}
```

### Cancel Order
```
POST /api/orders/orders/{order_number}/cancel/
```

**Response:**
```json
{
  "message": "Order cancelled successfully"
}
```

### Update Order Status (Staff Only)
```
POST /api/orders/orders/{order_number}/update_status/
```

**Request Body:**
```json
{
  "status": "shipped"
}
```

### Get Order History
```
GET /api/orders/orders/history/
```

**Response:**
Returns all orders for the authenticated user (or all orders for staff).

### Checkout
```
POST /api/orders/orders/checkout/
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "customer@example.com",
  "phone_number": "+1234567890",
  "billing_address_line1": "123 Main St",
  "billing_address_line2": "",
  "billing_city": "New York",
  "billing_state": "NY",
  "billing_postal_code": "10001",
  "billing_country": "USA",
  "shipping_address_line1": "123 Main St",
  "shipping_address_line2": "",
  "shipping_city": "New York",
  "shipping_state": "NY",
  "shipping_postal_code": "10001",
  "shipping_country": "USA",
  "payment_method": "credit_card",
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    }
  ],
  "notes": ""
}
```

## Order Status Values

- `pending`: Order placed but not yet confirmed
- `confirmed`: Order confirmed, awaiting processing
- `processing`: Order is being processed
- `shipped`: Order has been shipped
- `out_for_delivery`: Order is out for delivery
- `delivered`: Order has been delivered
- `cancelled`: Order was cancelled
- `returned`: Order was returned
- `refunded`: Order was refunded

## Payment Method Values

- `credit_card`: Credit card payment
- `debit_card`: Debit card payment
- `paypal`: PayPal payment
- `bank_transfer`: Bank transfer
- `cash_on_delivery`: Cash on delivery
- `upi`: UPI payment

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

## Permissions

- **Authenticated users** can:
  - View their own orders
  - Cancel their own orders (if status allows)
  - View order history

- **Staff users** can:
  - View all orders
  - Update order status
  - Add internal notes
  - Perform all actions available to regular users

## Rate Limiting

The API implements rate limiting to prevent abuse. Exceeding the limit will result in a 429 Too Many Requests response.

## Example Usage

### Get all orders for current user
```bash
curl -X GET \
  http://localhost:8000/api/orders/orders/ \
  -H 'Authorization: Bearer <your_token>'
```

### Create a new order
```bash
curl -X POST \
  http://localhost:8000/api/orders/orders/ \
  -H 'Authorization: Bearer <your_token>' \
  -H 'Content-Type: application/json' \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone_number": "+1234567890",
    "billing_address_line1": "123 Main St",
    "billing_city": "New York",
    "billing_state": "NY",
    "billing_postal_code": "10001",
    "billing_country": "USA",
    "shipping_address_line1": "123 Main St",
    "shipping_city": "New York",
    "shipping_state": "NY",
    "shipping_postal_code": "10001",
    "shipping_country": "USA",
    "payment_method": "credit_card",
    "subtotal": "100.00",
    "tax_amount": "8.00",
    "shipping_cost": "10.00",
    "discount_amount": "0.00",
    "total_amount": "118.00",
    "items": [
      {
        "product": 1,
        "quantity": 2
      }
    ]
  }'
```

### Cancel an order
```bash
curl -X POST \
  http://localhost:8000/api/orders/orders/ORD-A1B2C3D4/cancel/ \
  -H 'Authorization: Bearer <your_token>'
```