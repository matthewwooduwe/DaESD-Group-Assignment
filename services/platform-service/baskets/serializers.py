from rest_framework import serializers
from .models import Basket, BasketItem
from products.serializers import ProductSerializer
from users.serializers import ProducerProfileSerializer
from collections import defaultdict

class BasketItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = BasketItem
        fields = ('id', 'product', 'product_id', 'quantity', 'subtotal', 'added_at')
        read_only_fields = ('id', 'added_at')
    
    def get_subtotal(self, obj):
        return obj.subtotal


class BasketSerializer(serializers.ModelSerializer):
    items = BasketItemSerializer(many=True, read_only=True)
    items_by_producer = serializers.SerializerMethodField()
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    customer_username = serializers.ReadOnlyField(source='customer.username')

    class Meta:
        model = Basket
        fields = ('id', 'customer', 'customer_username', 'items', 'items_by_producer', 'total_items', 'total_price', 'created_at', 'updated_at')
        read_only_fields = ('id', 'customer', 'created_at', 'updated_at')
    
    def get_total_items(self, obj):
        """
        Get total number of items in the basket.
        """
        return obj.total_items
    
    def get_total_price(self, obj):
        """
        Get total price of all items in the basket.
        """
        return obj.total_price
    
    def get_items_by_producer(self, obj):
        """
        Group basket items by producer for better visibility.
        """

        items = obj.items.select_related('product', 'product__producer').all()
        
        # Group items by producer
        grouped = defaultdict(list)
        for item in items:
            producer = item.product.producer
            grouped[producer].append(item)
        
        # Format the grouped data to return the correct result response
        result = []
        for producer, producer_items in grouped.items():
            producer_subtotal = sum(
                item.product.price * item.quantity 
                for item in producer_items
            )
            
            result.append({
                'producer_id': producer.id,
                'producer_name': producer.username,
                'producer_profile': ProducerProfileSerializer(producer.producer_profile).data,
                'items': BasketItemSerializer(producer_items, many=True).data,
                'subtotal': producer_subtotal
            })
            
        return result