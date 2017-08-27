import os
from ..core.tasks import _base
from rest_framework.test import APIRequestFactory

_request_factory = APIRequestFactory()
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def get_example_descriptor():
    return open(os.path.join(BASE_DIR, 'example.pdb'), 'rb')


def make_req(user):

    fp = get_example_descriptor()

    request = _request_factory.post('/', {'file': fp})

    return request, fp


class AbacusTestCase(_base.TaskTestCase):

    pass


class AbacusLiveTestCase(_base.ChannelLiveServerTestCase, AbacusTestCase):
    pass
