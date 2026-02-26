from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductProxyView.as_view(), name='product-list-create'),
    path('<int:pk>/', views.ProductDetailProxyView.as_view(), name='product-detail'),
]
