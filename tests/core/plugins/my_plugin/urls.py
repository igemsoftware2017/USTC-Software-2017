from rest_framework.response import Response
from rest_framework.decorators import api_view

from biohub.core.routes import register_api, url

from .models import TestModel

register_api(r'^my_plugin/', [
    url(
        r'^$',
        api_view(['GET'])(lambda r: Response(list(TestModel.objects.all()))),
        name='index')
], namespace='my_plugin')
