import json
import os
import tempfile

from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from biohub.accounts.models import User
from biohub.forum.models import Activity, ActivityParam, Experience, Brick
from biohub.forum.serializers import ActivityParamSerializer, ActivitySerializer


class ActivityParamTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='abc')
        self.user.set_password('123456000+')
        another_user = User.objects.create(username='another')     
        another_user.set_password('hahaha')
        another_user.save()
        self.user.save()

    def test_param_serialization(self):
        self.param = ActivityParam.objects.create(
            type='Experience', user=self.user, partName='B0015', expLink='/api/forum/experiences/15', intro='')

        param_serializer = ActivityParamSerializer(self.param)
        data = param_serializer.data
        # self.assertEqual(len(data),4)
        param2 = ActivityParam.objects.create(
            type='Comment', user=self.user, partName='B0015', expLink='/api/forum/experiences/15', intro='')
        param3 = ActivityParam.objects.create(
            type='Star', user=self.user, partName='B0015', expLink='/api/forum/experiences/15', intro='')
        param4 = ActivityParam.objects.create(
            type='Rating', user=self.user, partName='B0015', expLink='/api/foorum/experiences/15', score=3.7)
        set_serializer = ActivityParamSerializer(
            ActivityParam.objects.all(), many=True)
        data_set = set_serializer.data
        pass

    def test_simulation(self):
        client = APIClient()
        response = client.login(username='abc', password='123456000+')

        ActivityParam.objects.all().delete()
        set_serializer = ActivityParamSerializer(
            ActivityParam.objects.all(), many=True)
        data_set = set_serializer.data
        # fetch some bricks and experiences
        response = client.get('/api/forum/bricks/B0032/')
        data = json.loads(response.content)
        # publish an experience
        loads2 = {'brick_id': data['id'], 'content_data': {
            'text': 'this is a sample text','file_ids':[]}}
        response = client.post('/api/forum/experiences/', loads2, format='json')
        self.assertEqual(response.status_code, 201)
        exp_id = (json.loads(response.content))['id']
        # rate a brick
        response = client.post('/api/forum/bricks/'+str(data['id'])+'/rate/',{'score':2.9})
        self.assertEqual(response.status_code, 200)        
        # comment a experience
        response = client.post('/api/forum/posts/',{'experience_id':exp_id,'content':'Uhhh...what you wrote is holly shit!'},format='json')
        self.assertEqual(response.status_code, 201)
        # star an experience
        client.logout()
        client.login(username='another',password='hahaha')
        response = client.post('/api/forum/experiences/'+str(exp_id)+'/up_vote/')
        self.assertEqual(response.status_code, 200)
        # watch a brick
        response = client.post('/api/forum/bricks/'+str(data['id'])+'/watch/')
        self.assertEqual(response.status_code, 200)
        exp_set = Experience.objects.all()
        # examine activities
        act_serializer = ActivitySerializer(
            Activity.objects.all(), many=True)
        data_set = act_serializer.data

        response = client.get('/api/forum/activities/')
        with open(os.path.join(tempfile.gettempdir(),'activities_data.txt'),'wb') as f:
            f.write(response.content)
        pass

    def test_only_fetching_one_user_activities(self):
        client = APIClient()
        self.assertIs(client.login(username='abc', password='123456000+'), True)
        brick = Brick.objects.create(name='emmm')
        Experience.objects.create(brick=brick, author=self.user)
        brick.watch(self.user)
        brick.rate(2.3, self.user)
        response = client.get('/api/forum/activities/?user=abc')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        # print(response.content)
        self.assertEqual(len(data['results']), 3)
