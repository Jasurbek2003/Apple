from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from products.serializers import ProductListSerializer, ProductVariantSerializer
from users.serializers import AddressSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'variant', 'product_id', 'variant_id',
            'quantity', 'unit_price', 'subtotal'
        ]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'item_count', 'created_at', 'updated_at']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_variant',
            'product_sku', 'quantity', 'unit_price', 'subtotal'
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'status_display',
            'total_price', 'shipping_price', 'tax_amount',
            'items', 'shipping_address', 'billing_address',
            'payment_method', 'is_paid', 'paid_at',
            'tracking_number', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'is_paid', 'paid_at']


class OrderCreateSerializer(serializers.ModelSerializer):
    shipping_address_id = serializers.IntegerField()
    billing_address_id = serializers.IntegerField()

    class Meta:
        model = Order
        fields = [
            'shipping_address_id', 'billing_address_id',
            'payment_method', 'notes'
        ]
