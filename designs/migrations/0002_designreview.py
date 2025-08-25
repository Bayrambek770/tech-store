from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Migration(migrations.Migration):
    dependencies = [
        ('designs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DesignReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('rating', models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])),
                ('comment', models.TextField(blank=True)),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='designs.designasset')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='design_reviews', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Design Review',
                'verbose_name_plural': 'Design Reviews',
                'unique_together': {('asset', 'user')},
            },
        ),
        migrations.AddIndex(
            model_name='designreview',
            index=models.Index(fields=['-created_at'], name='designs_des_created_57af1a_idx'),
        ),
    ]
