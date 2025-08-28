from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from parler.models import TranslatableModel, TranslatedFields

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    

class Contact(models.Model):
    name = models.CharField(_("Name"), max_length=255, blank=True)
    email = models.EmailField(_("Email"), max_length=255, blank=True)
    subject = models.CharField(_("Subject"), max_length=255, blank=True, null=True)
    message = models.TextField(_("Message"))
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")
        ordering = ["-created_at"]

class BlogsModel(TranslatableModel):
    translations = TranslatedFields(
        title = models.CharField(_("Title"), max_length=255),
        content = models.TextField(_("Content")),
    )
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)

    def __str__(self):
        title = self.safe_translation_getter('title', any_language=True)
        return title or str(self.pk)

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")