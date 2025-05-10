from django.contrib import admin
from django.utils.html import format_html
from django import forms
from tinymce.widgets import TinyMCE
from .models import (
    Category,
    Product,
    ProductImages,
    ProductVariant,
    ProductVariantColor,
    ProductImage,
    ProductVariantStorage
)


# Custom forms with TinyMCE widgets
class CategoryAdminForm(forms.ModelForm):
    description = forms.CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 20}),
        required=False
    )

    class Meta:
        model = Category
        fields = '__all__'


class ProductAdminForm(forms.ModelForm):
    description = forms.CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 30})
    )

    class Meta:
        model = Product
        fields = '__all__'


class ProductVariantAdminForm(forms.ModelForm):
    description = forms.CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 20}),
        required=False
    )

    class Meta:
        model = ProductVariant
        fields = '__all__'


# Inlines
class ProductImagesInline(admin.TabularInline):
    model = ProductImages
    extra = 1
    fields = ['image', 'alt_text', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html('<img src="{}" width="100" height="auto" />', obj.image.url)
        return "No image"

    image_preview.short_description = 'Preview'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'image_preview']
    readonly_fields = ['image_preview']

    def image_preview(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
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
    fields = ['storage_capacity', 'price_adjustment', 'price', 'is_active']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    form = ProductVariantAdminForm
    extra = 1
    fields = ['name', 'price_adjustment', 'price', 'is_active', 'description', 'main_image']
    show_change_link = True


# Main ModelAdmin classes
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    form = CategoryAdminForm
    list_display = ['name', 'is_active', 'created_at', 'description_preview']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

    def description_preview(self, obj):
        if obj.description:
            from django.utils.html import strip_tags
            text = strip_tags(obj.description)
            return text[:50] + '...' if len(text) > 50 else text
        return "-"

    description_preview.short_description = 'Description Preview'

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'is_active'),
        }),
        ('Content', {
            'fields': ('description',),
            'classes': ('wide',),
        }),
        ('Media', {
            'fields': ('image', 'video'),
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ['name', 'category', 'price', 'sku', 'is_active', 'created_at']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImagesInline, ProductVariantInline]
    save_on_top = True

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'category', 'price', 'sale_price', 'icon', 'main_image_desktop', 'main_image_tablet', 'main_image_phone',),
        }),
        ('Content', {
            'fields': ('description',),
            'classes': ('wide', 'extrapretty'),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
    )


# @admin.register(ProductImages)
class ProductImagesAdmin(admin.ModelAdmin):
    list_display = ['get_product_name', 'image_preview', 'alt_text']
    search_fields = ['product__name', 'alt_text']
    list_filter = ['product__category']
    readonly_fields = ['image_preview']

    def get_product_name(self, obj):
        return obj.product.name

    get_product_name.short_description = 'Product'

    def image_preview(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html('<img src="{}" width="150" height="auto" />', obj.image.url)
        return "No image"

    image_preview.short_description = 'Preview'


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    form = ProductVariantAdminForm
    list_display = ['get_product_name', 'name', 'price', 'price_adjustment', 'is_active', 'slug']
    list_filter = ['is_active', 'product__category']
    search_fields = ['name', 'description', 'product__name']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductVariantColorInline]

    def get_product_name(self, obj):
        return obj.product.name

    get_product_name.short_description = 'Product'

    fieldsets = (
        ('Variant Information', {
            'fields': ('product', 'name', 'price', 'price_adjustment', 'is_active', 'main_image', 'slug'),
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('wide',),
        }),
    )


@admin.register(ProductVariantColor)
class ProductVariantColorAdmin(admin.ModelAdmin):
    list_display = ['get_product', 'get_variant', 'color_name', 'color_preview']
    list_filter = ['product_variant__product__category', 'product_variant']
    search_fields = ['color_name', 'product_variant__name', 'product_variant__product__name']
    readonly_fields = ['color_preview']
    inlines = [ProductImageInline, ProductVariantStorageInline]

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


# @admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['get_product', 'get_variant', 'get_color', 'is_primary', 'image_preview']
    list_filter = ['is_primary', 'product_variant_color__product_variant__product__category']
    search_fields = ['alt_text', 'product_variant_color__color_name',
                     'product_variant_color__product_variant__name',
                     'product_variant_color__product_variant__product__name']
    readonly_fields = ['image_preview']

    def get_product(self, obj):
        return obj.product_variant_color.product_variant.product.name

    get_product.short_description = 'Product'

    def get_variant(self, obj):
        return obj.product_variant_color.product_variant.name

    get_variant.short_description = 'Variant'

    def get_color(self, obj):
        return obj.product_variant_color.color_name

    get_color.short_description = 'Color'

    def image_preview(self, obj):
        if obj.image and hasattr(obj.image, 'url'):
            return format_html('<img src="{}" width="150" height="auto" />', obj.image.url)
        return "No image"

    image_preview.short_description = 'Preview'


@admin.register(ProductVariantStorage)
class ProductVariantStorageAdmin(admin.ModelAdmin):
    list_display = ['get_product', 'get_variant', 'storage_capacity', 'price', 'price_adjustment', 'is_active']
    list_filter = ['is_active', 'product_variant__product_variant__product']
    search_fields = ['storage_capacity', 'product_variant__color_name', 'product_variant__product_variant__name']

    def get_product(self, obj):
        return obj.product_variant.product_variant.name

    get_product.short_description = 'Product'

    def get_variant(self, obj):
        return obj.product_variant.product_variant


    get_variant.short_description = 'Variant'

