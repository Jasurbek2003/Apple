# products/serializers.py
from rest_framework import serializers
from django.utils.html import strip_tags
from .models import (
    Category,
    Product,
    ProductImages,
    ProductVariant,
    ProductVariantColor,
    ProductImage,
    ProductVariantStorage
)


class CategorySerializer(serializers.ModelSerializer):
    description_plain = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'description_plain', 'image', 'video', 'is_active', 'icon']

    def get_description_plain(self, obj):
        """Return plain text version of the description (without HTML)"""
        return strip_tags(obj.description) if obj.description else ""


class ProductImagesSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImages
        fields = ['id', 'image', 'image_url', 'alt_text']

    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None


class ProductVariantStorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantStorage
        fields = ['id', 'storage_capacity', 'price_adjustment', 'price', 'is_active']


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'alt_text', 'is_primary']

    def get_image_url(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None


class ProductVariantColorSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = ProductVariantColor
        fields = ['id', 'color_name', 'color_code', 'images']


class ProductVariantSerializer(serializers.ModelSerializer):
    colors = ProductVariantColorSerializer(many=True, read_only=True)
    storage = ProductVariantStorageSerializer(many=True, read_only=True)
    description_plain = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'name', 'price_adjustment', 'price', 'description',
            'description_plain', 'is_active', 'colors', 'storage'
        ]

    def get_description_plain(self, obj):
        """Return plain text version of the description (without HTML)"""
        return strip_tags(obj.description) if obj.description else ""


class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    primary_image = serializers.SerializerMethodField()
    icon_url = serializers.SerializerMethodField()
    description_preview = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category_name', 'price',
            'sale_price', 'primary_image', 'icon_url',
            'description_preview', 'main_image',
        ]

    def get_icon_url(self, obj):
        if obj.icon:
            return self.context['request'].build_absolute_uri(obj.icon.url)
        return None

    def get_primary_image(self, obj):
        """Get the primary image for the product"""
        # First check product images
        product_images = obj.images.all()
        if product_images.exists():
            return ProductImagesSerializer(product_images.first(), context=self.context).data

        # Then check variant color images
        for variant in obj.variants.all():
            for color in variant.colors.all():
                primary_image = color.images.filter(is_primary=True).first()
                if primary_image:
                    return ProductImageSerializer(primary_image, context=self.context).data
        return None

    def get_description_preview(self, obj):
        """Get a plain text preview of the description"""
        if not obj.description:
            return ""
        plain_text = strip_tags(obj.description)
        if len(plain_text) > 150:
            return plain_text[:147] + "..."
        return plain_text


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImagesSerializer(many=True, read_only=True)
    icon_url = serializers.SerializerMethodField()
    description_plain = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'name', 'slug', 'sku', 'description',
            'description_plain', 'tech_specs', 'price', 'sale_price',
            'icon', 'icon_url', 'images', 'variants', 'created_at',
            'updated_at', 'main_image'
        ]

    def get_icon_url(self, obj):
        if obj.icon:
            return self.context['request'].build_absolute_uri(obj.icon.url)
        return None

    def get_description_plain(self, obj):
        """Return plain text version of the description (without HTML)"""
        return strip_tags(obj.description) if obj.description else ""