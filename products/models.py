from email.mime import image
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.db.models import Q, F
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
import uuid
from users.models import CustomUser as User


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(_("Name"), max_length=255)
    description = models.TextField(_("Description"), blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        db_table = "categories"


class Product(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("Name"), max_length=255)
    slug = models.SlugField(_("Slug"), max_length=280, unique=True, blank=True)
    price = models.DecimalField(_("Price"), max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    discount = models.PositiveIntegerField(_("Discount (%)"), default=0,
                                           validators=[MinValueValidator(0), MaxValueValidator(90)])
    is_active = models.BooleanField(_("Is active"), default=True)

    category = models.ForeignKey(
        Category,
        verbose_name=_("Category"),
        related_name='products',
        on_delete=models.CASCADE,
        related_query_name='product'
    )
    image = models.ImageField(upload_to="products/images/", blank=True, null=True)

    def __str__(self):
        return f"{self.name[:20]}..."

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:50]
            candidate = base
            counter = 1
            while Product.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                counter += 1
                candidate = f"{base}-{counter}"[:70]
            self.slug = candidate
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")
        db_table = "products"
        ordering = ["-created_at"]
        


class Review(BaseModel):
    product = models.ForeignKey(
        Product,
        verbose_name=_("Product"),
        related_name='reviews',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        related_name='reviews',
        on_delete=models.CASCADE
    )
    rating = models.PositiveIntegerField(
        _("Rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(_("Comment"), blank=True)

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        unique_together = (("product", "user"),)
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return _("Review for %(product)s by %(user)s") % {
            "product": self.product.name,
            "user": self.user.username
        }