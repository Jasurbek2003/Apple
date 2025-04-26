from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductVariant, ProductVariantColor, ProductImage, ProductVariantStorage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'product_variant_color', 'alt_text', 'is_primary', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image and obj.image.url:
            return format_html('<img src="{}" width="100" height="auto" />', obj.image.url)
        return "No image"

    image_preview.short_description = 'Preview'


class ProductVariantColorInline(admin.TabularInline):
    model = ProductVariantColor
    extra = 1
    fields = ['color_name', 'color_code', 'color_preview']
    readonly_fields = ['color_preview']

    def color_preview(self, obj):
        if obj.color_code:
            return format_html(
                '<div style="background-color: {}; width: 30px; height: 30px; border-radius: 50%; border: 1px solid #ddd"></div>',
                obj.color_code
            )
        return "No color code"

    color_preview.short_description = 'Color'


class ProductVariantStorageInline(admin.TabularInline):
    model = ProductVariantStorage
    extra = 1
    fields = ['storage_capacity', 'price_adjustment', 'is_active']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['name', 'price_adjustment', 'is_active', 'description']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_new', 'created_at']
    list_filter = ['category', 'is_new']
    search_fields = ['name', 'description']
    inlines = [ProductVariantInline, ProductImageInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'price')
        }),
        ('Description', {
            'fields': ('description', 'tech_specs'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_new',)
        }),
    )


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['get_product_name', 'name', 'price_adjustment', 'is_active']
    list_filter = ['is_active', 'product__category']
    search_fields = ['name', 'product__name']
    inlines = [ProductVariantColorInline, ProductVariantStorageInline]

    def get_product_name(self, obj):
        return obj.product.name

    get_product_name.short_description = 'Product'

    fieldsets = (
        ('Variant Information', {
            'fields': ('product', 'name', 'price_adjustment', 'is_active')
        }),
        ('Description', {
            'fields': ('description',),
        }),
    )


@admin.register(ProductVariantColor)
class ProductVariantColorAdmin(admin.ModelAdmin):
    list_display = ['get_product', 'get_variant', 'color_name', 'color_preview']
    list_filter = ['product_variant__product__category', 'product_variant']
    search_fields = ['color_name', 'product_variant__name', 'product_variant__product__name']
    readonly_fields = ['color_preview']

    def get_product(self, obj):
        return obj.product_variant.product.name

    get_product.short_description = 'Product'

    def get_variant(self, obj):
        return obj.product_variant.name

    get_variant.short_description = 'Variant'

    def color_preview(self, obj):
        if obj.color_code:
            return format_html(
                '<div style="background-color: {}; width: 30px; height: 30px; border-radius: 50%; border: 1px solid #ddd"></div>',
                obj.color_code
            )
        return "No color code"

    color_preview.short_description = 'Color'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['get_product', 'get_color', 'is_primary', 'image_preview']
    list_filter = ['is_primary', 'product_variant_color__product_variant__product__category']
    search_fields = ['alt_text', 'product_variant_color__color_name',
                     'product_variant_color__product_variant__product__name']
    readonly_fields = ['image_preview']

    def get_product(self, obj):
        # There seems to be a mismatch in your models - ProductImage has product_variant_color as ForeignKey to Product
        # This needs to be fixed in models.py, but I'll handle it gracefully here
        if hasattr(obj.product_variant_color, 'product_variant'):
            return obj.product_variant_color.product_variant.product.name
        return obj.product_variant_color.name  # Assuming this is actually a Product

    get_product.short_description = 'Product'

    def get_color(self, obj):
        # Same issue as above
        if hasattr(obj.product_variant_color, 'color_name'):
            return obj.product_variant_color.color_name
        return "N/A"  # If product_variant_color is actually a Product

    get_color.short_description = 'Color'

    def image_preview(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html('<img src="{}" width="150" height="auto" />', obj.image.url)
        return "No image"

    image_preview.short_description = 'Preview'


@admin.register(ProductVariantStorage)
class ProductVariantStorageAdmin(admin.ModelAdmin):
    list_display = ['get_product', 'get_variant', 'storage_capacity', 'price_adjustment', 'is_active']
    list_filter = ['is_active', 'product_variant__product__category']
    search_fields = ['storage_capacity', 'product_variant__name', 'product_variant__product__name']

    def get_product(self, obj):
        return obj.product_variant.product.name

    get_product.short_description = 'Product'

    def get_variant(self, obj):
        return obj.product_variant.name

    get_variant.short_description = 'Variant'