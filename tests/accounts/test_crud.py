from django.urls import reverse

from rest_framework.test import APITestCase

from biohub.accounts.models import User


class Test(APITestCase):

    def setUp(self):
        self.me = User.objects.create_user(username='me', password='me')
        self.you = User.objects.create_user(username='you', password='you')

    def _get(self, user, part):
        url = '/api/users/%s/%s/' % (user.id, part)
        return self.client.get(url)

    def _post(self, user, part):
        url = '/api/users/%s/%s/' % (user.id, part)
        return self.client.post(url)

    def test_fetch_bi_connections(self):
        self.me.follow(self.you)
        self.client.force_authenticate(self.me)

        self.assertEqual(
            self._get(self.you, 'followers').data['results'][0]['id'],
            self.me.id)
        self.assertEqual(
            self._get(self.me, 'following').data['results'][0]['id'],
            self.you.id)

    def test_follow(self):
        self.client.force_authenticate(self.me)
        self.assertEqual(
            self._post(self.me, 'follow').data,
            'OK'
        )

        self.assertEqual(
            self._post(self.you, 'follow').data,
            'OK'
        )
        self.assertEqual(
            self._get(self.me, 'following').data['results'][0]['id'],
            self.you.id
        )
        self.assertEqual(
            self._post(self.you, 'follow').data,
            'OK'
        )

    def test_unfollow(self):
        self.client.force_authenticate(self.me)

        self.assertEqual(
            self._post(self.you, 'unfollow').data,
            'OK'
        )

        self.me.follow(self.you)
        self.assertEqual(
            self._get(self.me, 'following').data['results'][0]['id'],
            self.you.id
        )

        self._post(self.you, 'unfollow')
        self.assertListEqual(
            self._get(self.me, 'following').data['results'],
            []
        )

    def test_retrieve(self):
        resp = self.client.get(self.me.api_url)

        self.assertDictContainsSubset({
            'username': 'me',
            'id': self.me.id
        }, resp.data)

    def test_retrieve_me(self):
        url = '/api/users/me/'
        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 404)

        self.client.force_authenticate(self.me)
        resp = self.client.get(url)

        self.assertEqual(resp.data['id'], self.me.id)

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
