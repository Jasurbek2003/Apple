import os
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    Category, Product, ProductVariant, ProductVariantColor,
    ProductImage, ProductVariantStorage
)
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductVariantSerializer, ProductVariantColorSerializer,
    ProductImageSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for browsing and managing categories"""
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

    @swagger_auto_schema(
        operation_description="Create a new category",
        operation_summary="Create Category",
        tags=['Categories'],
        request_body=CategorySerializer
    )
    def create(self, request, *args, **kwargs):
        # Auto-generate slug if not provided
        if 'slug' not in request.data and 'name' in request.data:
            request.data['slug'] = slugify(request.data['name'])
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a category",
        operation_summary="Update Category",
        tags=['Categories'],
        request_body=CategorySerializer
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for browsing and managing products with rich text descriptions"""
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

    def get_queryset(self):
        """Optimize queryset with prefetch related to reduce DB queries"""
        queryset = Product.objects.filter(is_active=True)

        # For detailed view, prefetch all related data
        if self.action == 'retrieve':
            return queryset.prefetch_related(
                'variants',
                'variants__colors',
                'variants__storage',
                'variants__colors__images',
            )

        return queryset

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

    @swagger_auto_schema(
        operation_description="Get a specific product by slug",
        operation_summary="Get Product",
        tags=['Products']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new product",
        operation_summary="Create Product",
        tags=['Products'],
        request_body=ProductDetailSerializer
    )
    def create(self, request, *args, **kwargs):
        # Auto-generate slug if not provided
        if 'slug' not in request.data and 'name' in request.data:
            request.data['slug'] = slugify(request.data['name'])
        return super().create(request, *args, **kwargs)

    # Additional product-specific actions
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        products = self.get_queryset().filter(is_featured=True)[:8]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        """Get new products"""
        products = self.get_queryset().filter(is_new=True).order_by('-created_at')[:8]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class ProductVariantViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product variants"""
    queryset = ProductVariant.objects.filter(is_active=True)
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        """Filter by product if specified"""
        queryset = ProductVariant.objects.filter(is_active=True)
        product_slug = self.request.query_params.get('product', None)

        if product_slug:
            return queryset.filter(product__slug=product_slug)
        return queryset


class ProductVariantColorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product variant colors"""
    queryset = ProductVariantColor.objects.all()
    serializer_class = ProductVariantColorSerializer
    permission_classes = [IsAdminUser]


class ProductImageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product images"""
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminUser]


@csrf_exempt
@login_required
def tinymce_image_upload(request):
    """Handle image uploads from TinyMCE editor."""
    if request.method != 'POST' or 'file' not in request.FILES:
        return JsonResponse({'error': 'No file found'}, status=400)

    uploaded_file = request.FILES['file']

    # Validate file type (only images)
    if not uploaded_file.content_type.startswith('image/'):
        return JsonResponse({'error': 'File must be an image'}, status=400)

    # Generate unique filename
    filename = f"{uuid.uuid4().hex}{os.path.splitext(uploaded_file.name)[1]}"
    file_path = os.path.join(settings.TINYMCE_UPLOAD_PATH, filename)

    # Save the file
    saved_path = default_storage.save(file_path, ContentFile(uploaded_file.read()))

    # Generate full URL to the file
    file_url = request.build_absolute_uri(default_storage.url(saved_path))

    # Return the URL to TinyMCE
    return JsonResponse({
        'location': file_url  # This key is required by TinyMCE
    })