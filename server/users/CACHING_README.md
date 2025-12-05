# Users App Caching Implementation

This document describes the caching strategy implemented for the users app to achieve zero-query performance with Redis.

## Caching Strategy

The users app implements two types of caching:

1. **User Data Caching**: User objects are cached to avoid database queries on subsequent requests
2. **OTP Caching**: One-Time Password codes are cached for authentication verification

## Implementation Details

### Cache Utility Functions

All caching logic is centralized in `cache_utils.py`:

- `get_user_from_cache(identifier)`: Retrieves user data from cache using email or phone number
- `cache_user(user)`: Stores user data in cache for both email and phone number identifiers
- `invalidate_user_cache(identifier)`: Removes user data from cache
- `store_otp(identifier, otp)`: Stores OTP codes with expiration
- `verify_otp(identifier, otp)`: Verifies OTP codes from cache
- `delete_otp(identifier)`: Removes OTP codes after successful verification

### Zero-Query Pattern

The implementation follows a zero-query pattern:

1. Check cache first before hitting the database
2. Cache user data after first database fetch
3. Use cached data for subsequent requests
4. Invalidate cache when user data changes

### Cache Keys

- User data: `user_{email_or_phone}`
- OTP codes: `otp_{email_or_phone}`

### Cache Expiration

- User data: 15 minutes (configurable via `USER_CACHE_TIMEOUT`)
- OTP codes: 10 minutes (configurable via `OTP_CACHE_TIMEOUT`)

## Performance Benefits

- Eliminates database queries for repeated user lookups
- Reduces authentication response times
- Decreases database load during peak traffic
- Improves overall application scalability

## Cache Invalidation

Cache invalidation occurs when:

1. User data is modified
2. OTP codes are verified or expire naturally
3. Manual cache clearing is performed

## Monitoring

Cache hits and misses are logged for performance monitoring.