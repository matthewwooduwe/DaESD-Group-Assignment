from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import ProducerProfile, CustomerProfile
import re

User = get_user_model()

UK_POSTCODE_RE = re.compile(
    r'^[A-Z]{1,2}[0-9][0-9A-Z]?\s*[0-9][A-Z]{2}$',
    re.IGNORECASE
)

def validate_uk_postcode(value):
    if not value or not value.strip():
        raise serializers.ValidationError("Postcode is required.")
    if not UK_POSTCODE_RE.match(value.strip()):
        raise serializers.ValidationError("Enter a valid UK postcode (e.g. BS1 1AA).")
    return value.strip().upper()

class ProducerProfileSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(required=False, allow_blank=True, default='')
    business_address = serializers.CharField(required=False, allow_blank=True, default='')
    postcode = serializers.CharField(required=True)
    bio = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = ProducerProfile
        fields = ('business_name', 'business_address', 'postcode', 'bio')

    def validate_postcode(self, value):
        return validate_uk_postcode(value)

class CustomerProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')
    delivery_address = serializers.CharField(required=False, allow_blank=True, default='')
    postcode = serializers.CharField(required=True)

    class Meta:
        model = CustomerProfile
        fields = ('first_name', 'last_name', 'delivery_address', 'postcode')

    def validate_postcode(self, value):
        return validate_uk_postcode(value)

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    producer_profile = ProducerProfileSerializer(required=False)
    customer_profile = CustomerProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'email', 'role', 'phone_number', 'producer_profile', 'customer_profile')
        read_only_fields = ('id',)

    def create(self, validated_data):
        producer_data = validated_data.pop('producer_profile', None)
        customer_data = validated_data.pop('customer_profile', None)

        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', ''),
            role=validated_data.get('role', 'CUSTOMER'),
            phone_number=validated_data.get('phone_number', ''),
        )

        if user.role == 'PRODUCER':
            ProducerProfile.objects.create(user=user, **(producer_data or {}))
        elif user.role == 'CUSTOMER':
            CustomerProfile.objects.create(user=user, **(customer_data or {}))

        return user

    def update(self, instance, validated_data):
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

class ProducerPublicSerializer(serializers.ModelSerializer):
    producer_profile = ProducerProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'producer_profile')
        read_only_fields = ('id', 'username', 'producer_profile')
