# Landing Page API Documentation

This document provides detailed information about the Landing Page API endpoints for your automotive e-commerce platform.

## Base URL

All endpoints are prefixed with `/landing/`.

## Authentication

Most endpoints are publicly accessible. No authentication required.

## Landing Page Endpoints

### Get Complete Landing Page Content
```
GET /landing/
```

**Response:**
```json
{
  "configuration": {
    "id": 1,
    "site_title": "AutoZen",
    "site_tagline": "Premium Automotive Spare Parts",
    "meta_description": "Your trusted partner for automotive spare parts and accessories",
    "favicon": null,
    "logo": null,
    "footer_text": "",
    "copyright_text": "",
    "created_at": "2025-12-03T10:00:00Z",
    "updated_at": "2025-12-03T10:00:00Z"
  },
  "hero_banners": [
    {
      "id": 1,
      "title": "Premium Automotive Parts",
      "subtitle": "Quality spare parts for all vehicle models",
      "description": "Discover our extensive collection of genuine and aftermarket parts",
      "image": null,
      "button_text": "Shop Now",
      "button_link": "",
      "is_active": true,
      "order": 1,
      "created_at": "2025-12-03T10:00:00Z",
      "updated_at": "2025-12-03T10:00:00Z"
    }
  ],
  "categories": [
    {
      "id": 1,
      "title": "Engine Parts",
      "slug": "engine-parts",
      "description": "",
      "category": {
        "id": 1,
        "name": "Engine Parts",
        "slug": "engine-parts",
        "description": "",
        "parent": null,
        "image": null,
        "is_active": true,
        "created_at": "2025-12-02T06:39:00Z",
        "updated_at": "2025-12-02T06:39:00Z",
        "url": "http://localhost:8000/api/products/categories/engine-parts/",
        "subcategories_count": 2,
        "is_parent_category": true,
        "full_path": "Engine Parts"
      },
      "image": null,
      "icon": null,
      "is_active": true,
      "order": 1,
      "created_at": "2025-12-03T10:00:00Z",
      "updated_at": "2025-12-03T10:00:00Z"
    }
  ],
  "featured_products": [
    {
      "id": 1,
      "name": "Innova Crysta Leather Steering Wheel",
      "slug": "innova-crysta-leather-steering-wheel",
      "short_description": "Premium leather steering wheel for Toyota Innova Crysta with comfortable grip and elegant design.",
      "featured_image": null,
      "sku": "TOY-INN-SW-001",
      "price": "85.99",
      "compare_price": "120.00",
      "is_active": true,
      "is_featured": true,
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
    }
  ],
  "advertisements": [],
  "testimonials": [
    {
      "id": 1,
      "name": "John Smith",
      "role": "Car Enthusiast",
      "company": "Auto Club",
      "content": "The quality of parts from AutoZen is exceptional. My Toyota runs smoother than ever!",
      "rating": 5,
      "avatar": null,
      "is_featured": true,
      "order": 1,
      "created_at": "2025-12-03T10:00:00Z",
      "updated_at": "2025-12-03T10:00:00Z"
    }
  ],
  "featured_brands": [
    {
      "id": 1,
      "name": "Toyota",
      "slug": "toyota",
      "description": "",
      "logo": null,
      "is_active": true,
      "created_at": "2025-12-02T06:39:00Z",
      "updated_at": "2025-12-02T06:39:00Z",
      "url": "http://localhost:8000/api/products/brands/toyota/",
      "models_count": 1
    }
  ]
}
```

### Get Hero Banners
```
GET /landing/hero-banners/
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Premium Automotive Parts",
    "subtitle": "Quality spare parts for all vehicle models",
    "description": "Discover our extensive collection of genuine and aftermarket parts",
    "image": null,
    "button_text": "Shop Now",
    "button_link": "",
    "is_active": true,
    "order": 1,
    "created_at": "2025-12-03T10:00:00Z",
    "updated_at": "2025-12-03T10:00:00Z"
  }
]
```

