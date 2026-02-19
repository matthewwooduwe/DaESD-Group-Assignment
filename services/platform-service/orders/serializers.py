from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price_at_sale')
        read_only_fields = ('id', 'price_at_sale')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_username = serializers.ReadOnlyField(source='customer.username')
    item_ids = serializers.ListField(
        child=serializers.DictField(child=serializers.IntegerField()), 
        write_only=True,
        help_text=" List of {'product_id': int, 'quantity': int}"
    )

    class Meta:
        model = Order
        fields = ('id', 'customer', 'customer_username', 'total_amount', 'status', 'delivery_date', 'created_at', 'items', 'item_ids')
        read_only_fields = ('id', 'customer', 'total_amount', 'created_at', 'items')

    def create(self, validated_data):
        item_ids = validated_data.pop('item_ids')
        order = Order.objects.create(**validated_data)
        
        total_amount = 0
        for item_data in item_ids:
            product = Product.objects.get(id=item_data['product_id'])
            # Check stock
            if product.stock_quantity < item_data['quantity']:
                raise serializers.ValidationError(f"Not enough stock for {product.name}")
            
            # Create OrderItem
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item_data['quantity'],
                price_at_sale=product.price
            )
            
            # Update stock
            product.stock_quantity -= item_data['quantity']
            product.save()
            
            total_amount += product.price * item_data['quantity']
            
        order.total_amount = total_amount
        order.save()
        
        return order
