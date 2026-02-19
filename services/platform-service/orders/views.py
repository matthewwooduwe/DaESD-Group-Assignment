from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PRODUCER':
            # Producers see orders containing their products (complex query, for now let's simplify or filter)
            # Actually, per schema, orders are linked to customer. 
            # Producers need to see OrderItems related to them. This might need a separate view or filtering.
            # For this MVP step, let's allow users to see their own orders.
            return Order.objects.none() # Placeholder for producer logic
        return Order.objects.filter(customer=user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Order.objects.all()
        return Order.objects.filter(customer=user)
