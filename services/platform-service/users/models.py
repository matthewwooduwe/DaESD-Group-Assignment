from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        PRODUCER = "PRODUCER", "Producer"
        CUSTOMER = "CUSTOMER", "Customer"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.CUSTOMER)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        db_table = 'users'

    groups = models.ManyToManyField(
        'auth.Group',
        related_name="user_set",
        related_query_name="user",
        db_table='users_groups',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name="user_set",
        related_query_name="user",
        db_table='users_permissions',
        blank=True,
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
