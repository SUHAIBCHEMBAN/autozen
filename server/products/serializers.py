from rest_framework import serializers
from django.core.cache import cache
from .models import Brand, VehicleModel, PartCategory, Product
from .cache_utils import (
    get_cached_brand, get_cached_model, get_cached_category,
    get_cached_brands_list, get_cached_models_list, get_cached_categories_list
)


class BrandSerializer(serializers.ModelSerializer):
    """Serializer for Brand model"""
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
            
        # Use cached models list for more efficient counting
        models_list = get_cached_models_list(brand_id=obj.id)
        count = len(models_list)
        cache.set(cache_key, count, 60 * 15)  # Cache for 15 minutes
        return count


class BrandDetailSerializer(BrandSerializer):
    """Detailed serializer for Brand with related models"""
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
            
        # Use cached models list for zero-query implementation
        models_list = get_cached_models_list(brand_id=obj.id)
        result = VehicleModelSerializer(models_list, many=True, context=self.context).data
        cache.set(cache_key, result, 60 * 15)  # Cache for 15 minutes
        return result


class VehicleModelSerializer(serializers.ModelSerializer):
    """Serializer for VehicleModel model"""
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
            
        # More efficient approach using direct query
        from .models import Product
        count = Product.objects.filter(vehicle_model=obj, is_active=True).count()
        cache.set(cache_key, count, 60 * 15)  # Cache for 15 minutes
        return count


class VehicleModelDetailSerializer(VehicleModelSerializer):
    """Detailed serializer for VehicleModel with related products"""
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
            
        # Use direct query for consistency
        from .models import Product
        products_queryset = Product.objects.filter(vehicle_model=obj, is_active=True).select_related(
            'brand', 'vehicle_model', 'part_category'
        )
        products_list = list(products_queryset)
        result = ProductListSerializer(products_list, many=True, context=self.context).data
        cache.set(cache_key, result, 60 * 15)  # Cache for 15 minutes
        return result


class PartCategorySerializer(serializers.ModelSerializer):
    """Serializer for PartCategory model"""
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
            
        # Use cached categories list for more efficient counting
        subcategories_list = get_cached_categories_list(parent_id=obj.id)
        count = len(subcategories_list)
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
    """Detailed serializer for PartCategory with subcategories and products"""
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
            
        # Use cached categories list for zero-query implementation
        subcategories_list = get_cached_categories_list(parent_id=obj.id)
        result = PartCategorySerializer(subcategories_list, many=True, context=self.context).data
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
            
        # Use direct query for consistency
        from .models import Product
        products_queryset = Product.objects.filter(part_category=obj, is_active=True).select_related(
            'brand', 'vehicle_model', 'part_category'
        )
        products_list = list(products_queryset)
        result = ProductListSerializer(products_list, many=True, context=self.context).data
        cache.set(cache_key, result, 60 * 15)  # Cache for 15 minutes
        return result


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings"""
    url = serializers.HyperlinkedIdentityField(view_name='products:product-detail', lookup_field='slug')
    brand_name = serializers.SerializerMethodField()
    model_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    amount_saved = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)
    
    def get_brand_name(self, obj):
        """Get brand name from cached or loaded brand object"""
        if hasattr(obj, 'brand') and obj.brand:
            return obj.brand.name
        return ''
    
    def get_model_name(self, obj):
        """Get model name from cached or loaded vehicle_model object"""
        if hasattr(obj, 'vehicle_model') and obj.vehicle_model:
            return obj.vehicle_model.name
        return ''
    
    def get_category_name(self, obj):
        """Get category name from cached or loaded part_category object"""
        if hasattr(obj, 'part_category') and obj.part_category:
            return obj.part_category.name
        return ''
    
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
        Override to_representation to use cached Brand, VehicleModel, and PartCategory instances.
        
        This reduces database queries by using cached instances when available.
        
        Args:
            instance (Product): The product instance
            
        Returns:
            dict: The serialized representation
        """
        # Use cached Brand instances to reduce database queries
        if hasattr(instance, 'brand_id') and instance.brand_id:
            cached_brand = Brand.get_cached_by_id(instance.brand_id)
            if cached_brand:
                # Temporarily replace the brand with the cached version
                instance.brand = cached_brand
        
        # Use cached VehicleModel instances to reduce database queries
        if hasattr(instance, 'vehicle_model_id') and instance.vehicle_model_id:
            cached_model = VehicleModel.get_cached_by_id(instance.vehicle_model_id)
            if cached_model:
                # Temporarily replace the vehicle_model with the cached version
                instance.vehicle_model = cached_model
        
        # Use cached PartCategory instances to reduce database queries
        if hasattr(instance, 'part_category_id') and instance.part_category_id:
            cached_category = PartCategory.get_cached_by_id(instance.part_category_id)
            if cached_category:
                # Temporarily replace the part_category with the cached version
                instance.part_category = cached_category
        
        return super().to_representation(instance)


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for product details"""
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