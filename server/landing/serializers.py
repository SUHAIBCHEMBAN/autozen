from rest_framework import serializers
from products.serializers import ProductListSerializer, PartCategorySerializer
from .models import HeroBanner, CategorySection, AdvertisementBanner, Testimonial, LandingPageConfiguration


class HeroBannerSerializer(serializers.ModelSerializer):
    """Serializer for hero banners"""
    class Meta:
        model = HeroBanner
        fields = [
            'id', 'title', 'subtitle', 'description', 'image', 
            'button_text', 'button_link', 'is_active', 'order', 
            'created_at', 'updated_at'
        ]


class CategorySectionSerializer(serializers.ModelSerializer):
    """Serializer for category sections"""
    category = PartCategorySerializer(read_only=True)
    
    class Meta:
        model = CategorySection
        fields = [
            'id', 'title', 'slug', 'description', 'category', 
            'image', 'icon', 'is_active', 'order', 
            'created_at', 'updated_at'
        ]


class AdvertisementBannerSerializer(serializers.ModelSerializer):
    """Serializer for advertisement banners"""
    class Meta:
        model = AdvertisementBanner
        fields = [
            'id', 'title', 'subtitle', 'description', 'image', 
            'link', 'is_active', 'order', 'start_date', 'end_date',
            'created_at', 'updated_at'
        ]


class TestimonialSerializer(serializers.ModelSerializer):
    """Serializer for testimonials"""
    class Meta:
        model = Testimonial
        fields = [
            'id', 'name', 'role', 'company', 'content', 
            'rating', 'avatar', 'is_featured', 'order', 
            'created_at', 'updated_at'
        ]


class LandingPageConfigurationSerializer(serializers.ModelSerializer):
    """Serializer for landing page configuration"""
    class Meta:
        model = LandingPageConfiguration
        fields = [
            'id', 'site_title', 'site_tagline', 'meta_description', 
            'favicon', 'logo', 'footer_text', 'copyright_text',
            'created_at', 'updated_at'
        ]


class LandingPageContentSerializer(serializers.Serializer):
    """Serializer for the complete landing page content"""
    configuration = LandingPageConfigurationSerializer()
    hero_banners = HeroBannerSerializer(many=True)
    categories = CategorySectionSerializer(many=True)
    featured_products = ProductListSerializer(many=True)
    advertisements = AdvertisementBannerSerializer(many=True)
    testimonials = TestimonialSerializer(many=True)
    featured_brands = serializers.SerializerMethodField()
    
    def get_featured_brands(self, obj):
        from products.models import Brand
        brands = Brand.objects.filter(is_active=True)[:10]  # Limit to 10 brands
        from products.serializers import BrandSerializer
        # Pass the request context to the serializer
        request = self.context.get('request')
        return BrandSerializer(brands, many=True, context={'request': request}).data