from rest_framework import serializers
from .models import Product, Category
from orders.models import SurplusDeal
from django.utils import timezone
from users.serializers import ProducerProfileSerializer
import datetime

class SurplusDealSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurplusDeal
        fields = ('id', 'discount_percentage', 'expiry_date', 'deal_note')

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

    is_surplus = serializers.ReadOnlyField()
    current_price = serializers.ReadOnlyField()
    surplus_deal = SurplusDealSerializer(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = (
            'id', 'producer', 'producer_username', 'producer_profile', 'category', 'name', 'description', 
            'price', 'current_price', 'is_surplus', 'surplus_deal', 'unit', 'stock_quantity', 'allergens', 'allergen_info', 'is_organic', 
            'is_available', 'harvest_date', 'best_before_date', 
            'seasonal_start_month', 'seasonal_end_month', 'image',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'producer', 'created_at', 'updated_at', 'is_surplus', 'current_price')

    def create(self, validated_data):
        surplus_deal_data = validated_data.pop('surplus_deal', None)
        
        request = self.context.get('request')
        if not surplus_deal_data and request and hasattr(request, 'data'):
            has_surplus = str(request.data.get('is_surplus', '')).lower() == 'true'
            if has_surplus:
                surplus_deal_data = {}
                if request.data.get('surplus_deal.discount_percentage'):
                    surplus_deal_data['discount_percentage'] = request.data.get('surplus_deal.discount_percentage')
                if request.data.get('surplus_deal.expiry_date'):
                    surplus_deal_data['expiry_date'] = request.data.get('surplus_deal.expiry_date')
                if request.data.get('surplus_deal.deal_note'):
                    surplus_deal_data['deal_note'] = request.data.get('surplus_deal.deal_note')

        product = super().create(validated_data)
        
        if surplus_deal_data:
            SurplusDeal.objects.create(product=product, **surplus_deal_data)
            
        return product

    def update(self, instance, validated_data):
        surplus_deal_data = validated_data.pop('surplus_deal', None)
        
        request = self.context.get('request')
        if not surplus_deal_data and request and hasattr(request, 'data'):
            has_surplus = str(request.data.get('is_surplus', '')).lower() == 'true'
            if has_surplus:
                surplus_deal_data = {}
                if request.data.get('surplus_deal.discount_percentage'):
                    surplus_deal_data['discount_percentage'] = request.data.get('surplus_deal.discount_percentage')
                if request.data.get('surplus_deal.expiry_date'):
                    surplus_deal_data['expiry_date'] = request.data.get('surplus_deal.expiry_date')
                if request.data.get('surplus_deal.deal_note'):
                    surplus_deal_data['deal_note'] = request.data.get('surplus_deal.deal_note')

        product = super().update(instance, validated_data)
        
        # Determine if we need to update/create/delete the surplus deal
        # The frontend might send an explicit null to clear it, or send data to update it
        if request and 'is_surplus' in request.data:
            is_surplus_str = str(request.data.get('is_surplus')).lower()
            wants_surplus = is_surplus_str == 'true'
            
            if wants_surplus and surplus_deal_data:
                # Update currently active deal or create new
                active_deal = product.surplus_deal
                if active_deal:
                    for attr, value in surplus_deal_data.items():
                        setattr(active_deal, attr, value)
                    active_deal.save()
                else:
                    SurplusDeal.objects.create(product=product, **surplus_deal_data)
            elif not wants_surplus:
                # Delete existing active deal if any
                active_deal = product.surplus_deal
                if active_deal:
                    active_deal.delete()

        return product
