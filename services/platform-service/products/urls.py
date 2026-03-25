from django.urls import path
from .views import (
    ProductListCreateView, ProductDetailView, 
    CategoryList, CategoryDetail,
    RecipeListCreateView, RecipeDetailView,
    FarmStoryListCreateView, FarmStoryDetailView
)

urlpatterns = [
    path('', ProductListCreateView.as_view(), name='product-list-create'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),
    path('recipes/', RecipeListCreateView.as_view(), name='recipe-list-create'),
    path('recipes/<int:pk>/', RecipeDetailView.as_view(), name='recipe-detail'),
    path('farm-stories/', FarmStoryListCreateView.as_view(), name='farmstory-list-create'),
    path('farm-stories/<int:pk>/', FarmStoryDetailView.as_view(), name='farmstory-detail'),
]
