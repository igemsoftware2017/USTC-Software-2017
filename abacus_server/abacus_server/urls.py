from django.conf.urls import url
from django.conf import settings
from django.views.static import serve

from .views import MainView, QueryView

reg_hex = '[0-9a-f-]'
reg_guid = r'%s{8}-%s{4}-%s{4}-%s{4}-%s{12}' % ((reg_hex,) * 5)

urlpatterns = [
    url(r'^$', MainView.as_view(), name='main'),
    url(r'^(%s)/$' % reg_guid, QueryView.as_view(), name='query')
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, dict(document_root=settings.MEDIA_ROOT))
    ]
