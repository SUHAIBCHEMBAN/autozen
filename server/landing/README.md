# Landing Page App Documentation

This Django app provides a complete landing page system for an automotive spare parts and accessories e-commerce platform.

## Overview

The landing page app delivers a rich, engaging homepage experience with all the essential elements for an automotive e-commerce platform:
- Hero banners for promotions
- Category sections with images/icons
- New arrivals product showcase
- Advertisement banners
- Customer testimonials
- Featured brands

## Key Features

### Modular Content Sections
- Separate models for each content type
- Flexible ordering system
- Active/inactive status control
- Rich media support (images, icons)

### Rich Content Types
- **Hero Banners**: Promotional banners with call-to-action buttons
- **Category Sections**: Product category highlights with images/icons
- **New Arrivals**: Showcase of newest products
- **Advertisements**: Scheduled promotional banners
- **Testimonials**: Customer reviews and ratings
- **Featured Brands**: Highlighted vehicle manufacturers

### Performance Optimized
- Efficient database queries
- Proper indexing
- Prefetching related data
- Clean serialization
- **Redis caching for improved performance**

### Easy Management
- Full Django admin integration
- Drag-and-drop ordering
- Status toggles
- Scheduled publishing for ads

## Models

### HeroBanner
Represents hero banners for the landing page.

Key fields:
- `title`: Banner headline
- `subtitle`: Secondary text
- `description`: Detailed description
- `image`: Background image
- `button_text`: Call-to-action text
- `button_link`: Call-to-action URL
- `is_active`: Visibility toggle
- `order`: Display order

### CategorySection
Represents category sections with images or icons.

Key fields:
- `title`: Section title
- `slug`: URL-friendly identifier
- `description`: Section description
- `category`: Link to PartCategory model
- `image`: Category image
- `icon`: Category icon
- `is_active`: Visibility toggle
- `order`: Display order

### AdvertisementBanner
Represents advertisement banners.

Key fields:
- `title`: Banner headline
- `subtitle`: Secondary text
- `description`: Detailed description
- `image`: Banner image
- `link`: Destination URL
- `is_active`: Visibility toggle
- `order`: Display order
- `start_date`: Publishing start date
- `end_date`: Publishing end date

### Testimonial
Represents customer testimonials.

Key fields:
- `name`: Customer name
- `role`: Customer role
- `company`: Customer company
- `content`: Testimonial text
- `rating`: Star rating (1-5)
- `avatar`: Customer photo
- `is_featured`: Featured status
- `order`: Display order

### LandingPageConfiguration
Site-wide configuration settings.

Key fields:
- `site_title`: Website title
- `site_tagline`: Website tagline
- `meta_description`: SEO meta description
- `favicon`: Website favicon
- `logo`: Website logo
- `footer_text`: Footer content
- `copyright_text`: Copyright notice

## API Endpoints

All endpoints return JSON data and are prefixed with `/api/landing/`.

### Main Landing Page Content
- `GET /`: Complete landing page content including all sections

### Individual Sections
- `GET /hero-banners/`: Active hero banners
- `GET /categories/`: Active category sections
- `GET /new-arrivals/`: Newest products
- `GET /advertisements/`: Active advertisement banners
- `GET /testimonials/`: Featured testimonials
- `GET /featured-brands/`: Featured brands

## Helper Utilities

The `utils.py` file provides functions for:
- Retrieving complete landing page content
- Getting individual content sections
- Initializing default content
- Creating default configuration
- **Cache management and invalidation**

## Performance Optimization

### Caching Strategy
The landing page app implements a comprehensive caching strategy using Redis to improve performance:

1. **Complete Page Content Caching**
   - Entire landing page content is cached for 15 minutes
   - Reduces database queries for frequently accessed landing page
   - Cache key: `landing_page_content`

2. **Individual Section Caching**
   - Each content section is cached separately for flexible updates
   - Hero banners: `active_hero_banners`
   - Category sections: `active_category_sections`
   - New arrivals: `new_arrival_products_{limit}`
   - Advertisements: `active_advertisements`
   - Testimonials: `featured_testimonials`
   - Featured brands: `featured_brands_{limit}`

3. **Configuration Caching**
   - Landing page configuration cached for 1 hour (changes less frequently)
   - Cache invalidation when configuration is updated

4. **Cache Invalidation**
   - Automatic cache invalidation on all content updates
   - Targeted cache clearing to minimize performance impact
   - Graceful fallback to database when cache misses occur

### Cache Keys
- `landing_page_content`: Complete landing page content
- `active_hero_banners`: Active hero banners
- `active_category_sections`: Active category sections
- `new_arrival_products_{limit}`: New arrival products with limit
- `active_advertisements`: Active advertisement banners
- `featured_testimonials`: Featured testimonials
- `featured_brands_{limit}`: Featured brands with limit

### Configuration
Cache timeouts can be customized by setting these variables in settings.py:
- `LANDING_CONTENT_CACHE_TIMEOUT`: Timeout for content (default: 900 seconds/15 minutes)
- `LANDING_CONFIG_CACHE_TIMEOUT`: Timeout for configuration (default: 3600 seconds/1 hour)

## Best Practices Implemented

1. **Data Integrity**
   - Proper foreign key relationships
   - Data validation
   - Unique constraints where appropriate

2. **Performance**
   - Proper indexing on frequently queried fields
   - Efficient querying patterns
   - Select/prefetch related optimizations
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
       'landing',
       ...
   ]
   ```

2. Add to `urls.py`:
   ```python
   urlpatterns = [
       ...
       path('landing/', include('landing.urls')),
       ...
   ]
   ```

3. Run migrations:
   ```bash
   python manage.py makemigrations landing
   python manage.py migrate landing
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

### Getting Landing Page Content
```python
from landing.utils import get_landing_page_content

content = get_landing_page_content()
hero_banners = content['hero_banners']
categories = content['categories']
```

### Creating a Hero Banner
```python
from landing.models import HeroBanner

banner = HeroBanner.objects.create(
    title="Summer Sale",
    subtitle="Up to 50% off on selected items",
    description="Limited time offer on premium automotive parts",
    button_text="Shop Sale",
    button_link="/products/",
    order=1
)
```

### Cache Invalidation
Cache is automatically invalidated when content is updated, but you can manually invalidate:
```python
from landing.utils import invalidate_landing_page_cache

# Manually clear all landing page cache
invalidate_landing_page_cache()
```