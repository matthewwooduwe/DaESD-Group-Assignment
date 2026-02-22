from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    producer_username = serializers.ReadOnlyField(source='producer.username')

    class Meta:
        model = Product
        fields = (
            'id', 'producer', 'producer_username', 'name', 'description', 
            'price', 'category', 'stock_quantity', 'image', 'allergen_info', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'producer', 'created_at', 'updated_at')
