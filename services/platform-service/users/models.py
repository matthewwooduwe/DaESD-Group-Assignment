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

    # Override the groups and user_permissions fields to set custom db_table names
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="user_set",
        related_query_name="user",
        db_table='users_groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="user_set",
        related_query_name="user",
        db_table='users_permissions',
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
