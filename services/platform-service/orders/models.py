from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from products.models import Product
from decimal import Decimal

class ActiveManager(models.Manager):
    """Manager to filter out soft-deleted objects."""
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class CustomerOrder(models.Model):
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_order'
    )
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text=_("The total amount of the overall order including multi-vendor subtotals."))
    commission_total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00,
        help_text=_("Total 5% commission across all producer orders")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customer_orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Customer Order #{self.id} - {self.customer.username}"
    
    @property
    def total_items(self):
        return sum(
            item.quantity
            for order in self.orders.all()
            for item in order.items.all()
        )
    
    @property
    def overall_status(self):
        """
        Calculate overall status based on producer orders:
        - All delivered = DELIVERED
        - All confirmed/ready/delivered = CONFIRMED
        - Any pending = PENDING
        """
        producer_orders = self.orders.all()
        if not producer_orders:
            return "PENDING"
        
        statuses = set(po.status for po in producer_orders)
        
        if statuses == {'DELIVERED'}:
            return 'DELIVERED'
        elif 'PENDING' in statuses:
            return 'PENDING'
        elif statuses <= {'CONFIRMED', 'READY', 'DELIVERED'}:
            return 'CONFIRMED'
        else:
            return 'READY'

class Order(models.Model):
    """
    Represents a customer order within the platform.
    """
    class Status(models.TextChoices):
        # Initial state when order is placed
        PENDING = 'PENDING', _('Pending')
        # Confirmed by the producer
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        # Product is prepared and ready for delivery/pickup
        READY = 'READY', _('Ready')
        # Order successfully delivered to the customer
        DELIVERED = 'DELIVERED', _('Delivered')

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', help_text=_("Customer user that placed the order."))
    customer_order = models.ForeignKey(CustomerOrder, on_delete=models.CASCADE, related_name='orders',help_text=_("Parent customer order item this order belongs to."))
    producer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,null=True, blank=True, related_name='producer_orders')
    producer_payout = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    commission_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text=_("Calculated 5% network commission"))
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    delivery_date = models.DateField(blank=True, null=True, help_text=_("Must enforce 48-hour lead time"))
    collection_type = models.CharField(blank=True, null=True, max_length=50, help_text=_("The collection type for the order. Options are deliver to address or collect from producer."))
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = 'orders'

    def delete(self, *args, **kwargs):
        """Soft delete the order."""
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"

class OrderStatusLog(models.Model):
    """
    Audit trail for order status changes. Tracks the producer who made the change
    and any optional notes they added.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_logs')
    producer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Order.Status.choices)
    note = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'order_status_logs'
        ordering = ['-created_at']

class OrderItem(models.Model):
    """
    Individual products included in an order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT) 
    quantity = models.PositiveIntegerField()
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2, help_text=_("Snapshot for financial auditing"))
    producer_payout = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text=_("95% of item value"))
    network_commission = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text=_("5% of item value"))
    is_deleted = models.BooleanField(default=False)

    objects = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        db_table = 'order_items'

    def delete(self, *args, **kwargs):
        """Soft delete the order item."""
        self.is_deleted = True
        self.save()

    def save(self, *args, **kwargs):
        # Capture current product price if not set
        if not self.price_at_sale:
            self.price_at_sale = self.product.current_price
        
        # Calculate financial splits: 5% to network, 95% to producer
        total_val = self.price_at_sale * self.quantity
        self.network_commission = total_val * Decimal('0.05')
        self.producer_payout = total_val * Decimal('0.95')
        
        super().save(*args, **kwargs)

class SurplusDeal(models.Model):
    """
    Promotional deals for surplus products to reduce food waste.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='surplus_deals')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text=_("Target 10-50% for waste reduction"))
    expiry_date = models.DateTimeField()
    deal_note = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'surplus_deals'

class RecurringOrder(models.Model):
    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, 'Monday'
        TUESDAY = 1, 'Tuesday'
        WEDNESDAY = 2, 'Wednesday'
        THURSDAY = 3, 'Thursday'
        FRIDAY = 4, 'Friday'
        SATURDAY = 5, 'Saturday'
        SUNDAY = 6, 'Sunday'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        PAUSED = 'PAUSED', 'Paused'
        CANCELLED = 'CANCELLED', 'Cancelled'

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recurring_orders')
    
    # Snapshot of what to reorder each week
    source_customer_order = models.ForeignKey(CustomerOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='recurring_schedules')
    order_day = models.IntegerField(choices=DayOfWeek.choices, help_text="Day of week the order is placed (e.g. Monday=0)")
    delivery_day = models.IntegerField(choices=DayOfWeek.choices, help_text="Day of week the delivery is expected (e.g. Wednesday=2)")
    collection_types = models.JSONField(default=dict, help_text="producer_id -> collection_type mapping")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    next_order_date = models.DateField(help_text="Date the next order will be automatically placed")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recurring_orders'

    def __str__(self):
        return f"Recurring Order #{self.id} - Customer: {self.customer.username}"


class RecurringOrderItem(models.Model):
    recurring_order = models.ForeignKey(RecurringOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product',on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        db_table = 'recurring_order_items'