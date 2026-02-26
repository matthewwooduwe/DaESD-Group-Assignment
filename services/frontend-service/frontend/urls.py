from django.contrib import admin
from django.urls import path
from web import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('products/new/', views.add_product_view, name='add_product'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('dashboard/', views.producer_dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]
