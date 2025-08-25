from django.contrib import admin
from .models import DesignCategory, DesignAsset, AssetImage, DesignReview

class AssetImageInline(admin.TabularInline):
    model = AssetImage
    extra = 1

@admin.register(DesignCategory)
class DesignCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "slug")
    list_filter = ("type", )
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name", )}

@admin.register(DesignAsset)
class DesignAssetAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "discount", "is_active")
    list_filter = ("category__type", "category", "is_active")
    search_fields = ("name", "slug", "description")
    inlines = [AssetImageInline]
    prepopulated_fields = {"slug": ("name", )}

@admin.register(DesignReview)
class DesignReviewAdmin(admin.ModelAdmin):
    list_display = ("asset", "user", "rating", "created_at")
    list_filter = ("rating", "asset__category__type")
    search_fields = ("asset__name", "user__username", "comment")
