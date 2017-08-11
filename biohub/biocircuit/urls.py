from django.conf.urls import url

from biohub.core.routes import register_api

# Place your route definition here.

from . import views

register_api(r'^biocircuit/', [
    url(r'^biocircuit/(?P<expr>.+)/$', views.BiocircuitView.as_view(), name='biocircuit-build'),  # the name seems wierd.
    url(r'^gates/$', views.GatesView.as_view(), name='biocircuit-gates'),
    url(r'^score/$', views.ScoreView.as_view(), name='biocircuit-score'),
], 'biocircuit')
