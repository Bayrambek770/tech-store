from django.core.management.base import BaseCommand
from django.utils.text import slugify
from decimal import Decimal
import random
import uuid
from products.models import Category, Product

CATEGORIES = [
    'Laptops', 'Phones', 'Accessories', 'Gaming', 'Audio'
]

class Command(BaseCommand):
    help = 'Seed demo categories and 20 products per category (idempotent-ish)'

    def add_arguments(self, parser):
        parser.add_argument('--per-category', type=int, default=20, help='Products per category')
        parser.add_argument('--force', action='store_true', help='Create even if products exist already')

    def handle(self, *args, **options):
        per = options['per_category']
        force = options['force']
        created_total = 0
        for name in CATEGORIES:
            cat, _ = Category.objects.get_or_create(name=name)
            existing = cat.products.count()
            if existing >= per and not force:
                self.stdout.write(self.style.WARNING(f'Skipping {name}: already has {existing} products'))
                continue
            to_create = per if force else (per - existing)
            products = []
            for i in range(to_create):
                base_name = f"{name} Item {existing + i + 1}"
                price = Decimal(random.randint(50, 1500)) + Decimal(random.randint(0, 99))/100
                discount = random.choice([0, 5, 10, 15, 20])
                slug = slugify(f"{base_name}-{uuid.uuid4().hex[:6]}")
                products.append(Product(
                    name=base_name,
                    slug=slug,
                    price=price,
                    discount=discount,
                    category=cat,
                ))
            Product.objects.bulk_create(products)
            created_total += len(products)
            self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products for {name}'))
        self.stdout.write(self.style.SUCCESS(f'Done. Total created: {created_total}'))
