# Payment System API Documentation

This document provides detailed information about the Payment System API endpoints for your automotive e-commerce platform.

## Base URL

All endpoints are prefixed with `/api/payment/`.

## Authentication

All endpoints require authentication using JWT tokens.

## Payment Endpoints

### Get Payment Configurations
```
GET /api/payment/configurations/
```

**Response:**
```json
[
  {
    "id": 1,
    "gateway": "dummy",
    "is_active": true,
    "merchant_id": "dummy_merchant",
    "public_key": "dummy_public_key",
    "currency": "USD",
    "created_at": "2025-12-03T10:00:00Z",
    "updated_at": "2025-12-03T10:00:00Z"
  }
]
```

### Get User Transactions
```
GET /api/payment/transactions/
```

**Response:**
```json
[
  {
    "id": 1,
    "transaction_id": "TXN-A1B2C3D4E5F6",
    "order": 1,
    "order_number": "ORD-ABC123",
    "user": 1,
    "user_email": "user@example.com",
    "gateway": "dummy",
    "gateway_transaction_id": "",
    "amount": "150.00",
    "currency": "USD",
    "status": "success",
    "metadata": {
      "payment_method": "dummy"
    },
    "error_message": "",
    "created_at": "2025-12-03T10:00:00Z",
    "updated_at": "2025-12-03T10:00:00Z"
  }
]
```

### Get Transaction Details
```
GET /api/payment/transactions/TXN-A1B2C3D4E5F6/
```

**Response:**
```json
{
  "id": 1,
  "transaction_id": "TXN-A1B2C3D4E5F6",
  "order": 1,
  "order_number": "ORD-ABC123",
  "user": 1,
  "user_email": "user@example.com",
  "gateway": "dummy",
  "gateway_transaction_id": "",
  "amount": "150.00",
  "currency": "USD",
  "status": "success",
  "metadata": {
    "payment_method": "dummy"
  },
  "error_message": "",
  "created_at": "2025-12-03T10:00:00Z",
  "updated_at": "2025-12-03T10:00:00Z"
}
```

### Create Payment Intent
```
POST /api/payment/create-intent/
```

**Request Body:**
```json
{
  "order_id": 1,
  "gateway": "dummy"
}
```

**Response:**
```json
{
  "transaction_id": "TXN-A1B2C3D4E5F6",
  "amount": "150.00",
  "currency": "USD",
  "gateway": "dummy",
  "client_secret": "dummy_secret_TXN-A1B2C3D4E5F6",
  "publishable_key": "dummy_public_key"
}
```

### Process Payment
```
POST /api/payment/process/
```

**Request Body:**
```json
{
  "transaction_id": "TXN-A1B2C3D4E5F6",
  "payment_method": "credit_card",
  "payment_data": {
    "card_number": "4111111111111111",
    "expiry_month": "12",
    "expiry_year": "2027",
    "cvv": "123"
  }
}
```

**Response (Success):**
```json
{
  "message": "Payment processed successfully",
  "transaction_id": "TXN-A1B2C3D4E5F6",
  "status": "success"
}
```

**Response (Failure):**
```json
{
  "error": "Payment processing failed"
}
```

### Refund Transaction
```
POST /api/payment/refund/
```

**Request Body:**
```json
{
  "transaction_id": "TXN-A1B2C3D4E5F6",
  "reason": "Customer request",
  "amount": "150.00"
}
```

**Response:**
```json
{
  "id": 1,
  "refund_id": "REF-A1B2C3D4E5F6",
  "transaction": 1,
  "transaction_id": "TXN-A1B2C3D4E5F6",
  "amount": "150.00",
  "currency": "USD",
  "status": "refunded",
  "reason": "Customer request",
  "gateway_refund_id": "",
  "metadata": {},
  "created_at": "2025-12-03T10:00:00Z",
  "updated_at": "2025-12-03T10:00:00Z"
}
```

## Error Responses

All error responses follow this format:
```json
{
  "detail": "Error message"
}
```

Or for custom errors:
```json
{
  "error": "Error message"
}
```

## Example Usage

### Get payment configurations
```bash
curl -X GET \
  http://localhost:8000/api/payment/configurations/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Create payment intent
```bash
curl -X POST \
  http://localhost:8000/api/payment/create-intent/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"order_id": 1, "gateway": "dummy"}'
```

### Process payment
```bash
curl -X POST \
  http://localhost:8000/api/payment/process/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"transaction_id": "TXN-A1B2C3D4E5F6", "payment_method": "credit_card"}'
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Exceeding the limit will result in a 429 Too Many Requests response.

## Implementation Details

### Models

1. **PaymentConfiguration**: Gateway configuration settings
   - Gateway type (Stripe, PayPal, Dummy, etc.)
   - API keys and merchant IDs
   - Active status

2. **Transaction**: Payment transactions
   - Transaction ID
   - Order and user references
   - Amount and currency
   - Status tracking
   - Metadata storage

3. **Refund**: Refund transactions
   - Refund ID
   - Associated transaction
   - Amount and reason
   - Status tracking

### Features

- **Multi-Gateway Support**: Easily extendable to support multiple payment providers
- **Transaction Tracking**: Complete audit trail of all payment activities
- **Refund Management**: Built-in refund processing
- **Security**: Secure handling of payment data
- **Flexibility**: Easy to integrate with third-party payment providers

### Supported Gateways

1. **Dummy Gateway**: For testing and development
2. **Stripe**: Full Stripe integration ready
3. **PayPal**: PayPal integration ready
4. **Razorpay**: Indian payment provider
5. **Flutterwave**: African payment provider

### Security

- Authentication required for all endpoints
- Secure storage of sensitive data
- Proper error handling without exposing sensitive information
- Audit trails for all transactions

### Performance

- Database indexing on frequently queried fields
- Efficient serialization
- Atomic database operations for consistency
- Redis-based caching for frequently accessed data (0-query pattern)

## Integration with Other Systems

The payment system integrates with:

1. **Order System**: Links to Order model for payment processing
2. **User System**: Tracks payments by user
3. **Admin System**: Fully manageable through Django admin

## Extensibility

The system can be easily extended to:

- Add new payment gateways
- Implement subscription payments
- Add recurring payments
- Integrate with accounting systems
- Add advanced fraud detection