from django.urls import reverse
from rest_framework.exceptions import ValidationError

from biohub.abacus.result import AbacusAsyncResult
from . import consts, remote


class BaseHandler(object):
    """
    Abstract task handler to adjust different environments.
    """

    def __init__(self, request):
        self._request = request

    def start_task(self, user):
        if 'file' not in self._request.FILES:
            raise ValidationError('Should upload a file.')

        task_id = self._perform_start_task()
        async_result = AbacusAsyncResult(task_id)
        async_result._set_ident(self.ident)
        async_result._set_user(user.pk)

        return dict(
            id=task_id,
            query_url=reverse(
                'api:abacus:abacus-query',
                kwargs=dict(task_id=task_id)
            )
        )


class LocalHandler(BaseHandler):

    ident = consts.LOCAL

    def _run_task(self, input_file_name):
        from biohub.abacus.tasks import AbacusTask

        return AbacusTask.apply_async(input_file_name)

    def _store_file(self):
        from biohub.core.files.utils import store_file

        return store_file(self._request.FILES['file'])[0]

    def _perform_start_task(self):

        return self._run_task(self._store_file()).task_id


class RemoteHandler(BaseHandler):

    ident = consts.REMOTE

    def _perform_start_task(self):
        return remote.start(self._request)


def get_handler_class():
    """
    To choose and return the right handler.
    """
    from .conf import settings

    return {
        consts.LOCAL: LocalHandler,
        consts.REMOTE: RemoteHandler
    }[settings.ident]


def get_handler(request):
    return get_handler_class()(request)


def query(task_id):
    """
    Queries and returns the status (and output if succeeded).
    """
    return AbacusAsyncResult(task_id).response()
