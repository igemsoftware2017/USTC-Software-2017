from rest_framework.test import APIClient
from django.test import TestCase
from biohub.accounts.models import User
from biohub.forum.models import Article
from biohub.core.files.models import File
import tempfile
import os
import json


class ArticleRestfulAPITest(TestCase):
    def setUp(self):
        user = User.objects.create(username='abc')
        user.set_password('123456000+')
        user.save()
        with open(os.path.join(tempfile.gettempdir(), 'for_test.txt'), "w") as f:
            pass
        with open(os.path.join(tempfile.gettempdir(), 'for_test.txt'), "r") as f:
            self.file = File.objects.create_from_file(f)
        self.article = Article.objects.create(text="124651321")
        self.article.files.add(self.file)
        self.client = APIClient()

    def test_list_articles_and_get_details_articles(self):
        response = self.client.get('/api/forum/articles/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/api/forum/articles/%d/' % self.article.id)
        # with open("articledata.txt",'wb') as f:
        #     f.write(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIs(self.client.login(username='abc', password='123456000+'), True)
        response = self.client.get('/api/forum/articles/')
        self.assertEqual(response.status_code, 404)

    def test_unable_to__change_text(self):
        response = self.client.patch('/api/forum/articles/%d/' % self.article.id, {
            'text': 'jjjjjjjjjjj'
        })
        self.assertEqual(response.status_code, 405)
        self.assertIs(self.client.login(username='abc', password='123456000+'), True)
        response = self.client.patch('/api/forum/articles/%d/' % self.article.id, {
            'text': 'jjjjjjjjjjj'
        })
        self.assertEqual(response.status_code, 405)
        # response = self.client.get('/api/forum/articles/%d/' % self.article.id)
        # self.assertEqual(json.loads(response.content)['text'], 'jjjjjjjjjjj')
        # user_other = User.objects.create(username="ddd")
        # user_other.set_password("123456000+")
        # user_other.save()
        # self.article = Article.objects.create(text="124651321")
        # response = self.client.patch('/api/forum/articles/%d/' % self.article.id, {
        #     'text': 'jjjjjjjjjjj'
        # })
        # self.assertEqual(response.status_code, 405)

    def test_unable_to_change_files(self):
        with open(os.path.join(tempfile.gettempdir(), 'for_test2.txt'), "w") as f:
            pass
        with open(os.path.join(tempfile.gettempdir(), 'for_test2.txt'), "r") as f:
            file = File.objects.create_from_file(f)
        self.assertIs(self.client.login(username='abc', password='123456000+'), True)
        response = self.client.put('/api/forum/articles/%d/' % self.article.id, {
            'text': 'jjjjjjjjjjj',
            'file_ids': [file.id]
        })
        self.assertEqual(response.status_code, 405)
        # self.assertEqual(self.article.files.count(), 1)
        # self.article.files.get(pk=file.id)
