from rest_framework.decorators import api_view
from rest_framework.response import Response

from biohub.core.plugins import plugins
from .serializers import PluginSerializer


@api_view(['GET'])
def plugins_list(request):
    data = PluginSerializer(plugins.plugin_configs.values(), many=True).data
    return Response(data)
