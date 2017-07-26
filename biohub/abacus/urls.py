from biohub.core.routes import register_api, url  # noqa:F401
from rest_framework.routers import DefaultRouter

from .views import AbacusView

router = DefaultRouter()

router.register(r'^abacus', AbacusView, base_name='abacus')


register_api('', [
] + router.urls, 'abacus')
