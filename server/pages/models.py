from django.db import models
from django.utils.text import slugify

class Page(models.Model):
    """Model representing a static page in the AutoZen platform."""
    
    PAGE_TYPES = [
        ('about', 'About'),
        ('terms', 'Terms & Conditions'),
        ('refund', 'Return, Refund & Safety Tips'),
        ('privacy', 'Privacy Policy'),
        ('faq', 'FAQs'),
    ]
    
    title = models.CharField(max_length=200, help_text="Title of the page")
    slug = models.SlugField(max_length=200, unique=True, blank=True, help_text="URL-friendly identifier for the page")
    content = models.TextField(help_text="Main content of the page")
    page_type = models.CharField(max_length=20, choices=PAGE_TYPES, help_text="Type/category of the page")
    is_active = models.BooleanField(default=True, help_text="Whether this page is currently active and visible")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the page was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the page was last updated")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Page'
        verbose_name_plural = 'Pages'
        
    def save(self, *args, **kwargs):
        """Save the page and invalidate related cache entries."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        # Invalidate cache when page is updated
        self.invalidate_cache()
    
    def delete(self, *args, **kwargs):
        """Delete the page and invalidate related cache entries."""
        # Invalidate cache when page is deleted
        self.invalidate_cache()
        super().delete(*args, **kwargs)
    
    def invalidate_cache(self):
        """
        Invalidate cache entries related to this page.
        
        This method clears cache entries for this specific page and general
        page lists to ensure data consistency when page content changes.
        """
        from django.core.cache import cache
        cache_keys = [
            'active_pages',
            f'page_{self.slug}',
            f'page_type_{self.page_type}',
        ]
        cache.delete_many(cache_keys)
    
    def __str__(self):
        """Return the string representation of the page."""
        return self.title

class FAQ(models.Model):
    """Model representing a Frequently Asked Question."""
    
    question = models.CharField(max_length=300, help_text="The FAQ question")
    answer = models.TextField(help_text="The FAQ answer")
    is_active = models.BooleanField(default=True, help_text="Whether this FAQ is currently active and visible")
    order = models.IntegerField(default=0, help_text="Display order for the FAQ (lower numbers first)")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the FAQ was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the FAQ was last updated")
    
    class Meta:
        ordering = ['order', 'created_at']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'
        
    def save(self, *args, **kwargs):
        """Save the FAQ and invalidate related cache entries."""
        super().save(*args, **kwargs)
        # Invalidate FAQs cache when FAQ is updated
        self.invalidate_cache()
    
    def delete(self, *args, **kwargs):
        """Delete the FAQ and invalidate related cache entries."""
        # Invalidate FAQs cache when FAQ is deleted
        self.invalidate_cache()
        super().delete(*args, **kwargs)
    
    def invalidate_cache(self):
        """
        Invalidate cache entries related to FAQs.
        
        This method clears cache entries for FAQs to ensure data consistency
        when FAQ content changes.
        """
        from django.core.cache import cache
        cache_keys = [
            'active_faqs',
        ]
        cache.delete_many(cache_keys)
        
    def __str__(self):
        """Return the string representation of the FAQ."""
        return self.question