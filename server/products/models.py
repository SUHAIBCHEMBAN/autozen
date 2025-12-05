from django.db import models
from django.utils.text import slugify
from django.core.cache import cache


class Brand(models.Model):
    """Represents a vehicle brand/manufacturer"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brands/logos/', blank=True, null=True)
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
        # Invalidate related cache when brand is updated
        from .cache_utils import invalidate_brand_cache
        invalidate_brand_cache(self.id)

    def delete(self, *args, **kwargs):
        # Invalidate related cache when brand is deleted
        from .cache_utils import invalidate_brand_cache
        invalidate_brand_cache(self.id)
        super().delete(*args, **kwargs)

    def invalidate_cache(self):
        """Invalidate cache entries related to this brand"""
        from .cache_utils import invalidate_brand_cache
        invalidate_brand_cache(self.id)

    @classmethod
    def get_cached_by_id(cls, brand_id):
        """
        Get a Brand instance by ID with caching.
        
        Args:
            brand_id (int): The ID of the brand
            
        Returns:
            Brand: The brand instance or None if not found
        """
        cache_key = f'brand_instance_{brand_id}'
        cached_brand = cache.get(cache_key)
        
        if cached_brand is not None:
            return cached_brand
            
        try:
            brand = cls.objects.get(id=brand_id)
            cache.set(cache_key, brand, 60 * 15)  # Cache for 15 minutes
            return brand
        except cls.DoesNotExist:
            return None
    
    def __str__(self):
        return self.name


class VehicleModel(models.Model):
    """Represents a specific vehicle model"""
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    year_from = models.PositiveIntegerField()
    year_to = models.PositiveIntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='models/images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_vehicle_models'
        verbose_name = 'Vehicle Model'
        verbose_name_plural = 'Vehicle Models'
        ordering = ['brand', 'name']
        unique_together = ['brand', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        # Invalidate related cache when vehicle model is updated
        from .cache_utils import invalidate_model_cache
        invalidate_model_cache(self.id, self.brand_id)

    def delete(self, *args, **kwargs):
        # Invalidate related cache when vehicle model is deleted
        from .cache_utils import invalidate_model_cache
        invalidate_model_cache(self.id, self.brand_id)
        super().delete(*args, **kwargs)

    def invalidate_cache(self):
        """Invalidate cache entries related to this vehicle model"""
        from .cache_utils import invalidate_model_cache
        invalidate_model_cache(self.id, self.brand_id)

    @classmethod
    def get_cached_by_id(cls, model_id):
        """
        Get a VehicleModel instance by ID with caching.
        
        Args:
            model_id (int): The ID of the vehicle model
            
        Returns:
            VehicleModel: The vehicle model instance or None if not found
        """
        cache_key = f'vehicle_model_instance_{model_id}'
        cached_model = cache.get(cache_key)
        
        if cached_model is not None:
            return cached_model
            
        try:
            model = cls.objects.select_related('brand').get(id=model_id)
            cache.set(cache_key, model, 60 * 15)  # Cache for 15 minutes
            return model
        except cls.DoesNotExist:
            return None
    
    def __str__(self):
        if self.year_to:
            return f"{self.brand.name} {self.name} ({self.year_from}-{self.year_to})"
        return f"{self.brand.name} {self.name} ({self.year_from}-Present)"


class PartCategory(models.Model):
    """Represents a part category in a hierarchical structure"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='subcategories')
    image = models.ImageField(upload_to='categories/images/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_part_categories'
        verbose_name = 'Part Category'
        verbose_name_plural = 'Part Categories'
        ordering = ['name']
        unique_together = ['parent', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        # Invalidate related cache when part category is updated
        from .cache_utils import invalidate_category_cache
        invalidate_category_cache(self.id, self.parent_id)

    def delete(self, *args, **kwargs):
        # Invalidate related cache when part category is deleted
        from .cache_utils import invalidate_category_cache
        invalidate_category_cache(self.id, self.parent_id)
        super().delete(*args, **kwargs)

    def invalidate_cache(self):
        """Invalidate cache entries related to this part category"""
        from .cache_utils import invalidate_category_cache
        invalidate_category_cache(self.id, self.parent_id)

    @classmethod
    def get_cached_by_id(cls, category_id):
        """
        Get a PartCategory instance by ID with caching.
        
        Args:
            category_id (int): The ID of the part category
            
        Returns:
            PartCategory: The part category instance or None if not found
        """
        cache_key = f'part_category_instance_{category_id}'
        cached_category = cache.get(cache_key)
        
        if cached_category is not None:
            return cached_category
            
        try:
            category = cls.objects.get(id=category_id)
            cache.set(cache_key, category, 60 * 15)  # Cache for 15 minutes
            return category
        except cls.DoesNotExist:
            return None

    def is_parent(self):
        """
        Check if this category is a parent category (has subcategories) with caching.
        
        Returns:
            bool: True if category has subcategories, False otherwise
        """
        cache_key = f'part_category_is_parent_{self.id}'
        cached_result = cache.get(cache_key)
        
        if cached_result is not None:
            return cached_result
            
        result = self.subcategories.exists()
        cache.set(cache_key, result, 60 * 15)  # Cache for 15 minutes
        return result

    def get_full_path(self):
        """
        Get the full hierarchical path of the category with caching.
        
        Returns:
            str: The full path of the category
        """
        cache_key = f'part_category_full_path_{self.id}'
        cached_path = cache.get(cache_key)
        
        if cached_path is not None:
            return cached_path
            
        path_parts = []
        current = self
        while current:
            path_parts.insert(0, current.name)
            current = current.parent
        path = ' > '.join(path_parts)
        cache.set(cache_key, path, 60 * 15)  # Cache for 15 minutes
        return path

    def __str__(self):
        return self.get_full_path() if self.parent else self.name


class Product(models.Model):
    """Represents a product in the store"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    short_description = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    featured_image = models.ImageField(upload_to='products/featured/', blank=True, null=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Relationships
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='products')
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, related_name='products')
    part_category = models.ForeignKey(PartCategory, on_delete=models.CASCADE, related_name='products')
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        # Invalidate related cache when product is updated
        from .cache_utils import invalidate_product_cache
        invalidate_product_cache(self.id)

    def delete(self, *args, **kwargs):
        # Invalidate related cache when product is deleted
        from .cache_utils import invalidate_product_cache
        invalidate_product_cache(self.id)
        super().delete(*args, **kwargs)

    @property
    def amount_saved(self):
        """Calculate the amount saved when compare price is higher than price"""
        if self.compare_price and self.compare_price > self.price:
            return self.compare_price - self.price
        return 0

    @property
    def discount_percentage(self):
        """Calculate the discount percentage when compare price is higher than price"""
        if self.compare_price and self.compare_price > self.price:
            return int(((self.compare_price - self.price) / self.compare_price) * 100)
        return 0

    @property
    def is_in_stock(self):
        """Check if product is in stock"""
        return self.stock_quantity > 0

    def __str__(self):
        return f"{self.name} ({self.sku})"