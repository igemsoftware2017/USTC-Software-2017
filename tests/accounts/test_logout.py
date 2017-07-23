from rest_framework.test import APITestCase

from biohub.accounts.models import User


class Test(APITestCase):

    def setUp(self):
        self.client.force_authenticate(
            User.objects.create_user(
                username='user1',
                email='123@123.com',
                password='12345'))

    def test_success(self):
        resp = self.client.get('/api/users/logout/')

        self.assertEqual('OK', resp.data)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_fail(self):
        self.client.force_authenticate(None)
        resp = self.client.get('/api/users/logout/')

        self.assertEqual(403, resp.status_code)