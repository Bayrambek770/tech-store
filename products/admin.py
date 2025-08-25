from django.contrib import admin
from .models import Product, Category, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category", "is_active")
    search_fields = ("name", "category__name")
    list_filter = ("category", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ('is_active',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    search_fields = ("product__name", "user__username")
    list_filter = ("rating", "created_at")
