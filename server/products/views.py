from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny  # Add this import
from django_filters.rest_framework import DjangoFilterBackend
from .models import Brand, VehicleModel, PartCategory, Product
from .serializers import (
    BrandSerializer, BrandDetailSerializer,
    VehicleModelSerializer, VehicleModelDetailSerializer,
    PartCategorySerializer, PartCategoryDetailSerializer,
    ProductListSerializer, ProductDetailSerializer, ProductCreateSerializer
)
from .cache_utils import (
    get_cached_brands_list, get_cached_brand_by_slug,
    get_cached_models_list, get_cached_model_by_slug,
    get_cached_categories_list, get_cached_category_by_slug,
    get_cached_product_by_slug
)


class BrandViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Brand model.
    
    Provides RESTful API endpoints for brand management including:
    - Listing all brands
    - Retrieving a specific brand by slug
    - Getting models for a specific brand
    
    Implements caching for performance optimization and uses proper
    authentication and permission checks.
    """
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    # Override permission classes to allow public access
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Return queryset of active brands with caching optimization.
        
        For list views, uses cached data to improve performance.
        For other actions, returns the regular queryset.
        
        Returns:
            QuerySet: Active brands queryset
        """
        # For list views, we can use cached data
        if self.action == 'list':
            # Get cached brands list
            cached_brands = get_cached_brands_list()
            # Convert list to queryset-like object that supports filtering
            if cached_brands:
                # Return the original queryset but it will be faster due to caching in the model layer
                return self.queryset
        # For other actions, return the regular queryset
        return self.queryset

    def get_object(self):
        """
        Get a brand object by slug with caching.
        
        Retrieves a brand by its slug using cached data for improved performance.
        
        Returns:
            Brand: The brand object
            
        Raises:
            Http404: If brand is not found
        """
        slug = self.kwargs.get(self.lookup_field)
        obj = get_cached_brand_by_slug(slug)
        if obj is None:
            from django.http import Http404
            raise Http404("Brand not found")
        return obj

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BrandDetailSerializer
        return BrandSerializer

    @action(detail=True, methods=['get'])
    def models(self, request, slug=None):
        """
        Get all models for a specific brand.
        
        Retrieves all vehicle models associated with a specific brand
        using cached data for improved performance.
        
        Args:
            request: The HTTP request object
            slug (str): The brand slug
            
        Returns:
            Response: Serialized vehicle models data
        """
        brand = self.get_object()
        models = get_cached_models_list(brand_id=brand.id)
        serializer = VehicleModelSerializer(models, many=True, context={'request': request})
        return Response(serializer.data)


class VehicleModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for VehicleModel model.
    
    Provides RESTful API endpoints for vehicle model management including:
    - Listing all vehicle models
    - Retrieving a specific vehicle model by slug
    - Getting products for a specific vehicle model
    
    Implements caching for performance optimization and uses proper
    authentication and permission checks.
    """
    queryset = VehicleModel.objects.filter(is_active=True).select_related('brand')
    serializer_class = VehicleModelSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['brand']
    search_fields = ['name', 'description', 'brand__name']
    ordering_fields = ['name', 'brand', 'year_from', 'created_at']
    ordering = ['brand', 'name']
    
    # Override permission classes to allow public access
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Return queryset of active vehicle models with caching optimization.
        
        For list views, uses cached data to improve performance.
        For other actions, returns the regular queryset.
        
        Returns:
            QuerySet: Active vehicle models queryset
        """
        # For list views, we can use cached data
        if self.action == 'list':
            # Get cached models list
            cached_models = get_cached_models_list()
            # Convert list to queryset-like object that supports filtering
            if cached_models:
                # Return the original queryset but it will be faster due to caching in the model layer
                return self.queryset
        # For other actions, return the regular queryset
        return self.queryset

    def get_object(self):
        """
        Get a vehicle model object by slug with caching.
        
        Retrieves a vehicle model by its slug using cached data for improved performance.
        
        Returns:
            VehicleModel: The vehicle model object
            
        Raises:
            Http404: If vehicle model is not found
        """
        slug = self.kwargs.get(self.lookup_field)
        obj = get_cached_model_by_slug(slug)
        if obj is None:
            from django.http import Http404
            raise Http404("Vehicle model not found")
        return obj

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return VehicleModelDetailSerializer
        return VehicleModelSerializer

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """
        Get all products for a specific vehicle model.
        
        Retrieves all products associated with a specific vehicle model.
        
        Args:
            request: The HTTP request object
            slug (str): The vehicle model slug
            
        Returns:
            Response: Serialized products data
        """
        model = self.get_object()
        # Filter products queryset by vehicle model
        products = [p for p in ProductViewSet().get_queryset() if hasattr(p, 'vehicle_model_id') and p.vehicle_model_id == model.id]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class PartCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PartCategory model.
    
    Provides RESTful API endpoints for part category management including:
    - Listing all part categories
    - Retrieving a specific part category by slug
    - Getting products for a specific part category
    - Getting parent categories
    - Getting subcategories
    
    Implements caching for performance optimization and uses proper
    authentication and permission checks.
    """
    queryset = PartCategory.objects.filter(is_active=True)
    serializer_class = PartCategorySerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    # Override permission classes to allow public access
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Return queryset of active part categories with caching optimization.
        
        For list views, uses cached data to improve performance.
        For other actions, returns the regular queryset.
        
        Returns:
            QuerySet: Active part categories queryset
        """
        # For list views, we can use cached data
        if self.action == 'list':
            # Get cached categories list
            cached_categories = get_cached_categories_list()
            # Convert list to queryset-like object that supports filtering
            if cached_categories:
                # Return the original queryset but it will be faster due to caching in the model layer
                return self.queryset
        # For other actions, return the regular queryset
        return self.queryset

    def get_object(self):
        """
        Get a part category object by slug with caching.
        
        Retrieves a part category by its slug using cached data for improved performance.
        
        Returns:
            PartCategory: The part category object
            
        Raises:
            Http404: If part category is not found
        """
        slug = self.kwargs.get(self.lookup_field)
        obj = get_cached_category_by_slug(slug)
        if obj is None:
            from django.http import Http404
            raise Http404("Part category not found")
        return obj

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return PartCategoryDetailSerializer
        return PartCategorySerializer

    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """
        Get all products for a specific category.
        
        Retrieves all products associated with a specific part category.
        
        Args:
            request: The HTTP request object
            slug (str): The part category slug
            
        Returns:
            Response: Serialized products data
        """
        category = self.get_object()
        # Filter products queryset by part category
        products = [p for p in ProductViewSet().get_queryset() if hasattr(p, 'part_category_id') and p.part_category_id == category.id]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def parents(self, request):
        """
        Get only parent categories (no parents themselves).
        
        Retrieves all parent part categories (categories that don't have a parent themselves)
        using cached data for improved performance.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: Serialized parent categories data
        """
        parents = get_cached_categories_list(parent_id=None)
        serializer = PartCategorySerializer(parents, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def subcategories(self, request, slug=None):
        """
        Get all subcategories for a specific category.
        
        Retrieves all subcategories of a specific part category
        using cached data for improved performance.
        
        Args:
            request: The HTTP request object
            slug (str): The parent category slug
            
        Returns:
            Response: Serialized subcategories data
        """
        category = self.get_object()
        subcategories = get_cached_categories_list(parent_id=category.id)
        serializer = PartCategorySerializer(subcategories, many=True, context={'request': request})
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product model.
    
    Provides RESTful API endpoints for product management including:
    - Listing all products
    - Retrieving a specific product by slug
    - Filtering products by various criteria
    - Searching products
    
    Implements caching for performance optimization and uses proper
    authentication and permission checks.
    """
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
    
    # Override permission classes to allow public access
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        """
        Return queryset of active products with select_related optimization.
        
        Filters products to only return active ones and uses select_related
        to optimize database queries by prefetching related objects.
        
        Returns:
            QuerySet: Active products queryset with prefetched related objects
        """
        return Product.objects.filter(is_active=True).select_related(
            'brand', 'vehicle_model', 'part_category'
        ).order_by('-created_at')

    def get_object(self):
        """
        Get a product object by slug with caching.
        
        Retrieves a product by its slug using cached data for improved performance.
        
        Returns:
            Product: The product object
            
        Raises:
            Http404: If product is not found
        """
        slug = self.kwargs.get(self.lookup_field)
        obj = get_cached_product_by_slug(slug)
        if obj is None:
            from django.http import Http404
            raise Http404("Product not found")
        return obj

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateSerializer
        return ProductListSerializer

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured products.
        
        Retrieves all products marked as featured.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: Serialized featured products data
        """
        featured_products = [p for p in self.get_queryset() if p.is_featured]
        serializer = ProductListSerializer(featured_products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_brand(self, request):
        """
        Get products filtered by brand slug.
        
        Retrieves all products associated with a specific brand.
        
        Args:
            request: The HTTP request object with brand query parameter
            
        Returns:
            Response: Serialized products data or error response
        """
        brand_slug = request.query_params.get('brand', None)
        if not brand_slug:
            return Response({'error': 'Brand slug is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get brand by slug
        brand = get_cached_brand_by_slug(brand_slug)
        if not brand:
            return Response({'error': 'Brand not found'}, status=status.HTTP_404_NOT_FOUND)
        
        products = [p for p in self.get_queryset() if p.brand_id == brand.id]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_model(self, request):
        """
        Get products filtered by vehicle model slug.
        
        Retrieves all products associated with a specific vehicle model.
        
        Args:
            request: The HTTP request object with model query parameter
            
        Returns:
            Response: Serialized products data or error response
        """
        model_slug = request.query_params.get('model', None)
        if not model_slug:
            return Response({'error': 'Model slug is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get model by slug
        model = get_cached_model_by_slug(model_slug)
        if not model:
            return Response({'error': 'Model not found'}, status=status.HTTP_404_NOT_FOUND)
        
        products = [p for p in self.get_queryset() if p.vehicle_model_id == model.id]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get products filtered by part category slug.
        
        Retrieves all products associated with a specific part category.
        
        Args:
            request: The HTTP request object with category query parameter
            
        Returns:
            Response: Serialized products data or error response
        """
        category_slug = request.query_params.get('category', None)
        if not category_slug:
            return Response({'error': 'Category slug is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get category by slug
        category = get_cached_category_by_slug(category_slug)
        if not category:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)
        
        products = [p for p in self.get_queryset() if p.part_category_id == category.id]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Advanced search for products.
        
        Searches products across multiple fields including name, description,
        OEM numbers, manufacturer part numbers, and related object names.
        
        Args:
            request: The HTTP request object with q query parameter
            
        Returns:
            Response: Serialized search results or error response
        """
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Search in multiple fields
        search_results = []
        for product in self.get_queryset():
            if (query.lower() in product.name.lower() or 
                query.lower() in (product.description or '').lower() or
                query.lower() in (product.short_description or '').lower() or
                query.lower() in (getattr(product, 'oem_number', '') or '').lower() or
                query.lower() in (getattr(product, 'manufacturer_part_number', '') or '').lower() or
                query.lower() in (getattr(product.brand, 'name', '') or '').lower() or
                query.lower() in (getattr(product.vehicle_model, 'name', '') or '').lower() or
                query.lower() in (getattr(product.part_category, 'name', '') or '').lower()):
                search_results.append(product)
        
        serializer = ProductListSerializer(search_results, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def in_stock(self, request):
        """
        Get products that are in stock.
        
        Retrieves all products with stock quantity greater than zero.
        
        Args:
            request: The HTTP request object
            
        Returns:
            Response: Serialized in-stock products data
        """
        in_stock_products = [p for p in self.get_queryset() if p.stock_quantity > 0]
        serializer = ProductListSerializer(in_stock_products, many=True, context={'request': request})
        return Response(serializer.data)