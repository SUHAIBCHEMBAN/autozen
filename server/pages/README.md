# Pages App

The pages app provides static content management for the AutoZen platform, including pages for About, Terms & Conditions, Privacy Policy, Return & Refund Policy, and FAQs.

## Features

### Content Management
- Manage static pages with different types (About, Terms, Privacy, etc.)
- FAQ management with ordering support
- SEO-friendly URLs using slugs
- Active/inactive status toggles

### Performance Optimized
- Efficient database queries
- Proper indexing
- **Redis caching for improved performance**

### Easy Management
- Full Django admin integration
- Status toggles
- Automatic slug generation

## API Endpoints

- `GET /pages/`: List all active pages
- `GET /pages/{slug}/`: Retrieve a specific page by slug
- `GET /pages/type/{type}/`: Retrieve a page by type
- `GET /faqs/`: List all active FAQs

## Helper Utilities

The `utils.py` file provides functions for:
- Retrieving active pages with caching
- Getting pages by slug with caching
- Getting pages by type with caching
- Retrieving active FAQs with caching
- Cache management and invalidation

## Performance Optimization

### Caching Strategy
The pages app implements a comprehensive caching strategy using Redis to improve performance:

1. **Pages List Caching**
   - Entire pages list is cached for 15 minutes
   - Reduces database queries for frequently accessed pages list
   - Cache key: `active_pages`

2. **Individual Page Caching**
   - Each page is cached separately by slug for flexible updates
   - Pages by type are cached separately
   - Individual page cache keys: `page_{slug}`, `page_type_{type}`

3. **FAQs Caching**
   - FAQs list is cached for 15 minutes
   - Reduces database queries for frequently accessed FAQs
   - Cache key: `active_faqs`

4. **Cache Invalidation**
   - Automatic cache invalidation on all content updates
   - Targeted cache clearing to minimize performance impact
   - Graceful fallback to database when cache misses occur

### Cache Keys
- `active_pages`: List of all active pages
- `page_{slug}`: Individual page by slug
- `page_type_{type}`: Page by type
- `active_faqs`: List of all active FAQs

### Configuration
Cache timeout can be customized by setting `PAGES_CONTENT_CACHE_TIMEOUT` in settings.py (default: 900 seconds/15 minutes).

## Best Practices Implemented

1. **Data Integrity**
   - Proper data validation
   - Unique constraints where appropriate

2. **Performance**
   - Proper indexing on frequently queried fields
   - Efficient querying patterns
   - **Redis caching for frequently accessed data**

3. **Scalability**
   - Modular design with clear separation of concerns
   - Efficient serialization strategies

4. **Developer Experience**
   - Comprehensive documentation
   - Consistent naming conventions
   - Clear error handling
   - Helpful admin interface

## Installation

1. Ensure the app is in `INSTALLED_APPS` in `settings.py`:
   ```python
   INSTALLED_APPS = [
       ...
       'pages',
       ...
   ]
   ```

2. Add to `urls.py`:
   ```python
   urlpatterns = [
       ...
       path('api/pages/', include('pages.urls')),
       ...
   ]
   ```

3. Run migrations:
   ```bash
   python manage.py makemigrations pages
   python manage.py migrate pages
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