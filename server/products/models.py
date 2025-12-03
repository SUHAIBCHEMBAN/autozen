from django.db import models
from django.utils.text import slugify
from django.urls import reverse


class Brand(models.Model):
    """
    Represents a vehicle brand/manufacture (e.g., Toyota, Honda, Ford)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_brands'
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('products:brand-detail', kwargs={'slug': self.slug})


class VehicleModel(models.Model):
    """
    Represents a specific vehicle model (e.g., Innova Crysta, Civic, F-150)
    """
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    year_from = models.PositiveIntegerField(help_text="Manufacturing start year")
    year_to = models.PositiveIntegerField(help_text="Manufacturing end year (leave blank for ongoing)", blank=True, null=True)
    image = models.ImageField(upload_to='models/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_vehicle_models'
        verbose_name = 'Vehicle Model'
        verbose_name_plural = 'Vehicle Models'
        unique_together = ['brand', 'name']
        ordering = ['brand', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand.name}-{self.name}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.brand.name} {self.name}"

    def get_absolute_url(self):
        return reverse('products:model-detail', kwargs={'brand_slug': self.brand.slug, 'slug': self.slug})


class PartCategory(models.Model):
    """
    Represents a part category/type (e.g., Steering Wheel, Brake Pad, Engine Oil)
    Supports hierarchical categories (e.g., Engine -> Engine Parts -> Pistons)
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_part_categories'
        verbose_name = 'Part Category'
        verbose_name_plural = 'Part Categories'
        unique_together = ['name', 'parent']
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def get_absolute_url(self):
        return reverse('products:category-detail', kwargs={'slug': self.slug})

    @property
    def is_parent(self):
        """Check if category is a parent (has no parent itself)"""
        return self.parent is None

    @property
    def get_full_path(self):
        """Get full category path as a string (e.g., 'Engine > Engine Parts > Pistons')"""
        path = [self.name]
        parent = self.parent
        while parent:
            path.append(parent.name)
            parent = parent.parent
        return ' > '.join(reversed(path))


class Product(models.Model):
    """
    Represents a product in the automotive spare parts store
    """
    # Basic product information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, blank=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    
    # Vehicle compatibility - the hierarchical structure
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, related_name='products')
    part_category = models.ForeignKey(PartCategory, on_delete=models.CASCADE, related_name='products')
    
    # Product attributes
    sku = models.CharField(max_length=100, unique=True, help_text="Stock Keeping Unit")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, 
                                       help_text="Original price for comparison")
    cost_per_item = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    track_inventory = models.BooleanField(default=True)
    continue_selling = models.BooleanField(default=False, 
                                          help_text="Continue selling when out of stock")
    
    # Media
    featured_image = models.ImageField(upload_to='products/', blank=True, null=True)
    gallery_images = models.JSONField(blank=True, null=True, 
                                     help_text="JSON array of additional image URLs")
    
    # SEO and metadata
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Status and visibility
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields for automotive parts
    oem_number = models.CharField(max_length=100, blank=True, 
                                 help_text="Original Equipment Manufacturer number")
    manufacturer_part_number = models.CharField(max_length=100, blank=True)
    compatibility_notes = models.TextField(blank=True, 
                                          help_text="Additional compatibility information")
    weight = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, 
                                help_text="Weight in kg")
    dimensions = models.CharField(max_length=100, blank=True, 
                                 help_text="Dimensions (L x W x H in cm)")

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['brand', 'vehicle_model']),
            models.Index(fields=['part_category']),
            models.Index(fields=['is_active', 'is_featured']),
            models.Index(fields=['created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        # Auto-generate short description if not provided
        if not self.short_description and self.description:
            self.short_description = self.description[:297] + "..." if len(self.description) > 300 else self.description
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.vehicle_model})"

    def get_absolute_url(self):
        return reverse('products:product-detail', kwargs={
            'brand_slug': self.brand.slug,
            'model_slug': self.vehicle_model.slug,
            'slug': self.slug
        })

    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        if not self.track_inventory:
            return True
        return self.stock_quantity > 0 or self.continue_selling

    @property
    def amount_saved(self):
        """Calculate amount saved if compare price is set"""
        if self.compare_price and self.compare_price > self.price:
            return self.compare_price - self.price
        return None

    @property
    def discount_percentage(self):
        """Calculate discount percentage if compare price is set"""
        if self.compare_price and self.compare_price > self.price:
            return round(((self.compare_price - self.price) / self.compare_price) * 100)
        return None