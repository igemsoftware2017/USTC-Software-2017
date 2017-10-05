from rest_framework.routers import DefaultRouter

from biohub.core.routes import register_api, url

from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet)

register_api(r'^', [
    url(r'^users/register/$', views.register, name='register'),
    url(r'^users/login/$', views.login, name='login'),
    url(r'^users/logout/$', views.logout, name='logout'),
    url(r'^users/upload_avatar/$', views.upload_avatar, name='upload-avatar'),
    url(r'^users/change_password/$',
        views.change_password, name='change-password'),
    url(r'^users/reset_password/$',
        views.PasswordResetView.as_view(), name='reset-password')
] + router.urls, 'accounts')

extra_router = DefaultRouter()
views.UserRelationViewSet.add_to_router(extra_router)
register_api(r'^', extra_router.urls)
