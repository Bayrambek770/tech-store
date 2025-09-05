from django.urls import path

from .views import PaylovAPIView

urlpatterns = [
    path("paylov/", PaylovAPIView.as_view(), name='api'),
]
