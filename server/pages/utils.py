"""
Utility functions for the pages app with Redis caching support
"""

from django.core.cache import cache
from django.conf import settings

# Cache timeout settings
PAGES_CONTENT_CACHE_TIMEOUT = getattr(settings, 'PAGES_CONTENT_CACHE_TIMEOUT', 60 * 15)  # 15 minutes


def get_active_pages():
    """
    Get all active pages with Redis caching.
    
    This function retrieves all active pages from cache if available,
    otherwise fetches from database and stores in cache for future requests.
    
    Returns:
        QuerySet: Active Page objects ordered by creation date
    """
    cache_key = 'active_pages'
    cached_pages = cache.get(cache_key)
    
    if cached_pages is not None:
        return cached_pages
    
    # Import model inside function to avoid circular imports
    from .models import Page
    pages = Page.objects.filter(is_active=True).order_by('-created_at')
    cache.set(cache_key, pages, PAGES_CONTENT_CACHE_TIMEOUT)
    return pages


def get_page_by_slug(slug):
    """
    Get a specific page by slug with Redis caching.
    
    This function retrieves a page by its slug from cache if available,
    otherwise fetches from database and stores in cache for future requests.
    
    Args:
        slug (str): The slug of the page to retrieve
        
    Returns:
        Page: The Page object or None if not found
    """
    cache_key = f'page_{slug}'
    cached_page = cache.get(cache_key)
    
    if cached_page is not None:
        return cached_page
    
    # Import model inside function to avoid circular imports
    from .models import Page
    try:
        page = Page.objects.filter(is_active=True).get(slug=slug)
        cache.set(cache_key, page, PAGES_CONTENT_CACHE_TIMEOUT)
        return page
    except Page.DoesNotExist:
        return None


def get_page_by_type(page_type):
    """
    Get a specific page by type with Redis caching.
    
    This function retrieves a page by its type from cache if available,
    otherwise fetches from database and stores in cache for future requests.
    
    Args:
        page_type (str): The type of the page to retrieve
        
    Returns:
        Page: The Page object or None if not found
    """
    cache_key = f'page_type_{page_type}'
    cached_page = cache.get(cache_key)
    
    if cached_page is not None:
        return cached_page
    
    # Import model inside function to avoid circular imports
    from .models import Page
    try:
        page = Page.objects.filter(is_active=True).get(page_type=page_type)
        cache.set(cache_key, page, PAGES_CONTENT_CACHE_TIMEOUT)
        return page
    except Page.DoesNotExist:
        return None


def get_active_faqs():
    """
    Get all active FAQs with Redis caching.
    
    This function retrieves all active FAQs from cache if available,
    otherwise fetches from database and stores in cache for future requests.
    
    Returns:
        QuerySet: Active FAQ objects ordered by display order and creation date
    """
    cache_key = 'active_faqs'
    cached_faqs = cache.get(cache_key)
    
    if cached_faqs is not None:
        return cached_faqs
    
    # Import model inside function to avoid circular imports
    from .models import FAQ
    faqs = FAQ.objects.filter(is_active=True).order_by('order', '-created_at')
    cache.set(cache_key, faqs, PAGES_CONTENT_CACHE_TIMEOUT)
    return faqs


def invalidate_pages_cache():
    """
    Invalidate all pages-related cache entries.
    
    This method clears all cache keys related to pages content to ensure
    data consistency when pages content is updated.
    """
    cache_keys = [
        'active_pages',
        'active_faqs',
    ]
    # Also clear individual page caches
    from .models import Page, FAQ
    try:
        pages = Page.objects.all()
        for page in pages:
            cache_keys.append(f'page_{page.slug}')
            cache_keys.append(f'page_type_{page.page_type}')
    except:
        pass  # If there's an error, just clear what we can
    
    cache.delete_many(cache_keys)


def invalidate_page_cache(slug):
    """
    Invalidate cache for a specific page.
    
    This method clears the cache for a specific page by its slug.
    
    Args:
        slug (str): The slug of the page to invalidate cache for
    """
    cache_keys = [
        f'page_{slug}',
    ]
    # Also try to get the page type to invalidate that cache too
    try:
        from .models import Page
        page = Page.objects.get(slug=slug)
        cache_keys.append(f'page_type_{page.page_type}')
    except Page.DoesNotExist:
        pass
    
    cache.delete_many(cache_keys)