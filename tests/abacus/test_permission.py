from rest_framework.test import APITestCase

from biohub.accounts.models import User


class Test(APITestCase):

    def test_start(self):
        self.assertEqual(
            self.client.post('/api/abacus/start/').status_code,
            403
        )

    def test_query(self):
        self.assertEqual(
            self.client.get('/api/abacus/query/f924886b-0f7e-49c1-b189-74bc30c60268/').status_code,
            403
        )

    def test_callback(self):
        self.client.force_authenticate(User.objects.create_test_user('me'))
        self.assertEqual(
            self.client.get('/api/abacus/callback/?task_id=f924886b-0f7e-49c1-b189-74bc30c60268').status_code,
            400
        )
