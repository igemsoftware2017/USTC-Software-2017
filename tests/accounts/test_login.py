from rest_framework.test import APITestCase
from biohub.accounts.models import User


class Test(APITestCase):

    def setUp(self):
        self.user = User.objects.create_test_user('user1')

    def _post(self, **payload):
        return self.client.post('/api/users/login/', payload)

    def test_success(self):
        resp = self._post(username='user1', password=User._test_password)

        self.assertEqual(resp.status_code, 200)
        self.assertDictContainsSubset({
            'username': 'user1',
            'id': self.user.id
        }, resp.data)
        self.assertEqual(
            str(self.user.id), self.client.session.get('_auth_user_id', None))

    def test_fail(self):
        resp = self._post(username='user1', password='12')

        self.assertEqual(resp.status_code, 400)
        self.assertIn(b'incorrect', resp.content)
