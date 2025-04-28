from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


# @admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_id', 'item_count', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'session_id']
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'product_variant', 'product_sku', 'unit_price', 'subtotal']


# @admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'total_price', 'is_paid', 'created_at']
    list_filter = ['status', 'is_paid', 'created_at']
    search_fields = ['order_number', 'user__username', 'user__email']
    readonly_fields = ['order_number', 'total_price']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'notes')
        }),
        ('Pricing', {
            'fields': ('total_price', 'shipping_price', 'tax_amount')
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_id', 'is_paid', 'paid_at')
        }),
        ('Shipping', {
            'fields': ('shipping_address', 'billing_address', 'tracking_number')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

