from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Product, Category
from orders.models import SurplusDeal
from decimal import Decimal

User = get_user_model()

class ProductSurplusDealTests(TestCase):
    def setUp(self):
        self.producer = User.objects.create_user(username='producer', password='password', role='PRODUCER')
        self.category = Category.objects.create(name='Vegetables')
        self.product = Product.objects.create(
            producer=self.producer,
            category=self.category,
            name='Carrots',
            price=Decimal('10.00'),
            stock_quantity=100
        )

    def test_no_surplus_deal(self):
        self.assertFalse(self.product.is_surplus)
        self.assertEqual(self.product.current_price, Decimal('10.00'))
        self.assertIsNone(self.product.surplus_deal)

    def test_active_surplus_deal(self):
        deal = SurplusDeal.objects.create(
            product=self.product,
            discount_percentage=Decimal('20.00'),
            expiry_date=timezone.now() + timedelta(days=1)
        )
        self.assertTrue(self.product.is_surplus)
        self.assertEqual(self.product.current_price, Decimal('8.00'))
        self.assertEqual(self.product.surplus_deal, deal)

    def test_expired_surplus_deal(self):
        deal = SurplusDeal.objects.create(
            product=self.product,
            discount_percentage=Decimal('50.00'),
            expiry_date=timezone.now() - timedelta(days=1)
        )
        # Should not be considered surplus since deal is expired
        self.assertFalse(self.product.is_surplus)
        self.assertEqual(self.product.current_price, Decimal('10.00'))
        self.assertIsNone(self.product.surplus_deal)
