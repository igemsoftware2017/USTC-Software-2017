import io
import os.path

from celery.result import AsyncResult

from django.views.generic import View
from django.http.response import JsonResponse
from django.core.validators import URLValidator
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.urls import reverse

from abacus_server.tasks import run_abacus


class MainView(View):

    def post(self, request):
        errors = self._validate_request(request)

        if errors:
            return JsonResponse(dict(errors=errors), status=400)

        file_name = request.FILES['file']. name
        callback = request.GET['callback']

        result = run_abacus.delay(
            file_name, callback,
            *self._prepare_output_file(file_name)
        )
        return JsonResponse({
            'task_id': result.task_id,
            'status': request.build_absolute_uri(
                reverse('query', args=(result.task_id,))
            )
        })

    def _prepare_output_file(self, input_file_name):
        """
        Given the input file name, generate the output file name.

        Returns a 2-tuple: (output_file_name, output_file_absolute_url).
        """
        with io.StringIO('') as empty_file:
            output_file_name = default_storage.save(
                os.path.join('output', input_file_name),
                empty_file
            )

        return output_file_name, self.request.build_absolute_uri(
            default_storage.url(output_file_name))

    def _validate_request(self, request):
        """
        Validates request parameters.

         + `.FILES['file']` should be specified.
         + `.GET['callback']` should be a valid URL.
        """
        error_list = []

        if 'file' not in request.FILES:
            error_list.append('Should specify an input file.')

        callback = request.GET.get('callback', '')
        try:
            URLValidator()(callback)
        except ValidationError as e:
            error_list.append('Should specify a valid callback URL.')

        return error_list


class QueryView(View):
    """
    Given a task id, queries the status of the associated task.
    """

    def get(self, request, task_id):
        result_object = AsyncResult(task_id)
        response = {
            'status': result_object.state
        }
        if result_object.successful():
            response['output'] = result_object.result

        return JsonResponse(response)
