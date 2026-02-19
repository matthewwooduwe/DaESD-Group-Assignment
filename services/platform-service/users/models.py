from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Extends Django's AbstractUser to include role-based access control (RBAC).
    """
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        PRODUCER = "PRODUCER", "Producer"
        CUSTOMER = "CUSTOMER", "Customer"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CUSTOMER)
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text="Required for producer/customer contact")
    
    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class ProducerProfile(models.Model):
    """
    Detailed profile information for users with the 'PRODUCER' role.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='producer_profile')
    business_name = models.CharField(max_length=255)
    business_address = models.TextField()
    postcode = models.CharField(max_length=20, help_text="Used for Food Miles calculation")
    bio = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'producer_profiles'

    def __str__(self):
        return self.business_name

class CustomerProfile(models.Model):
    """
    Detailed profile information for users with the 'CUSTOMER' role.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    full_name = models.CharField(max_length=255)
    delivery_address = models.TextField()
    postcode = models.CharField(max_length=20, help_text="Used for Food Miles calculation")

    class Meta:
        db_table = 'customer_profiles'

    def __str__(self):
        return self.full_name
