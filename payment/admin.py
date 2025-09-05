from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id','currency','amount','created_at')
    list_filter = ('currency','created_at')