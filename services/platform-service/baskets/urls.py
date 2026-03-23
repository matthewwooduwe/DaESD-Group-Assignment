from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    BasketView,
    AddToBasketView,
    UpdateBasketItemView,
    RemoveFromBasketView,
    ClearBasketView,
    CheckoutView
)

urlpatterns = [
    path('', BasketView.as_view(), name='basket-detail'),
    path('add/', AddToBasketView.as_view(), name='basket-add'),
    path('items/<int:item_id>/', UpdateBasketItemView.as_view(), name='basket-item-update'),
    path('items/<int:item_id>/remove/', RemoveFromBasketView.as_view(), name='basket-item-remove'),
    path('clear/', ClearBasketView.as_view(), name='basket-clear'),
    path('checkout/', CheckoutView.as_view(), name='basket-checkout'),
]