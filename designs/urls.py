from django.urls import path
from .views import marketplace, asset_detail

app_name = 'designs'

urlpatterns = [
    path('marketplace/', marketplace, name='marketplace'),
    path('asset/<slug:slug>/', asset_detail, name='asset_detail'),
]
