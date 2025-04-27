from django.db import models
from django.utils.text import slugify
from tinymce.models import HTMLField

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = HTMLField(blank=True)  # Using TinyMCE HTMLField
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    video = models.FileField(upload_to='videos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    sku = models.CharField(max_length=20, unique=True)
    main_image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = HTMLField()  # Using TinyMCE HTMLField
    tech_specs = models.JSONField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    icon = models.ImageField(upload_to='products/icons/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProductImages(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        verbose_name_plural = 'Product Images'

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # e.g., "Pro", "Pro max"
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = HTMLField(blank=True, null=True)  # Using TinyMCE HTMLField
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    main_image = models.ImageField(upload_to='products/variants/', blank=True, null=True)


    def __str__(self):
        return f"{self.product.name} - {self.name}"


class ProductVariantColor(models.Model):
    product_variant = models.ForeignKey(ProductVariant, related_name='colors', on_delete=models.CASCADE)
    color_name = models.CharField(max_length=50)
    color_code = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.product_variant.name} - {self.color_name} ({self.color_code})"


class ProductImage(models.Model):
    product_variant_color = models.ForeignKey(ProductVariantColor, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['is_primary', 'created_at']

    def __str__(self):
        return f"Image for {self.product_variant_color.product_variant.product.name} - {self.product_variant_color.color_name}"


class ProductVariantStorage(models.Model):
    product_variant = models.ForeignKey(ProductVariant, related_name='storage', on_delete=models.CASCADE)
    storage_capacity = models.CharField(max_length=50)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product_variant.name} - {self.storage_capacity}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Product Variant Storage'
        unique_together = ('product_variant', 'storage_capacity')
