from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer

class OrderListCreateView(generics.ListCreateAPIView):
    """
    Handles listing and creating orders.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Order.objects.all()
        if user.role == 'PRODUCER':
            # Return orders that contain items from this producer's products
            return Order.objects.filter(items__product__producer=user).distinct()
        # Standard customers see only their own orders
        return Order.objects.filter(customer=user)

    def perform_create(self, serializer):
        # Automatically assign the current user as the order customer
        serializer.save(customer=self.request.user)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Order.objects.all()
        if user.role == 'PRODUCER':
            return Order.objects.filter(items__product__producer=user).distinct()
        return Order.objects.filter(customer=user)
