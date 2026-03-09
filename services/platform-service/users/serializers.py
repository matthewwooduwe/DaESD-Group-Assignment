from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ProducerProfile, CustomerProfile

User = get_user_model()

class ProducerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProducerProfile
        fields = ('business_name', 'business_address', 'postcode', 'bio')

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ('full_name', 'delivery_address', 'postcode')

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    producer_profile = ProducerProfileSerializer(required=False)
    customer_profile = CustomerProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'role', 'phone_number', 'producer_profile', 'customer_profile')
        read_only_fields = ('id',)

    def create(self, validated_data):
        """
        Custom create logic to automatically instantiate profiles based on the user's role.
        """
        producer_data = validated_data.pop('producer_profile', None)
        customer_data = validated_data.pop('customer_profile', None)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            role=validated_data.get('role', 'CUSTOMER'),
            phone_number=validated_data.get('phone_number', ''),
        )
        
        if user.role == 'PRODUCER' and producer_data:
            ProducerProfile.objects.create(user=user, **producer_data)
        elif user.role == 'CUSTOMER' and customer_data:
            CustomerProfile.objects.create(user=user, **customer_data)
            
        return user

    def update(self, instance, validated_data):
        """
        Custom update logic to handle nested profiles and password changes.
        """
        producer_data = validated_data.pop('producer_profile', None)
        customer_data = validated_data.pop('customer_profile', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()

        if producer_data and instance.role == 'PRODUCER':
            ProducerProfile.objects.update_or_create(user=instance, defaults=producer_data)
        if customer_data and instance.role == 'CUSTOMER':
            CustomerProfile.objects.update_or_create(user=instance, defaults=customer_data)

        return instance
