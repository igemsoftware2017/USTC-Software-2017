import json
from rest_framework.test import APIClient
from django.test import TestCase
from biohub.accounts.models import User
from biohub.forum.models import Post, Experience, Brick
import json


class PostRestfulAPITest(TestCase):
    def setUp(self):
        # don't pass the password on create() method,
        # or the database won't save the hash, but only the raw password.
        self.user1 = User.objects.create(username="abc")
        self.user1.set_password("abc546565132")
        self.user1.save()
        self.brick = Brick.objects.create(name='K314110')
        self.experience = Experience.objects.create(title="hhh", author=self.user1, brick=self.brick)
        self.user2 = User.objects.create(username="fff")
        self.user2.set_password("1593562120")
        self.user2.save()
        self.post1 = Post.objects.create(author=self.user1, content="15210", experience=self.experience)
        self.post2 = Post.objects.create(author=self.user2, content="777777", experience=self.experience)

    def test_unauthenticated_visitors_can_only_read_post(self):
        client = APIClient()
        response = client.get('/api/forum/posts/')
        self.assertEqual(response.status_code, 200)
        response = client.post('/api/forum/posts/', {
            'experience_id': self.experience.id,
            'content': 'test_test_test'
        })
        self.assertEqual(response.status_code, 403)

    def test_authenticated_visitors_can_read_create_post(self):
        client = APIClient()
        self.assertIs(client.login(username='abc', password='abc546565132'), True)
        response = client.post('/api/forum/posts/', {
            'experience_id': self.experience.id,
            'content': 'test_test_test',
        })
        self.assertEqual(response.status_code, 201)
        response = client.get('/api/forum/posts/')
        self.assertEqual(response.status_code, 200)

    def test_modify_my_post(self):
        client = APIClient()
        self.assertIs(client.login(username='abc', password='abc546565132'), True)
        my_post = Post.objects.create(author=self.user1, content='dgfl', experience=self.experience)
        response = client.patch('/api/forum/posts/' + str(my_post.id) + '/', {
            'content': 'sdgfhfghgjgj'
        })
        self.assertEqual(response.status_code, 200)

    def test_modify_posts_of_others(self):
        client = APIClient()
        self.assertIs(client.login(username='abc', password='abc546565132'), True)
        other_post = Post.objects.create(author=self.user2, content='lll', experience=self.experience)
        response = client.patch('/api/forum/posts/' + str(other_post.id) + '/', {
            'content': 'wawawawa'
        })
        self.assertEqual(response.status_code, 403)

    def test_vote(self):
        client = APIClient()
        # unauthenticated user can't vote
        response = client.post('/api/forum/posts/' + str(self.post1.id) + '/up_vote/')
        self.assertEqual(response.status_code, 403)
        # vote for others
        self.assertIs(client.login(username='abc', password='abc546565132'), True)
        other_post = Post.objects.create(author=self.user2, content='125', experience=self.experience)
        response = client.post('/api/forum/posts/' + str(other_post.id) + '/up_vote/')
        self.assertEqual(response.status_code, 200)
        response = client.get('/api/forum/posts/' + str(other_post.id) + '/')
        post_detail = json.loads(response.content)
        self.assertEqual(post_detail['up_vote_num'], 1)
        # vote for my post
        my_post = Post.objects.create(author=self.user1, content='dgfl', experience=self.experience)
        response = client.post('/api/forum/posts/' + str(my_post.id) + '/up_vote/')
        self.assertEqual(response.status_code, 400)

    def test_cancel_vote(self):
        client = APIClient()
        other_post = Post.objects.create(author=self.user2, content='125', experience=self.experience)
        self.assertIs(client.login(username='abc', password='abc546565132'), True)
        # test cancel a vote which does not exist
        response = client.post('/api/forum/posts/9999999999999999999999999999999/cancel_up_vote/')
        self.assertEqual(response.status_code, 404)
        response = client.post('/api/forum/posts/' + str(other_post.id) + '/cancel_up_vote/')
        self.assertEqual(response.status_code, 400)
        # test cancel a normal vote
        client.post('/api/forum/posts/' + str(other_post.id) + '/up_vote/')
        response = client.get('/api/forum/posts/' + str(other_post.id) + '/')
        post_detail = json.loads(response.content)
        self.assertEqual(post_detail['up_vote_num'], 1)
        client.post('/api/forum/posts/' + str(other_post.id) + '/cancel_up_vote/')
        response = client.get('/api/forum/posts/' + str(other_post.id) + '/')
        post_detail = json.loads(response.content)
        self.assertEqual(post_detail['up_vote_num'], 0)

    def test_listing_posts(self):
        client = APIClient()
        self.post1.is_visible = False
        self.post1.save()
        response = client.get('/api/forum/posts/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
        response = client.get('/api/forum/posts/?author=abc')
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 0)
        self.assertIs(client.login(username='abc', password='abc546565132'), True)
        response = client.get('/api/forum/posts/?author=abc')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
