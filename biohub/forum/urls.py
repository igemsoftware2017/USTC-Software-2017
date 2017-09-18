from django.conf.urls import url  # noqa
from biohub.core.routes import register_api
from rest_framework.routers import DefaultRouter
from biohub.forum.views import PostViewSet, ArticleViewSet,\
    ExperienceViewSet, ActivityViewSet, UserExperienceViewSet

from biohub.biobrick.views import BiobrickViewSet, UserBrickViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, base_name='post')
router.register(r'articles', ArticleViewSet, base_name='article')
router.register(r'bricks', BiobrickViewSet, base_name='biobrick')
router.register(r'experiences', ExperienceViewSet, base_name='experience')
router.register(r'activities', ActivityViewSet, base_name='activity')
router.register(r'experiences/(?P<experience_id>\d+)/posts', PostViewSet, base_name='post')
ExperienceViewSet.add_to_router(router, 'experiences')


register_api(r'^forum/', router.urls, 'forum')

extra_router = DefaultRouter()
UserBrickViewSet.add_to_router(extra_router)
UserExperienceViewSet.add_to_router(extra_router)
register_api(r'^', extra_router.urls)
