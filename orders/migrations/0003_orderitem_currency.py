from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0002_order_customer_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='currency',
            field=models.CharField(max_length=8, default='UZS'),
        ),
    ]
