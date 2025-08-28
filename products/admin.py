from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import Product, Category, Review

@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ("name", "description")
    search_fields = ("translations__name",)


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ("name", "price", "category", "is_active")
    search_fields = ("translations__name", "category__translations__name")
    list_filter = ("category", "is_active")
    # Removed prepopulated_fields because 'name' is translated (Parler stores it separately)
    readonly_fields = ('slug','is_active',)
    ordering = ('translations__name',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    search_fields = ("product__name", "user__username")
    list_filter = ("rating", "created_at")
