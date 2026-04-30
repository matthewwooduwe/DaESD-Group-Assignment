from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from baskets.models import Basket
from baskets.views import IsCustomer

from .models import Order, OrderItem, CustomerOrder
from .serializers import OrderSerializer, CustomerOrderSerializer

from decimal import Decimal
from django.db import transaction
from collections import defaultdict

import requests
import math
import os


NOTIFICATIONS_API_URL = os.environ.get('NOTIFICATIONS_API_URL', 'http://notifications-api:8001')


def _get_postcode_coords(postcode, session=None):
    """Fetch lat/lng for a UK postcode from postcodes.io."""
    if not postcode:
        return None, None
    try:
        url = f"https://api.postcodes.io/postcodes/{postcode.strip().replace(' ', '%20')}"
        resp = (session or requests).get(url, timeout=5)
        if resp.status_code == 200:
            result = resp.json().get('result') or {}
            return result.get('latitude'), result.get('longitude')
    except Exception:
        pass
    return None, None


def _haversine_miles(lat1, lon1, lat2, lon2):
    R = 3958.8
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def _calculate_food_miles(customer_postcode, producer_postcode):
    """Calculate food miles between two postcodes. Returns float or None."""
    if not customer_postcode or not producer_postcode:
        return None
    lat1, lon1 = _get_postcode_coords(customer_postcode)
    lat2, lon2 = _get_postcode_coords(producer_postcode)
    if None in (lat1, lon1, lat2, lon2):
        return None
    return round(_haversine_miles(lat1, lon1, lat2, lon2), 1)


class OrderCreateView(APIView):
    """
    Handles checkout processing and order placement.
    Creates a CustomerOrder and splits into separate orders by producer.
    Calculates and stores food miles at order creation time.
    """
    permission_classes = [IsCustomer]

    @transaction.atomic
    def post(self, request):
        delivery_dates = request.data.get('delivery_dates', {})
        collection_types = request.data.get('collection_types', {})

        try:
            basket = Basket.objects.get(customer=request.user)
        except Basket.DoesNotExist:
            return Response({'error': 'Your basket is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        basket_items = basket.items.select_related('product', 'product__producer').all()

        if not basket_items:
            return Response({'error': 'Your basket is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get customer postcode once
        customer_postcode = None
        try:
            customer_postcode = request.user.customer_profile.postcode
        except Exception:
            pass

        # Group by producer
        items_by_producer = defaultdict(list)
        for basket_item in basket_items:
            items_by_producer[basket_item.product.producer].append(basket_item)

        # Pre-fetch all producer postcodes and calculate food miles in bulk
        # to avoid multiple API calls during order creation
        producer_postcodes = {}
        for producer in items_by_producer.keys():
            try:
                producer_postcodes[producer.id] = producer.producer_profile.postcode
            except Exception:
                producer_postcodes[producer.id] = None

        customer_order = CustomerOrder.objects.create(customer=request.user)
        total_amount = Decimal('0.00')

        for producer, producer_basket_items in items_by_producer.items():
            producer_id = str(producer.id)
            collection_type = collection_types.get(producer_id, '')

            # Calculate food miles — only for delivery orders
            food_miles = None
            if collection_type and 'collect' not in collection_type.lower():
                producer_postcode = producer_postcodes.get(producer.id)
                if customer_postcode and producer_postcode:
                    food_miles = _calculate_food_miles(customer_postcode, producer_postcode)

            order = Order.objects.create(
                customer_order=customer_order,
                customer=request.user,
                producer=producer,
                delivery_date=delivery_dates.get(producer_id),
                collection_type=collection_type,
                food_miles=food_miles,
            )

            order_subtotal = Decimal('0.00')

            for basket_item in producer_basket_items:
                try:
                    product = basket_item.product
                    if product.stock_quantity < basket_item.quantity:
                        raise ValueError(f'Insufficient stock for {product.name}')
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=basket_item.quantity,
                        price_at_sale=product.price,
                    )
                    product.stock_quantity -= basket_item.quantity
                    product.save()
                    order_subtotal += product.price * basket_item.quantity
                except ValueError as e:
                    return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            order.total_amount = order_subtotal
            order.commission_total = order_subtotal * Decimal('0.05')
            order.save()
            total_amount += order_subtotal

        customer_order.total_amount = total_amount
        customer_order.save()
        basket.items.all().delete()

        serializer = CustomerOrderSerializer(customer_order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomerOrderDetailView(generics.RetrieveAPIView):
    serializer_class = CustomerOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return CustomerOrder.objects.all()
        return CustomerOrder.objects.filter(customer=user)


class CustomerOrderListView(generics.ListAPIView):
    serializer_class = CustomerOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return CustomerOrder.objects.all()
        return CustomerOrder.objects.filter(customer=self.request.user)


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Order.objects.all()
        if user.role == 'PRODUCER':
            return Order.objects.filter(producer=user).distinct()
        return Order.objects.filter(customer=user)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return Order.objects.all()
        if user.role == 'PRODUCER':
            return Order.objects.filter(producer=user).distinct()
        return Order.objects.filter(customer=user)


class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        if request.user.role != 'PRODUCER':
            return Response({'error': 'Only producers can update status'}, status=status.HTTP_403_FORBIDDEN)

        try:
            order = Order.objects.filter(pk=pk, producer=request.user).distinct().get()
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get('status')
        note = request.data.get('note', '')

        if not new_status:
            return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)

        valid_statuses = [choice[0] for choice in Order.Status.choices]
        if new_status not in valid_statuses:
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)

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

        order.status = new_status
        order.save()

        from .models import OrderStatusLog
        OrderStatusLog.objects.create(order=order, producer=request.user, status=new_status, note=note)

        try:
            requests.post(
                f"{NOTIFICATIONS_API_URL}/api/notifications/",
                json={
                    'user': order.customer.id,
                    'message': f"Order #{order.id} status updated to {new_status}" + (f" - Note: {note}" if note else ""),
                    'type': 'ORDER_UPDATE',
                },
                timeout=5,
            )
        except Exception:
            pass

        return Response({'success': True, 'status': new_status})
