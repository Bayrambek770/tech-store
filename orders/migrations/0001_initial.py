# Generated manually
from django.db import migrations, models
import django.db.models.deletion
import uuid

class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('products','0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Quantity')),
                ('currency', models.CharField(max_length=8, default='UZS', verbose_name='Currency')),
                ('total_price', models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Total Price')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='orders', to='products.product', verbose_name='Product')),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
                'ordering': ['-created_at'],
            },
        ),
    ]
