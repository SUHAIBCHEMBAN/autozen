from rest_framework import serializers
from .models import Brand, VehicleModel, PartCategory, Product


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
        return obj.models.count()


class BrandDetailSerializer(BrandSerializer):
    """Detailed serializer for Brand with related models"""
    models = serializers.SerializerMethodField()
    
    class Meta(BrandSerializer.Meta):
        fields = BrandSerializer.Meta.fields + ['models']
    
    def get_models(self, obj):
        models = obj.models.all()
        return VehicleModelSerializer(models, many=True, context=self.context).data


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
        return obj.products.count()


class VehicleModelDetailSerializer(VehicleModelSerializer):
    """Detailed serializer for VehicleModel with related products"""
    products = serializers.SerializerMethodField()
    
    class Meta(VehicleModelSerializer.Meta):
        fields = VehicleModelSerializer.Meta.fields + ['products']
    
    def get_products(self, obj):
        products = obj.products.all()
        return ProductListSerializer(products, many=True, context=self.context).data


class PartCategorySerializer(serializers.ModelSerializer):
    """Serializer for PartCategory model"""
    url = serializers.HyperlinkedIdentityField(view_name='products:category-detail', lookup_field='slug')
    subcategories_count = serializers.SerializerMethodField()
    is_parent_category = serializers.BooleanField(source='is_parent', read_only=True)
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    
    class Meta:
        model = PartCategory
        fields = [
            'id', 'name', 'slug', 'description', 'parent', 'image', 'is_active',
            'created_at', 'updated_at', 'url', 'subcategories_count', 
            'is_parent_category', 'full_path'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_subcategories_count(self, obj):
        return obj.subcategories.count()


class PartCategoryDetailSerializer(PartCategorySerializer):
    """Detailed serializer for PartCategory with subcategories and products"""
    subcategories = serializers.SerializerMethodField()
    products = serializers.SerializerMethodField()
    
    class Meta(PartCategorySerializer.Meta):
        fields = PartCategorySerializer.Meta.fields + ['subcategories', 'products']
    
    def get_subcategories(self, obj):
        subcategories = obj.subcategories.all()
        return PartCategorySerializer(subcategories, many=True, context=self.context).data
    
    def get_products(self, obj):
        products = obj.products.all()
        return ProductListSerializer(products, many=True, context=self.context).data


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings"""
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