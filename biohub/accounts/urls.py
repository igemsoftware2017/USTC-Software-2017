from biohub.core.routes import register_api, url

from . import views

register_api(r'^', [
    url(r'^users/register/$', views.register, name='register'),
    url(r'^users/login/$', views.login, name='login'),
    url(r'^users/logout/$', views.logout, name='logout'),
], 'accounts')
