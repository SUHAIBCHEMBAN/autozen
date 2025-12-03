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
- `category`: Linked PartCategory
- `image`: Category image
- `icon`: Category icon
- `is_active`: Visibility toggle
- `order`: Display order

### AdvertisementBanner
Represents advertisement banners with scheduling.

Key fields:
- `title`: Banner headline
- `subtitle`: Secondary text
- `description`: Detailed description
- `image`: Banner image
- `link`: Destination URL
- `is_active`: Visibility toggle
- `order`: Display order
- `start_date`: Publication start
- `end_date`: Publication end

### Testimonial
Represents customer testimonials.

Key fields:
- `name`: Customer name
- `role`: Customer role/title
- `company`: Customer company
- `content`: Testimonial text
- `rating`: Star rating (1-5)
- `avatar`: Customer photo
- `is_featured`: Featured status
- `order`: Display order

### LandingPageConfiguration
Site-wide landing page configuration.

Key fields:
- `site_title`: Website title
- `site_tagline`: Website tagline
- `meta_description`: SEO meta description
- `favicon`: Website favicon
- `logo`: Website logo
- `footer_text`: Footer content
- `copyright_text`: Copyright notice

## API Endpoints

See [API_DOCS.md](API_DOCS.md) for detailed API documentation.

## Admin Interface

All models are registered in the Django admin with:
- Custom list displays with relevant information
- Filtering by key attributes
- Search functionality
- Drag-and-drop ordering
- Status toggles
- Scheduled publishing controls
- Rich text editors where appropriate

## Management Commands

### init_landing
Initialize the landing page with sample data:
```bash
python manage.py init_landing
```

## Helper Utilities

The `utils.py` file provides functions for:
- Retrieving complete landing page content
- Getting individual content sections
- Initializing default content
- Creating default configuration

## Best Practices Implemented

1. **Data Integrity**
   - Proper foreign key relationships
   - Data validation
   - Unique constraints where appropriate

2. **Performance**
   - Proper indexing on frequently queried fields
   - Efficient querying patterns
   - Select/prefetch related optimizations

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

### Getting New Arrivals
```python
from landing.utils import get_new_arrival_products

new_products = get_new_arrival_products(limit=12)
```

## API Integration

### Frontend Integration Example
```javascript
// Get complete landing page content
fetch('/landing/')
  .then(response => response.json())
  .then(data => {
    console.log('Hero banners:', data.hero_banners);
    console.log('Categories:', data.categories);
    console.log('New arrivals:', data.featured_products);
    console.log('Testimonials:', data.testimonials);
  });

// Get hero banners only
fetch('/landing/hero-banners/')
  .then(response => response.json())
  .then(banners => {
    // Render hero banner carousel
  });
```

## Content Management

### Admin Workflow
1. **Configure Site**: Set up site title, logo, and meta information
2. **Add Hero Banners**: Create promotional banners for homepage
3. **Set Up Categories**: Link product categories to visual sections
4. **Upload Ads**: Schedule promotional banners
5. **Add Testimonials**: Collect and showcase customer reviews
6. **Feature Brands**: Highlight popular vehicle manufacturers

### Content Strategy
- **Hero Banners**: Rotate 2-3 promotional banners
- **Categories**: Highlight 6-12 most popular categories
- **New Arrivals**: Showcase 8-12 newest products
- **Advertisements**: 2-4 active campaigns at a time
- **Testimonials**: Feature 3-6 best reviews
- **Brands**: Showcase 8-12 popular manufacturers

## Integration with Other Systems

The landing page system integrates with:

1. **Product System**: Links to Product and PartCategory models
2. **Brand System**: Displays featured brands
3. **Admin System**: Fully manageable through Django admin
4. **Frontend**: Provides structured data for React components

## Extending the App

The modular design makes it easy to extend:
- Add newsletter signup functionality
- Implement dynamic content blocks
- Add social media integration
- Create seasonal landing pages
- Add analytics tracking
- Implement A/B testing for banners

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests if applicable
5. Submit a pull request

## License

[Your license information here]