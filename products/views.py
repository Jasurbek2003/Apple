import os
import uuid
import bleach
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import (
    Category, Product, ProductImages, ProductVariant,
    ProductVariantColor, ProductImage, ProductVariantStorage
)
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductVariantSerializer, ProductVariantColorSerializer,
    ProductImageSerializer, ProductImagesSerializer,
    ProductVariantStorageSerializer
)


# Helper for HTML sanitization
def sanitize_html(html_content):
    """
    Sanitize HTML content to prevent XSS attacks
    """
    if not html_content:
        return ""

    allowed_tags = [
        'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'hr', 'table', 'thead',
        'tbody', 'tr', 'th', 'td', 'a', 'img', 'span', 'div', 'sub', 'sup'
    ]

    allowed_attrs = {
        '*': ['class', 'style'],
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'title', 'width', 'height', 'loading'],
        'table': ['border', 'cellpadding', 'cellspacing', 'width'],
    }

    allowed_styles = [
        'color', 'background-color', 'font-size', 'text-align',
        'margin', 'padding', 'width', 'height', 'border', 'font-weight',
        'font-style', 'text-decoration'
    ]

    clean_html = bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        styles=allowed_styles,
        strip=True
    )

    return clean_html


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for browsing and managing categories with rich text descriptions"""
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

    def perform_create(self, serializer):
        """Sanitize HTML content before saving"""
        if 'description' in serializer.validated_data:
            serializer.validated_data['description'] = sanitize_html(serializer.validated_data['description'])
        serializer.save()

    def perform_update(self, serializer):
        """Sanitize HTML content before saving"""
        if 'description' in serializer.validated_data:
            serializer.validated_data['description'] = sanitize_html(serializer.validated_data['description'])
        serializer.save()


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for browsing and managing products with rich text descriptions"""
    queryset = Product.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug']
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
                'images',
                'variants',
                'variants__colors',
                # 'variants__storage',
                'variants__colors__images',
            )

        return queryset

    def perform_create(self, serializer):
        """Sanitize HTML content before saving"""
        if 'description' in serializer.validated_data:
            serializer.validated_data['description'] = sanitize_html(serializer.validated_data['description'])

        # Auto-generate slug if not provided
        if 'name' in serializer.validated_data and not serializer.validated_data.get('slug'):
            serializer.validated_data['slug'] = slugify(serializer.validated_data['name'])

        serializer.save()

    def perform_update(self, serializer):
        """Sanitize HTML content before saving"""
        if 'description' in serializer.validated_data:
            serializer.validated_data['description'] = sanitize_html(serializer.validated_data['description'])
        serializer.save()


class ProductImagesViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product images"""
    queryset = ProductImages.objects.all()
    serializer_class = ProductImagesSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        product_id = self.request.query_params.get('product_id')
        if product_id:
            return ProductImages.objects.filter(product_id=product_id)
        return ProductImages.objects.all()


class ProductVariantViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product variants"""
    queryset = ProductVariant.objects.filter(is_active=True)
    serializer_class = ProductVariantSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Filter by product if specified"""
        queryset = ProductVariant.objects.filter(is_active=True)
        product_id = self.request.query_params.get('product_id')
        product_slug = self.request.query_params.get('product_slug')

        if product_id:
            return queryset.filter(product_id=product_id)
        elif product_slug:
            return queryset.filter(product__slug=product_slug)
        return queryset

    def perform_create(self, serializer):
        """Sanitize HTML content before saving"""
        if 'description' in serializer.validated_data:
            serializer.validated_data['description'] = sanitize_html(serializer.validated_data['description'])
        serializer.save()

    def perform_update(self, serializer):
        """Sanitize HTML content before saving"""
        if 'description' in serializer.validated_data:
            serializer.validated_data['description'] = sanitize_html(serializer.validated_data['description'])
        serializer.save()


class ProductVariantColorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product variant colors"""
    queryset = ProductVariantColor.objects.all()
    serializer_class = ProductVariantColorSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        variant_id = self.request.query_params.get('variant_id')
        if variant_id:
            return ProductVariantColor.objects.filter(product_variant_id=variant_id)
        return ProductVariantColor.objects.all()


class ProductImageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product variant color images"""
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        color_id = self.request.query_params.get('color_id')
        if color_id:
            return ProductImage.objects.filter(product_variant_color_id=color_id)
        return ProductImage.objects.all()


class ProductVariantStorageViewSet(viewsets.ModelViewSet):
    """ViewSet for managing product variant storage options"""
    queryset = ProductVariantStorage.objects.filter(is_active=True)
    serializer_class = ProductVariantStorageSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        variant_id = self.request.query_params.get('variant_id')
        if variant_id:
            return ProductVariantStorage.objects.filter(product_variant_id=variant_id, is_active=True)
        return ProductVariantStorage.objects.filter(is_active=True)


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

    # Validate file size (limit to 5MB)
    if uploaded_file.size > 5 * 1024 * 1024:
        return JsonResponse({'error': 'File size must be less than 5MB'}, status=400)

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


# API endpoint for uploading from frontend
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_image_upload(request):
    """API endpoint for uploading images from frontend TinyMCE editors"""
    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    uploaded_file = request.FILES['file']

    # Validate file type
    if not uploaded_file.content_type.startswith('image/'):
        return Response({'error': 'File must be an image'}, status=status.HTTP_400_BAD_REQUEST)

    # Validate file size (limit to 5MB)
    if uploaded_file.size > 5 * 1024 * 1024:
        return Response({'error': 'File size must be less than 5MB'}, status=status.HTTP_400_BAD_REQUEST)

    # Generate unique filename
    filename = f"{uuid.uuid4().hex}{os.path.splitext(uploaded_file.name)[1]}"
    file_path = os.path.join(settings.TINYMCE_UPLOAD_PATH, filename)

    # Save the file
    saved_path = default_storage.save(file_path, ContentFile(uploaded_file.read()))

    # Generate full URL to the file
    file_url = request.build_absolute_uri(default_storage.url(saved_path))

    return Response({
        'location': file_url,
        'url': file_url
    })