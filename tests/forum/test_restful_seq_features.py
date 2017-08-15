from rest_framework.test import APIClient
from django.test import TestCase
from biohub.accounts.models import User
from biohub.forum.models import Brick, Article, Experience, SeqFeature
import json


class SeqFeatureRestfulAPITest(TestCase):
    def setUp(self):
        self.document = Article.objects.create(text='aaa')
        self.brick = Brick.objects.create(name='K314110', group_name='well',
                                          document=self.document)
        self.experience = Experience.objects.create(title="hhh", brick=self.brick)
        self.seq_feature = SeqFeature.objects.create(brick=self.brick, feature_type='ha')
        self.client = APIClient()

    def test_unable_to_list_or_put_seq_features(self):
        response = self.client.get('/api/forum/seq_features/')
        self.assertEqual(response.status_code, 404)
        user = User.objects.create_test_user(username="abc")
        user.set_password("101")
        user.save()
        self.assertEqual(self.client.login(username='abc', password='101'), True)
        response = self.client.put('/api/forum/seq_features/%d/' % self.seq_feature.id, {})
        self.assertEqual(response.status_code, 405)

    def test_retrieve_seq_feature(self):
        response = self.client.get('/api/forum/seq_features/%d/' % self.seq_feature.id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['feature_type'], 'ha')
        # response = self.client.get('/api/forum/bricks/K266000/')
        # data = json.loads(response.content)
        # response = self.client.get(data['seqFeatures'][0])
        # with open("sequenceFeature_content.txt",'wb') as f:
        #     f.write(response.content)
