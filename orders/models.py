# orders/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from products.models import Product, ProductVariant
from users.models import Address
import uuid


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', null=True, blank=True,
                                verbose_name=_('User'))
    session_id = models.CharField(_('Session ID'), max_length=100, null=True, blank=True)  # For non-logged in users
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')

    def __str__(self):
        if self.user:
            return _("Cart - %(username)s") % {'username': self.user.username}
        return _("Cart - %(session_id)s") % {'session_id': self.session_id}

    @property
    def total_price(self):
        """Calculate the total price of all items in the cart"""
        return sum(item.subtotal for item in self.items.all())

    @property
    def item_count(self):
        """Get the total number of items in the cart"""
        return self.items.count()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name=_('Cart'))
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_('Product'))
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True,
                                verbose_name=_('Variant'))
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        unique_together = ('cart', 'product', 'variant')

    def __str__(self):
        variant_str = f" - {self.variant.name}" if self.variant else ""
        return f"{self.product.name}{variant_str} × {self.quantity}"

    @property
    def unit_price(self):
        """Calculate the unit price including any variant price adjustments"""
        base_price = self.product.sale_price if self.product.sale_price else self.product.price
        if self.variant:
            return base_price + self.variant.price_adjustment
        return base_price

    @property
    def subtotal(self):
        """Calculate the subtotal for this cart item"""
        return self.unit_price * self.quantity


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('shipped', _('Shipped')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='orders', null=True, verbose_name=_('User'))
    order_number = models.CharField(_('Order Number'), max_length=20, unique=True)
    shipping_address = models.ForeignKey(
        Address, related_name='shipping_orders',
        on_delete=models.SET_NULL, null=True,
        verbose_name=_('Shipping Address')
    )
    billing_address = models.ForeignKey(
        Address, related_name='billing_orders',
        on_delete=models.SET_NULL, null=True,
        verbose_name=_('Billing Address')
    )
    total_price = models.DecimalField(_('Total Price'), max_digits=10, decimal_places=2)
    shipping_price = models.DecimalField(_('Shipping Price'), max_digits=6, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(_('Tax Amount'), max_digits=6, decimal_places=2, default=0.00)
    status = models.CharField(_('Status'), max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(_('Payment Method'), max_length=50, null=True)
    payment_id = models.CharField(_('Payment ID'), max_length=100, null=True, blank=True)
    is_paid = models.BooleanField(_('Is Paid'), default=False)
    paid_at = models.DateTimeField(_('Paid At'), null=True, blank=True)
    notes = models.TextField(_('Notes'), blank=True, null=True)
    tracking_number = models.CharField(_('Tracking Number'), max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']

    def __str__(self):
        return _("Order %(order_number)s") % {'order_number': self.order_number}

    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate a unique order number based on the current timestamp
            self.order_number = f"ORD-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name=_('Order'))
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name=_('Product'))
    product_name = models.CharField(_('Product Name'), max_length=200)  # Store name in case product is deleted
    product_variant = models.CharField(_('Product Variant'), max_length=100, null=True, blank=True)
    product_sku = models.CharField(_('Product SKU'), max_length=50)
    quantity = models.PositiveIntegerField(_('Quantity'), default=1)
    unit_price = models.DecimalField(_('Unit Price'), max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(_('Subtotal'), max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    def save(self, *args, **kwargs):
        # Calculate subtotal
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
