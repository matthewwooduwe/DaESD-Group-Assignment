from rest_framework import serializers
from .models import Product, Category
from users.serializers import ProducerProfileSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    producer_username = serializers.ReadOnlyField(source='producer.username')
    producer_profile = ProducerProfileSerializer(source='producer.producer_profile', read_only=True)

    category = serializers.SlugRelatedField(
        slug_field='name', 
        queryset=Category.objects.all(),
        help_text="Name of the category (e.g., 'Vegetables', 'Dairy')"
    )

    class Meta:
        model = Product
        fields = (
            'id', 'producer', 'producer_username', 'producer_profile', 'category', 'name', 'description', 
            'price', 'unit', 'stock_quantity', 'allergen_info', 'is_organic', 
            'is_available', 'harvest_date', 'best_before_date', 
            'seasonal_start_month', 'seasonal_end_month', 'image',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'producer', 'created_at', 'updated_at')
