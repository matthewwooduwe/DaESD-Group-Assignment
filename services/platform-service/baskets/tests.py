from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Category
from baskets.models import Basket, BasketItem
from orders.models import SurplusDeal
from decimal import Decimal

User = get_user_model()

class BasketSurplusDealTests(TestCase):
    def setUp(self):
        self.producer = User.objects.create_user(username='producer', password='password', role='PRODUCER')
        self.customer = User.objects.create_user(username='customer', password='password', role='CUSTOMER')
        self.category = Category.objects.create(name='Vegetables')
        self.product = Product.objects.create(
            producer=self.producer,
            category=self.category,
            name='Carrots',
            price=Decimal('10.00'),
            stock_quantity=100
        )
        self.basket = Basket.objects.create(customer=self.customer)

    def test_basket_total_with_surplus_deal(self):
        # Initial basket with regular price product
        BasketItem.objects.create(basket=self.basket, product=self.product, quantity=2)
        self.assertEqual(self.basket.total_price, Decimal('20.00'))

        # Add a surplus deal (50% off)
        SurplusDeal.objects.create(
            product=self.product,
            discount_percentage=Decimal('50.00'),
            expiry_date=timezone.now() + timedelta(days=1)
        )
        
        # Product is now half price
        self.assertEqual(self.product.current_price, Decimal('5.00'))
        
        # Basket total automatically updates to using the discounted price
        # since it goes through BasketItem.subtotal -> product.current_price
        self.assertEqual(self.basket.total_price, Decimal('10.00'))
