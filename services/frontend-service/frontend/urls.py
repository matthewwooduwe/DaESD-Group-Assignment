from django.contrib import admin
from django.urls import path
from web import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('basket/', views.basket_view, name='basket'),
    path('basket/add/<int:product_id>/', views.add_to_basket, name='add-to-basket'),
    path('basket/update/<int:item_id>/', views.update_basket_item, name='update-basket-item'),
    path('basket/remove/<int:item_id>/', views.remove_from_basket, name='remove-from-basket'),
    path('basket/clear/', views.clear_basket, name='clear-basket'),
]