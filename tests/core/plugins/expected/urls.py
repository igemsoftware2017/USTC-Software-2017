from biohub.core.routes import register_api, register_default, url  # noqa
from rest_framework.routers import DefaultRouter  # noqa

# Place your route definition here.
#
# Example:
#
# from .views import my_view, MyModelViewSet
#
# router = DefaultRouter()
# router.register(r'^mymodel', MyModelViewSet, base_name='mymodel')
#
# register_api('^myplugin/', [
#   url(r'^my_view/$', my_view)
# ], 'myplugin')
#
# References:
#
#  + http://www.django-rest-framework.org/api-guide/routers/
