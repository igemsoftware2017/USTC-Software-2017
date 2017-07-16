from rest_framework.test import APITestCase
from biohub.accounts.models import User

from django.contrib.auth import authenticate


class Test(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='user1', password='user1')
        self.client.force_authenticate(self.user)

    def test_change_password(self):
        resp = self.client.post('/api/users/change_password/', {
            'old': 'user',
            'new1': 'user2',
            'new2': 'user2'
        })
        self.assertIn(b'Old', resp.content)

        resp = self.client.post('/api/users/change_password/', {
            'old': 'user1',
            'new1': 'user1',
            'new2': 'user2'
        })
        self.assertIn(b'New', resp.content)

        self.client.post('/api/users/change_password/', {
            'old': 'user1',
            'new1': 'user2',
            'new2': 'user2'
        })

        self.assertIsNotNone(authenticate(username='user1', password='user2'))
