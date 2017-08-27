from biohub.core.routes import register_api, url
from . import views

register_api(r'^abacus/', [
    url(r'^start/$', views.StartView.as_view(), name='abacus-start'),
    url(r'^query/(?P<task_id>[0-9a-f-]+)/$', views.QueryView.as_view(), name='abacus-query'),
    url(r'^callback/$', views.CallbackView.as_view(), name='remote-callback')
], 'abacus')
