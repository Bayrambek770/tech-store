from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='first_name',
            field=models.CharField(blank=True, max_length=60, null=True, verbose_name='First name'),
        ),
        migrations.AddField(
            model_name='order',
            name='last_name',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Last name'),
        ),
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.EmailField(blank=True, max_length=150, null=True, verbose_name='Email'),
        ),
        migrations.AddField(
            model_name='order',
            name='phone',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='Phone'),
        ),
        migrations.AddField(
            model_name='order',
            name='address1',
            field=models.CharField(blank=True, max_length=160, null=True, verbose_name='Address line 1'),
        ),
        migrations.AddField(
            model_name='order',
            name='address2',
            field=models.CharField(blank=True, max_length=160, null=True, verbose_name='Address line 2'),
        ),
        migrations.AddField(
            model_name='order',
            name='country',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Country'),
        ),
        migrations.AddField(
            model_name='order',
            name='state',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='State/Region'),
        ),
        migrations.AddField(
            model_name='order',
            name='zip',
            field=models.CharField(blank=True, max_length=24, null=True, verbose_name='ZIP'),
        ),
    ]