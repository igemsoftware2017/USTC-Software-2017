from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from biohub.accounts.models import User
from biohub.forum.models import Post, Experience, Article
from biohub.biobrick.models import Biobrick
from biohub.core.files.models import File


class ExperienceRestfulAPITest(APITestCase):

    def setUp(self):
        self.brick = Biobrick.objects.get(part_name='BBa_B0032')
        self.brick_meta = self.brick.ensure_meta_exists(True)
        self.article = Article.objects.create(text='aha?')
        self.user1 = User.objects.create_test_user(username="abc")
        self.user1.set_password("abc546565132")
        self.user1.save()
        self.experience = Experience.objects.create(
            title="hhh", author=self.user1,
            brick=self.brick_meta, content=self.article
        )
        self.user2 = User.objects.create_test_user(username="fff")
        self.user2.set_password("1593562120")
        self.user2.save()
        self.post1 = Post.objects.create(author=self.user1, content="15210", experience=self.experience)
        self.post2 = Post.objects.create(author=self.user2, content="777777", experience=self.experience)
        self.client = APIClient()

    def test_partial_fields(self):
        response = self.client.get('/api/forum/experiences/')

        for item in response.data['results']:
            self.assertNotIn('text', item['content'])
            self.assertIn('digest', item['content'])

            resp = self.client.get('/api/forum/experiences/%d/' % item['id'])
            self.assertNotIn('digest', resp.data['content'])
            self.assertIn('text', resp.data['content'])

    def test_text(self):

        resp = self.client.get('/api/forum/experiences/%d/text/' % self.experience.id)

        self.assertEqual('aha?', resp.data)

    def test_list_experiences(self):
        response = self.client.get('/api/forum/experiences/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        response = self.client.get('/api/forum/experiences/?author=' + self.user2.username)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)
        response = self.client.get(
            '/api/forum/experiences/?author=' + self.user1.username + '&short=true'
        )
        self.assertEqual(response.status_code, 200)

        exp = response.data['results'][0]
        self.assertNotIn('content', exp)
        self.assertNotIn('voted_users', exp)
        self.assertNotIn('post_set', exp)
        self.assertEqual('BBa_B0032', exp['brick'])
        self.assertIn('avatar_url', exp['author'])

    def test_post_empty_title_experience_failed(self):
        payload = {
            'title': '',
            'content_input': {
                'text': 'hahaha',
                'file_ids': []
            },
            'brick_name': self.brick_meta.part_name
        }
        self.client.force_authenticate(self.user1)

        resp = self.client.post('/api/forum/experiences/', payload, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('title', resp.data)

    def test_file(self):
        from .test_restful_articles import make_file

        f = File.objects.create_from_file(make_file())

        payloads = {
            'title': 'f**k',
            'content_input': {
                'text': 'hahaha',
                'file_ids': [f.id]
            },
            'brick_name': self.brick_meta.part_name
        }
        self.assertTrue(self.client.login(username='abc', password='abc546565132'))
        response = self.client.post('/api/forum/experiences/', payloads, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertDictContainsSubset({
            'id': f.id,

        }, response.data['content']['files'][0])

    def test_post_experiences(self):
        payloads = {
            'title': 'f**k',
            'content_input': {
                'text': 'hahaha',
                'file_ids': []
            },
            'brick_name': self.brick_meta.part_name
        }
        response = self.client.post('/api/forum/experiences/', payloads, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.client.login(username='abc', password='abc546565132'))
        response = self.client.post('/api/forum/experiences/', payloads, format='json')
        self.assertEqual(response.status_code, 201)
        response = self.client.get('/api/forum/experiences/')
        data = response.data
        self.assertEqual(len(data['results']), 2)
        response = self.client.get('/api/forum/articles/%d/'
                                   % Experience.objects.get(pk=data['results'][0]['id']).content.id)
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(data['text'], 'hahaha')
        response = self.client.post('/api/forum/experiences/', {
            'title': '??',
            'content_input': {
                'text': 'no file ids'
            },
            'brick_name': self.brick.part_name
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_patch_experiences(self):
        payloads = {
            'content_input': {
                'text': 'hahaha'
            },
            'brick_name': self.brick.part_name
        }
        response = self.client.patch(
            '/api/forum/experiences/%d/' % self.experience.id,
            payloads, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.client.login(username='fff', password='1593562120'))
        response = self.client.patch('/api/forum/experiences/%d/' % self.experience.id,
                                     payloads, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.client.login(username='abc', password='abc546565132'))
        response = self.client.patch('/api/forum/experiences/%d/' % self.experience.id,
                                     payloads, format='json')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/forum/articles/%d/' % self.experience.content.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['text'], 'hahaha')
        response = self.client.patch('/api/forum/experiences/%d/' % self.experience.id, {
            'content_input': {
                'text': ['unable to pass validation']
            }
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_fetch_posts_of_particular_experience(self):
        response = self.client.get('/api/forum/experiences/%d/posts/' % self.experience.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)
        response = self.client.get('/api/forum/experiences/%d/posts/?author=%s'
                                   % (self.experience.id, self.user1.username))
        self.assertEqual(response.status_code, 200)
        data = response.data
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['content'], '15210')

    def test_api_url_field(self):
        response = self.client.get('/api/forum/experiences/%d/' % self.experience.id)
        self.assertEqual(response.data['api_url'], '/api/forum/experiences/%d/' % self.experience.id)

    def test_vote(self):
        client = self.client
        # unauthenticated user can't vote
        response = client.post('/api/forum/experiences/' + str(self.experience.id) + '/vote/')
        self.assertEqual(response.status_code, 403)
        # vote for others
        self.assertTrue(client.login(username='abc', password='abc546565132'))
        other = Experience.objects.create(brick=self.brick_meta)
        response = client.post('/api/forum/experiences/' + str(other.id) + '/vote/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            client.get('/api/users/me/voted_experiences/').data['count'],
            1
        )
        response = client.get('/api/forum/experiences/' + str(other.id) + '/voted_users/')
        self.assertEqual(
            response.data['results'][0]['id'],
            self.user1.id
        )
        response = client.get('/api/forum/experiences/' + str(other.id) + '/')
        post_detail = response.data
        self.assertEqual(post_detail['votes'], 1)
        self.assertTrue(post_detail['voted'])
        self.assertNotIn('voted_users', post_detail)
        # vote for my experience
        mine = Experience.objects.create(author=self.user1, brick=self.brick_meta, author_name=self.user1.username)
        response = client.post('/api/forum/experiences/' + str(mine.id) + '/vote/')
        self.assertEqual(response.status_code, 400)

    def test_cancel_vote(self):
        client = self.client
        other = Experience.objects.create(author=self.user2, brick=self.brick_meta)
        self.assertTrue(client.login(username='abc', password='abc546565132'))
        # test cancel a vote which does not exist
        response = client.post('/api/forum/experiences/9999999999999999999999999999999/unvote/')
        self.assertEqual(response.status_code, 404)
        response = client.post('/api/forum/experiences/' + str(other.id) + '/unvote/')
        self.assertEqual(response.status_code, 400)
        # test cancel a normal vote
        client.post('/api/forum/experiences/' + str(other.id) + '/vote/')
        response = client.get('/api/forum/experiences/' + str(other.id) + '/')
        self.assertEqual(response.data['votes'], 1)
        client.post('/api/forum/experiences/' + str(other.id) + '/unvote/')
        response = client.get('/api/forum/experiences/' + str(other.id) + '/')
        self.assertEqual(response.data['votes'], 0)

    def test_throttle(self):
        from biohub.core.conf import settings as biohub_settings
        import time

        biohub_settings.THROTTLE['experience'] = 1

        self.client.force_authenticate(self.user1)
        response = self.client.post('/api/forum/experiences/', {
            'title': 'f**k',
            'content_input': {
                'text': 'hahaha',
                'file_ids': []
            },
            'brick_name': self.brick_meta.part_name
        }, format='json')
        self.assertEqual(response.status_code, 429)
        time.sleep(1)
        self.client.force_authenticate(self.user1)
        response = self.client.post('/api/forum/experiences/', {
            'title': 'f**k',
            'content_input': {
                'text': 'hahaha',
                'file_ids': []
            },
            'brick_name': self.brick_meta.part_name
        }, format='json')
        self.assertNotEqual(response.status_code, 429)

        biohub_settings.THROTTLE['experience'] = 0

    def test_throttle_vote(self):
        from biohub.core.conf import settings as biohub_settings
        import time

        biohub_settings.THROTTLE['vote'] = 1

        self.client.force_authenticate(self.user2)
        response = self.client.post('/api/forum/experiences/' + str(self.experience.id) + '/vote/')
        response = self.client.post('/api/forum/experiences/' + str(self.experience.id) + '/vote/')
        self.assertEqual(response.status_code, 429)
        time.sleep(1)
        response = self.client.post('/api/forum/experiences/' + str(self.experience.id) + '/vote/')
        self.assertNotEqual(response.status_code, 429)

        biohub_settings.THROTTLE['vote'] = 0
