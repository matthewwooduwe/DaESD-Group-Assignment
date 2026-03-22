from django.contrib import admin
from django.urls import path
from web import views
urlpatterns = [
    # Index
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    
    # Products listing and catalogue
    path('products/new/', views.add_product_view, name='add_product'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/edit/', views.edit_product_view, name='edit_product'),
    path('products/<int:product_id>/delete/', views.delete_product_view, name='delete_product'),
    
    # Producer dashboard
    path('dashboard/', views.producer_dashboard, name='dashboard'),
    
    # Login & registration
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Customer basket and checkout
    path('basket/', views.basket_view, name='basket'),
    path('basket/add/<int:product_id>/', views.add_to_basket, name='add-to-basket'),
    path('basket/update/<int:item_id>/', views.update_basket_item, name='update-basket-item'),
    path('basket/remove/<int:item_id>/', views.remove_from_basket, name='remove-from-basket'),
    path('basket/clear/', views.clear_basket, name='clear-basket'),
    path('basket/checkout/', views.checkout_view, name='checkout'),
    
    # Orders placement
    path('orders/', views.customer_order_history_view, name='customer-orders'),
    path('orders/place/', views.create_order, name='create-order'),
    path('orders/customer/<int:order_id>/', views.customer_order_detail_view, name='customer-order-detail'),

    # Producer dashboard and orders
    path('profile/', views.profile_view, name='profile'),
    path('admin-dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('admin-dashboard/users/<int:user_id>/delete/', views.admin_delete_user, name='admin-delete-user'),
    path('admin-dashboard/users/<int:user_id>/edit/', views.admin_edit_user, name='admin-edit-user'),
    path('admin-dashboard/products/<int:product_id>/delete/', views.admin_delete_product, name='admin-delete-product'),
    path('dashboard/orders/', views.producer_orders_view, name='producer_orders'),
    path('dashboard/orders/<int:order_id>/', views.producer_order_detail_view, name='producer_order_detail'),
    path('dashboard/orders/<int:order_id>/status/', views.producer_update_order_status_view, name='producer_update_order_status'),
]
