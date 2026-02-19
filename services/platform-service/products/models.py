from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text=_("Vegetables, Dairy, Bakery, etc."))

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    # Removed internal Category enum, using ForeignKey to Category model
    
    producer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=50, blank=True, null=True, help_text=_("e.g., 'dozen', 'kg'"))
    
    stock_quantity = models.PositiveIntegerField(default=0, help_text=_("Real-time inventory tracking"))
    allergen_info = models.TextField(blank=True, null=True, help_text=_("Compliance with food safety regulations"))
    
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

    def __str__(self):
        return f"{self.name} - {self.producer.username}"
