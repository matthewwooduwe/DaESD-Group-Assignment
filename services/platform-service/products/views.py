from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category, Recipe, FarmStory
from .serializers import ProductSerializer, CategorySerializer, RecipeSerializer, FarmStorySerializer

class IsProducerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow Producers to edit or create products.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'PRODUCER'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only the producer who created the product can edit/delete it
        return obj.producer == request.user

class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Allow admins to create? For now open or just producers? Let's generic.

class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsProducerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__name', 'is_organic', 'producer__username', 'is_available']
    search_fields = ['name', 'description', 'producer__username']
    ordering_fields = ['price', 'created_at', 'stock_quantity']

    def get_queryset(self):
        queryset = Product.objects.all()
        # Filter out products containing specified allergens
        exclude_allergens = self.request.query_params.getlist('exclude_allergen')
        if exclude_allergens:
            for allergen in exclude_allergens:
                # Exclude products whose allergens JSON list contains this allergen
                queryset = queryset.exclude(allergens__contains=allergen)
        return queryset

    def perform_create(self, serializer):
        serializer.save(producer=self.request.user)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsProducerOrReadOnly]

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class RecipeListCreateView(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsProducerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['producer__username', 'products__id']
    search_fields = ['title', 'description', 'ingredients', 'producer__username']
    ordering_fields = ['created_at']

    def perform_create(self, serializer):
        serializer.save(producer=self.request.user)

class RecipeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [IsProducerOrReadOnly]

class FarmStoryListCreateView(generics.ListCreateAPIView):
    queryset = FarmStory.objects.all()
    serializer_class = FarmStorySerializer
    permission_classes = [IsProducerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['producer__username']
    search_fields = ['title', 'content', 'producer__username']
    ordering_fields = ['created_at']

    def perform_create(self, serializer):
        serializer.save(producer=self.request.user)

class FarmStoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FarmStory.objects.all()
    serializer_class = FarmStorySerializer
    permission_classes = [IsProducerOrReadOnly]
