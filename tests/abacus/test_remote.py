import time
import requests

from rest_framework.test import APILiveServerTestCase
from biohub.core.websocket.test import BiohubWSClient
from channels.test.base import ChannelTestCaseMixin
from biohub.abacus.conf import settings


class BaseTest(APILiveServerTestCase):

    def setUp(self):
        from biohub.accounts.models import User

        self.me = User.objects.create_test_user('me')

    @property
    def server_name(self):
        return '%s:%s' % (self.host, self.server_thread.port)


class TestRemote(ChannelTestCaseMixin, BaseTest):

    def _pre_setup(self):
        super(TestRemote, self)._pre_setup()

    def _post_teardown(self):
        super(TestRemote, self)._post_teardown()

    def setUp(self):
        super(TestRemote, self).setUp()
        self.client.force_authenticate(self.me)
        settings._wrapped['ident'] = 'remote'

    def tearDown(self):
        settings._wrapped['ident'] = 'local'

    def test_handler(self):
        from ._base import get_example_descriptor
        from biohub.abacus.result import AbacusAsyncResult

        client = BiohubWSClient.from_user(self.me)
        client.connect()

        fp = get_example_descriptor()
        resp = self.client.post('/api/abacus/start/', {'file': fp}, SERVER_NAME=self.server_name)
        task_id = resp.data['id']

        fp2 = get_example_descriptor()
        resp2 = self.client.post('/api/abacus/start/', {'file': fp2}, SERVER_NAME=self.server_name)
        task_id2 = resp2.data['id']

        self.tearDown()

        resp = self.client.get(resp.data['query_url'])
        self.assertEqual(resp.data['status'], 'PENDING')

        resp2 = self.client.get(resp2.data['query_url'])
        self.assertEqual(resp2.data['status'], 'PENDING')

        time.sleep(2)

        ar = AbacusAsyncResult(task_id)
        self.assertEqual(ar.status.value, 'SUCCESS')
        self.assertEqual(requests.get(ar.result).status_code, 200)

        ar2 = AbacusAsyncResult(task_id2)
        self.assertEqual(ar2.status.value, 'SUCCESS')
        self.assertEqual(requests.get(ar2.result).status_code, 200)

        outputs = set()

        while True:
            data = client.receive()
            if data is None:
                raise Exception('No data received.')
            elif data['handler'] == 'abacus':
                outputs.add(data['data']['output'])
                self.assertEqual(data['data']['status'], 'SUCCESS')
                break

        while True:
            data = client.receive()
            if data is None:
                raise Exception('No data received.')
            elif data['handler'] == 'abacus':
                outputs.add(data['data']['output'])
                self.assertEqual(data['data']['status'], 'SUCCESS')
                break

        self.assertEqual(outputs, {ar.result, ar2.result})

        messages = self.me.notices.values_list('message', flat=True)
        for result in (ar, ar2):
            message = (
                'ABACUS finished processing {input}. [[Check output]]((plugin.abacus))(({id})).'
                .format(input=result.input_file_name, id=result.task_id)
            )
            self.assertIn(message, messages)
        fp.close()
        fp2.close()
