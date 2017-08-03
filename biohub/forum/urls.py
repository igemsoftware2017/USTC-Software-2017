from django.conf.urls import url
from biohub.core.routes import register_api
from rest_framework.routers import DefaultRouter
from biohub.forum.views import PostViewSet, ArticleViewSet, BrickViewSet,\
    ExperienceViewSet, SeqFeatureViewSet
from biohub.forum.views.post_views import PostsOfExperiencesListView

router = DefaultRouter()
router.register(r'posts', PostViewSet, base_name='post')
router.register(r'articles', ArticleViewSet, base_name='article')
router.register(r'bricks', BrickViewSet, base_name='brick')
router.register(r'experiences', ExperienceViewSet, base_name='experience')
router.register(r'seq_features', SeqFeatureViewSet, base_name='seq_feature')

register_api(r'^forum/', [
    url(r'^experiences/(?P<experience_id>\d+)/posts/$', PostsOfExperiencesListView.as_view()),
] + router.urls, 'forum')