### Get Category Sections
```
GET /landing/categories/
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Engine Parts",
    "slug": "engine-parts",
    "description": "",
    "category": {
      "id": 1,
      "name": "Engine Parts",
      "slug": "engine-parts",
      "description": "",
      "parent": null,
      "image": null,
      "is_active": true,
      "created_at": "2025-12-02T06:39:00Z",
      "updated_at": "2025-12-02T06:39:00Z",
      "url": "http://localhost:8000/api/products/categories/engine-parts/",
      "subcategories_count": 2,
      "is_parent_category": true,
      "full_path": "Engine Parts"
    },
    "image": null,
    "icon": null,
    "is_active": true,
    "order": 1,
    "created_at": "2025-12-03T10:00:00Z",
    "updated_at": "2025-12-03T10:00:00Z"
  }
]
```

### Get New Arrivals
```
GET /landing/new-arrivals/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Innova Crysta Leather Steering Wheel",
    "slug": "innova-crysta-leather-steering-wheel",
    "short_description": "Premium leather steering wheel for Toyota Innova Crysta with comfortable grip and elegant design.",
    "featured_image": null,
    "sku": "TOY-INN-SW-001",
    "price": "85.99",
    "compare_price": "120.00",
    "is_active": true,
    "is_featured": true,
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
  }
]
```

### Get Advertisements
```
GET /landing/advertisements/
```

**Response:**
```json
[]
```

### Get Testimonials
```
GET /landing/testimonials/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "John Smith",
    "role": "Car Enthusiast",
    "company": "Auto Club",
    "content": "The quality of parts from AutoZen is exceptional. My Toyota runs smoother than ever!",
    "rating": 5,
    "avatar": null,
    "is_featured": true,
    "order": 1,
    "created_at": "2025-12-03T10:00:00Z",
    "updated_at": "2025-12-03T10:00:00Z"
  }
]
```

### Get Featured Brands
```
GET /landing/featured-brands/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Toyota",
    "slug": "toyota",
    "description": "",
    "logo": null,
    "is_active": true,
    "created_at": "2025-12-02T06:39:00Z",
    "updated_at": "2025-12-02T06:39:00Z",
    "url": "http://localhost:8000/api/products/brands/toyota/",
    "models_count": 1
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

Or for custom errors:
```json
{
  "error": "Error message"
}
```

## Example Usage

### Get complete landing page content
```bash
curl -X GET \
  http://localhost:8000/landing/
```

### Get hero banners
```bash
curl -X GET \
  http://localhost:8000/landing/hero-banners/
```

### Get new arrivals
```bash
curl -X GET \
  http://localhost:8000/landing/new-arrivals/
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Exceeding the limit will result in a 429 Too Many Requests response.

## Implementation Details

### Models

1. **HeroBanner**: Represents hero banners for the landing page
   - Title, subtitle, description
   - Image and button configuration
   - Active status and ordering

2. **CategorySection**: Represents category sections with images/icons
   - Title and description
   - Link to PartCategory model
   - Image and icon support
   - Active status and ordering

3. **AdvertisementBanner**: Represents advertisement banners
   - Title, subtitle, description
   - Image and link
   - Scheduled publishing (start/end dates)
   - Active status and ordering

4. **Testimonial**: Represents customer testimonials
   - Customer name, role, company
   - Testimonial content and rating
   - Avatar image
   - Featured status and ordering

5. **LandingPageConfiguration**: Site-wide configuration
   - Site title, tagline, meta description
   - Logo and favicon
   - Footer and copyright text

### Features

- **Modular Design**: Separate endpoints for each section
- **Flexible Content**: Easily customizable through admin interface
- **Performance Optimized**: Efficient database queries
- **Scheduled Publishing**: Time-based advertisement banners
- **Rich Media Support**: Images for all content types
- **Ordering System**: Customizable display order
- **Redis Caching**: Comprehensive caching strategy for improved performance

### Security

- Publicly accessible endpoints
- Admin interface protected by Django authentication
- Data validation
- Image upload security

### Performance

- Database indexing on frequently queried fields
- Efficient serialization
- Prefetching related objects
- Proper use of select_related
- **Redis caching for frequently accessed data**
- **Automatic cache invalidation on content updates**

### Caching Strategy

The landing page API implements a comprehensive caching strategy using Redis to improve performance:

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

## Integration with Other Systems

The landing page system integrates with:

1. **Product System**: Links to Product and PartCategory models
2. **Brand System**: Displays featured brands
3. **Admin System**: Fully manageable through Django admin

## Extensibility

The system can be easily extended to:

- Add newsletter signup functionality
- Implement dynamic content blocks
- Add social media integration
- Create seasonal landing pages
- Add analytics tracking