from rest_framework import views, permissions, parsers
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .handlers import get_handler, query
from .result import AbacusAsyncResult
from .security import validate_signature


class StartView(views.APIView):

    permission_classes = (permissions.IsAuthenticated,)
    parser_classes = (parsers.MultiPartParser, parsers.FormParser,)

    def post(self, request):
        handler = get_handler(request)
        return Response(handler.start_task(request.user))


class QueryView(views.APIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, task_id):
        return Response(query(task_id))


class CallbackView(views.APIView):

    def fail(self, detail):
        raise ValidationError(detail)

    def get(self, request):
        async_result = AbacusAsyncResult(request.GET.get('task_id', ''))

        if not validate_signature(async_result, request.GET.get('s', '')):
            self.fail('Bad signature.')

        if async_result._get_field('status') is None:
            self.fail('Task not exists.')

        if 'error' in request.GET:
            async_result.error(None)
        elif 'output' in request.GET:
            async_result.resolve(request.GET['output'])
        else:
            self.fail('Should specify either error or output.')
        return Response('')
