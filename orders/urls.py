from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.create_order, name='create'),
    path('success/<uuid:order_id>/', views.order_success, name='success'),
]
