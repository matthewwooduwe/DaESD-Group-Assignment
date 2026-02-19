from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import ProducerProfile, CustomerProfile
from products.models import Category, Product
from orders.models import Order, OrderItem
from reviews.models import Review
from decimal import Decimal
from django.utils import timezone
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial test data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Cleaning old data...')
        
        # Delete in order of dependency to avoid potential PROTECT issues
        # OrderItem has PROTECT on Product, so Orders (cascading to Items) must go before Products
        Review.objects.all().delete()
        Order.objects.all().delete() 
        Product.objects.all().delete()
        Category.objects.all().delete()
        
        # Delete non-superuser users
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS('Old data cleared.'))

        self.stdout.write('Seeding database...')

        # unique username helper
        def get_unique_username(base):
            if not User.objects.filter(username=base).exists():
                return base
            i = 1
            while User.objects.filter(username=f"{base}{i}").exists():
                i += 1
            return f"{base}{i}"

        # 1. Create Users
        admin_username = get_unique_username('admin')
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin')
            self.stdout.write(self.style.SUCCESS(f'Created superuser: {admin_username}'))

        producer_username = get_unique_username('producer_bob')
        producer, created = User.objects.get_or_create(
            username=producer_username,
            defaults={
                'email': 'bob@farm.com',
                'role': 'PRODUCER',
                'phone_number': '1234567890'
            }
        )
        if created:
            producer.set_password('password123')
            producer.save()
            ProducerProfile.objects.create(
                user=producer,
                business_name="Bob's Farm",
                business_address="123 Farm Lane",
                postcode="BS1 1AA",
                bio="Fresh produce from Bristol."
            )
            self.stdout.write(self.style.SUCCESS(f'Created producer: {producer_username}'))

        customer_username = get_unique_username('customer_alice')
        customer, created = User.objects.get_or_create(
            username=customer_username,
            defaults={
                'email': 'alice@example.com',
                'role': 'CUSTOMER',
                'phone_number': '0987654321'
            }
        )
        if created:
            customer.set_password('password123')
            customer.save()
            CustomerProfile.objects.create(
                user=customer,
                full_name="Alice Smith",
                delivery_address="456 City Road",
                postcode="BS2 2BB"
            )
            self.stdout.write(self.style.SUCCESS(f'Created customer: {customer_username}'))

        # 2. Create Categories
        categories = ['Vegetables', 'Fruits', 'Dairy', 'Bakery', 'Meat']
        cat_objs = {}
        for cat_name in categories:
            cat, _ = Category.objects.get_or_create(name=cat_name)
            cat_objs[cat_name] = cat
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} categories'))

        # 3. Create Products
        products_data = [
            {
                'name': 'Carrots',
                'category': 'Vegetables',
                'price': Decimal('1.50'),
                'unit': 'kg',
                'stock': 100,
                'organic': True
            },
            {
                'name': 'Milk',
                'category': 'Dairy',
                'price': Decimal('1.20'),
                'unit': 'L',
                'stock': 50,
                'organic': False
            },
            {
                'name': 'Bread',
                'category': 'Bakery',
                'price': Decimal('3.50'),
                'unit': 'loaf',
                'stock': 20,
                'organic': True
            }
        ]

        created_products = []
        for p_data in products_data:
            cat = cat_objs.get(p_data['category'])
            if cat:
                prod, created = Product.objects.get_or_create(
                    name=p_data['name'],
                    producer=producer,
                    defaults={
                        'category': cat,
                        'description': f"Delicious {p_data['name']}",
                        'price': p_data['price'],
                        'unit': p_data['unit'],
                        'stock_quantity': p_data['stock'],
                        'is_organic': p_data['organic'],
                        'is_available': True
                    }
                )
                if created:
                    created_products.append(prod)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(created_products)} products'))

        # 4. Create Order
        if created_products and customer:
            order, created = Order.objects.get_or_create(
                customer=customer,
                status='PENDING',
                defaults={
                    'total_amount': Decimal('0.00'), # Will calculate
                    'delivery_date': timezone.now().date() + timezone.timedelta(days=2)
                }
            )
            
            if created:
                total = Decimal('0.00')
                for prod in created_products:
                    qty = 2
                    OrderItem.objects.create(
                        order=order,
                        product=prod,
                        quantity=qty,
                        price_at_sale=prod.price
                    )
                    total += prod.price * qty
                    # Update stock
                    prod.stock_quantity -= qty
                    prod.save()
                
                order.total_amount = total
                order.save()
                self.stdout.write(self.style.SUCCESS(f'Created order for {customer.username}'))

        # 5. Create Review
        if created_products and customer:
            Review.objects.get_or_create(
                customer=customer,
                product=created_products[0],
                defaults={
                    'rating': 5,
                    'comment': "Amazing quality!"
                }
            )
            self.stdout.write(self.style.SUCCESS('Created review'))

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
