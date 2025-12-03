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
    ViewSet for Brand model
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
        """Get all models for a specific brand"""
        brand = self.get_object()
        models = brand.models.filter(is_active=True).order_by('name')
        serializer = VehicleModelSerializer(models, many=True, context={'request': request})
        return Response(serializer.data)


class VehicleModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for VehicleModel model
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
        """Get all products for a specific vehicle model"""
        model = self.get_object()
        products = model.products.filter(is_active=True).order_by('-created_at')
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class PartCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PartCategory model
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
        """Get all products for a specific category"""
        category = self.get_object()
        products = category.products.filter(is_active=True).order_by('-created_at')
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def parents(self, request):
        """Get only parent categories (no parents themselves)"""
        parents = PartCategory.objects.filter(is_active=True, parent=None).order_by('name')
        serializer = PartCategorySerializer(parents, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def subcategories(self, request, slug=None):
        """Get all subcategories for a specific category"""
        category = self.get_object()
        subcategories = category.subcategories.filter(is_active=True).order_by('name')
        serializer = PartCategorySerializer(subcategories, many=True, context={'request': request})
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product model
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
        'oem_number', 'manufacturer_part_number',
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
        """Get featured products"""
        featured_products = self.queryset.filter(is_featured=True)
        serializer = ProductListSerializer(featured_products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_brand(self, request):
        """Get products filtered by brand slug"""
        brand_slug = request.query_params.get('brand', None)
        if not brand_slug:
            return Response({'error': 'Brand slug is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        products = self.queryset.filter(brand__slug=brand_slug)
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_model(self, request):
        """Get products filtered by vehicle model slug"""
        model_slug = request.query_params.get('model', None)
        if not model_slug:
            return Response({'error': 'Model slug is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        products = self.queryset.filter(vehicle_model__slug=model_slug)
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get products filtered by part category slug"""
        category_slug = request.query_params.get('category', None)
        if not category_slug:
            return Response({'error': 'Category slug is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        products = self.queryset.filter(part_category__slug=category_slug)
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search for products"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in multiple fields
        search_results = self.queryset.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(oem_number__icontains=query) |
            Q(manufacturer_part_number__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(vehicle_model__name__icontains=query) |
            Q(part_category__name__icontains=query)
        ).distinct()
        
        serializer = ProductListSerializer(search_results, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def in_stock(self, request):
        """Get products that are in stock"""
        in_stock_products = self.queryset.filter(
            Q(track_inventory=False) | 
            Q(stock_quantity__gt=0) | 
            Q(continue_selling=True)
        )
        serializer = ProductListSerializer(in_stock_products, many=True, context={'request': request})
        return Response(serializer.data)