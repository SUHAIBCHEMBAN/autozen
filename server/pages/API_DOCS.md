# Pages API Documentation

## Overview

The Pages API provides access to static content pages and FAQ information for the AutoZen platform. All endpoints implement Redis caching for improved performance.

## Base URL

```
/api/pages/
```

## Endpoints

### List All Active Pages

```
GET /api/pages/
```

Retrieves a list of all active pages with caching enabled.

#### Response

```json
{
  "pages": [
    {
      "id": 1,
      "title": "About Us",
      "slug": "about-us",
      "content": "Our company story...",
      "page_type": "about",
      "is_active": true,
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z"
    }
  ]
}
```

#### Caching

- Cache Key: `active_pages`
- Timeout: 15 minutes
- Cache is automatically invalidated when any page is created, updated, or deleted

---

### Retrieve Page by Slug

```
GET /api/pages/{slug}/
```

Retrieves a specific page by its slug with caching enabled.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| slug | string | The unique slug identifier for the page |

#### Response

```json
{
  "id": 1,
  "title": "About Us",
  "slug": "about-us",
  "content": "Our company story...",
  "page_type": "about",
  "is_active": true,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

#### Error Responses

- 404: Page not found or inactive

#### Caching

- Cache Key: `page_{slug}`
- Timeout: 15 minutes
- Cache is automatically invalidated when the specific page is updated or deleted

---

### Retrieve Page by Type

```
GET /api/pages/type/{page_type}/
```

Retrieves a specific page by its type with caching enabled.

#### Parameters

| Name | Type | Description |
|------|------|-------------|
| page_type | string | The type of page (about, terms, privacy, refund, faq) |

#### Response

```json
{
  "id": 1,
  "title": "About Us",
  "slug": "about-us",
  "content": "Our company story...",
  "page_type": "about",
  "is_active": true,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

#### Error Responses

- 404: Page not found or inactive

#### Caching

- Cache Key: `page_type_{page_type}`
- Timeout: 15 minutes
- Cache is automatically invalidated when the specific page is updated or deleted

---

### List All Active FAQs

```
GET /api/pages/faqs/
```

Retrieves a list of all active FAQs with caching enabled.

#### Response

```json
{
  "faqs": [
    {
      "id": 1,
      "question": "How do I return an item?",
      "answer": "You can return items within 30 days...",
      "is_active": true,
      "order": 1,
      "created_at": "2023-01-01T12:00:00Z",
      "updated_at": "2023-01-01T12:00:00Z"
    }
  ]
}
```

#### Caching

- Cache Key: `active_faqs`
- Timeout: 15 minutes
- Cache is automatically invalidated when any FAQ is created, updated, or deleted

---

## Caching Strategy

The Pages API implements a comprehensive caching strategy using Redis to improve performance:

### Cache Keys

- `active_pages`: List of all active pages
- `page_{slug}`: Individual page by slug
- `page_type_{type}`: Page by type
- `active_faqs`: List of all active FAQs

### Cache Invalidation

Cache is automatically invalidated when content is updated:

1. **Page Updates**: When a page is created, updated, or deleted, the following cache keys are invalidated:
   - `active_pages`
   - `page_{slug}` (for the specific page)
   - `page_type_{type}` (for the specific page type)

2. **FAQ Updates**: When an FAQ is created, updated, or deleted, the following cache keys are invalidated:
   - `active_faqs`

### Configuration

Cache timeouts can be customized by setting these variables in settings.py:

- `PAGES_CONTENT_CACHE_TIMEOUT`: Timeout for content (default: 900 seconds/15 minutes)