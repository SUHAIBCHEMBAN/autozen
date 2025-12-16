from rest_framework import serializers
from products.serializers import ProductListSerializer, PartCategorySerializer
from .models import HeroBanner, CategorySection, AdvertisementBanner, Testimonial, LandingPageConfiguration, FeaturedVehicle


class FeaturedVehicleSerializer(serializers.ModelSerializer):
    """Serializer for featured vehicles"""
    
    class Meta:
        model = FeaturedVehicle
        fields = [
            'id', 'name', 'image', 'hover_title', 'hover_description',
            'link', 'order', 'created_at', 'updated_at'
        ]


class HeroBannerSerializer(serializers.ModelSerializer):
    """Serializer for hero banners with caching support"""
    featured_vehicles = FeaturedVehicleSerializer(many=True, read_only=True)
    
    class Meta:
        model = HeroBanner
        fields = [
            'id', 'title', 'subtitle', 'description', 'image', 
            'button_text', 'button_link', 'is_active', 'order', 
            'featured_vehicles', 'created_at', 'updated_at'
        ]


class CategorySectionSerializer(serializers.ModelSerializer):
    """Serializer for category sections with caching support"""
    # Include the full category object with parent information
    category = PartCategorySerializer(read_only=True)
    
    class Meta:
        model = CategorySection
        fields = [
            'id', 'title', 'slug', 'description', 'category', 
            'image', 'icon', 'is_active', 'order', 
            'created_at', 'updated_at'
        ]
    
    def to_representation(self, instance):
        """
        Override to_representation to use cached PartCategory instances.
        
        This reduces database queries by using cached PartCategory instances
        when available.
        
        Args:
            instance (CategorySection): The category section instance
            
        Returns:
            dict: The serialized representation
        """
        # Use cached PartCategory instances to reduce database queries
        if hasattr(instance, 'category_id') and instance.category_id:
            from products.models import PartCategory
            cached_category = PartCategory.get_cached_by_id(instance.category_id)
            if cached_category:
                # Temporarily replace the category with the cached version
                instance.category = cached_category
        
        return super().to_representation(instance)


class AdvertisementBannerSerializer(serializers.ModelSerializer):
    """Serializer for advertisement banners with caching support"""
    
    class Meta:
        model = AdvertisementBanner
        fields = [
            'id', 'title', 'subtitle', 'description', 'image', 
            'link', 'is_active', 'order', 'start_date', 'end_date',
            'created_at', 'updated_at'
        ]


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for testimonials with caching support"""
    
    class Meta:
        model = Testimonial
        fields = [
            'id', 'name', 'role', 'company', 'content', 
            'rating', 'avatar', 'is_featured', 'order', 
            'created_at', 'updated_at'
        ]


class LandingPageConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for landing page configuration with caching support"""
    
    class Meta:
        model = LandingPageConfiguration
        fields = [
            'id', 'site_title', 'site_tagline', 'meta_description', 
            'favicon', 'logo', 'footer_text', 'copyright_text',
            'created_at', 'updated_at'
        ]


class LandingPageContentSerializer(serializers.Serializer):
    """Serializer for the complete landing page content with caching support"""
    configuration = LandingPageConfigurationSerializer()
    hero_banners = HeroBannerSerializer(many=True)
    categories = CategorySectionSerializer(many=True)
    featured_products = ProductListSerializer(many=True)
    advertisements = AdvertisementBannerSerializer(many=True)
    testimonials = TestimonialSerializer(many=True)
    featured_brands = serializers.SerializerMethodField()
    
    # def get_featured_brands(self, obj):
    #     """
    #     Get featured brands from cached data or database.
        
    #     This method retrieves featured brands either from the passed object
    #     (when using cached data) or directly from the database.
        
    #     Args:
    #         obj (dict): The serialized object containing landing page data
            
    #     Returns:
    #         list: Serialized brand data
    #     """
    #     from products.models import Brand
    #     from products.serializers import BrandSerializer
        
    #     # Check if featured brands are already in the object (from cache)
    #     if 'featured_brands' in obj and hasattr(obj['featured_brands'], '__iter__'):
    #         # Use the cached brands data
    #         brands = obj['featured_brands']
    #     else:
    #         # Fallback to database query
    #         brands = Brand.objects.filter(is_active=True)[:10]  # Limit to 10 brands
        
    #     # Pass the request context to the serializer
    #     request = self.context.get('request')
    #     return BrandSerializer(brands, many=True, context={'request': request}).data
    
    def get_configuration(self, obj):
        # Import here to avoid circular imports
        from .models import LandingPageConfiguration
        config = obj.get('configuration')
        if config:
            from .serializers import LandingPageConfigurationSerializer
            return LandingPageConfigurationSerializer(config, context=self.context).data
        return None
    
    def get_categories(self, obj):
        categories = obj.get('categories', [])
        if categories:
            from .serializers import CategorySectionSerializer
            return CategorySectionSerializer(categories, many=True, context=self.context).data
        return []
    
    def get_featured_products(self, obj):
        products = obj.get('featured_products', [])
        if products:
            from products.serializers import ProductListSerializer
            return ProductListSerializer(products, many=True, context=self.context).data
        return []
    
    def get_advertisements(self, obj):
        ads = obj.get('advertisements', [])
        if ads:
            from .serializers import AdvertisementBannerSerializer
            return AdvertisementBannerSerializer(ads, many=True, context=self.context).data
        return []
    
    def get_testimonials(self, obj):
        testimonials = obj.get('testimonials', [])
        if testimonials:
            from .serializers import TestimonialSerializer
            return TestimonialSerializer(testimonials, many=True, context=self.context).data
        return []
    
    def get_featured_brands(self, obj):
        from products.models import Brand
        from products.serializers import BrandSerializer
        
        if 'featured_brands' in obj and hasattr(obj['featured_brands'], '__iter__'):
            brands = obj['featured_brands']
        else:
            brands = Brand.objects.filter(is_active=True)[:10]
        
        request = self.context.get('request')
        return BrandSerializer(brands, many=True, context={'request': request}).data