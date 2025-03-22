from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, ProductImage, ProductVariant
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    ProductVariantSerializer
)
from api.swagger import product_list_swagger_schema

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="List all categories with filtering options",
        operation_summary="List Categories",
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search in name and description",
                type=openapi.TYPE_STRING
            ),
        ],
        tags=['Categories']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get a specific category by slug",
        operation_summary="Get Category",
        tags=['Categories']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'is_featured', 'is_new', 'in_stock']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at', 'name']
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="List all products with filtering options",
        operation_summary="List Products",
        manual_parameters=[
            openapi.Parameter(
                'category__slug',
                openapi.IN_QUERY,
                description="Filter by category slug",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'is_new',
                openapi.IN_QUERY,
                description="Filter by new products",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'is_featured',
                openapi.IN_QUERY,
                description="Filter by featured products",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'in_stock',
                openapi.IN_QUERY,
                description="Filter by in-stock products",
                type=openapi.TYPE_BOOLEAN
            ),
            openapi.Parameter(
                'search',
                openapi.IN_QUERY,
                description="Search in name, description and SKU",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'ordering',
                openapi.IN_QUERY,
                description="Order by field (prefix with - for descending)",
                type=openapi.TYPE_STRING,
                enum=['price', '-price', 'name', '-name', 'created_at', '-created_at']
            ),
        ],
        tags=['Products']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Add Swagger documentation to retrieve method
    @swagger_auto_schema(
        operation_description="Get a specific product by slug",
        operation_summary="Get Product",
        tags=['Products']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)