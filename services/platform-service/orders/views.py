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

from rest_framework.views import APIView
import requests
import os

NOTIFICATIONS_API_URL = os.environ.get('NOTIFICATIONS_API_URL', 'http://notifications-api:8001')

class OrderStatusUpdateView(APIView):
    """
    Allows a producer to update the status of an order and log it.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        if request.user.role != 'PRODUCER':
            return Response({'error': 'Only producers can update status'}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            order = Order.objects.filter(pk=pk, items__product__producer=request.user).distinct().get()
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        note = request.data.get('note', '')

        if not new_status:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)

        valid_statuses = [choice[0] for choice in Order.Status.choices]
        if new_status not in valid_statuses:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

        # Basic progression check
        progression = ['PENDING', 'CONFIRMED', 'READY', 'DELIVERED']
        try:
            current_idx = progression.index(order.status)
            new_idx = progression.index(new_status)
            if new_idx <= current_idx:
                return Response({'error': 'Cannot revert to a previous status'}, status=status.HTTP_400_BAD_REQUEST)
            if new_idx > current_idx + 1:
                return Response({'error': 'Status cannot skip a required stage'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            pass

        # Update order status
        order.status = new_status
        order.save()

        # Create log
        from .models import OrderStatusLog
        OrderStatusLog.objects.create(
            order=order,
            producer=request.user,
            status=new_status,
            note=note
        )

        # Trigger notification to customer
        try:
            requests.post(
                f"{NOTIFICATIONS_API_URL}/api/notifications/",
                json={
                    'user': order.customer.id,
                    'message': f"Order #{order.id} status updated to {new_status}" + (f" - Note: {note}" if note else ""),
                    'type': 'ORDER_UPDATE'
                },
                timeout=5
            )
        except Exception:
            pass # Non-critical if notification fails

        return Response({'success': True, 'status': new_status})
