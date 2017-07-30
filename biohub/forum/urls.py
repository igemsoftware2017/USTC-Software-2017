from biohub.core.routes import register_api
from rest_framework.routers import DefaultRouter
from biohub.forum.views import PostViewSet, ArticleViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, base_name='post')
router.register(r'articles', ArticleViewSet, base_name='article')

register_api(r'^forum/', [

] + router.urls, 'forum')
