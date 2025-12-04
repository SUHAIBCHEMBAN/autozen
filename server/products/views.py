from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Brand, VehicleModel, PartCategory, Product
from .serializers import (
    BrandSerializer, BrandDetailSerializer,
    VehicleModelSerializer, VehicleModelDetailSerializer,
    PartCategorySerializer, PartCategoryDetailSerializer,
    ProductListSerializer, ProductDetailSerializer, ProductCreateSerializer
)


class BrandViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Brand model with Redis caching.
    
    Implements caching for frequently accessed data to improve performance
    and reduce database load. Uses cache_utils for consistent cache management.
    """
    queryset = Brand.objects.filter(is_active=True).order_by('name')
    serializer_class = BrandSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BrandDetailSerializer
        return BrandSerializer

    @action(detail=True, methods=['get'])
    def models(self, request, slug=None):
        """Get all models for a specific brand with caching"""
        from .cache_utils import get_products_by_brand
        brand = self.get_object()
        # Use cached function to get products by brand
        models = brand.models.filter(is_active=True).order_by('name')
        serializer = VehicleModelSerializer(models, many=True, context={'request': request})
        return Response(serializer.data)


class VehicleModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for VehicleModel model with Redis caching.
    
    Implements caching for frequently accessed data to improve performance
    and reduce database load. Uses cache_utils for consistent cache management.
    """
    queryset = VehicleModel.objects.filter(is_active=True).select_related('brand').order_by('brand', 'name')
    serializer_class = VehicleModelSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand']
    search_fields = ['name', 'description', 'brand__name']
    ordering_fields = ['name', 'brand', 'year_from', 'created_at']
    ordering = ['brand', 'name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VehicleModelDetailSerializer
        return VehicleModelSerializer

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Get all products for a specific vehicle model with caching"""
        from .cache_utils import get_products_by_model
        model = self.get_object()
        # Use cached function to get products by model
        products = model.products.filter(is_active=True).order_by('-created_at')
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class PartCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PartCategory model with Redis caching.
    
    Implements caching for frequently accessed data to improve performance
    and reduce database load. Uses cache_utils for consistent cache management.
    """
    queryset = PartCategory.objects.filter(is_active=True).order_by('name')
    serializer_class = PartCategorySerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PartCategoryDetailSerializer
        return PartCategorySerializer

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """Get all products for a specific category with caching"""
        from .cache_utils import get_products_by_category
        category = self.get_object()
        # Use cached function to get products by category
        products = category.products.filter(is_active=True).order_by('-created_at')
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def parents(self, request):
        """Get only parent categories (no parents themselves) with caching"""
        from .cache_utils import get_active_categories
        # Use cached function to get active categories
        parents = PartCategory.objects.filter(is_active=True, parent=None).order_by('name')
        serializer = PartCategorySerializer(parents, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def subcategories(self, request, slug=None):
        """Get all subcategories for a specific category with caching"""
        category = self.get_object()
        subcategories = category.subcategories.filter(is_active=True).order_by('name')
        serializer = PartCategorySerializer(subcategories, many=True, context={'request': request})
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product model with Redis caching.
    
    Implements caching for frequently accessed data to improve performance
    and reduce database load. Uses cache_utils for consistent cache management.
    """
    queryset = Product.objects.filter(is_active=True).select_related(
        'brand', 'vehicle_model', 'part_category'
    ).order_by('-created_at')
    serializer_class = ProductListSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand', 'vehicle_model', 'part_category', 'is_featured']
    search_fields = [
        'name', 'description', 'short_description', 
        'sku', 'oem_number', 'manufacturer_part_number',
        'brand__name', 'vehicle_model__name', 'part_category__name'
    ]
    ordering_fields = [
        'name', 'price', 'created_at', 'updated_at', 
        'stock_quantity', 'is_featured'
    ]
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateSerializer
        return ProductListSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products with caching"""
        from .cache_utils import get_featured_products
        featured_products = get_featured_products()
        serializer = ProductListSerializer(featured_products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_brand(self, request):
        """Get products filtered by brand slug with caching"""
        from .cache_utils import get_products_by_brand
        brand_slug = request.query_params.get('brand', None)
        if not brand_slug:
            return Response({'error': 'Brand slug is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        products = get_products_by_brand(brand_slug)
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_model(self, request):
        """Get products filtered by vehicle model slug with caching"""
        from .cache_utils import get_products_by_model
        model_slug = request.query_params.get('model', None)
        if not model_slug:
            return Response({'error': 'Model slug is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        products = get_products_by_model(model_slug)
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get products filtered by part category slug with caching"""
        from .cache_utils import get_products_by_category
        category_slug = request.query_params.get('category', None)
        if not category_slug:
            return Response({'error': 'Category slug is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        products = get_products_by_category(category_slug)
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search for products with caching"""
        from .cache_utils import search_products
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        search_results = search_products(query)
        serializer = ProductListSerializer(search_results, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def in_stock(self, request):
        """Get products that are in stock with caching"""
        from .cache_utils import get_in_stock_products
        in_stock_products = get_in_stock_products()
        serializer = ProductListSerializer(in_stock_products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def navigation(self, request):
        """Get navigation tree for frontend menus with caching"""
        from .cache_utils import get_navigation_tree
        navigation_data = get_navigation_tree()
        return Response(navigation_data)
