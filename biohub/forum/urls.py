from biohub.core.routes import register_api
from rest_framework.routers import DefaultRouter
from biohub.forum.views import PostViewSet

router = DefaultRouter()
router.register(r'^posts', PostViewSet, base_name='post')

register_api('', [

] + router.urls, 'posts')
