from biohub.core.routes import urlpatterns as biohub_urlpatterns

from django.conf import settings
from django.conf.urls import url
from django.views.static import serve

urlpatterns = biohub_urlpatterns

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve,
            dict(document_root=settings.MEDIA_ROOT))
    ]
