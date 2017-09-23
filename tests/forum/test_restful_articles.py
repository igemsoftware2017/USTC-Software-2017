from rest_framework.test import APIClient
from django.test import TestCase
from biohub.accounts.models import User
from biohub.forum.models import Article
from biohub.forum.serializers.article_serializers import ArticleSerializer
from biohub.core.files.models import File
import tempfile
import os


def make_file():

    name = tempfile.mktemp(dir='/tmp')

    with open(name, 'w'):
        pass

    return open(name, 'r')


class ArticleRestfulAPITest(TestCase):

    def setUp(self):
        user = User.objects.create_test_user(username='abc')
        user.set_password('123456000+')
        user.save()

        self.files = []

        for _ in range(10):
            f = make_file()
            self.files.append(File.objects.create_from_file(f))
            f.close()

        self.article = Article.objects.create(text="124651321")
        self.article.files.add(*self.files)
        self.client = APIClient()

    def make_new_file_ids(self):
        with make_file() as f:
            new = File.objects.create_from_file(f)

        return new, [o.id for o in self.files[:5]] + [new.id]

    def test_update_files_serializer(self):

        def f(new, file_ids):
            s = ArticleSerializer(self.article, data={'file_ids': file_ids}, partial=True)
            self.assertTrue(s.is_valid())
            s.save()

        self._test_update_files(f)

    def test_update_files(self):
        self._test_update_files(lambda new, file_ids: self.article.update_files(file_ids))

    def _test_update_files(self, action):
        new, file_ids = self.make_new_file_ids()

        action(new, file_ids)

        self.assertIn(new.id, self.article.files.values_list('id', flat=True))

        for item in self.files[:5]:
            self.assertTrue(os.path.exists(item.file.path))

        for item in self.files[5:]:
            self.assertFalse(os.path.exists(item.file.path))

    def test_list_articles_and_get_details_articles(self):
        response = self.client.get('/api/forum/articles/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/api/forum/articles/%d/' % self.article.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.client.login(username='abc', password='123456000+'))
        response = self.client.get('/api/forum/articles/')
        self.assertEqual(response.status_code, 404)

    def test_unable_to__change_text(self):
        response = self.client.patch('/api/forum/articles/%d/' % self.article.id, {
            'text': 'jjjjjjjjjjj'
        })
        self.assertEqual(response.status_code, 405)
        self.assertTrue(self.client.login(username='abc', password='123456000+'))
        response = self.client.patch('/api/forum/articles/%d/' % self.article.id, {
            'text': 'jjjjjjjjjjj'
        })
        self.assertEqual(response.status_code, 405)

    def test_unable_to_change_files(self):
        with open(os.path.join(tempfile.gettempdir(), 'for_test2.txt'), "w") as f:
            pass
        with open(os.path.join(tempfile.gettempdir(), 'for_test2.txt'), "r") as f:
            file = File.objects.create_from_file(f)
        self.assertTrue(self.client.login(username='abc', password='123456000+'))
        response = self.client.put('/api/forum/articles/%d/' % self.article.id, {
            'text': 'jjjjjjjjjjj',
            'file_ids': [file.id]
        })
        self.assertEqual(response.status_code, 405)
