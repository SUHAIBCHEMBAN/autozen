from django.db import models
from django.utils.text import slugify
from products.models import Brand, Product, PartCategory


class HeroBanner(models.Model):
    """
    Represents a hero banner for the landing page
    """
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='landing/hero_banners/')
    button_text = models.CharField(max_length=50, default="Shop Now")
    button_link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'landing_hero_banners'
        verbose_name = 'Hero Banner'
        verbose_name_plural = 'Hero Banners'
        ordering = ['order', '-created_at']
    
    def save(self, *args, **kwargs):
        """
        Save the hero banner and invalidate landing page cache.
        
        Overrides the default save method to ensure landing page cache
        is invalidated whenever a hero banner is created or updated.
        """
        super().save(*args, **kwargs)
        # Invalidate landing page cache when hero banner is updated
        self.invalidate_cache()
    
    def delete(self, *args, **kwargs):
        """
        Delete the hero banner and invalidate landing page cache.
        
        Overrides the default delete method to ensure landing page cache
        is invalidated whenever a hero banner is deleted.
        """
        super().delete(*args, **kwargs)
        # Invalidate landing page cache when hero banner is deleted
        self.invalidate_cache()
    
    @staticmethod
    def invalidate_cache():
        """
        Invalidate landing page cache.
        
        This method clears all cache keys related to the landing page content.
        """
        from django.core.cache import cache
        cache_keys = [
            'landing_page_content',
            'active_hero_banners',
        ]
        cache.delete_many(cache_keys)
    
    def __str__(self):
        return self.title


