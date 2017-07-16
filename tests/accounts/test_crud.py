from django.urls import reverse

from rest_framework.test import APITestCase

from biohub.accounts.models import User


class Test(APITestCase):

    def setUp(self):
        self.me = User.objects.create_user(username='me', password='me')
        self.you = User.objects.create_user(username='you', password='you')

    def test_retrieve(self):
        resp = self.client.get(self.me.api_url)

        self.assertDictContainsSubset({
            'username': 'me',
            'id': self.me.id
        }, resp.data)

    def test_list(self):
        resp = self.client.get(reverse('api:accounts:user-list'))

        self.assertIn('results', resp.data)
        self.assertEqual(2, len(resp.data['results']))

    def _patch(self, user, **payload):
        return self.client.patch(user.api_url, payload)

    def test_update(self):
        resp = self._patch(self.me)
        self.assertEqual(resp.status_code, 403)

        self.client.force_authenticate(self.me)

        resp = self._patch(self.me, education='ustc')
        self.assertDictContainsSubset({
            'education': 'ustc'
        }, resp.data)

        resp = self._patch(self.you)
        self.assertEqual(resp.status_code, 403)

        resp = self._patch(self.me, education='')
        self.assertDictContainsSubset({
            'education': ''
        }, resp.data)
