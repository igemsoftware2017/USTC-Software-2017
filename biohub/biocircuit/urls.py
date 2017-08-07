from django.conf.urls import url

from biohub.core.routes import register_api

# Place your route definition here.

from . import views

register_api(r'^', [
    url(r'^build/$', views.BiocircuitView.as_view()),
    url(r'^gates/$', views.GatesView.as_view()),
    url(r'^score/$', views.ScoreView.as_view()),
], 'biocircuit')
