from rest_framework import generics, permissions
from .models import Product
from .serializers import ProductSerializer

class IsProducerOrReadOnly(permissions.BasePermission):
    """
    Allows only Producers to create content. Read-only for others.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'PRODUCER'

class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsProducerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(producer=self.request.user)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsProducerOrReadOnly]
