# API Consistency Across Apps

This document explains the changes made to ensure consistent API design across all Django apps in the project.

## Why Router-Based URLs Are Better

The router-based approach offers several advantages over manual URL configuration:

1. **Consistency**: All apps follow the same pattern, making the codebase easier to understand and maintain
2. **Automatic URL Generation**: DRF routers automatically generate standardized URLs for common operations
3. **Reduced Boilerplate**: Less manual configuration required for basic CRUD operations
4. **Standardized Naming**: Consistent naming conventions for URLs and reverse lookups
5. **Extensibility**: Easy to add new endpoints and functionality
6. **Best Practices**: Aligns with Django REST Framework conventions

## Changes Made

### Users App
- Kept existing class-based views since they implement custom logic (OTP sending/verification)
- Added router imports for consistency
- Maintained existing URL structure but prepared for future ViewSet conversion

### Pages App
- Converted existing class-based views to ViewSets for better organization
- Implemented router-based URL configuration
- Maintained all existing functionality while improving structure

### Products App
- Already implemented with ViewSets and router-based URLs

## New URL Structures

### Users App (unchanged functionality)
- `/api/auth/send-otp/` - POST to send OTP
- `/api/auth/verify-otp/` - POST to verify OTP

### Pages App (improved structure)
- `/api/pages/pages/` - List all pages
- `/api/pages/pages/{slug}/` - Retrieve specific page by slug
- `/api/pages/pages/type/{page_type}/` - Retrieve page by type
- `/api/pages/faqs/` - List all FAQs

### Products App (unchanged)
- `/api/products/brands/` - Brand operations
- `/api/products/models/` - Vehicle model operations
- `/api/products/categories/` - Category operations
- `/api/products/products/` - Product operations

## Benefits of This Approach

1. **Uniform API Design**: All apps now follow the same structural pattern
2. **Future Scalability**: Easy to add new endpoints as ViewSets
3. **Maintainability**: Standardized structure reduces cognitive load
4. **Developer Experience**: Consistent patterns make development faster
5. **Documentation**: Uniform structure simplifies API documentation

## Migration Notes

Existing clients using the previous URLs will need to update their endpoints:
- Pages app URLs have moved from `/pages/` to `/api/pages/`
- Page detail URLs remain the same (`{slug}/`)
- FAQ URLs have changed from `/pages/faq/list/` to `/api/pages/faqs/`

## Future Improvements

Consider converting the users app to ViewSets when additional functionality is needed:
- User registration endpoint
- Profile management endpoints
- Password reset functionality
- Social authentication endpoints

This would allow leveraging the full power of DRF's ViewSet features like:
- Automatic OPTIONS responses
- Built-in filtering and pagination
- Standardized error handling
- Reduced code duplication