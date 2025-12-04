from rest_framework import serializers
from django.core.cache import cache
from .models import Brand, VehicleModel, PartCategory, Product


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model with Redis caching support"""
    url = serializers.HyperlinkedIdentityField(view_name='products:brand-detail', lookup_field='slug')
    models_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 'is_active',
            'created_at', 'updated_at', 'url', 'models_count'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_models_count(self, obj):
        """
        Get the count of models for this brand with caching.
        
        Args:
            obj (Brand): The brand object
            
        Returns:
            int: Number of models for this brand
        """
        cache_key = f'brand_models_count_{obj.id}'
        cached_count = cache.get(cache_key)
        
        if cached_count is not None:
            return cached_count
            
        count = obj.models.count()
        cache.set(cache_key, count, 60 * 15)  # Cache for 15 minutes
        return count


class BrandDetailSerializer(BrandSerializer):
    """Detailed serializer for Brand with related models and caching support"""
    models = serializers.SerializerMethodField()
    
    class Meta(BrandSerializer.Meta):
        fields = BrandSerializer.Meta.fields + ['models']
    
    def get_models(self, obj):
        """
        Get models for this brand with caching.
        
        Args:
            obj (Brand): The brand object
            
        Returns:
            list: Serialized model data
        """
        cache_key = f'brand_models_{obj.id}'
        cached_models = cache.get(cache_key)
        
        if cached_models is not None:
            return cached_models
            
        models = obj.models.all()
        result = VehicleModelSerializer(models, many=True, context=self.context).data
        cache.set(cache_key, result, 60 * 15)  # Cache for 15 minutes
        return result


class VehicleModelSerializer(serializers.ModelSerializer):
    """Serializer for VehicleModel model with Redis caching support"""
    url = serializers.HyperlinkedIdentityField(
        view_name='products:model-detail', 
        lookup_field='slug',
        lookup_url_kwarg='slug'
    )
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = VehicleModel
        fields = [
            'id', 'name', 'slug', 'description', 'year_from', 'year_to',
            'image', 'is_active', 'created_at', 'updated_at', 
            'brand', 'brand_name', 'url', 'products_count'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_products_count(self, obj):
        """
        Get the count of products for this vehicle model with caching.
        
        Args:
            obj (VehicleModel): The vehicle model object
            
        Returns:
            int: Number of products for this vehicle model
        """
        cache_key = f'vehicle_model_products_count_{obj.id}'
        cached_count = cache.get(cache_key)
        
        if cached_count is not None:
            return cached_count
            
        count = obj.products.count()
        cache.set(cache_key, count, 60 * 15)  # Cache for 15 minutes
        return count


class VehicleModelDetailSerializer(VehicleModelSerializer):
    """Detailed serializer for VehicleModel with related products and caching support"""
    products = serializers.SerializerMethodField()
    
    class Meta(VehicleModelSerializer.Meta):
        fields = VehicleModelSerializer.Meta.fields + ['products']
    
    def get_products(self, obj):
        """
        Get products for this vehicle model with caching.
        
        Args:
            obj (VehicleModel): The vehicle model object
            
        Returns:
            list: Serialized product data
        """
        cache_key = f'vehicle_model_products_{obj.id}'
        cached_products = cache.get(cache_key)
        
        if cached_products is not None:
            return cached_products
            
        products = obj.products.all()
        result = ProductListSerializer(products, many=True, context=self.context).data
        cache.set(cache_key, result, 60 * 15)  # Cache for 15 minutes
        return result


class PartCategorySerializer(serializers.ModelSerializer):
    """Serializer for PartCategory model with Redis caching support"""
    url = serializers.HyperlinkedIdentityField(view_name='products:category-detail', lookup_field='slug')
    subcategories_count = serializers.SerializerMethodField()
    is_parent_category = serializers.SerializerMethodField()  # Changed from source to method
    full_path = serializers.SerializerMethodField()  # Changed from source to method
    
    class Meta:
        model = PartCategory
        fields = [
            'id', 'name', 'slug', 'description', 'parent', 'image', 'is_active',
            'created_at', 'updated_at', 'url', 'subcategories_count', 
            'is_parent_category', 'full_path'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_subcategories_count(self, obj):
        """
        Get the count of subcategories for this part category with caching.
        
        Args:
            obj (PartCategory): The part category object
            
        Returns:
            int: Number of subcategories for this part category
        """
        cache_key = f'part_category_subcategories_count_{obj.id}'
        cached_count = cache.get(cache_key)
        
        if cached_count is not None:
            return cached_count
            
        count = obj.subcategories.count()
        cache.set(cache_key, count, 60 * 15)  # Cache for 15 minutes
        return count
    
    def get_is_parent_category(self, obj):
        """
        Get whether this category is a parent category with caching.
        
        Args:
            obj (PartCategory): The part category object
            
        Returns:
            bool: True if category has subcategories, False otherwise
        """
        return obj.is_parent()
    
    def get_full_path(self, obj):
        """
        Get the full hierarchical path of the category with caching.
        
        Args:
            obj (PartCategory): The part category object
            
        Returns:
            str: The full path of the category
        """
        return obj.get_full_path()


class PartCategoryDetailSerializer(PartCategorySerializer):
    """Detailed serializer for PartCategory with subcategories, products and caching support"""
    subcategories = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    
    class Meta(PartCategorySerializer.Meta):
        fields = PartCategorySerializer.Meta.fields + ['subcategories', 'products']
    
    def get_subcategories(self, obj):
        """
        Get subcategories for this part category with caching.
        
        Args:
            obj (PartCategory): The part category object
            
        Returns:
            list: Serialized subcategory data
        """
        cache_key = f'part_category_subcategories_{obj.id}'
        cached_subcategories = cache.get(cache_key)
        
        if cached_subcategories is not None:
            return cached_subcategories
            
        subcategories = obj.subcategories.all()
        result = PartCategorySerializer(subcategories, many=True, context=self.context).data
        cache.set(cache_key, result, 60 * 15)  # Cache for 15 minutes
        return result
    
    def get_products(self, obj):
        """
        Get products for this part category with caching.
        
        Args:
            obj (PartCategory): The part category object
            
        Returns:
            list: Serialized product data
        """
        cache_key = f'part_category_products_{obj.id}'
        cached_products = cache.get(cache_key)
        
        if cached_products is not None:
            return cached_products
            
        products = obj.products.all()
        result = ProductListSerializer(products, many=True, context=self.context).data
        cache.set(cache_key, result, 60 * 15)  # Cache for 15 minutes
        return result


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings with Redis caching support"""
    url = serializers.HyperlinkedIdentityField(view_name='products:product-detail', lookup_field='slug')
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    model_name = serializers.CharField(source='vehicle_model.name', read_only=True)
    category_name = serializers.CharField(source='part_category.name', read_only=True)
    amount_saved = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'featured_image',
            'sku', 'price', 'compare_price', 'is_active', 'is_featured',
            'brand', 'brand_name', 'vehicle_model', 'model_name', 
            'part_category', 'category_name', 'stock_quantity',
            'amount_saved', 'discount_percentage', 'is_in_stock',
            'created_at', 'url'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'amount_saved', 
                           'discount_percentage', 'is_in_stock']
    
    def to_representation(self, instance):
        """
        Override to_representation to use cached PartCategory instances.
        
        This reduces database queries by using cached PartCategory instances
        when available.
        
        Args:
            instance (Product): The product instance
            
        Returns:
            dict: The serialized representation
        """
        # Use cached PartCategory instances to reduce database queries
        if hasattr(instance, 'part_category_id') and instance.part_category_id:
            cached_category = PartCategory.get_cached_by_id(instance.part_category_id)
            if cached_category:
                # Temporarily replace the part_category with the cached version
                instance.part_category = cached_category
        
        return super().to_representation(instance)


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for product details with Redis caching support"""
    brand = BrandSerializer(read_only=True)
    vehicle_model = VehicleModelSerializer(read_only=True)
    part_category = PartCategorySerializer(read_only=True)
    amount_saved = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'updated_at', 'amount_saved', 
                           'discount_percentage', 'is_in_stock']


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating products"""
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def validate_sku(self, value):
        """Ensure SKU is unique"""
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("A product with this SKU already exists.")
        return value
    
    def validate_compare_price(self, value):
        """Ensure compare price is greater than actual price"""
        if value and self.initial_data.get('price') and value <= float(self.initial_data['price']):
            raise serializers.ValidationError("Compare price must be greater than actual price.")
        return value