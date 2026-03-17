from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusLog
from products.models import Product
from django.utils import timezone
from decimal import Decimal
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
    
    # Producer specific total
    producer_total = serializers.SerializerMethodField()

    item_ids = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()), 
        write_only=True,
        help_text=" List of {'product_id': int, 'quantity': int}"
    )

    class Meta:
        model = Order
        fields = (
            'id', 'customer', 'customer_username', 'customer_full_name', 'customer_phone', 
            'customer_email', 'delivery_address', 'total_amount', 'commission_total',
            'producer_total', 'status', 'status_logs', 'delivery_date', 'created_at', 
            'items', 'item_ids'
        )
        read_only_fields = ('id', 'customer', 'total_amount', 'commission_total', 'created_at', 'items', 'producer_total', 'status_logs')

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

    def create(self, validated_data):
        """
        Custom create logic to handle multiple order items and stock validation.
        """
        item_ids = validated_data.pop('item_ids')
        order = Order.objects.create(**validated_data)
        
        total_amount = 0
        for item_data in item_ids:
            product = Product.objects.get(id=item_data['product_id'])
            
            # Atomic check for stock availability
            if product.stock_quantity < item_data['quantity']:
                raise serializers.ValidationError(f"Not enough stock for {product.name}")
            
            # Create the order item snapshot
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price_at_sale=product.price
            )
            
            # Deduct from inventory
            product.stock_quantity -= item_data['quantity']
            product.save()
            
            total_amount += product.price * item_data['quantity']
            
        order.total_amount = total_amount
        order.commission_total = total_amount * Decimal('0.05')
        order.save()
        
        return order
