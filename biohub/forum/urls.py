from django.conf.urls import url
from biohub.core.routes import register_api
from rest_framework.routers import DefaultRouter
from biohub.forum.views import PostViewSet, ArticleViewSet, BrickViewSet,\
    ExperienceViewSet, SeqFeatureViewSet, ActivityViewSet
from biohub.forum.views.post_views import PostsOfExperiencesListView
from biohub.forum.views.experience_views import ExperiencesOfBricksListView
from biohub.forum.views.seq_feature_views import SeqFeaturesOfBricksListView
from biohub.forum.views.brick_views import retrieve_brick_by_name

router = DefaultRouter()
router.register(r'posts', PostViewSet, base_name='post')
router.register(r'articles', ArticleViewSet, base_name='article')
router.register(r'bricks', BrickViewSet, base_name='brick')
router.register(r'experiences', ExperienceViewSet, base_name='experience')
router.register(r'seq_features', SeqFeatureViewSet, base_name='seq_feature')
router.register(r'activities', ActivityViewSet, base_name='activity')

register_api(r'^forum/', [
    url(r'^experiences/(?P<experience_id>\d+)/posts/$', PostsOfExperiencesListView.as_view()),
    url(r'^bricks/(?P<brick_id>\d+)/experiences/$', ExperiencesOfBricksListView.as_view()),
    url(r'^bricks/(?P<brick_id>\d+)/seq_features/$', SeqFeaturesOfBricksListView.as_view()),
    url(r'bricks/(?P<brick_name>[A-Za-z]\d+)/$', retrieve_brick_by_name)
] + router.urls, 'forum')
