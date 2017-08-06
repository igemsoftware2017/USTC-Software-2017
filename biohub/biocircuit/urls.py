from rest_framework.routers import DefaultRouter

from biohub.core.routes import register_api

# Place your route definition here.

from . import views

router = DefaultRouter()
router.register(r'', views.BiocircuitView, base_name='')
router.register(r'score', views.ScoreView, base_name='')

register_api(r'^', router.urls, 'biocircuit')
