from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/order/<uuid:order_id>/', views.dashboard_order_detail, name='dashboard_order_detail'),
    path('create/', views.create_order, name='create'),
    path('success/<uuid:order_id>/', views.order_success, name='success'),
    path('payment-return/', views.payment_return, name='payment_return'),
]
