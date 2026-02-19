from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    customer_username = serializers.ReadOnlyField(source='customer.username')

    class Meta:
        model = Review
        fields = ('id', 'customer', 'customer_username', 'product', 'order', 'rating', 'comment', 'created_at')
        read_only_fields = ('id', 'customer', 'created_at')
