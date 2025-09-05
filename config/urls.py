from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf.urls.i18n import i18n_patterns
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('healthz/', lambda request: JsonResponse({'status': 'ok'})),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('designs/', include('designs.urls', namespace='designs')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('', include('products.urls')),  # do not prefix default 'ru' in URLs
    prefix_default_language=False,
)

if 'rosetta' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('rosetta/', include('rosetta.urls'))
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

def loaderio_verify(request):
    return HttpResponse("loaderio-e6da3c1bb4025cc9378003dd3c8deb4a", content_type="text/plain")

urlpatterns += [
    path("loaderio-e6da3c1bb4025cc9378003dd3c8deb4a/", loaderio_verify),
]
