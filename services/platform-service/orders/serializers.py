from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusLog, CustomerOrder
from products.models import Product
from django.utils import timezone
import datetime

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price_at_sale')
        read_only_fields = ('id', 'price_at_sale')

class OrderStatusLogSerializer(serializers.ModelSerializer):
    producer_name = serializers.ReadOnlyField(source='producer.username')

    class Meta:
        model = OrderStatusLog
        fields = ('id', 'producer', 'producer_name', 'status', 'note', 'created_at')
        read_only_fields = ('id', 'producer', 'producer_name', 'created_at')

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    status_logs = OrderStatusLogSerializer(many=True, read_only=True)
    customer_username = serializers.ReadOnlyField(source='customer.username')
    
    # Customer Details for Producers
    customer_full_name = serializers.CharField(source='customer.customer_profile.full_name', read_only=True)
    customer_phone = serializers.CharField(source='customer.phone_number', read_only=True)
    customer_email = serializers.CharField(source='customer.email', read_only=True)
    delivery_address = serializers.CharField(source='customer.customer_profile.delivery_address', read_only=True)
    
    # Producer Details for Overall Customer Orders
    producer_name = serializers.CharField(source='producer.producer_profile.business_name')
    
    # Producer specific total
    producer_total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id', 'customer', 'customer_username', 'customer_full_name', 'customer_phone', 
            'customer_email', 'delivery_address', 'collection_type', 'total_amount', 'producer_name',
            'producer_total', 'status', 'status_logs', 'delivery_date', 'created_at', 'items'
        )
        read_only_fields = ('id', 'customer', 'total_amount', 'created_at', 'items', 'producer_total', 'status_logs')

    def get_items(self, obj):
        request = self.context.get('request')
        items = obj.items.all()
        
        # If the requester is a PRODUCER, only show their products in this order
        if request and hasattr(request, 'user') and request.user.role == 'PRODUCER':
            items = items.filter(product__producer=request.user)
            
        return OrderItemSerializer(items, many=True).data

    def get_producer_total(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.role == 'PRODUCER':
            items = obj.items.filter(product__producer=request.user)
            # Sum up producer_payout or just unit price * quantity depending on need
            # We'll use price_at_sale * quantity as total value the customer paid for their items
            return sum(item.price_at_sale * item.quantity for item in items)
        return None

    def validate_delivery_date(self, value):
        if value:
            # Enforce 48 hour lead time
            # Assuming delivery dates are whole dates, 48 hours means delivery date must be >= today + 2 days
            min_date = timezone.now().date() + datetime.timedelta(days=2)
            if value < min_date:
                raise serializers.ValidationError("Delivery date must be at least 48 hours from now.")
        return value

class CustomerOrderSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True)
    overall_status = serializers.CharField(read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = CustomerOrder
        fields = (
            'id', 'customer', 'total_amount', 'commission_total', 'overall_status',
            'total_items', 'orders', 'created_at', 'updated_at'
        )