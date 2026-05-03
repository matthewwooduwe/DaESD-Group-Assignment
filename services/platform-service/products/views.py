from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from django.db.models import Q, F
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Category, Recipe, FarmStory
from .serializers import ProductSerializer, CategorySerializer, RecipeSerializer, FarmStorySerializer

class IsProducerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow Producers to edit or create products.
    Admins can delete any product.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        return request.user.role in ('PRODUCER', 'ADMIN')

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Admins can edit or delete any product
        if request.user.role == 'ADMIN':
            return True
        # Producers can only edit/delete their own products
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
                
        user = self.request.user
        
        # We no longer filter out-of-season products at the database level.
        # They should be visible on the frontend but marked as 'Out of Season'
        # and unpurchasable.
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(producer=self.request.user)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsProducerOrReadOnly]
    
    def perform_update(self, serializer):
        product_before = self.get_object()
        from orders.models import SurplusDeal
        from django.utils import timezone
        was_surplus_before = SurplusDeal.objects.filter(
            product=product_before,
            expiry_date__gt=timezone.now()
        ).exists()
        product = serializer.save()

        # Notify customers if product just became a surplus deal (TC-019)
        if not was_surplus_before and product.is_surplus:
            import requests as http_requests
            import os
            from orders.models import Order

            NOTIFICATIONS_API_URL = os.environ.get('NOTIFICATIONS_API_URL', 'http://notifications-api:8001')
            # Find all unique customers who have ordered from this producer
            customer_ids = Order.objects.filter(
                producer=product.producer
            ).values_list('customer_id', flat=True).distinct()

            for customer_id in customer_ids:
                try:
                    http_requests.post(
                        f"{NOTIFICATIONS_API_URL}/api/notifications/",
                        headers={'X-Service-Secret': os.environ.get('JWT_SECRET_KEY', '')},
                        json={
                            'user': customer_id,
                            'message': f"Surplus Deal: {product.name} from {product.producer.username} is now available at a discount!",
                            'type': 'SURPLUS_DEAL'
                        },
                        timeout=5
                    )
                except Exception:
                    pass

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            # Product has order history — mark as unavailable instead of deleting
            instance.is_available = False
            instance.save()
            return Response(
                {'detail': 'Product has existing orders and cannot be deleted. It has been marked as unavailable instead.'},
                status=status.HTTP_200_OK
            )

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
