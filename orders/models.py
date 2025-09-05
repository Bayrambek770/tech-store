import uuid
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from products.models import Product
from designs.models import DesignAsset


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    currency = models.CharField(_('Currency'), max_length=8, default='UZS')
    total_price = models.DecimalField(_('Total Price'), max_digits=14, decimal_places=2, default=0)
    # customer info (optional until payment success)
    first_name = models.CharField(_('First name'), max_length=60, blank=True, null=True)
    last_name = models.CharField(_('Last name'), max_length=80, blank=True, null=True)
    email = models.EmailField(_('Email'), max_length=150, blank=True, null=True)
    phone = models.CharField(_('Phone'), max_length=32, blank=True, null=True)
    address1 = models.CharField(_('Address line 1'), max_length=160, blank=True, null=True)
    address2 = models.CharField(_('Address line 2'), max_length=160, blank=True, null=True)
    country = models.CharField(_('Country'), max_length=80, blank=True, null=True)
    state = models.CharField(_('State/Region'), max_length=80, blank=True, null=True)
    zip = models.CharField(_('ZIP'), max_length=24, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.pk} ({self.currency} {self.total_price})"

    def recalc_total(self, commit=True):
        total = Decimal('0')
        for item in self.items.all():
            total += item.line_total
        self.total_price = total
        if commit:
            super().save(update_fields=['total_price'])
        return total


class OrderItem(models.Model):
    KIND_CHOICES = (
        ('product', _('Product')),
        ('design', _('Design Asset')),
        ('donation', _('Donation')),
    )
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    kind = models.CharField(max_length=12, choices=KIND_CHOICES)
    product = models.ForeignKey(Product, null=True, blank=True, on_delete=models.PROTECT)
    design_asset = models.ForeignKey(DesignAsset, null=True, blank=True, on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # Stored in same currency as parent order for now (denormalized clarity)
    currency = models.CharField(max_length=8, default='UZS')
    line_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        ordering = ['created_at', 'pk']

    def __str__(self):
        return f"{self.name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.line_total = (self.unit_price or Decimal('0')) * self.quantity
        super().save(*args, **kwargs)
        if self.order_id:
            self.order.recalc_total(commit=True)
