from django.db import models


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
    ]

    order_id = models.CharField(max_length=64, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='gbp')
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING',
    )
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    request_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

    def __str__(self):
        reference = self.order_id or self.stripe_session_id or self.pk
        return f"Payment {reference} - {self.amount} {self.currency} ({self.status})"
