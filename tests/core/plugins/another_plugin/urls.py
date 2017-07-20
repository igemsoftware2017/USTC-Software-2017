from biohub.core.routes import register_api, url

from .models import AnotherModel

from rest_framework.response import Response
from rest_framework.decorators import api_view

register_api(r'^another_plugin/', [
    url(r'^$', api_view(['GET'])(
        lambda r: Response(list(AnotherModel.objects.all()))), name='index')
], namespace='another')
