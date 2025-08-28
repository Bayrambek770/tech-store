import uuid
from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class DesignCategory(TranslatableModel, BaseModel):
    TYPE_CHOICES = (
        ("3d", "3D Max Product"),
        ("interior", "Interior Design"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    translations = TranslatedFields(
        name = models.CharField(max_length=180),
        description = models.TextField(blank=True),
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    slug = models.SlugField(max_length=220, unique=True, blank=True)

    class Meta:
        verbose_name = 'Design Category'
        verbose_name_plural = 'Design Categories'
        # Can't order by translated field directly at model meta; admin can specify ordering.
        ordering = ['created_at']

    def __str__(self):
        nm = self.safe_translation_getter('name', any_language=True) or ''
        return f"{self.get_type_display()}: {nm}" if self.type else nm

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:60]
            candidate = base
            counter = 1
            while DesignCategory.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                counter += 1
                candidate = f"{base}-{counter}"[:80]
            self.slug = candidate
        super().save(*args, **kwargs)


class DesignAsset(TranslatableModel, BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(DesignCategory, related_name='assets', on_delete=models.CASCADE)
    translations = TranslatedFields(
        name = models.CharField(max_length=255),
        description = models.TextField(blank=True),
        price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    )
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    cover_image = models.ImageField(upload_to='designs/covers/', blank=True, null=True)
    discount = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(90)])
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Design Asset'
        verbose_name_plural = 'Design Assets'
        ordering = ['-created_at']

    def __str__(self):
        return self.safe_translation_getter('name', any_language=True) or str(self.pk)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.safe_translation_getter('name', any_language=True) or str(self.pk))[:50]
            candidate = base
            counter = 1
            while DesignAsset.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                counter += 1
                candidate = f"{base}-{counter}"[:70]
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        if self.discount:
            return self.price * (100 - self.discount) / 100
        return self.price


class AssetImage(BaseModel):
    asset = models.ForeignKey(DesignAsset, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='designs/gallery/')
    alt_text = models.CharField(max_length=180, blank=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordering', 'id']
        verbose_name = 'Asset Image'
        verbose_name_plural = 'Asset Images'

    def __str__(self):
        return f"Image for {self.asset.name} ({self.ordering})"


class DesignReview(BaseModel):
    asset = models.ForeignKey(DesignAsset, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='design_reviews', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = (('asset', 'user'),)
        ordering = ['-created_at']
        indexes = [models.Index(fields=['-created_at'])]
        verbose_name = 'Design Review'
        verbose_name_plural = 'Design Reviews'

    def __str__(self):
        return f"Review {self.rating}* by {self.user} on {self.asset}"
