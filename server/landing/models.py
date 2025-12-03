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
    
    def __str__(self):
        return self.title


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
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
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
        # Ensure only one configuration exists
        if not self.pk and LandingPageConfiguration.objects.exists():
            # Update existing configuration instead of creating new one
            existing = LandingPageConfiguration.objects.first()
            for field in self._meta.fields:
                if field.name not in ['id', 'created_at', 'updated_at']:
                    setattr(existing, field.name, getattr(self, field.name))
            existing.save()
            return
        super().save(*args, **kwargs)
    
    @classmethod
    def get_config(cls):
        """Get the landing page configuration or create default"""
        config, created = cls.objects.get_or_create(
            defaults={
                'site_title': 'AutoZen',
                'site_tagline': 'Premium Automotive Spare Parts',
                'meta_description': 'Your trusted partner for automotive spare parts and accessories'
            }
        )
        return config