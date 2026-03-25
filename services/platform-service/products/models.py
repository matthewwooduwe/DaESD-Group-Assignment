from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from decimal import Decimal
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """
    Grouping for products (e.g., Vegetables, Dairy).
    """
    name = models.CharField(max_length=100, unique=True, help_text=_("Vegetables, Dairy, Bakery, etc."))

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    """
    Represents a food item offered by a producer.
    """
    # Removed internal Category enum, using ForeignKey to Category model
    
    producer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, blank=True, null=True, help_text=_("e.g., 'dozen', 'kg'"))
    
    stock_quantity = models.PositiveIntegerField(default=0, help_text=_("Real-time inventory tracking"))
    allergen_info = models.TextField(blank=True, null=True, help_text=_("Additional allergen information not covered by the 14 major allergens"))
    allergens = models.JSONField(default=list, blank=True, help_text=_("List of major allergens from the UK 14 allergens list"))
    
    is_organic = models.BooleanField(default=False, help_text=_("Supports customer quality filters"))
    is_available = models.BooleanField(default=True)
    
    harvest_date = models.DateField(blank=True, null=True)
    best_before_date = models.DateField(blank=True, null=True, help_text=_("Required for customer transparency"))
    
    seasonal_start_month = models.PositiveSmallIntegerField(blank=True, null=True, help_text=_("Automation for seasonal visibility (1-12)"))
    seasonal_end_month = models.PositiveSmallIntegerField(blank=True, null=True, help_text=_("Automation for seasonal visibility (1-12)"))
    
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'

    @property
    def surplus_deal(self):
        """Returns the active surplus deal if one exists."""
        now = timezone.now()
        # Find a deal that hasn't expired yet
        # Evaluate in memory so prefetch_related works efficiently
        deals = [d for d in self.surplus_deals.all() if d.expiry_date > now]
        if deals:
            # return the deal with the highest discount
            return max(deals, key=lambda d: d.discount_percentage)
        return None

    @property
    def is_surplus(self):
        """Returns True if there is an active surplus deal."""
        return self.surplus_deal is not None

    @property
    def current_price(self):
        """Calculates the current price, applying any active surplus discount."""
        deal = self.surplus_deal
        if deal:
            discount_multiplier = Decimal('1') - (deal.discount_percentage / Decimal('100'))
            return (self.price * discount_multiplier).quantize(Decimal('0.01'))
        return self.price

    def __str__(self):
        return f"{self.name} - {self.producer.username}"
