from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response

from biohub.utils.rest.permissions import IsAuthenticated
from biohub.core.files.serializers import FileSerializer
from biohub.core.files.handlers import handle_permanent_file
from biohub.core.files.utils import store_file, default_storage


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload(request):

    store_db = request.GET.get('store_db', False)

    if store_db:
        instance = handle_permanent_file(request, 'file')
        data = FileSerializer(instance).data
    else:
        name, mime_type = store_file(request.FILES['file'])
        data = dict(file=default_storage.url(name),
                    mime_typ=mime_type)

    return Response(data)
