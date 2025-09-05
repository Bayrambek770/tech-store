from django.contrib import admin
from .models import Order, OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','currency','total_price','created_at')
    list_filter = ('currency','created_at')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id','order','product','quantity','line_total')
    list_filter = ('order__currency',)
    search_fields = ('id','product__translations__name')
    autocomplete_fields = ('product',)

