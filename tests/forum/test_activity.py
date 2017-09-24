from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from biohub.accounts.models import User
from biohub.forum.models import Activity, Experience
from biohub.biobrick.models import Biobrick
from biohub.forum.serializers.activity_serializers import ActivitySerializer


class ActivityTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_test_user(username='abc')
        self.user.set_password('123456000+')
        self.another_user = User.objects.create_test_user(username='another')
        self.another_user.set_password('hahaha')
        self.another_user.save()
        self.user.save()

    def test_simulation(self):
        client = APIClient()
        response = client.login(username='abc', password='123456000+')

        # fetch some bricks and experiences
        response = client.get('/api/forum/bricks/BBa_B0032/')
        data = response.data
        # publish an experience
        payload = {
            'brick_name': data['part_name'],
            'title': 'title',
            'content': {
                'text': 'this is a sample text',
                'file_ids': []
            }
        }
        response = client.post('/api/forum/experiences/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        exp_id = response.data['id']
        # rate a brick
        response = client.post('/api/forum/bricks/' + str(data['part_name']) + '/rate/', {'score': 2.9})
        self.assertEqual(response.status_code, 200)
        # comment a experience
        response = client.post(
            '/api/forum/posts/',
            {
                'experience_id': exp_id,
                'content': 'Uhhh...what you wrote is holly shit!'
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        # star an experience
        client.logout()
        client.login(username='another', password='hahaha')
        response = client.post('/api/forum/experiences/' + str(exp_id) + '/vote/')
        self.assertEqual(response.status_code, 200)
        # watch a brick
        response = client.post('/api/forum/bricks/' + str(data['part_name']) + '/watch/')
        self.assertEqual(response.status_code, 200)
        # examine activities
        act_serializer = ActivitySerializer(
            Activity.objects.all(), many=True)
        act_serializer.data

        client.get('/api/forum/activities/')

    def test_only_fetching_one_user_activities(self):
        client = APIClient()
        brick = Biobrick.objects.get(part_name='BBa_B0032')
        meta = brick.ensure_meta_exists(fetch=True)
        Experience.objects.create(brick=meta, author=self.user)
        self.assertTrue(brick.watch(self.user))
        Experience.objects.create(brick=meta, author=self.another_user)
        self.assertTrue(brick.watch(self.another_user))
        self.assertTrue(brick.rate(self.user, 2.3))
        response = client.get('/api/forum/activities/?user=abc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)

    def test_fetching_specific_type_activities(self):
        client = APIClient()

        brick = Biobrick.objects.get(part_name='BBa_B0032')
        meta = brick.ensure_meta_exists(fetch=True)
        Experience.objects.create(brick=meta, author=self.user)
        self.assertTrue(brick.watch(self.user))
        Experience.objects.create(brick=meta, author=self.another_user)
        self.assertTrue(brick.watch(self.another_user))
        self.assertTrue(brick.rate(self.user, 2.3))

        response = client.get('/api/forum/activities/?user=abc&type=Rating')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['type'], 'Rating')

        response = client.get('/api/forum/activities/?user=abc&type=Rating,Watch')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(
            set(x['type'] for x in response.data['results']),
            {'Rating', 'Watch'}
        )
