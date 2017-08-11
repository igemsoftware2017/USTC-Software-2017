from rest_framework.test import APIClient
from django.test import TestCase
from biohub.accounts.models import User
from biohub.forum.models import Brick, Article, Experience, SeqFeature
import json
# from time import sleep


class BrickRestfulAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(username="abc")
        self.user.set_password("123456000+")
        self.user.save()
        self.document = Article.objects.create(text='aaa')
        self.client.get('/api/forum/bricks/E0240/')
        self.brick = Brick.objects.create(name='K314110', group_name='well',
                                          document=self.document)
        self.brick = Brick.objects.get(name='E0240')

    # def test_checking_whether_database_has_brick(self):
    #     response = self.client.get('/api/forum/bricks/check_database/?name=ADD')
    #     self.assertEqual(response.status_code, 404)
    #     response = self.client.get('/api/forum/bricks/check_database/')
    #     self.assertEqual(response.status_code, 400)
    #     brick = Brick.objects.create(name='lalala')
    #     response = self.client.get('/api/forum/bricks/check_database/?name=lalala')
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_checking_whether_igem_has_brick(self):
    #     response = self.client.get('/api/forum/bricks/check_igem/?name=ADD')
    #     self.assertEqual(response.status_code, 404)
    #     response = self.client.get('/api/forum/bricks/check_igem/')
    #     self.assertEqual(response.status_code, 400)
    #     response = self.client.get('/api/forum/bricks/check_igem/?name=K314110')
    #     self.assertEqual(response.status_code, 200)

    # def test_automatically_update_bricks_when_retrieving(self):
    #     # TODO: add tests for updating experiences after bugs in ExperienceSpider is fixed.
    #     # TODO: WTF, delete updating experiences...
    #     brick = Brick.objects.get(name='K314110')
    #     brick.group_name = 'emmm'
    #     brick.save()
    #     # Because auto_now is set to True in Brick model, update_time is impossible to be set manually.
    #     # To use this test, please set UPDATE_DELTA = datetime.timedelta(seconds=1) in views.
    #     sleep(5)
    #     response = self.client.get('/api/forum/bricks/%d/' % brick.id)
    #     sleep(5)
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.content)
    #     self.assertEqual(data['group_name'], 'iGEM10_Washington')
    #     brick = Brick.objects.create(name='a')
    #     response = self.client.get('/api/forum/bricks/%d/' % brick.id)
    #     self.assertEqual(response.status_code, 500)

    def test_list_data_with_and_without_param_short(self):
        response = self.client.get('/api/forum/bricks/')
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['results'][0]['group_name'], 'well')
        response = self.client.get('/api/forum/bricks/?short=true')
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        group_name = data['results'][0].get('group_name', None)
        self.assertEqual(group_name, None)

    def test_unable_to_upload_brick(self):
        self.client.login(username='abc', password='123456000+')
        response = self.client.post('/api/forum/bricks/', {
            'name': 'haha'
        })
        self.assertEqual(response.status_code, 405)

    # def test_visiting_igem_fails_returns_500(self):
    #     # Note: Run this test without network and
    #     # comment test_checking_whether_igem_has_brick test at the same time.
    #     response = self.client.get('/api/forum/bricks/check_igem/?name=K314110')
    #     self.assertEqual(response.status_code, 500)

    def test_fetch_experiences_of_particular_brick(self):
        Experience.objects.create(title='ha', brick=self.brick, author=self.user)
        Experience.objects.create(title='emmmm', brick=self.brick)
        b = Brick.objects.create(name='a')
        Experience.objects.create(title='e', brick=b)
        response = self.client.get('/api/forum/bricks/%d/experiences/' % self.brick.id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 2)
        response = self.client.get('/api/forum/bricks/%d/experiences/?author=%s'
                                   % (self.brick.id, self.user.username))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], 'ha')
        # test short=true
        response = self.client.get('/api/forum/bricks/%d/experiences/?author=%s&short=true'
                                   % (self.brick.id, self.user.username))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 1)
        self.assertIs('pub_time' in data['results'][0], False)
        # test: can not post experiences
        self.assertEqual(self.client.login(username='abc', password='123456000+'), True)
        response = self.client.post('/api/forum/bricks/%d/experiences/' % self.brick.id, {})
        self.assertEqual(response.status_code, 405)

    def test_fetch_seq_features_of_particular_brick(self):
        SeqFeature.objects.create(brick=self.brick, name='1')
        SeqFeature.objects.create(brick=self.brick, name='2')
        b = Brick.objects.create(name='a')
        SeqFeature.objects.create(brick=b, name='1')
        response = self.client.get('/api/forum/bricks/%d/seq_features/' % self.brick.id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['results']), 2)

    def test_using_name_rather_than_id_to_retrieve_brick(self):
        response = self.client.get('/api/forum/bricks/I718017/')
        self.assertEqual(response.status_code, 200)
        # with open("brick_content.txt",'wb') as f:
        #     f.write(response.content)
        data = json.loads(response.content)
        self.assertEqual(data['group_name'], 'iGEM07_Paris')
        # TODO: continue the test after bugs in ExperienceSpider is fixed...
        experience_url = data['experience_set'][0]
        response = self.client.get(experience_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        content_url = data['content']
        response = self.client.get(content_url)
        self.assertEqual(response.status_code, 200)
        # self.assertEqual()

    def test_retrieve_using_id(self):
        response = self.client.get('/api/forum/bricks/%d/' % self.brick.id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['group_name'], 'well')
        # TODO: add the tests for fetching experiences after bugs in ExperienceSpider is fixed.
        # but the APIs are NOT designed for fetching only experiences with the existing brick

    def test_list_using_searching_param(self):
        # fetch several bricks
        response = self.client.get('/api/forum/bricks/I6101/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/forum/bricks/E0240/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/forum/bricks/I742158/')
        self.assertEqual(response.status_code, 200)
        # list all bricks
        response = self.client.get('/api/forum/bricks/')
        # with open("brick_content_list.txt",'wb') as f:
        #     f.write(response.content)
        data = json.loads(response.content)
        # there ought to be 4 items, including the one in setUp()
        # search bricks beginning with 'I'
        self.assertEqual(len(data['results']), 4)
        response = self.client.get('/api/forum/bricks/?name=I')
        data = json.loads(response.content)
        # there ought to be 2 items
        self.assertEqual(len(data['results']), 2)

    def test_star_a_brick(self):
        self.assertEqual(self.brick.star_users.all().count(), 0)
        response = self.client.post('/api/forum/bricks/%d/star/' % self.brick.id)
        self.assertEqual(response.status_code, 403)
        self.assertIs(self.client.login(username='abc', password='123456000+'), True)
        response = self.client.post('/api/forum/bricks/%d/star/' % self.brick.id)
        self.assertEqual(response.status_code, 200)
        # response = self.client.get('/api/forum/bricks/%d/' % self.brick.id)
        # with open("brick_star_content.txt",'wb') as f:
        #     f.write(response.content)
        self.assertEqual(self.brick.star_users.all().count(), 1)

    def test_cancel_star_a_brick(self):
        self.assertIs(self.brick.star(self.user), True)
        self.assertEqual(self.brick.star_users.all().count(), 1)
        response = self.client.post('/api/forum/bricks/%d/cancel_star/' % self.brick.id)
        self.assertEqual(response.status_code, 403)
        self.assertIs(self.client.login(username='abc', password='123456000+'), True)
        response = self.client.post('/api/forum/bricks/%d/cancel_star/' % self.brick.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.brick.star_users.all().count(), 0)

    def test_watch_a_brick(self):
        self.assertEqual(self.brick.watch_users.all().count(), 0)
        response = self.client.post('/api/forum/bricks/%d/watch/' % self.brick.id)
        self.assertEqual(response.status_code, 403)
        self.assertIs(self.client.login(username='abc', password='123456000+'), True)
        response = self.client.post('/api/forum/bricks/%d/watch/' % self.brick.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.brick.watch_users.all().count(), 1)

    def test_cancel_watch_a_brick(self):
        self.assertIs(self.brick.watch(self.user), True)
        self.assertEqual(self.brick.watch_users.all().count(), 1)
        response = self.client.post('/api/forum/bricks/%d/cancel_watch/' % self.brick.id)
        self.assertEqual(response.status_code, 403)
        self.assertIs(self.client.login(username='abc', password='123456000+'), True)
        response = self.client.post('/api/forum/bricks/%d/cancel_watch/' % self.brick.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.brick.watch_users.all().count(), 0)
