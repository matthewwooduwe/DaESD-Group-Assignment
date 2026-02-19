from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from products.models import Product
from decimal import Decimal

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        READY = 'READY', _('Ready')
        DELIVERED = 'DELIVERED', _('Delivered')

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    commission_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text=_("Calculated 5% network commission"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    delivery_date = models.DateField(blank=True, null=True, help_text=_("Must enforce 48-hour lead time"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'orders'

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT) # Protect to keep history if product deleted? Or set null?
    quantity = models.PositiveIntegerField()
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Snapshot for financial auditing"))
    producer_payout = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text=_("95% of item value"))
    network_commission = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text=_("5% of item value"))

    class Meta:
        db_table = 'order_items'

    def save(self, *args, **kwargs):
        if not self.price_at_sale:
            self.price_at_sale = self.product.price
        
        # Calculate splits
        total_val = self.price_at_sale * self.quantity
        self.network_commission = total_val * Decimal('0.05')
        self.producer_payout = total_val * Decimal('0.95')
        
        super().save(*args, **kwargs)

class SurplusDeal(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='surplus_deals')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text=_("Target 10-50% for waste reduction"))
    expiry_date = models.DateTimeField()
    deal_note = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'surplus_deals'
