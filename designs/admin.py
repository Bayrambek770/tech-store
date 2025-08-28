from django.contrib import admin
from parler.admin import TranslatableAdmin
from .models import DesignCategory, DesignAsset, AssetImage, DesignReview

class AssetImageInline(admin.TabularInline):
    model = AssetImage
    extra = 1

@admin.register(DesignCategory)
class DesignCategoryAdmin(TranslatableAdmin):
    list_display = ("name", "type", "slug")
    list_filter = ("type", )
    search_fields = ("translations__name", "slug")
    readonly_fields = ('slug',)
    ordering = ('translations__name',)

@admin.register(DesignAsset)
class DesignAssetAdmin(TranslatableAdmin):
    list_display = ("name", "category", "price", "discount", "is_active")
    list_filter = ("category__type", "category", "is_active")
    search_fields = ("translations__name", "slug", "translations__description")
    inlines = [AssetImageInline]
    readonly_fields = ('slug',)
    ordering = ('translations__name',)

@admin.register(DesignReview)
class DesignReviewAdmin(admin.ModelAdmin):
    list_display = ("asset", "user", "rating", "created_at")
    list_filter = ("rating", "asset__category__type")
    search_fields = ("asset__name", "user__username", "comment")
