from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from biohub.accounts.models import User
from biohub.forum.models import Post, Experience
from biohub.biobrick.models import Biobrick


class PostRestfulAPITest(APITestCase):

    def setUp(self):
        # don't pass the password on create() method,
        # or the database won't save the hash, but only the raw password.
        self.user1 = User.objects.create_test_user(username="abc")
        self.user1.set_password("abc546565132")
        self.user1.save()
        self.brick = Biobrick.objects.get(part_name='BBa_K314110')
        self.experience = Experience.objects.create(title="hhh", author=self.user1, brick=self.brick.meta_instance)
        self.user2 = User.objects.create_test_user(username="fff")
        self.user2.set_password("1593562120")
        self.user2.save()
        self.post1 = Post.objects.create(author=self.user1, content="15210", experience=self.experience)
        self.post2 = Post.objects.create(author=self.user2, content="777777", experience=self.experience)

    def test_10_items_per_page(self):
        for _ in range(20):
            Post.objects.create(author=self.user1, content='23333', experience=self.experience)

        self.client.force_authenticate(self.user1)

        data = self.client.get('/api/forum/posts/?experience_id={}'.format(self.experience.id)).data
        self.assertEqual(len(data['results']), 10)
        self.assertIn('avatar_url', data['results'][0]['author'])

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
        self.assertTrue(client.login(username='abc', password='abc546565132'))
        experience = Experience.objects.create(title="hhh", author=self.user1, brick=self.brick.meta_instance)
        response = client.post('/api/forum/posts/', {
            'experience_id': experience.id,
            'content': 'test_test_test',
        })

        self.assertEqual(
            self.client.get(
                '/api/forum/experiences/{}/'.format(experience.id)
            ).data['posts_num'],
            1
        )
        self.assertEqual(response.status_code, 201)
        response = client.get('/api/forum/posts/')
        self.assertEqual(response.status_code, 200)

    def test_modify_my_post(self):
        client = APIClient()
        self.assertTrue(client.login(username='abc', password='abc546565132'))
        my_post = Post.objects.create(author=self.user1, content='dgfl', experience=self.experience)
        response = client.patch('/api/forum/posts/' + str(my_post.id) + '/', {
            'content': 'sdgfhfghgjgj'
        })
        self.assertEqual(response.status_code, 200)

    def test_modify_posts_of_others(self):
        client = APIClient()
        self.assertTrue(client.login(username='abc', password='abc546565132'))
        other_post = Post.objects.create(author=self.user2, content='lll', experience=self.experience)
        response = client.patch('/api/forum/posts/' + str(other_post.id) + '/', {
            'content': 'wawawawa'
        })
        self.assertEqual(response.status_code, 403)

    def test_listing_posts(self):
        client = APIClient()
        self.post1.is_visible = False
        self.post1.save()
        response = client.get('/api/forum/posts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        response = client.get('/api/forum/posts/?author=abc')
        self.assertEqual(len(response.data['results']), 0)
        self.assertTrue(client.login(username='abc', password='abc546565132'))
        response = client.get('/api/forum/posts/?author=abc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_throttle(self):
        from biohub.core.conf import settings as biohub_settings
        import time

        biohub_settings.THROTTLE['post'] = 1

        self.client.force_authenticate(self.user1)
        response = self.client.post('/api/forum/posts/', {
            'experience_id': self.experience.id,
            'content': 'test_test_test'
        })
        self.assertEqual(response.status_code, 429)
        time.sleep(1)
        response = self.client.post('/api/forum/posts/', {
            'experience_id': self.experience.id,
            'content': 'test_test_test'
        })
        self.assertNotEqual(response.status_code, 429)

        biohub_settings.THROTTLE['post'] = 0
