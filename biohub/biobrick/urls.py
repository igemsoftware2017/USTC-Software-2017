from rest_framework.routers import DefaultRouter
# from django.conf.urls import url, include

from biohub.core.routes import register_api

# Place your route definition here.

from . import views

router = DefaultRouter()
router.register(r'biobricks', views.BiobrickViewSet, base_name='biobrick')

register_api(r'^', router.urls, 'biobrick')
