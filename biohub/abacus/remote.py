import requests
from django.urls import reverse

from biohub.utils.url import add_params
from .conf import settings
from . import security

__all__ = ['start', 'query']


def _ensure_success(response):
    """
    To ensure the request succeeded.
    """
    assert response.status_code == 200, \
        "Remote call failed with status code {}\nContent: {}".format(response.status_code, response.text)


def start(request):
    """
    Uploads the file to remote server.

    Returns a tuple (task_id, signature).
    """
    signature = security.signature()
    response = requests.post(
        settings.ABACUS_REMOTE_SERVER,
        params={
            'callback': add_params(
                request.build_absolute_uri(reverse('api:abacus:remote-callback')),
                s=signature
            ),
        },
        files={
            'file': request.FILES['file']
        }
    )
    _ensure_success(response)
    return response.json()['task_id'], signature


def query(task_id):
    """
    Queries the task specified by task_id and returns the raw response.
    """
    response = requests.get(
        '{}{}/'.format(settings.ABACUS_REMOTE_SERVER, task_id)
    )
    _ensure_success(response)
    return response.json()
