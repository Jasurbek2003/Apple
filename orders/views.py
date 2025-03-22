from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from products.models import Product, ProductVariant
from users.models import Address
from .models import CartItem, Order, Cart, OrderItem
from .serializers import (
    CartSerializer, CartItemSerializer,
    OrderSerializer, OrderCreateSerializer
)
from api.swagger import cart_swagger_schema, order_create_swagger_schema

class CartViewSet(viewsets.GenericViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get or create cart for the current user
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return Cart.objects.filter(id=cart.id)

    def get_object(self):
        return self.get_queryset().first()

    @swagger_auto_schema(
        operation_description="Get the current user's shopping cart",
        operation_summary="Get Cart",
        tags=['Cart']
    )
    def retrieve(self, request):
        """Get current user's cart"""
        cart = self.get_object()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Add an item to the cart",
        operation_summary="Add Item to Cart",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['product_id'],
            properties={
                'product_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'variant_id': openapi.Schema(type=openapi.TYPE_INTEGER, nullable=True),
                'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, default=1),
            }
        ),
        tags=['Cart']
    )
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart"""
        cart = self.get_object()
        serializer = CartItemSerializer(data=request.data)

        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            variant_id = serializer.validated_data.get('variant_id')
            quantity = serializer.validated_data.get('quantity', 1)

            # Validate product exists
            product = get_object_or_404(Product, id=product_id)

            # Validate variant exists if provided
            variant = None
            if variant_id:
                variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

            # Check if the item is already in the cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                variant=variant,
                defaults={'quantity': quantity}
            )

            # If item already exists, update quantity
            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Update cart item quantity"""
        cart = self.get_object()
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity', 1)

        if not item_id:
            return Response(
                {'error': _('Item ID is required')},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)

            if quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = quantity
                cart_item.save()

            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

        except CartItem.DoesNotExist:
            return Response(
                {'error': _('Item not found in cart')},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """Remove item from cart"""
        cart = self.get_object()
        item_id = request.data.get('item_id')

        if not item_id:
            return Response(
                {'error': _('Item ID is required')},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart_item = CartItem.objects.get(cart=cart, id=item_id)
            cart_item.delete()
            return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

        except CartItem.DoesNotExist:
            return Response(
                {'error': _('Item not found in cart')},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear all items from cart"""
        cart = self.get_object()
        cart.items.all().delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @order_create_swagger_schema
    def create(self, request):
        """Create a new order from cart"""
        serializer = OrderCreateSerializer(data=request.data)

        if serializer.is_valid():
            # Get user's cart
            try:
                cart = Cart.objects.get(user=request.user)
                if cart.items.count() == 0:
                    return Response(
                        {'error': _('Your cart is empty')},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Cart.DoesNotExist:
                return Response(
                    {'error': _('Your cart is empty')},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate addresses
            shipping_address = get_object_or_404(
                Address,
                id=serializer.validated_data['shipping_address_id'],
                user=request.user
            )

            billing_address = get_object_or_404(
                Address,
                id=serializer.validated_data['billing_address_id'],
                user=request.user
            )

            # Calculate order totals
            cart_total = cart.total_price
            shipping_price = 0  # You may calculate based on shipping method
            tax_rate = 0.05  # Example tax rate (5%)
            tax_amount = cart_total * tax_rate
            order_total = cart_total + shipping_price + tax_amount

            # Create order
            order = Order.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                billing_address=billing_address,
                total_price=order_total,
                shipping_price=shipping_price,
                tax_amount=tax_amount,
                payment_method=serializer.validated_data.get('payment_method'),
                notes=serializer.validated_data.get('notes')
            )

            # Create order items from cart items
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    product_variant=cart_item.variant.name if cart_item.variant else None,
                    product_sku=cart_item.product.sku,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    subtotal=cart_item.subtotal
                )

            # Clear the cart after order creation
            cart.items.all().delete()

            return Response(
                OrderSerializer(order).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an order if it's in a cancellable state"""
        order = self.get_object()

        # Only allow cancellation of pending or processing orders
        if order.status not in ['pending', 'processing']:
            return Response(
                {'error': _('This order cannot be cancelled')},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'cancelled'
        order.save()

        return Response(
            {'message': _('Order cancelled successfully')},
            status=status.HTTP_200_OK
        )
