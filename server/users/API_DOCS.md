# Users API Documentation

This document describes the API endpoints for the users app with caching implementation.

## Endpoints

### Send OTP

Send a One-Time Password to a user's email or phone number.

**Endpoint:** `POST /api/auth/send-otp/`

**Request Body:**
```json
{
  "email_or_phone": "user@example.com"
}
```

**Response:**
```json
{
  "message": "OTP sent successfully to your email.",
  "identifier": "user@example.com"
}
```

**Caching:** OTP is cached for 10 minutes to enable verification without database queries.

### Verify OTP

Verify the One-Time Password sent to a user's email or phone number.

**Endpoint:** `POST /api/auth/verify-otp/`

**Request Body:**
```json
{
  "email_or_phone": "user@example.com",
  "otp": "123456"
}
```

**Response:**
```json
{
  "message": "Login successful.",
  "user_id": 1,
  "email": "user@example.com",
  "phone_number": "+1234567890"
}
```

**Caching:** User data is cached for 15 minutes to enable zero-query authentication on subsequent requests.

## Caching Implementation

The users app implements two layers of caching:

1. **OTP Caching:** OTP codes are stored in Redis with a 10-minute expiration
2. **User Data Caching:** User objects are cached with a 15-minute expiration

### Cache Keys

- OTP: `otp_{email_or_phone}`
- User Data: `user_{email_or_phone}`

### Cache Invalidation

Cache is automatically invalidated when:
- User data is modified
- OTP codes are verified
- Cache entries expire naturally

## Performance Benefits

- Eliminates database queries for OTP verification
- Reduces user lookup times to zero queries after first access
- Decreases database load during authentication
- Improves API response times