import json
from rest_framework.test import APIClient
from django.test import TestCase
from biohub.accounts.models import User
from biohub.forum.models import Post, Experience, Brick, Article
# from time import sleep


class ExperienceRestfulAPITest(TestCase):
    def setUp(self):
        self.brick = Brick.objects.create(name='emmmm')
        self.article = Article.objects.create(text='aha?')
        self.user1 = User.objects.create_test_user(username="abc")
        self.user1.set_password("abc546565132")
        self.user1.save()
        self.experience = Experience.objects.create(title="hhh", author=self.user1,
                                                    brick=self.brick, content=self.article)
        self.user2 = User.objects.create_test_user(username="fff")
        self.user2.set_password("1593562120")
        self.user2.save()
        self.post1 = Post.objects.create(author=self.user1, content="15210", experience=self.experience)
        self.post2 = Post.objects.create(author=self.user2, content="777777", experience=self.experience)
        self.client = APIClient()

    def test_list_experiences(self):
        response = self.client.get('/api/forum/experiences/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
        response = self.client.get('/api/forum/experiences/?author=' + self.user2.username)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 0)
        response = self.client.get('/api/forum/experiences/?author=' + self.user1.username
                                   + '&short=true')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIs(data['results'][0].get('content'), None)

    def test_post_experiences(self):
        payloads = {
            'title': 'f**k',
            'content_data': {
                'text': 'hahaha',
                'file_ids': []
            },
            'brick_id': self.brick.id
        }
        response = self.client.post('/api/forum/experiences/', payloads, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIs(self.client.login(username='abc', password='abc546565132'), True)
        response = self.client.post('/api/forum/experiences/', payloads, format='json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.content)
        response = self.client.get('/api/forum/experiences/')
        # with open('experiences_list.txt','wb') as f:
        #     f.write(response.content)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 2)
        response = self.client.get('/api/forum/articles/%d/'
                                   % Experience.objects.get(pk=data['results'][0]['id']).content.id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['text'], 'hahaha')
        response = self.client.post('/api/forum/experiences/', {
            'title': '??',
            'content_data': {
                'text': 'no file ids'
            },
            'brick_id': self.brick.id
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_patch_experiences(self):
        payloads = {
            'content_data': {
                'text': 'hahaha'
            },
            'brick_id': self.brick.id
        }
        response = self.client.patch('/api/forum/experiences/%d/' % self.experience.id,
                                     payloads, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIs(self.client.login(username='fff', password='1593562120'), True)
        response = self.client.patch('/api/forum/experiences/%d/' % self.experience.id,
                                     payloads, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIs(self.client.login(username='abc', password='abc546565132'), True)
        response = self.client.patch('/api/forum/experiences/%d/' % self.experience.id,
                                     payloads, format='json')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/forum/articles/%d/' % self.experience.content.id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['text'], 'hahaha')
        response = self.client.patch('/api/forum/experiences/%d/' % self.experience.id, {
            'content_data': {
                'text': ['unable to pass validation']
            }
        }, format='json')
        self.assertEqual(response.status_code, 400)

    # def test_auto_updating_experience_from_igem(self):
    #     """
    #     To run this test, please set UPDATE_DELTA = datetime.timedelta(seconds=1).
    #     Same reason as it is in test_restful_bricks.py
    #     """
    #     brick = Brick.objects.create(name='I718017')
    #     experience = Experience.objects.create(brick=brick, author_name='igem2010 UT-Tokyo ')
    #     self.assertEqual(experience.content, None)
    #     sleep(5)
    #     response = self.client.get('/api/forum/experiences/%d/' % experience.id)
    #     sleep(5)
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.content)
    #     self.assertNotEqual(data['content'], None)

    def test_fetch_posts_of_particular_experience(self):
        response = self.client.get('/api/forum/experiences/%d/posts/' % self.experience.id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 2)
        response = self.client.get('/api/forum/experiences/%d/posts/?author=%s'
                                   % (self.experience.id, self.user1.username))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['content'], '15210')
        # test: can not post posts
        self.client.login(username='abc', password='abc546565132')
        response = self.client.post('/api/forum/experiences/%d/posts/' % self.experience.id, {})
        self.assertEqual(response.status_code, 405)

    def test_api_url_field(self):
        response = self.client.get('/api/forum/experiences/%d/' % self.experience.id)
        data = json.loads(response.content)
        self.assertEqual(data['api_url'], 'http://testserver/api/forum/experiences/%d/' % self.experience.id)

    def test_vote(self):
        client = self.client
        # unauthenticated user can't vote
        response = client.post('/api/forum/experiences/' + str(self.post1.id) + '/up_vote/')
        self.assertEqual(response.status_code, 403)
        # vote for others
        self.assertIs(client.login(username='abc', password='abc546565132'), True)
        other = Experience.objects.create(brick=self.brick)
        response = client.post('/api/forum/experiences/' + str(other.id) + '/up_vote/')
        self.assertEqual(response.status_code, 200)
        response = client.get('/api/forum/experiences/' + str(other.id) + '/')
        post_detail = json.loads(response.content)
        # response = client.get('/api/forum/experiences/')
        # with open('experiences_list.txt','wb') as f:
        #     f.write(response.content)
        self.assertEqual(post_detail['up_vote_num'], 1)
        # vote for my experience
        mine = Experience.objects.create(author=self.user1, brick=self.brick, author_name=self.user1.username)
        response = client.post('/api/forum/experiences/' + str(mine.id) + '/up_vote/')
        self.assertEqual(response.status_code, 400)

    def test_cancel_vote(self):
        client = self.client
        other = Experience.objects.create(author=self.user2, brick=self.brick)
        self.assertIs(client.login(username='abc', password='abc546565132'), True)
        # test cancel a vote which does not exist
        response = client.post('/api/forum/experiences/9999999999999999999999999999999/cancel_up_vote/')
        self.assertEqual(response.status_code, 404)
        response = client.post('/api/forum/experiences/' + str(other.id) + '/cancel_up_vote/')
        self.assertEqual(response.status_code, 400)
        # test cancel a normal vote
        client.post('/api/forum/experiences/' + str(other.id) + '/up_vote/')
        response = client.get('/api/forum/experiences/' + str(other.id) + '/')
        data = json.loads(response.content)
        self.assertEqual(data['up_vote_num'], 1)
        client.post('/api/forum/experiences/' + str(other.id) + '/cancel_up_vote/')
        response = client.get('/api/forum/experiences/' + str(other.id) + '/')
        data = json.loads(response.content)
        self.assertEqual(data['up_vote_num'], 0)
