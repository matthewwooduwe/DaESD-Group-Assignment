from rest_framework import serializers
from .models import Basket, BasketItem
from products.serializers import ProductSerializer

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
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    customer_username = serializers.ReadOnlyField(source='customer.username')

    class Meta:
        model = Basket
        fields = ('id', 'customer', 'customer_username', 'items', 'total_items', 'total_price', 'created_at', 'updated_at')
        read_only_fields = ('id', 'customer', 'created_at', 'updated_at')
    
    def get_total_items(self, obj):
        return obj.total_items
    
    def get_total_price(self, obj):
        return obj.total_price
