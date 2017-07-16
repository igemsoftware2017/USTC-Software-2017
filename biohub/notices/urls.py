from biohub.core.routes import register_api, url  # noqa:F401
from rest_framework.routers import DefaultRouter

from .views import NoticeViewSet

router = DefaultRouter()

router.register(r'^notices', NoticeViewSet, base_name='notice')


register_api('', [

] + router.urls, 'notices')
