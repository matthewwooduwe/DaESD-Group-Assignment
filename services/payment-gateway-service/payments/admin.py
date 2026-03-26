from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('order_id', 'stripe_session_id', 'stripe_payment_intent')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    fieldsets = (
        ('Payment Info', {
            'fields': ('order_id', 'amount', 'currency', 'status'),
        }),
        ('Stripe Integration', {
            'fields': ('stripe_session_id', 'stripe_payment_intent', 'request_payload'),
            'classes': ('collapse',),
            'description': 'Captured checkout details for Stripe session tracing.',
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
