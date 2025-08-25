from django.urls import path
from .views import home, store_view, cart_view, checkout_view, add_to_cart, update_cart_item, product_detail, donation_view, public_offer, brand_preview


urlpatterns = [
    path('', home, name='home'),
    path('store/', store_view, name='store'),
    path('cart/', cart_view, name='cart'),
    path('checkout/', checkout_view, name='checkout'),
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('cart/update/', update_cart_item, name='update_cart_item'),
    path('product/<slug:slug>/', product_detail, name='product_detail'),
    path('advance-payment/', donation_view, name='donation'),
    path('public-offer/', public_offer, name='public_offer'),
    path('brand-preview/', brand_preview, name='brand_preview'),
]
