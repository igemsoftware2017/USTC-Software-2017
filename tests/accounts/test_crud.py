import os.path as path

from django.urls import reverse

from rest_framework.test import APITestCase

from biohub.accounts.models import User

current_dir = path.dirname(__file__)


def open_img(name, mode='rb'):

    return open(path.join(current_dir, 'test_imgs', name), mode)


class Test(APITestCase):

    def setUp(self):
        self.me = User.objects.create_test_user('me')
        self.you = User.objects.create_test_user('you')

    def _get(self, user, part):
        url = '/api/users/%s/%s/' % (user.id, part)
        return self.client.get(url)

    def _post(self, user, part):
        url = '/api/users/%s/%s/' % (user.id, part)
        return self.client.post(url)

    def test_username_lookup(self):
        User.objects.create_test_user('testtest')

        resp = self.client.get('/api/users/n:testtest/')

        self.assertEqual(resp.data['username'], 'testtest')

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
        self.assertDictContainsSubset({
            'id': self.you.id,
            'followed': True
        }, self._get(self.me, 'following').data['results'][0])

        self.assertDictContainsSubset({
            'following_count': 0,
            'follower_count': 1
        }, self.client.get('/api/users/{}/stat/'.format(self.you.id)).data)
        self.assertDictContainsSubset({
            'following_count': 1,
            'follower_count': 0
        }, self.client.get('/api/users/me/stat/').data)

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

        resp = self._patch(self.me, description='ustc')
        self.assertDictContainsSubset({
            'description': 'ustc'
        }, resp.data)

        resp = self._patch(self.you)
        self.assertEqual(resp.status_code, 403)

        resp = self._patch(self.me, description='')
        self.assertDictContainsSubset({
            'description': ''
        }, resp.data)

        resp = self._patch(self.me, description='a' * 1024)
        self.assertEqual(resp.status_code, 400)

    def test_upload_avatar(self):
        self.client.force_authenticate(self.me)

        self.assertEqual(
            self.client.post('/api/users/upload_avatar/', {}).status_code,
            400)

        fd = open_img('a.png')
        resp = self.client.post('/api/users/upload_avatar/', {'file': fd})
        self.assertEqual(resp.status_code, 200)

        url_a = resp.data
        self.assertTrue(url_a.endswith('.png'))
        self.me.refresh_from_db()
        self.assertEqual(self.me.avatar_url, url_a)
        self.assertEqual(self.client.get(url_a).status_code, 200)

        fd.close()
        fd = open_img('b.png')
        resp = self.client.post('/api/users/upload_avatar/', {'file': fd})
        self.assertEqual(resp.status_code, 200)

        url_b = resp.data
        self.assertTrue(url_b.endswith('.png'))
        self.me.refresh_from_db()
        self.assertEqual(self.me.avatar_url, url_b)
        self.assertEqual(self.client.get(url_a).status_code, 404)
        self.assertEqual(self.client.get(url_b).status_code, 200)

        fd.close()
