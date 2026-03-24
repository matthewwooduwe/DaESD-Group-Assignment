from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('success/', views.checkout_success, name='success'),
    path('cancel/', views.checkout_cancel, name='cancel'),
    path('webhook/', views.webhook, name='webhook'),
    path('api/checkout/', views.create_checkout, name='api-checkout'),
    path('api/transactions/', views.list_transactions, name='api-transactions'),
    path('api/webhook/', views.webhook, name='api-webhook'),
]
