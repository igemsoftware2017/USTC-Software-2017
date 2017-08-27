from biohub.accounts.models import User
from ._base import AbacusLiveTestCase, make_req, get_example_descriptor


class Test1(AbacusLiveTestCase):

    def test_local_handler(self):
        from biohub.abacus.handlers import LocalHandler
        self.me = User.objects.create_test_user('me')
        req, fp = make_req(self.me)
        handler = LocalHandler(req)
        task = handler._run_task(handler._store_file())
        self.assertTrue(task.wait(20, 0.1))
        self.assertEqual('SUCCESS', task.status.value)
        fp.close()


class Test2(AbacusLiveTestCase):

    def test_start_view(self):
        from biohub.abacus.tasks import AbacusAsyncResult

        self.me = User.objects.create_test_user('me')
        self.client.force_authenticate(self.me)
        fp = get_example_descriptor()

        resp = self.client.post('/api/abacus/start/', {'file': fp})
        task_id = resp.data['id']
        query = resp.data['query_url']
        result = AbacusAsyncResult(task_id)
        self.assertIn(result.status.value, ('RUNNING', 'PENDING'))
        self.assertIn(self.client.get(query).data['status'], ('RUNNING', 'PENDING'))

        self.assertTrue(result.wait(20, 0.1))
        resp = self.client.get(query)
        self.assertEqual(self.client.get(resp.data['output']).status_code, 200)
        self.assertEqual(resp.data['status'], 'SUCCESS')

        fp.close()
