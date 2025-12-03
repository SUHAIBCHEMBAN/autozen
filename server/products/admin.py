from django.contrib import admin
from django.utils.html import format_html
from .models import Brand, VehicleModel, PartCategory, Product


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'slug', 'is_active', 'models_count', 'created_at']
    list_filter = ['is_active', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']

    def models_count(self, obj):
        return obj.models.count()
    models_count.short_description = 'Number of Models'


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'brand', 'year_range', 'is_active', 'products_count', 'created_at']
    list_filter = ['brand', 'is_active', 'year_from', 'created_at']
    search_fields = ['name', 'brand__name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['brand', 'name']

    def year_range(self, obj):
        if obj.year_to:
            return f"{obj.year_from} - {obj.year_to}"
        return f"{obj.year_from} - Present"
    year_range.short_description = 'Years'

    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Number of Products'


@admin.register(PartCategory)
class PartCategoryAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'parent', 'is_active', 'subcategories_count', 'products_count', 'created_at']
    list_filter = ['is_active', 'parent', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']

    def subcategories_count(self, obj):
        return obj.subcategories.count()
    subcategories_count.short_description = 'Subcategories'

    def products_count(self, obj):
        return obj.products.count()
    products_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'brand', 'vehicle_model', 'part_category', 'price', 'stock_status', 'is_active', 'is_featured', 'created_at']
    list_filter = ['brand', 'vehicle_model', 'part_category', 'is_active', 'is_featured', 'created_at', 'updated_at']
    search_fields = ['name', 'sku', 'oem_number', 'manufacturer_part_number']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at', 'amount_saved', 'discount_percentage']
    ordering = ['-created_at']
    
    # Organize fields into sections
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'short_description')
        }),
        ('Categorization', {
            'fields': ('brand', 'vehicle_model', 'part_category')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_price', 'cost_per_item')
        }),
        ('Inventory', {
            'fields': ('sku', 'stock_quantity', 'track_inventory', 'continue_selling')
        }),
        ('Media', {
            'fields': ('featured_image', 'gallery_images')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description', 'meta_keywords')
        }),
        ('Automotive Specific', {
            'fields': ('oem_number', 'manufacturer_part_number', 'compatibility_notes', 'weight', 'dimensions')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def stock_status(self, obj):
        if obj.is_in_stock:
            return format_html('<span style="color: green;">In Stock</span>')
        else:
            return format_html('<span style="color: red;">Out of Stock</span>')
    stock_status.short_description = 'Stock Status'

    def amount_saved(self, obj):
        if obj.amount_saved:
            return f"${obj.amount_saved}"
        return "N/A"
    amount_saved.short_description = 'Amount Saved'

    def discount_percentage(self, obj):
        if obj.discount_percentage:
            return f"{obj.discount_percentage}%"
        return "N/A"
    discount_percentage.short_description = 'Discount'