class FeaturedVehicle(models.Model):
    """
    Represents featured vehicles displayed as cards in the hero section
    """
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='landing/featured_vehicles/')
    hover_title = models.CharField(max_length=200, blank=True, help_text="Title shown on hover")
    hover_description = models.TextField(blank=True, help_text="Description shown on hover")
    link = models.URLField(blank=True, help_text="Link when card is clicked")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    hero_banner = models.ForeignKey(
        HeroBanner, 
        on_delete=models.CASCADE, 
        related_name='featured_vehicles',
        help_text="Hero banner this vehicle belongs to"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'landing_featured_vehicles'
        verbose_name = 'Featured Vehicle'
        verbose_name_plural = 'Featured Vehicles'
        ordering = ['order', '-created_at']
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        HeroBanner.invalidate_cache()
    
    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        HeroBanner.invalidate_cache()
    
    def __str__(self):
        return f"{self.name} - {self.hero_banner.title}"

class CategorySection(models.Model):
    """
    Represents a category section with image or icon
    """
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(PartCategory, on_delete=models.CASCADE, related_name='landing_sections')
    image = models.ImageField(upload_to='landing/categories/', blank=True, null=True)
    icon = models.ImageField(upload_to='landing/category_icons/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'landing_category_sections'
        verbose_name = 'Category Section'
        verbose_name_plural = 'Category Sections'
        ordering = ['order', '-created_at']
    
    def save(self, *args, **kwargs):
        """
        Save the category section and invalidate landing page cache.
        
        Overrides the default save method to ensure landing page cache
        is invalidated whenever a category section is created or updated.
        Also generates a slug if one doesn't exist.
        """
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        # Invalidate landing page cache when category section is updated
        self.invalidate_cache()
    
    def delete(self, *args, **kwargs):
        """
        Delete the category section and invalidate landing page cache.
        
        Overrides the default delete method to ensure landing page cache
        is invalidated whenever a category section is deleted.
        """
        super().delete(*args, **kwargs)
        # Invalidate landing page cache when category section is deleted
        self.invalidate_cache()
    
    @staticmethod
    def invalidate_cache():
        """
        Invalidate landing page cache.
        
        This method clears all cache keys related to the landing page content.
        """
        from django.core.cache import cache
        cache_keys = [
            'landing_page_content',
            'active_category_sections',
        ]
        cache.delete_many(cache_keys)
    
    def __str__(self):
        return self.title


class AdvertisementBanner(models.Model):
    """
    Represents an advertisement banner
    """
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='landing/ad_banners/')
    link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'landing_ad_banners'
        verbose_name = 'Advertisement Banner'
        verbose_name_plural = 'Advertisement Banners'
        ordering = ['order', '-created_at']
    
    def save(self, *args, **kwargs):
        """
        Save the advertisement banner and invalidate landing page cache.
        
        Overrides the default save method to ensure landing page cache
        is invalidated whenever an advertisement banner is created or updated.
        """
        super().save(*args, **kwargs)
        # Invalidate landing page cache when advertisement banner is updated
        self.invalidate_cache()
    
    def delete(self, *args, **kwargs):
        """
        Delete the advertisement banner and invalidate landing page cache.
        
        Overrides the default delete method to ensure landing page cache
        is invalidated whenever an advertisement banner is deleted.
        """
        super().delete(*args, **kwargs)
        # Invalidate landing page cache when advertisement banner is deleted
        self.invalidate_cache()
    
    @staticmethod
    def invalidate_cache():
        """
        Invalidate landing page cache.
        
        This method clears all cache keys related to the landing page content.
        """
        from django.core.cache import cache
        cache_keys = [
            'landing_page_content',
            'active_advertisements',
        ]
        cache.delete_many(cache_keys)
    
    def __str__(self):
        return self.title


class Testimonial(models.Model):
    """
    Represents a customer testimonial
    """
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    rating = models.PositiveIntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    avatar = models.ImageField(upload_to='landing/testimonials/', blank=True, null=True)
    is_featured = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'landing_testimonials'
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['order', '-created_at']
    
    def save(self, *args, **kwargs):
        """
        Save the testimonial and invalidate landing page cache.
        
        Overrides the default save method to ensure landing page cache
        is invalidated whenever a testimonial is created or updated.
        """
        super().save(*args, **kwargs)
        # Invalidate landing page cache when testimonial is updated
        self.invalidate_cache()
    
    def delete(self, *args, **kwargs):
        """
        Delete the testimonial and invalidate landing page cache.
        
        Overrides the default delete method to ensure landing page cache
        is invalidated whenever a testimonial is deleted.
        """
        super().delete(*args, **kwargs)
        # Invalidate landing page cache when testimonial is deleted
        self.invalidate_cache()
    
    @staticmethod
    def invalidate_cache():
        """
        Invalidate landing page cache.
        
        This method clears all cache keys related to the landing page content.
        """
        from django.core.cache import cache
        cache_keys = [
            'landing_page_content',
            'featured_testimonials',
        ]
        cache.delete_many(cache_keys)
    
    def __str__(self):
        return f"{self.name} - {self.company}"


class LandingPageConfiguration(models.Model):
    """
    Configuration for the landing page
    """
    site_title = models.CharField(max_length=200, default="AutoZen")
    site_tagline = models.CharField(max_length=300, blank=True)
    meta_description = models.TextField(blank=True)
    favicon = models.ImageField(upload_to='landing/favicon/', blank=True, null=True)
    logo = models.ImageField(upload_to='landing/logo/', blank=True, null=True)
    footer_text = models.TextField(blank=True)
    copyright_text = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'landing_configurations'
        verbose_name = 'Landing Page Configuration'
        verbose_name_plural = 'Landing Page Configurations'
    
    def __str__(self):
        return f"Landing Page Configuration - {self.site_title}"
    
    def save(self, *args, **kwargs):
        """
        Save the landing page configuration and invalidate landing page cache.
        
        Ensures only one configuration exists and invalidates cache when updated.
        """
        # Ensure only one configuration exists
        if not self.pk and LandingPageConfiguration.objects.exists():
            # Update existing configuration instead of creating new one
            existing = LandingPageConfiguration.objects.first()
            for field in self._meta.fields:
                if field.name not in ['id', 'created_at', 'updated_at']:
                    setattr(existing, field.name, getattr(self, field.name))
            existing.save()
            # Invalidate landing page cache when configuration is updated
            self.invalidate_cache()
            return
        super().save(*args, **kwargs)
        # Invalidate landing page cache when configuration is updated
        self.invalidate_cache()
    
    @staticmethod
    def invalidate_cache():
        """
        Invalidate landing page cache.
        
        This method clears all cache keys related to the landing page content.
        """
        from django.core.cache import cache
        cache_keys = [
            'landing_page_content',
            'landing_page_configuration',
        ]
        cache.delete_many(cache_keys)
    
    @classmethod
    def get_config(cls):
        """
        Get the landing page configuration or create default.
        
        Retrieves the existing configuration or creates a default one.
        Uses caching for improved performance.
        
        Returns:
            LandingPageConfiguration: The configuration object
        """
        config, created = cls.objects.get_or_create(
            defaults={
                'site_title': 'AutoZen',
                'site_tagline': 'Premium Automotive Spare Parts',
                'meta_description': 'Your trusted partner for automotive spare parts and accessories'
            }
        )
        return config