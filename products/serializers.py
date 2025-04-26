from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'is_active']


class ProductImageSerializer(serializers.ModelSerializer):
    variant_name = serializers.ReadOnlyField(source='variant.name', default=None)
    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all(),
        source='variant',
        required=False,
        allow_null=True
    )

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'variant_id', 'variant_name']


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'sku', 'price_adjustment', 'stock_qty', 'is_active']


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category_name', 'price',
            'sale_price', 'primary_image', 'is_new', 'is_featured'
        ]

    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image).data
        return None


# products/serializers.py
class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'name', 'slug', 'sku', 'description',
            'tech_specs', 'price', 'sale_price', 'is_new',
            'is_featured', 'in_stock', 'stock_qty', 'images',
            'variants', 'created_at', 'updated_at'
        ]

    def get_images(self, obj):
        # Group images - general product images and variant-specific images
        result = {
            'default': ProductImageSerializer(
                obj.images.filter(variant__isnull=True),
                many=True
            ).data,
            'variants': {}
        }

        # Add variant-specific images
        for variant in obj.variants.all():
            variant_images = obj.images.filter(variant=variant)
            if variant_images.exists():
                result['variants'][variant.id] = {
                    'name': variant.name,
                    'images': ProductImageSerializer(variant_images, many=True).data
                }

        return result
