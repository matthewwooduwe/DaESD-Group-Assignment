from django.db import models
from django.conf import settings


class Product(models.Model):
    class Category(models.TextChoices):
        VEGETABLES = "VEGETABLES", "Vegetables"
        DAIRY = "DAIRY", "Dairy"
        BAKERY = "BAKERY", "Bakery"
        PRESERVES = "PRESERVES", "Preserves"
        OTHER = "OTHER", "Other"

    producer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=Category.choices, default=Category.OTHER)
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    allergen_info = models.TextField(blank=True, help_text="List any allergens present in the product")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'products'

    def __str__(self):
        return f"{self.name} - {self.producer.username}"
