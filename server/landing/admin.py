from django.contrib import admin
from .models import (
    HeroBanner, CategorySection, AdvertisementBanner, 
    Testimonial, LandingPageConfiguration, FeaturedVehicle
)

class FeaturedVehicleInline(admin.TabularInline):
    model = FeaturedVehicle
    extra = 3
    fields = ['name', 'image', 'hover_title', 'hover_description', 'link', 'order', 'is_active']


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'subtitle', 'description']
    ordering = ['order', '-created_at']
    inlines = [FeaturedVehicleInline]
    
    fieldsets = (
        ('Banner Content', {
            'fields': ('title', 'subtitle', 'description', 'image')
        }),
        ('Call to Action', {
            'fields': ('button_text', 'button_link')
        }),
        ('Settings', {
            'fields': ('is_active', 'order')
        }),
    )

@admin.register(FeaturedVehicle)
class FeaturedVehicleAdmin(admin.ModelAdmin):
    list_display = ['name', 'hero_banner', 'hover_title', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'hero_banner', 'created_at']
    search_fields = ['name', 'hover_title', 'hover_description']
    ordering = ['order', '-created_at']
    
    fieldsets = (
        ('Vehicle Information', {
            'fields': ('hero_banner', 'name', 'image', 'link')
        }),
        ('Hover Content', {
            'fields': ('hover_title', 'hover_description'),
            'description': 'Content shown when user hovers over the vehicle card'
        }),
        ('Settings', {
            'fields': ('is_active', 'order')
        }),
    )    


@admin.register(CategorySection)
class CategorySectionAdmin(admin.ModelAdmin):
    """Admin for category sections"""
    list_display = ['title', 'category', 'is_active', 'order', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['title', 'category__name']
    list_editable = ['order', 'is_active']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['order', '-created_at']


@admin.register(AdvertisementBanner)
class AdvertisementBannerAdmin(admin.ModelAdmin):
    """Admin for advertisement banners"""
    list_display = ['title', 'is_active', 'order', 'start_date', 'end_date']
    list_filter = ['is_active', 'start_date', 'end_date', 'created_at']
    search_fields = ['title', 'subtitle']
    list_editable = ['order', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['order', '-created_at']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """Admin for testimonials"""
    list_display = ['name', 'company', 'rating', 'is_featured', 'order', 'created_at']
    list_filter = ['is_featured', 'rating', 'created_at']
    search_fields = ['name', 'company', 'content']
    list_editable = ['order', 'is_featured', 'rating']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['order', '-created_at']


@admin.register(LandingPageConfiguration)
class LandingPageConfigurationAdmin(admin.ModelAdmin):
    """Admin for landing page configuration"""
    list_display = ['site_title', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_add_permission(self, request):
        # Only allow one configuration
        return not LandingPageConfiguration.objects.exists()