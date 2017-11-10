from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from biohub.core.plugins import plugins
from biohub.utils.http import basicauth
from .serializers import PluginSerializer
from .user_plugin_manager import RepositoryRequest, Repository, get_requests


@api_view(['GET'])
def plugins_list(request):
    data = PluginSerializer(plugins.plugin_configs.values(), many=True).data
    return Response(data)


@basicauth('admin', 'biohub')
def plugin_admin(request):

    if request.method.lower() == 'post':

        req = RepositoryRequest.from_string(request.POST['target'])
        message = request.POST.get('message', '')

        if 'approve' in request.POST:
            req.approve(message)
        elif 'reject' in request.POST:
            req.reject(message)
        elif 'delete' in request.POST:
            req.delete()

        return HttpResponseRedirect(reverse('api:plugins:admin'))

    template = """
    <html>
        <head>
            <title>plugin admin</title>
        </head>
        <body>
            {}
        </body>
    </html>
    """.format(
        '<hr>'.join(
            """
            <form method="post" action="">
                <a href="https://github.com/{request.username}/{request.repo}/commit/{request.commit}" target="_blank">{request.value}</a>
                <input type="hidden" name="target" value="{request.value}">
                <textarea name="message"></textarea>
                <input type="submit" name="approve" value="approve">
                <input type="submit" name="reject" value="reject">
                <input type="submit" name="delete" value="delete">
            </form>
            """.format(request=RepositoryRequest.from_string(r))
            for r in get_requests()
        )
    )

    return HttpResponse(template)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def init_plugin(request):
    Repository(request.user).init(request.data.get('username'), request.data.get('repo'))

    return Response('OK')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upgrade_plugin(request):
    Repository(request.user).request_upgrade()

    return Response('OK')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_plugin(request):
    Repository(request.user).remove()

    return Response('OK')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def plugin_info(request):
    return Response(Repository(request.user).serialize())
